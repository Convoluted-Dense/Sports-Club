-- ============================================================================
-- SPORTS CLUB MEMBERSHIP AND TOURNAMENT MANAGEMENT SYSTEM
-- Mock Data Population Script (Strictly Consistent with 12 Tables)
-- Entities: membership_plan (100s), sport (200s), facility (300s),
--           coach (400s), club (500s), member (1000s, 27 Members),
--           club_member (1NF), payment (8000s), training_session (600s),
--           team (700s), tournament (900s), fixture (910s)
-- ============================================================================

-- Clean existing data in reverse dependency order
TRUNCATE TABLE 
    fixture,
    tournament,
    team,
    training_session,
    payment,
    club_member,
    member,
    club,
    coach,
    facility,
    sport,
    membership_plan
RESTART IDENTITY CASCADE;

-- ----------------------------------------------------------------------------
-- 1. SEED MEMBERSHIP PLANS (100-Series)
-- ----------------------------------------------------------------------------
INSERT INTO membership_plan (plan_id, plan_name, duration_months, fee_amount) VALUES
(101, 'Standard Monthly Pass', 1, 499.90),
(102, 'Quarterly Fitness Pass', 3, 1399.90),
(103, 'Annual Gold Elite Pass', 12, 4999.90),
(104, 'Student Semester Pass', 6, 1999.90),
(105, 'Weekend Warrior Pass', 1, 299.90);

SELECT setval('membership_plan_plan_id_seq', 105);

-- ----------------------------------------------------------------------------
-- 2. SEED SPORTS (200-Series)
-- ----------------------------------------------------------------------------
INSERT INTO sport (sport_id, sport_name) VALUES
(201, 'Football'),
(202, 'Cricket'),
(203, 'Badminton'),
(204, 'Basketball'),
(205, 'Tennis'),
(206, 'Swimming');

SELECT setval('sport_sport_id_seq', 206);

-- ----------------------------------------------------------------------------
-- 3. SEED FACILITIES / VENUES (300-Series: Available, Booked, Under Maintenance)
-- ----------------------------------------------------------------------------
INSERT INTO facility (facility_id, name, type, location, capacity, status) VALUES
(301, 'Main Arena Stadium Turf', 'Outdoor Football Pitch', 'North Campus Sector A', 1500, 'Available'),
(302, 'Imperial Cricket Oval', 'Outdoor Cricket Ground', 'East Sports Pavilion', 2500, 'Booked'),
(303, 'Grand Slam Center Court', 'Clay & Synthetic Court', 'West Wing Complex', 350, 'Booked'),
(304, 'Smash Point Badminton Arena', 'Indoor Wooden Court', 'Indoor Sports Complex Hall 1', 120, 'Available'),
(305, 'Skyline Basketball Dome', 'Indoor Hardwood Court', 'Indoor Sports Complex Hall 2', 400, 'Booked'),
(306, 'Olympic Aquatic Center', 'Olympic Pool (50m)', 'South Aquatic Complex', 250, 'Under Maintenance');

SELECT setval('facility_facility_id_seq', 306);

-- ----------------------------------------------------------------------------
-- 4. SEED COACHES (400-Series)
-- ----------------------------------------------------------------------------
INSERT INTO coach (coach_id, name, phone, email) VALUES
(401, 'Carlos Mendez', '+91-9820154321', 'carlos.mendez@gmail.com'),
(402, 'Vikram Singhania', '+91-9811234567', 'vikram.singh@gmail.com'),
(403, 'Elena Rostova', '+91-9717890123', 'elena.rostova@gmail.com'),
(404, 'Lee Wei Chen', '+91-9876543210', 'lee.wei@gmail.com'),
(405, 'Marcus Aurelius Hayes', '+91-9945012345', 'marcus.hayes@gmail.com'),
(406, 'Sarah Jenkins', '+91-9848098765', 'sarah.jenkins@gmail.com');

SELECT setval('coach_coach_id_seq', 406);

