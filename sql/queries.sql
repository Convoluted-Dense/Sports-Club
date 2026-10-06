-- ============================================================================
-- SPORTS CLUB MEMBERSHIP AND TOURNAMENT MANAGEMENT SYSTEM
-- Complex Data Retrieval, Reports, Joins, Aggregations & Subqueries
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Active Membership Directory with Plan & Subscription Details
-- (Multi-Table Inner and Lateral Joins with Payment History)
-- ----------------------------------------------------------------------------
SELECT 
    m.member_id,
    m.name AS member_name,
    m.gender,
    m.email,
    m.phone,
    m.status AS membership_status,
    COALESCE(latest_pay.plan_name, 'No Active Plan') AS current_plan,
    COALESCE(latest_pay.duration_months || ' Month(s)', 'N/A') AS plan_duration,
    COALESCE('₹' || TO_CHAR(latest_pay.fee_amount, 'FM99990.00'), 'N/A') AS plan_rate,
    COALESCE(latest_pay.payment_status, 'Unpaid') AS payment_status
FROM member m
LEFT JOIN LATERAL (
    SELECT mp.plan_name, mp.duration_months, mp.fee_amount, p.status AS payment_status
    FROM payment p
    JOIN membership_plan mp ON p.plan_id = mp.plan_id
    WHERE p.member_id = m.member_id
    ORDER BY p.payment_date DESC
    LIMIT 1
) latest_pay ON TRUE
WHERE m.status = 'Active'
ORDER BY m.name ASC;

-- ----------------------------------------------------------------------------
-- QUERY 2: Fee Collection & Overdue Payment Summary (Diverse Status Check)
-- (Categorizing Paid vs. Expired vs. Pending vs. Failed dues)
-- ----------------------------------------------------------------------------
SELECT 
    m.member_id,
    m.name AS member_name,
    m.email,
    p.amount AS billed_amount,
    p.payment_mode,
    p.payment_date,
    p.status AS payment_status,
    CASE 
        WHEN p.status = 'Paid' THEN 'Account in Good Standing'
        WHEN p.status = 'Expired' THEN 'Subscription Expired - Renewal Required'
        WHEN p.status = 'Pending' THEN 'Payment Processing'
        WHEN p.status = 'Failed' THEN 'Transaction Failed - Re-attempt Required'
        ELSE 'Refunded / Disputed'
    END AS account_remarks
FROM payment p
JOIN member m ON p.member_id = m.member_id
ORDER BY p.payment_date DESC;

-- ----------------------------------------------------------------------------
-- QUERY 3: Club Roster Breakdown by Sport, Coach, and Leadership Roles
-- (Aggregation with STRING_AGG, GROUP BY, and Multi-Level Joins)
-- ----------------------------------------------------------------------------
SELECT 
    c.club_name,
    s.sport_name,
    co.name AS head_coach,
    COUNT(cm.member_id) AS registered_athletes,
    STRING_AGG(m.name || ' (' || cm.role || ')', '; ') AS team_roster
FROM club c
JOIN sport s ON c.sport_id = s.sport_id
LEFT JOIN coach co ON c.coach_id = co.coach_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
LEFT JOIN member m ON cm.member_id = m.member_id
GROUP BY c.club_name, s.sport_name, co.name
ORDER BY c.club_name;

-- ----------------------------------------------------------------------------
-- QUERY 4: Revenue Analytics by Membership Tier & Payment Mode
-- (Aggregate Functions: SUM, AVG, COUNT with GROUP BY and HAVING)
-- ----------------------------------------------------------------------------
SELECT 
    mp.plan_name,
    p.payment_mode,
    COUNT(p.payment_id) AS total_transactions,
    SUM(p.amount) AS total_collected,
    ROUND(AVG(p.amount), 2) AS average_ticket_size
FROM payment p
JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE p.status = 'Paid'
GROUP BY mp.plan_name, p.payment_mode
HAVING SUM(p.amount) > 0
ORDER BY total_collected DESC;

-- ----------------------------------------------------------------------------
-- QUERY 5: Scheduled Training Sessions by Sport, Coach, and Facility
-- (Multi-Table Joins across Sport, Coach, Facility, and Training Session)
-- ----------------------------------------------------------------------------
SELECT 
    ts.session_id,
    s.sport_name,
    co.name AS coach_name,
    co.phone AS coach_phone,
    f.name AS venue_name,
    f.location AS venue_location,
    ts.session_date,
    ts.start_time || ' - ' || ts.end_time AS time_slot,
    ts.capacity AS participant_capacity,
    ts.status AS session_status
