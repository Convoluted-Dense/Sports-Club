import sqlite3
import os
import json
import re
import hashlib

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR) if os.path.basename(BACKEND_DIR) == "backend" else BACKEND_DIR
DB_FILE = os.path.join(PROJECT_ROOT, "sql", "sports_club.db")

def hash_password(password):
    """Simple SHA-256 hash for password storage."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_sqlite_db(force_recreate=True):
    if force_recreate and os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception as e:
            print(f"Notice: could not remove existing db file: {e}")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Membership Plan (100-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS membership_plan (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_name TEXT NOT NULL,
        duration_months INTEGER NOT NULL CHECK (duration_months > 0),
        fee_amount NUMERIC NOT NULL CHECK (fee_amount >= 0)
    );
    """)

    # 2. Sport (200-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sport (
        sport_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sport_name TEXT NOT NULL UNIQUE
    );
    """)

    # 3. Facility (300-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facility (
        facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL CHECK (capacity > 0),
        status TEXT NOT NULL DEFAULT 'Available' CHECK (status IN ('Available', 'Booked', 'Under Maintenance'))
    );
    """)

    # 4. Coach (400-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coach (
        coach_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    """)

    # 5. Club (500-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS club (
        club_id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_name TEXT NOT NULL,
        sport_id INTEGER NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
        coach_id INTEGER REFERENCES coach(coach_id) ON DELETE SET NULL,
        created_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended'))
    );
    """)

    # 6. Member (1000-Series IDs) — includes password for login
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS member (
        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female')),
        phone TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL DEFAULT '',
        address TEXT NOT NULL,
        join_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Expired', 'Pending', 'Suspended', 'Inactive'))
    );
    """)

    # 7. Club Member (N:N bridge — atomic 1NF roles)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS club_member (
        member_id INTEGER NOT NULL REFERENCES member(member_id) ON DELETE CASCADE,
        club_id INTEGER NOT NULL REFERENCES club(club_id) ON DELETE CASCADE,
        role TEXT NOT NULL DEFAULT 'Player',
        join_date DATE NOT NULL,
        PRIMARY KEY (member_id, club_id, role)
    );
    """)

    # 8. Payment (8000-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL REFERENCES member(member_id) ON DELETE RESTRICT,
        plan_id INTEGER NOT NULL REFERENCES membership_plan(plan_id) ON DELETE RESTRICT,
        amount NUMERIC NOT NULL CHECK (amount > 0),
        payment_mode TEXT NOT NULL CHECK (payment_mode IN ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash', 'Bank Transfer')),
        payment_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'Paid' CHECK (status IN ('Paid', 'Pending', 'Failed', 'Refunded', 'Expired')),
        transaction_ref TEXT UNIQUE
    );
    """)

    # 9. Training Session (600-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_session (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sport_id INTEGER NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
        coach_id INTEGER NOT NULL REFERENCES coach(coach_id) ON DELETE RESTRICT,
        venue_id INTEGER NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
        session_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL CHECK (end_time > start_time),
        capacity INTEGER NOT NULL CHECK (capacity > 0),
        status TEXT NOT NULL DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'In Progress', 'Full'))
    );
    """)

    # 10. Team (700-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER NOT NULL REFERENCES club(club_id) ON DELETE CASCADE,
        team_name TEXT NOT NULL,
        sport_id INTEGER NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
        coach_id INTEGER REFERENCES coach(coach_id) ON DELETE SET NULL,
        created_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended'))
    );
    """)

    # 11. Tournament (9000-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournament (
        tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sport_id INTEGER NOT NULL REFERENCES sport(sport_id) ON DELETE CASCADE,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL CHECK (end_date >= start_date),
        type TEXT NOT NULL CHECK (type IN ('Knockout', 'Round Robin', 'League', 'Single Elimination', 'Open Championship'))
    );
    """)

    # 12. Fixture (910-Series IDs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fixture (
        fixture_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER NOT NULL REFERENCES tournament(tournament_id) ON DELETE CASCADE,
        team1_id INTEGER NOT NULL REFERENCES team(team_id) ON DELETE RESTRICT,
        team2_id INTEGER NOT NULL REFERENCES team(team_id) ON DELETE RESTRICT,
        fixture_date DATETIME NOT NULL,
        venue_id INTEGER NOT NULL REFERENCES facility(facility_id) ON DELETE RESTRICT,
        status TEXT NOT NULL DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Postponed', 'Cancelled', 'Live')),
        CHECK (team1_id <> team2_id)
    );
    """)

    # ---- CREATE VIEWS ----
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_team_overview AS
    SELECT 
        t.team_id, t.team_name, c.club_name, s.sport_name,
        COALESCE(co.name, 'Unassigned') AS coach_name,
        COALESCE(co.phone, 'N/A') AS coach_phone,
        t.created_date, t.status AS team_status
    FROM team t
    JOIN club c ON t.club_id = c.club_id
    JOIN sport s ON t.sport_id = s.sport_id
    LEFT JOIN coach co ON t.coach_id = co.coach_id;
    """)

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_facility_utilization AS
    SELECT 
        f.facility_id, f.name AS facility_name, f.type AS facility_type,
        f.location, f.capacity, f.status AS current_status,
        COUNT(DISTINCT ts.session_id) AS total_training_sessions,
        COUNT(DISTINCT fix.fixture_id) AS total_tournament_fixtures,
        (COUNT(DISTINCT ts.session_id) + COUNT(DISTINCT fix.fixture_id)) AS total_events_hosted
    FROM facility f
    LEFT JOIN training_session ts ON f.facility_id = ts.venue_id
    LEFT JOIN fixture fix ON f.facility_id = fix.venue_id
    GROUP BY f.facility_id, f.name, f.type, f.location, f.capacity, f.status;
    """)

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_upcoming_fixtures AS
    SELECT 
        f.fixture_id, t.name AS tournament_name, s.sport_name,
        t1.team_name AS team1, t2.team_name AS team2,
        f.fixture_date, fac.name AS venue_name, f.status AS match_status
    FROM fixture f
    JOIN tournament t ON f.tournament_id = t.tournament_id
    JOIN sport s ON t.sport_id = s.sport_id
    JOIN team t1 ON f.team1_id = t1.team_id
    JOIN team t2 ON f.team2_id = t2.team_id
    JOIN facility fac ON f.venue_id = fac.facility_id;
    """)

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_financial_revenue_summary AS
    SELECT 
        mp.plan_name,
        COUNT(p.payment_id) AS total_payments,
        SUM(p.amount) AS total_revenue,
        AVG(p.amount) AS avg_payment_amount
    FROM membership_plan mp
    LEFT JOIN payment p ON mp.plan_id = p.plan_id AND p.status = 'Paid'
    GROUP BY mp.plan_id, mp.plan_name;
    """)

    # ---- POPULATE DATA ----
    populate_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "populate_data.sql")
    if os.path.exists(populate_file):
        with open(populate_file, "r", encoding="utf-8") as f:
            sql_text = f.read()

        # Extract INSERT statements and execute them
        insert_stmts = re.findall(r"(INSERT INTO [^;]+;)", sql_text, re.DOTALL | re.IGNORECASE)
        for stmt in insert_stmts:
            # The member inserts from populate_data.sql have 8 columns (no password).
            # We need to inject a default password for each member.
            if 'INSERT INTO member' in stmt:
                # Re-write member inserts to include password column
                # Original columns: (member_id, name, gender, phone, email, address, join_date, status)
                # New columns:      (member_id, name, gender, phone, email, password, address, join_date, status)
                lines = stmt.strip().split('\n')
                new_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('INSERT INTO member'):
                        # Replace the column list
                        new_line = line.replace(
                            '(member_id, name, gender, phone, email, address, join_date, status)',
                            '(member_id, name, gender, phone, email, password, address, join_date, status)'
                        )
                        new_lines.append(new_line)
                    elif stripped.startswith('(') and 'gmail.com' in stripped:
                        # This is a data row — inject the password after email
                        # Format: (1001, 'Aarav Sharma', 'Male', '+91-...', 'email@gmail.com', 'address', 'date', 'status')
                        # We need to find email value and insert password after it
                        import re as re2
                        # Find the email value and insert password after it
                        email_match = re2.search(r"'([^']+@gmail\.com)'", stripped)
                        if email_match:
                            email_val = email_match.group(1)
                            # Generate password: first part of email (before @) as default
                            default_pwd = email_val.split('@')[0].replace('.', '')
                            pwd_hash = hash_password(default_pwd)
                            # Insert password hash right after the email field
                            new_line = line.replace(
                                f"'{email_val}', '",
                                f"'{email_val}', '{pwd_hash}', '",
                                1
                            )
                            new_lines.append(new_line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                stmt = '\n'.join(new_lines)

            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Error inserting: {e}\nStatement: {stmt[:120]}...")

    conn.commit()
    conn.close()
    print("SQLite database successfully initialized and seeded (with password support)!")

if __name__ == "__main__":
    init_sqlite_db()