-- ----------------------------------------------------------------------------
-- 5. SEED SPORTS CLUBS (500-Series)
-- ----------------------------------------------------------------------------
INSERT INTO club (club_id, club_name, sport_id, coach_id, created_date, status) VALUES
(501, 'Thunderbolts FC', 201, 401, '2024-01-10', 'Active'),
(502, 'Apex Strikers CC', 202, 402, '2024-01-15', 'Active'),
(503, 'Ace Masters TC', 205, 403, '2024-02-01', 'Active'),
(504, 'Smash Point BC', 203, 404, '2024-02-10', 'Active'),
(505, 'Royal Hoops BC', 204, 405, '2024-03-01', 'Active'),
(506, 'Aqua Dolphins SC', 206, 406, '2024-03-15', 'Active');

SELECT setval('club_club_id_seq', 506);

-- ----------------------------------------------------------------------------
-- 6. SEED MEMBERS (1000-Series: Exactly 27 Members with gmail.com emails)
-- Attributes: member_id, name, gender, phone, email, address, join_date, status
-- ----------------------------------------------------------------------------
INSERT INTO member (member_id, name, gender, phone, email, address, join_date, status) VALUES
(1001, 'Aarav Sharma', 'Male', '+91-9820011223', 'aarav.sharma@gmail.com', 'Sector 14, Mumbai', '2024-01-12', 'Active'),
(1002, 'Sophia Martinez', 'Female', '+91-9819922334', 'sophia.martinez@gmail.com', 'Bandra West, Mumbai', '2024-01-15', 'Active'),
(1003, 'Daniel Kim', 'Male', '+91-9769933445', 'daniel.kim@gmail.com', 'Koramangala, Bengaluru', '2024-01-20', 'Expired'),
(1004, 'Fatima Al-Mansoor', 'Female', '+91-9920044556', 'fatima.mansoor@gmail.com', 'Marine Lines, Mumbai', '2024-02-02', 'Active'),
(1005, 'Lucas Silva', 'Male', '+91-9833055667', 'lucas.silva@gmail.com', 'Indiranagar, Bengaluru', '2024-02-10', 'Active'),
(1006, 'Priya Nair', 'Female', '+91-9870066778', 'priya.nair@gmail.com', 'Silver Oak, Kochi', '2024-02-18', 'Pending'),
(1007, 'Liam O''Connor', 'Male', '+91-9821077889', 'liam.oconnor@gmail.com', 'Jubilee Hills, Hyderabad', '2024-03-01', 'Active'),
(1008, 'Chloe Dubois', 'Female', '+91-9987088990', 'chloe.dubois@gmail.com', 'Whitefield, Bengaluru', '2024-03-10', 'Expired'),
(1009, 'Rohan Gupta', 'Male', '+91-9810099001', 'rohan.gupta@gmail.com', 'HITEC City, Hyderabad', '2024-03-15', 'Active'),
(1010, 'Aisha Hassan', 'Female', '+91-9871100112', 'aisha.hassan@gmail.com', 'DLF Phase 5, Gurugram', '2024-04-01', 'Active'),
(1011, 'Mateo Rossi', 'Male', '+91-9818811223', 'mateo.rossi@gmail.com', 'Vasant Vihar, New Delhi', '2024-04-12', 'Suspended'),
(1012, 'Ananya Patel', 'Female', '+91-9822222334', 'ananya.patel@gmail.com', 'SG Highway, Ahmedabad', '2024-04-20', 'Active'),
(1013, 'Jordan Taylor', 'Female', '+91-9930033445', 'jordan.taylor@gmail.com', 'Anna Nagar, Chennai', '2024-05-05', 'Active'),
(1014, 'Ethan Wright', 'Male', '+91-9845044556', 'ethan.wright@gmail.com', 'HSR Layout, Bengaluru', '2024-05-18', 'Active'),
(1015, 'Maya Tanaka', 'Female', '+91-9886055667', 'maya.tanaka@gmail.com', 'Pune Camp, Pune', '2024-06-01', 'Expired'),
(1016, 'Noah Van Der Berg', 'Male', '+91-9741066778', 'noah.vanderberg@gmail.com', 'Salt Lake, Kolkata', '2024-06-15', 'Active'),
(1017, 'Isabella Rossi', 'Female', '+91-9900077889', 'isabella.rossi@gmail.com', 'Banjara Hills, Hyderabad', '2024-07-01', 'Active'),
(1018, 'Kabir Mehta', 'Male', '+91-9844088990', 'kabir.mehta@gmail.com', 'Gomti Nagar, Lucknow', '2024-07-14', 'Pending'),
(1019, 'Samantha Green', 'Female', '+91-9840099001', 'samantha.green@gmail.com', 'Alwarpet, Chennai', '2024-08-01', 'Active'),
(1020, 'Diego Fernandez', 'Male', '+91-9884000112', 'diego.fernandez@gmail.com', 'Miramar, Panaji, Goa', '2024-08-20', 'Expired'),
(1021, 'Nina Kowalska', 'Female', '+91-9790011223', 'nina.kowalska@gmail.com', 'Adyar, Chennai', '2024-09-05', 'Active'),
(1022, 'Tariq Aziz', 'Male', '+91-9849022334', 'tariq.aziz@gmail.com', 'Gachibowli, Hyderabad', '2024-09-18', 'Active'),
(1023, 'Emily Chen', 'Female', '+91-9885033445', 'emily.chen@gmail.com', 'Park Street, Kolkata', '2024-10-01', 'Inactive'),
(1024, 'Alexander Novak', 'Male', '+91-9949044556', 'alex.novak@gmail.com', 'Powai, Mumbai', '2024-10-15', 'Active'),
(1025, 'Olivia Brown', 'Female', '+91-9830055667', 'olivia.brown@gmail.com', 'Ballygunge, Kolkata', '2024-11-02', 'Active'),
(1026, 'Zachary Miller', 'Male', '+91-9831066778', 'zach.miller@gmail.com', 'Calangute, Goa', '2024-11-20', 'Expired'),
(1027, 'Zara Khan', 'Female', '+91-9874077889', 'zara.khan@gmail.com', 'New Town, Kolkata', '2024-12-05', 'Active');

