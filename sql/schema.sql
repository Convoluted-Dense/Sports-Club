-- ============================================================================
-- SPORTS CLUB MEMBERSHIP AND TOURNAMENT MANAGEMENT SYSTEM
-- Relational Database Management System - PostgreSQL DDL Schema
-- Normalized to Third Normal Form (3NF) - Exactly 12 Tables
-- ============================================================================

-- Drop existing tables and views if they exist (in reverse dependency order)
DROP VIEW IF EXISTS v_team_overview CASCADE;
DROP VIEW IF EXISTS v_tournament_standings CASCADE;
DROP VIEW IF EXISTS v_member_subscription_status CASCADE;
DROP VIEW IF EXISTS v_club_rosters CASCADE;
DROP VIEW IF EXISTS v_facility_utilization CASCADE;
DROP VIEW IF EXISTS v_upcoming_fixtures CASCADE;
DROP VIEW IF EXISTS v_financial_revenue_summary CASCADE;

DROP TABLE IF EXISTS result CASCADE;
DROP TABLE IF EXISTS fixture CASCADE;
DROP TABLE IF EXISTS tournament CASCADE;
DROP TABLE IF EXISTS team CASCADE;
DROP TABLE IF EXISTS training_session CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS club_member CASCADE;
DROP TABLE IF EXISTS member CASCADE;
DROP TABLE IF EXISTS club CASCADE;
DROP TABLE IF EXISTS coach CASCADE;
DROP TABLE IF EXISTS facility CASCADE;
DROP TABLE IF EXISTS sport CASCADE;
DROP TABLE IF EXISTS membership_plan CASCADE;