FROM training_session ts
JOIN sport s ON ts.sport_id = s.sport_id
JOIN coach co ON ts.coach_id = co.coach_id
JOIN facility f ON ts.venue_id = f.facility_id
ORDER BY ts.session_date DESC, ts.start_time ASC;

-- ----------------------------------------------------------------------------
-- QUERY 6: Tournament Fixtures & Competing Squads Breakdown
-- (Multi-table Joins across Fixture, Tournament, Team, Club, and Venue)
-- ----------------------------------------------------------------------------
SELECT 
    t.name AS tournament_title,
    s.sport_name,
    f.fixture_id,
    t1.team_name AS team_1,
    c1.club_name AS club_1,
    t2.team_name AS team_2,
    c2.club_name AS club_2,
    f.fixture_date,
    fac.name AS stadium_venue,
    f.status AS match_status
FROM fixture f
JOIN tournament t ON f.tournament_id = t.tournament_id
JOIN sport s ON t.sport_id = s.sport_id
JOIN team t1 ON f.team1_id = t1.team_id
JOIN club c1 ON t1.club_id = c1.club_id
JOIN team t2 ON f.team2_id = t2.team_id
JOIN club c2 ON t2.club_id = c2.club_id
JOIN facility fac ON f.venue_id = fac.facility_id
ORDER BY f.fixture_date ASC;

-- ----------------------------------------------------------------------------
-- QUERY 7: Competitive Squads Overview by Club, Sport, and Assigned Coaches
-- (Querying the v_team_overview reporting view)
-- ----------------------------------------------------------------------------
SELECT 
    team_id,
    team_name,
    club_name,
    sport_name,
    coach_name,
    coach_phone,
    created_date AS squad_founded,
    team_status
FROM v_team_overview
ORDER BY sport_name, club_name, team_name;

-- ----------------------------------------------------------------------------
-- QUERY 8: Members with Expired or Pending Dues (Nested Subquery & Filtering)
-- ----------------------------------------------------------------------------
SELECT 
    m.member_id,
    m.name AS member_name,
    m.email,
    m.phone,
    m.status AS membership_status,
    p.status AS payment_status,
    p.amount AS unpaid_fee,
    p.payment_date
FROM member m
JOIN payment p ON m.member_id = p.member_id
WHERE p.status IN ('Expired', 'Pending', 'Failed')
  OR m.status IN ('Expired', 'Pending')
ORDER BY p.payment_date ASC;

-- ----------------------------------------------------------------------------
-- QUERY 9: Facility Usage Heatmap (Training Sessions vs Tournament Matches)
-- (Facility utilization aggregation across multiple activity tables)
-- ----------------------------------------------------------------------------
SELECT 
    facility_id,
    facility_name,
    facility_type,
    location,
    capacity,
    current_status,
    total_training_sessions,
    total_tournament_fixtures,
    total_events_hosted
FROM v_facility_utilization
ORDER BY total_events_hosted DESC;

-- ----------------------------------------------------------------------------
-- QUERY 10: Top Performing Sports by Athlete Affiliation (Window Function DENSE_RANK)
-- ----------------------------------------------------------------------------
SELECT 
    s.sport_name,
    COUNT(DISTINCT cm.member_id) AS total_enrolled_athletes,
    DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT cm.member_id) DESC) AS popularity_rank
FROM sport s
LEFT JOIN club c ON s.sport_id = c.sport_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
GROUP BY s.sport_name
ORDER BY popularity_rank ASC;

-- ----------------------------------------------------------------------------
-- QUERY 11: Transaction Demo - Registering New Member with Payment Atomically
-- ----------------------------------------------------------------------------
BEGIN;

INSERT INTO member (name, gender, phone, email, address, join_date, status)
VALUES ('Vikramaditya Roy', 'Male', '+91-9820099887', 'vikram.roy@gmail.com', '77 Heritage Square, Indiranagar, Bengaluru', CURRENT_DATE, 'Active')
RETURNING member_id;

-- Insert corresponding payment for new member
INSERT INTO payment (member_id, plan_id, amount, payment_mode, payment_date, status, transaction_ref)
VALUES (currval('member_member_id_seq'), 102, 1399.90, 'UPI', CURRENT_DATE, 'Paid', 'TXN_20261001_099');

COMMIT;