SELECT setval('member_member_id_seq', 1027);

-- ----------------------------------------------------------------------------
-- 7. SEED CLUB MEMBERS (Atomic 1NF Roles: 1 Role Per Row)
-- ----------------------------------------------------------------------------
INSERT INTO club_member (member_id, club_id, role, join_date) VALUES
-- Club 501: Thunderbolts FC (Football)
(1002, 501, 'Captain', '2024-01-16'),
(1002, 501, 'Striker', '2024-01-16'),
(1005, 501, 'Vice-Captain', '2024-02-12'),
(1005, 501, 'Midfielder', '2024-02-12'),
(1011, 501, 'Defender', '2024-04-13'),
(1016, 501, 'Goalkeeper', '2024-06-16'),
(1020, 501, 'Winger', '2024-08-21'),
(1027, 501, 'Forward', '2024-12-06'),

-- Club 502: Apex Strikers CC (Cricket)
(1001, 502, 'Captain', '2024-01-13'),
(1001, 502, 'All-Rounder', '2024-01-13'),
(1007, 502, 'Opening Batsman', '2024-03-02'),
(1009, 502, 'Wicket-Keeper', '2024-03-16'),
(1018, 502, 'Fast Bowler', '2024-07-15'),
(1024, 502, 'Spin Bowler', '2024-10-16'),

-- Club 503: Ace Masters TC (Tennis)
(1014, 503, 'Captain', '2024-05-19'),
(1014, 503, 'Singles Player', '2024-05-19'),
(1006, 503, 'Doubles Player', '2024-02-20'),
(1019, 503, 'Singles Player', '2024-08-02'),
(1025, 503, 'Junior Player', '2024-11-03'),

-- Club 504: Smash Point BC (Badminton)
(1004, 504, 'Captain', '2024-02-03'),
(1004, 504, 'Singles Player', '2024-02-03'),
(1012, 504, 'Doubles Player', '2024-04-21'),
(1015, 504, 'Doubles Specialist', '2024-06-02'),
(1023, 504, 'Reserve Player', '2024-10-02'),

-- Club 505: Royal Hoops BC (Basketball)
(1010, 505, 'Captain', '2024-04-02'),
(1010, 505, 'Point Guard', '2024-04-02'),
(1003, 505, 'Shooting Guard', '2024-01-21'),
(1017, 505, 'Power Forward', '2024-07-02'),
(1022, 505, 'Center', '2024-09-19'),

-- Club 506: Aqua Dolphins SC (Swimming)
(1013, 506, 'Captain', '2024-05-06'),
(1013, 506, 'Lead Swimmer', '2024-05-06'),
(1008, 506, 'Freestyle Specialist', '2024-03-11'),
(1021, 506, 'Breaststroke Specialist', '2024-09-06'),
(1026, 506, 'Backstroke Specialist', '2024-11-21');