-- ----------------------------------------------------------------------------
-- 1. TABLE: membership_plan
-- Stores subscription tier definitions and pricing (100-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE membership_plan (
    plan_id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    duration_months INT NOT NULL CHECK (duration_months > 0),
    fee_amount NUMERIC(10, 2) NOT NULL CHECK (fee_amount >= 0)
);

-- ----------------------------------------------------------------------------
-- 2. TABLE: sport
-- Stores distinct sports activities offered by the club complex (200-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE sport (
    sport_id SERIAL PRIMARY KEY,
    sport_name VARCHAR(100) NOT NULL UNIQUE
);

-- ----------------------------------------------------------------------------
-- 3. TABLE: facility
-- Venues and courts available within the sports club complex (300-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE facility (
    facility_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'Available' 
        CHECK (status IN ('Available', 'Booked', 'Under Maintenance'))
);

-- ----------------------------------------------------------------------------
-- 4. TABLE: coach
-- Professional sports coaches and certified instructors (400-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE coach (
    coach_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE
);

-- ----------------------------------------------------------------------------
-- 5. TABLE: club
-- Club franchises/teams organized under a sport, coached by a coach (500-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE club (
    club_id SERIAL PRIMARY KEY,
    club_name VARCHAR(100) NOT NULL,
    sport_id INT NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
    coach_id INT REFERENCES coach(coach_id) ON DELETE SET NULL,
    created_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active' 
        CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

-- ----------------------------------------------------------------------------
-- 6. TABLE: member
-- Registered club members/athletes (1000-Series IDs: 27 Members).
-- ----------------------------------------------------------------------------
CREATE TABLE member (
    member_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female')),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL DEFAULT '482c811da5d5b4bc6d497ffa98491e38',
    address VARCHAR(255) NOT NULL,
    join_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active' 
        CHECK (status IN ('Active', 'Expired', 'Pending', 'Suspended', 'Inactive'))
);

-- ----------------------------------------------------------------------------
-- 7. TABLE: club_member
-- Decomposes N:N relationship between Member and Club with atomic roles (1NF).
-- ----------------------------------------------------------------------------
CREATE TABLE club_member (
    member_id INT NOT NULL REFERENCES member(member_id) ON DELETE CASCADE,
    club_id INT NOT NULL REFERENCES club(club_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'Player',
    join_date DATE NOT NULL,
    PRIMARY KEY (member_id, club_id, role)
);

-- ----------------------------------------------------------------------------
-- 8. TABLE: payment
-- Financial transaction ledger for plan subscriptions (8000-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE payment (
    payment_id SERIAL PRIMARY KEY,
    member_id INT NOT NULL REFERENCES member(member_id) ON DELETE RESTRICT,
    plan_id INT NOT NULL REFERENCES membership_plan(plan_id) ON DELETE RESTRICT,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    payment_mode VARCHAR(50) NOT NULL 
        CHECK (payment_mode IN ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash', 'Bank Transfer')),
    payment_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Paid' 
        CHECK (status IN ('Paid', 'Pending', 'Failed', 'Refunded', 'Expired')),
    transaction_ref VARCHAR(100) UNIQUE
);

-- ----------------------------------------------------------------------------
-- 9. TABLE: training_session
-- Training and practice sessions held at specific venues (600-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE training_session (
    session_id SERIAL PRIMARY KEY,
    sport_id INT NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
    coach_id INT NOT NULL REFERENCES coach(coach_id) ON DELETE RESTRICT,
    venue_id INT NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL CHECK (end_time > start_time),
    capacity INT NOT NULL CHECK (capacity > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'Scheduled' 
        CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'In Progress', 'Full'))
);

-- ----------------------------------------------------------------------------
-- 10. TABLE: team
-- Competitive squad units formed within clubs (700-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE team (
    team_id SERIAL PRIMARY KEY,
    club_id INT NOT NULL REFERENCES club(club_id) ON DELETE CASCADE,
    team_name VARCHAR(100) NOT NULL,
    sport_id INT NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
    coach_id INT REFERENCES coach(coach_id) ON DELETE SET NULL,
    created_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active' 
        CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

-- ----------------------------------------------------------------------------
-- 11. TABLE: tournament
-- Organized competitive events, championships, and leagues (9000-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE tournament (
    tournament_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sport_id INT NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date >= start_date),
    type VARCHAR(50) NOT NULL 
        CHECK (type IN ('Knockout', 'Round Robin', 'League', 'Single Elimination', 'Open Championship'))
);

-- ----------------------------------------------------------------------------
-- 12. TABLE: fixture
-- Individual matches between two teams within a tournament (910-Series IDs).
-- ----------------------------------------------------------------------------
CREATE TABLE fixture (
    fixture_id SERIAL PRIMARY KEY,
    tournament_id INT NOT NULL REFERENCES tournament(tournament_id) ON DELETE CASCADE,
    team1_id INT NOT NULL REFERENCES team(team_id) ON DELETE RESTRICT,
    team2_id INT NOT NULL REFERENCES team(team_id) ON DELETE RESTRICT,
    fixture_date TIMESTAMP NOT NULL,
    venue_id INT NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL DEFAULT 'Scheduled' 
        CHECK (status IN ('Scheduled', 'Completed', 'Postponed', 'Cancelled', 'Live')),
    CHECK (team1_id <> team2_id)
);

-- ============================================================================
-- PERFORMANCE INDEXES (Optimizing frequent lookups, joins & filters)
-- ============================================================================
CREATE INDEX idx_member_email ON member(email);
CREATE INDEX idx_member_status ON member(status);
CREATE INDEX idx_payment_member ON payment(member_id);
CREATE INDEX idx_payment_status ON payment(status);
CREATE INDEX idx_payment_date ON payment(payment_date);
CREATE INDEX idx_club_sport ON club(sport_id);
CREATE INDEX idx_club_member_club ON club_member(club_id);
CREATE INDEX idx_training_venue_date ON training_session(venue_id, session_date);
CREATE INDEX idx_team_club ON team(club_id);
CREATE INDEX idx_team_sport ON team(sport_id);
CREATE INDEX idx_fixture_tournament ON fixture(tournament_id);
CREATE INDEX idx_fixture_team1 ON fixture(team1_id);
CREATE INDEX idx_fixture_team2 ON fixture(team2_id);
CREATE INDEX idx_fixture_date ON fixture(fixture_date);
CREATE INDEX idx_fixture_venue ON fixture(venue_id);

-- ============================================================================
-- BUSINESS INTEGRITY TRIGGERS & FUNCTIONS
-- ============================================================================

-- Trigger 1: Validate competing teams play the tournament sport
CREATE OR REPLACE FUNCTION fn_check_fixture_team_sport()
RETURNS TRIGGER AS $$
DECLARE
    v_tourn_sport INT;
    v_t1_sport INT;
    v_t2_sport INT;
BEGIN
    SELECT sport_id INTO v_tourn_sport FROM tournament WHERE tournament_id = NEW.tournament_id;
    SELECT sport_id INTO v_t1_sport FROM team WHERE team_id = NEW.team1_id;
    SELECT sport_id INTO v_t2_sport FROM team WHERE team_id = NEW.team2_id;

    IF v_t1_sport <> v_tourn_sport OR v_t2_sport <> v_tourn_sport THEN
        RAISE EXCEPTION 'Fixture Sport Mismatch: Both competing teams must belong to tournament sport ID %', v_tourn_sport;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_fixture_team_sport ON fixture;
CREATE TRIGGER trg_check_fixture_team_sport
BEFORE INSERT OR UPDATE ON fixture
FOR EACH ROW EXECUTE FUNCTION fn_check_fixture_team_sport();

-- Trigger 2: Prevent overlapping training sessions at the same facility venue
CREATE OR REPLACE FUNCTION fn_check_venue_session_overlap()
RETURNS TRIGGER AS $$
DECLARE
    v_overlap_count INT;
BEGIN
    SELECT COUNT(*) INTO v_overlap_count
    FROM training_session
    WHERE venue_id = NEW.venue_id
      AND session_date = NEW.session_date
      AND session_id <> COALESCE(NEW.session_id, -1)
      AND status NOT IN ('Cancelled')
      AND (
          (NEW.start_time >= start_time AND NEW.start_time < end_time) OR
          (NEW.end_time > start_time AND NEW.end_time <= end_time) OR
          (NEW.start_time <= start_time AND NEW.end_time >= end_time)
      );

    IF v_overlap_count > 0 THEN
        RAISE EXCEPTION 'Facility booking conflict: Venue % is already booked for another training session on % during this time slot.', NEW.venue_id, NEW.session_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_venue_session_overlap ON training_session;
CREATE TRIGGER trg_check_venue_session_overlap
BEFORE INSERT OR UPDATE ON training_session
FOR EACH ROW EXECUTE FUNCTION fn_check_venue_session_overlap();

-- ============================================================================
-- BUSINESS REPORTING VIEWS
-- ============================================================================

-- View 1: Member Subscription & Payment Status Overview
CREATE OR REPLACE VIEW v_member_subscription_status AS
SELECT 
    m.member_id,
    m.name AS member_name,
    m.gender,
    m.email,
    m.phone,
    m.join_date,
    m.status AS membership_status,
    latest_pay.plan_name,
    latest_pay.duration_months,
    latest_pay.fee_amount AS plan_fee,
    COALESCE(latest_pay.payment_date, NULL) AS last_payment_date,
    COALESCE(latest_pay.payment_status, 'No Payment') AS fee_payment_status,
    COALESCE(latest_pay.amount, 0.00) AS last_amount_paid
FROM member m
LEFT JOIN LATERAL (
    SELECT 
        p.payment_date,
        p.status AS payment_status,
        p.amount,
        mp.plan_name,
        mp.duration_months,
        mp.fee_amount
    FROM payment p
    JOIN membership_plan mp ON p.plan_id = mp.plan_id
    WHERE p.member_id = m.member_id
    ORDER BY p.payment_date DESC, p.payment_id DESC
    LIMIT 1
) latest_pay ON TRUE;

-- View 2: Club Rosters with Coaches, Captains, and Player Counts
CREATE OR REPLACE VIEW v_club_rosters AS
SELECT 
    c.club_id,
    c.club_name,
    s.sport_name,
    co.name AS coach_name,
    co.phone AS coach_phone,
    c.status AS club_status,
    COUNT(cm.member_id) AS total_squad_members,
    STRING_AGG(CASE WHEN cm.role ILIKE '%Captain%' THEN m.name || ' (' || cm.role || ')' END, ', ') AS captains_and_leaders
FROM club c
JOIN sport s ON c.sport_id = s.sport_id
LEFT JOIN coach co ON c.coach_id = co.coach_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
LEFT JOIN member m ON cm.member_id = m.member_id
GROUP BY c.club_id, c.club_name, s.sport_name, co.name, co.phone, c.status;

-- View 3: Team Overview & Affiliation
CREATE OR REPLACE VIEW v_team_overview AS
SELECT 
    t.team_id,
    t.team_name,
    c.club_name,
    s.sport_name,
    co.name AS coach_name,
    co.phone AS coach_phone,
    t.created_date,
    t.status AS team_status
FROM team t
JOIN club c ON t.club_id = c.club_id
JOIN sport s ON t.sport_id = s.sport_id
LEFT JOIN coach co ON t.coach_id = co.coach_id;

-- View 4: Facility Utilization & Activity Metrics
CREATE OR REPLACE VIEW v_facility_utilization AS
SELECT 
    f.facility_id,
    f.name AS facility_name,
    f.type AS facility_type,
    f.location,
    f.capacity,
    f.status AS current_status,
    COUNT(DISTINCT ts.session_id) AS total_training_sessions,
    COUNT(DISTINCT fix.fixture_id) AS total_tournament_fixtures,
    (COUNT(DISTINCT ts.session_id) + COUNT(DISTINCT fix.fixture_id)) AS total_events_hosted
FROM facility f
LEFT JOIN training_session ts ON f.facility_id = ts.venue_id
LEFT JOIN fixture fix ON f.facility_id = fix.venue_id
GROUP BY f.facility_id, f.name, f.type, f.location, f.capacity, f.status;

-- View 5: Comprehensive Fixture & Match Schedule
CREATE OR REPLACE VIEW v_upcoming_fixtures AS
SELECT 
    f.fixture_id,
    t.name AS tournament_name,
    s.sport_name,
    t1.team_name AS team_1,
    c1.club_name AS club_1,
    t2.team_name AS team_2,
    c2.club_name AS club_2,
    f.fixture_date,
    fac.name AS venue_name,
    fac.location AS venue_location,
    f.status AS match_status
FROM fixture f
JOIN tournament t ON f.tournament_id = t.tournament_id
JOIN sport s ON t.sport_id = s.sport_id
JOIN team t1 ON f.team1_id = t1.team_id
JOIN club c1 ON t1.club_id = c1.club_id
JOIN team t2 ON f.team2_id = t2.team_id
JOIN club c2 ON t2.club_id = c2.club_id
JOIN facility fac ON f.venue_id = fac.facility_id;

-- View 6: Financial Revenue & Payment Breakdown
CREATE OR REPLACE VIEW v_financial_revenue_summary AS
SELECT 
    p.status AS payment_status,
    p.payment_mode,
    COUNT(p.payment_id) AS transaction_count,
    SUM(p.amount) AS total_amount,
    ROUND(AVG(p.amount), 2) AS average_transaction_amount
FROM payment p
GROUP BY p.status, p.payment_mode;