-- ----------------------------------------------------------------------------
-- 8. SEED PAYMENTS (8000-Series: 8001 to 8030)
-- ----------------------------------------------------------------------------
INSERT INTO payment (payment_id, member_id, plan_id, amount, payment_mode, payment_date, status, transaction_ref) VALUES
(8001, 1001, 103, 4999.90, 'UPI', '2024-01-12', 'Paid', 'TXN_20240112_001'),
(8002, 1002, 103, 4999.90, 'Credit Card', '2024-01-15', 'Paid', 'TXN_20240115_002'),
(8003, 1003, 101, 499.90, 'Cash', '2024-01-20', 'Expired', 'TXN_20240120_003'),
(8004, 1004, 102, 1399.90, 'Net Banking', '2024-02-02', 'Paid', 'TXN_20240202_004'),
(8005, 1005, 103, 4999.90, 'Credit Card', '2024-02-10', 'Paid', 'TXN_20240210_005'),
(8006, 1006, 104, 1999.90, 'Bank Transfer', '2024-02-18', 'Pending', 'TXN_20240218_006'),
(8007, 1007, 102, 1399.90, 'UPI', '2024-03-01', 'Paid', 'TXN_20240301_007'),
(8008, 1008, 105, 299.90, 'Debit Card', '2024-03-10', 'Expired', 'TXN_20240310_008'),
(8009, 1009, 103, 4999.90, 'UPI', '2024-03-15', 'Paid', 'TXN_20240315_009'),
(8010, 1010, 102, 1399.90, 'Credit Card', '2024-04-01', 'Paid', 'TXN_20240401_010'),
(8011, 1011, 101, 499.90, 'Credit Card', '2024-04-12', 'Failed', 'TXN_20240412_011'),
(8012, 1012, 104, 1999.90, 'UPI', '2024-04-20', 'Paid', 'TXN_20240420_012'),
(8013, 1013, 102, 1399.90, 'Net Banking', '2024-05-05', 'Paid', 'TXN_20240505_013'),
(8014, 1014, 103, 4999.90, 'Credit Card', '2024-05-18', 'Paid', 'TXN_20240518_014'),
(8015, 1015, 101, 499.90, 'Cash', '2024-06-01', 'Expired', 'TXN_20240601_015'),
(8016, 1016, 102, 1399.90, 'UPI', '2024-06-15', 'Paid', 'TXN_20240615_016'),
(8017, 1017, 103, 4999.90, 'Credit Card', '2024-07-01', 'Paid', 'TXN_20240701_017'),
(8018, 1018, 104, 1999.90, 'UPI', '2024-07-14', 'Pending', 'TXN_20240714_018'),
(8019, 1019, 102, 1399.90, 'Net Banking', '2024-08-01', 'Paid', 'TXN_20240801_019'),
(8020, 1020, 105, 299.90, 'Cash', '2024-08-20', 'Expired', 'TXN_20240820_020'),
(8021, 1021, 103, 4999.90, 'Credit Card', '2024-09-05', 'Paid', 'TXN_20240905_021'),
(8022, 1022, 102, 1399.90, 'UPI', '2024-09-18', 'Paid', 'TXN_20240918_022'),
(8023, 1023, 101, 499.90, 'Net Banking', '2024-10-01', 'Refunded', 'TXN_20241001_023'),
(8024, 1024, 103, 4999.90, 'UPI', '2024-10-15', 'Paid', 'TXN_20241015_024'),
(8025, 1025, 104, 1999.90, 'Debit Card', '2024-11-02', 'Paid', 'TXN_20241102_025'),
(8026, 1026, 101, 499.90, 'Cash', '2024-11-20', 'Expired', 'TXN_20241120_026'),
(8027, 1027, 102, 1399.90, 'Credit Card', '2024-12-05', 'Paid', 'TXN_20241205_027'),
(8028, 1001, 103, 4999.90, 'UPI', '2025-01-10', 'Paid', 'TXN_20250110_028'),
(8029, 1002, 103, 4999.90, 'Credit Card', '2025-01-12', 'Paid', 'TXN_20250112_029'),
(8030, 1004, 102, 1399.90, 'Net Banking', '2024-05-02', 'Paid', 'TXN_20240502_030');

SELECT setval('payment_payment_id_seq', 8030);

-- ----------------------------------------------------------------------------
-- 9. SEED TRAINING SESSIONS (600-Series: 601 to 609)
-- ----------------------------------------------------------------------------
INSERT INTO training_session (session_id, sport_id, coach_id, venue_id, session_date, start_time, end_time, capacity, status) VALUES
(601, 201, 401, 301, '2025-02-15', '07:00:00', '09:00:00', 25, 'Completed'),
(602, 202, 402, 302, '2025-02-16', '08:00:00', '11:00:00', 20, 'Completed'),
(603, 205, 403, 303, '2025-02-17', '16:00:00', '18:00:00', 10, 'Completed'),
(604, 203, 404, 304, '2025-02-18', '17:00:00', '19:00:00', 12, 'Completed'),
(605, 204, 405, 305, '2025-02-19', '18:00:00', '20:00:00', 15, 'Completed'),
(606, 206, 406, 306, '2025-02-20', '06:30:00', '08:30:00', 18, 'Completed'),
(607, 201, 401, 301, '2026-10-05', '07:00:00', '09:00:00', 25, 'Scheduled'),
(608, 202, 402, 302, '2026-10-06', '08:00:00', '11:00:00', 20, 'Scheduled'),
(609, 204, 405, 305, '2026-10-07', '18:00:00', '20:00:00', 15, 'Scheduled');

SELECT setval('training_session_session_id_seq', 609);

-- ----------------------------------------------------------------------------
-- 10. SEED TEAMS / SQUADS (700-Series: 701 to 708)
-- Formed under clubs, assigned to sports and coaches
-- ----------------------------------------------------------------------------
INSERT INTO team (team_id, club_id, team_name, sport_id, coach_id, created_date, status) VALUES
(701, 501, 'Thunderbolts Senior A', 201, 401, '2024-01-15', 'Active'),
(702, 501, 'Thunderbolts Under-21', 201, 401, '2024-02-01', 'Active'),
(703, 502, 'Apex Strikers XI', 202, 402, '2024-01-20', 'Active'),
(704, 502, 'Apex Colts XI', 202, 402, '2024-02-15', 'Active'),
(705, 503, 'Ace Masters Pro Squad', 205, 403, '2024-02-10', 'Active'),
(706, 504, 'Smash Point Shuttlers', 203, 404, '2024-02-18', 'Active'),
(707, 505, 'Royal Hoops Varsity', 204, 405, '2024-03-05', 'Active'),
(708, 505, 'Royal Hoops Ballers', 204, 405, '2024-03-10', 'Active');

SELECT setval('team_team_id_seq', 708);

-- ----------------------------------------------------------------------------
-- 11. SEED TOURNAMENTS (9000-Series: 9001 to 9003)
-- ----------------------------------------------------------------------------
INSERT INTO tournament (tournament_id, name, sport_id, start_date, end_date, type) VALUES
(9001, 'Inter-Club Football Super League', 201, '2025-03-01', '2025-03-20', 'League'),
(9002, 'Champions Cricket Cup 2025', 202, '2025-04-05', '2025-04-25', 'Round Robin'),
(9003, 'Autumn Invitational Basketball Trophy', 204, '2025-05-10', '2025-05-25', 'Knockout');

SELECT setval('tournament_tournament_id_seq', 9003);

-- ----------------------------------------------------------------------------
-- 12. SEED FIXTURES (910-Series: 911 to 916)
-- Competing teams (team1_id vs team2_id) matched to tournament sport
-- ----------------------------------------------------------------------------
INSERT INTO fixture (fixture_id, tournament_id, team1_id, team2_id, fixture_date, venue_id, status) VALUES
(911, 9001, 701, 702, '2025-03-05 16:00:00', 301, 'Completed'),
(912, 9001, 702, 701, '2025-03-12 16:00:00', 301, 'Completed'),
(913, 9002, 703, 704, '2025-04-10 10:00:00', 302, 'Completed'),
(914, 9003, 707, 708, '2025-05-15 18:00:00', 305, 'Completed'),
(915, 9001, 701, 702, '2026-10-15 17:00:00', 301, 'Scheduled'),
(916, 9002, 703, 704, '2026-10-20 09:30:00', 302, 'Scheduled');

SELECT setval('fixture_fixture_id_seq', 916);
