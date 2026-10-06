import os
import sys
import json
import sqlite3
import time
import hashlib
import urllib.parse
import uuid
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading

PORT = 5000
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR) if os.path.basename(BACKEND_DIR) == "backend" else BACKEND_DIR
DB_FILE = os.path.join(PROJECT_ROOT, "sql", "sports_club.db")

class DualStackServer(HTTPServer):
    """Dual-stack IPv4/IPv6 HTTP Server for seamless Windows localhost resolution."""
    address_family = socket.AF_INET6

    def server_bind(self):
        # Enable dual-stack IPv4 and IPv6 on Windows
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        super().server_bind()

# ============================================================================
# In-memory session store (simple token -> member_id / "admin")
# ============================================================================
SESSIONS = {}  # { token: { "role": "member"|"admin", "member_id": int|None, "name": str } }

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ============================================================================
# 10 Predefined SQL Queries (loaded into the SQL Studio sidebar)
# ============================================================================
PREDEFINED_QUERIES = [
    {
        "id": 1,
        "title": "Active Membership Directory & Plan Details",
        "description": "Lists all active members with their latest subscribed membership plan and payment status.",
        "sql": """SELECT 
    m.member_id, m.name AS member_name, m.gender, m.email, m.phone,
    m.status AS membership_status,
    COALESCE(mp.plan_name, 'No Active Plan') AS current_plan,
    COALESCE(mp.duration_months || ' Month(s)', 'N/A') AS plan_duration,
    COALESCE('₹' || printf('%.2f', p.amount), 'N/A') AS plan_rate,
    COALESCE(p.status, 'Unpaid') AS payment_status
FROM member m
LEFT JOIN payment p ON p.payment_id = (
    SELECT payment_id FROM payment WHERE member_id = m.member_id ORDER BY payment_date DESC LIMIT 1
)
LEFT JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE m.status = 'Active' ORDER BY m.name ASC;"""
    },
    {
        "id": 2,
        "title": "Fee Collection & Payment Dues Status",
        "description": "Categorizes paid, expired, pending, and failed payment transactions across members.",
        "sql": """SELECT 
    m.member_id, m.name AS member_name, m.email, p.amount AS billed_amount,
    p.payment_mode, p.payment_date, p.status AS payment_status,
    CASE 
        WHEN p.status = 'Paid' THEN 'Account in Good Standing'
        WHEN p.status = 'Expired' THEN 'Subscription Expired - Renewal Required'
        WHEN p.status = 'Pending' THEN 'Payment Processing'
        WHEN p.status = 'Failed' THEN 'Transaction Failed - Re-attempt Required'
        ELSE 'Refunded / Disputed'
    END AS account_remarks
FROM payment p JOIN member m ON p.member_id = m.member_id ORDER BY p.payment_date DESC;"""
    },
    {
        "id": 3,
        "title": "Club Roster Breakdown by Sport & Coach",
        "description": "Aggregates athletes and their tactical roles for each sports club franchise.",
        "sql": """SELECT 
    c.club_name, s.sport_name, COALESCE(co.name, 'Unassigned') AS head_coach,
    COUNT(cm.member_id) AS registered_athletes,
    group_concat(m.name || ' (' || cm.role || ')', '; ') AS team_roster
FROM club c
JOIN sport s ON c.sport_id = s.sport_id
LEFT JOIN coach co ON c.coach_id = co.coach_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
LEFT JOIN member m ON cm.member_id = m.member_id
GROUP BY c.club_name, s.sport_name, co.name ORDER BY c.club_name;"""
    },
    {
        "id": 4,
        "title": "Revenue Analytics by Plan & Payment Mode",
        "description": "Aggregates total collections and ticket sizes categorized by membership plan and payment channel.",
        "sql": """SELECT 
    mp.plan_name, p.payment_mode,
    COUNT(p.payment_id) AS total_transactions,
    SUM(p.amount) AS total_collected,
    ROUND(AVG(p.amount), 2) AS average_ticket_size
FROM payment p JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE p.status = 'Paid' GROUP BY mp.plan_name, p.payment_mode
HAVING SUM(p.amount) > 0 ORDER BY total_collected DESC;"""
    },
    {
        "id": 5,
        "title": "Scheduled Training Sessions & Venue Allocation",
        "description": "Multi-table join across training sessions, sports, coaches, and sports facility venues.",
        "sql": """SELECT 
    ts.session_id, s.sport_name, co.name AS coach_name, co.phone AS coach_phone,
    f.name AS venue_name, f.location AS venue_location, ts.session_date,
    ts.start_time || ' - ' || ts.end_time AS time_slot,
    ts.capacity AS participant_capacity, ts.status AS session_status
FROM training_session ts
JOIN sport s ON ts.sport_id = s.sport_id
JOIN coach co ON ts.coach_id = co.coach_id
JOIN facility f ON ts.venue_id = f.facility_id
ORDER BY ts.session_date DESC, ts.start_time ASC;"""
    },
    {
        "id": 6,
        "title": "Tournament Fixtures & Competing Squads",
        "description": "Displays tournament matches with team names, club affiliations, and stadium venues.",
        "sql": """SELECT 
    t.name AS tournament_title, s.sport_name, f.fixture_id,
    t1.team_name AS team_1, c1.club_name AS club_1,
    t2.team_name AS team_2, c2.club_name AS club_2,
    f.fixture_date, fac.name AS stadium_venue, f.status AS match_status
FROM fixture f
JOIN tournament t ON f.tournament_id = t.tournament_id
JOIN sport s ON t.sport_id = s.sport_id
JOIN team t1 ON f.team1_id = t1.team_id
JOIN club c1 ON t1.club_id = c1.club_id
JOIN team t2 ON f.team2_id = t2.team_id
JOIN club c2 ON t2.club_id = c2.club_id
JOIN facility fac ON f.venue_id = fac.facility_id ORDER BY f.fixture_date ASC;"""
    },
    {
        "id": 7,
        "title": "Competitive Squads Overview (v_team_overview)",
        "description": "Queries the v_team_overview reporting view for squad rosters and coaches.",
        "sql": """SELECT team_id, team_name, club_name, sport_name, coach_name, coach_phone,
    created_date AS squad_founded, team_status
FROM v_team_overview ORDER BY sport_name, club_name, team_name;"""
    },
    {
        "id": 8,
        "title": "Members with Expired or Pending Dues",
        "description": "Identifies delinquent accounts requiring automated renewal notices.",
        "sql": """SELECT 
    m.member_id, m.name AS member_name, m.email, m.phone,
    m.status AS membership_status, p.status AS payment_status,
    p.amount AS unpaid_fee, p.payment_date
FROM member m JOIN payment p ON m.member_id = p.member_id
WHERE p.status IN ('Expired', 'Pending', 'Failed') OR m.status IN ('Expired', 'Pending')
ORDER BY p.payment_date ASC;"""
    },
    {
        "id": 9,
        "title": "Facility Usage Heatmap (v_facility_utilization)",
        "description": "Measures total training sessions and tournament matches hosted per sports facility.",
        "sql": """SELECT facility_id, facility_name, facility_type, location, capacity,
    current_status, total_training_sessions, total_tournament_fixtures, total_events_hosted
FROM v_facility_utilization ORDER BY total_events_hosted DESC;"""
    },
    {
        "id": 10,
        "title": "Top Performing Sports by Athlete Enrollment (Window DENSE_RANK)",
        "description": "Ranks sports by overall athlete enrollment across all participating clubs.",
        "sql": """SELECT 
    s.sport_name,
    COUNT(DISTINCT cm.member_id) AS total_enrolled_athletes,
    DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT cm.member_id) DESC) AS popularity_rank
FROM sport s
LEFT JOIN club c ON s.sport_id = c.sport_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
GROUP BY s.sport_name ORDER BY popularity_rank ASC;"""
    }
]

# ============================================================================
# Ensure DB exists
# ============================================================================
def ensure_db():
    if not os.path.exists(DB_FILE):
        print("Database not found. Initializing...")
        from db_manager import init_sqlite_db
        init_sqlite_db()

def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ============================================================================
# COMPLETE ER DIAGRAM & RELATIONAL SCHEMA CONTEXT (12 TABLES, 7 VIEWS)
# ============================================================================
FULL_DB_SCHEMA_CONTEXT = """
You are an expert AI Database Administrator and SQL Compiler for the 'Sports Club Management System'.
The database is normalized to Third Normal Form (3NF) in SQLite / PostgreSQL and consists of exactly 12 tables and 7 views.

### ENTITY RELATIONSHIP DIAGRAM (ERD) & 3NF SCHEMA:
1. membership_plan(plan_id PK, plan_name, duration_months, fee_amount)
   - Relationship: 1 Plan has Many Payments (1:N).
2. sport(sport_id PK, sport_name UNIQUE)
   - Relationship: 1 Sport has Many Clubs (1:N), Many Training Sessions (1:N), Many Tournaments (1:N), Many Teams (1:N).
3. facility(facility_id PK, name, type, location, capacity, status [Available/Booked/Under Maintenance])
   - Relationship: 1 Facility hosts Many Training Sessions (1:N) and Many Tournament Fixtures (1:N).
4. coach(coach_id PK, name, phone, email UNIQUE)
   - Relationship: 1 Coach coaches Many Clubs (1:N), conducts Many Training Sessions (1:N), coaches Many Teams (1:N).
5. club(club_id PK, club_name, sport_id FK->sport, coach_id FK->coach, created_date, status [Active/Inactive/Suspended])
   - Relationship: 1 Club has Many Teams (1:N), participates in N:N relationship with Member via club_member.
6. member(member_id PK, name, gender [Male/Female], phone, email UNIQUE, password, address, join_date, status [Active/Expired/Pending/Suspended/Inactive])
   - Relationship: 1 Member has Many Payments (1:N), joins Many Clubs via club_member (N:M).
7. club_member(member_id FK->member, club_id FK->club, role, join_date) [PK: (member_id, club_id, role)]
   - Bridge Table: Resolves N:M between Member and Club with tactical/positional roles (e.g., Striker, Batsman, Forward, Captain).
8. payment(payment_id PK, member_id FK->member, plan_id FK->membership_plan, amount, payment_mode [UPI/Credit Card/Debit Card/Net Banking/Cash], payment_date, status [Paid/Pending/Failed/Refunded/Expired], transaction_ref UNIQUE)
   - Financial Ledger for subscriptions.
9. training_session(session_id PK, sport_id FK->sport, coach_id FK->coach, venue_id FK->facility, session_date, start_time, end_time, capacity, status [Scheduled/Completed/Cancelled/In Progress/Full])
10. team(team_id PK, club_id FK->club, team_name, sport_id FK->sport, coach_id FK->coach, created_date, status [Active/Inactive/Suspended])
11. tournament(tournament_id PK, name, sport_id FK->sport, start_date, end_date, type [Knockout/Round Robin/League/Single Elimination/Open Championship])
12. fixture(fixture_id PK, tournament_id FK->tournament, team1_id FK->team, team2_id FK->team, fixture_date, venue_id FK->facility, status [Scheduled/Completed/Postponed/Cancelled/Live])

### PRE-BUILT 3NF ANALYTIC VIEWS:
- v_club_rosters: club_id, club_name, sport_name, head_coach, coach_phone, member_id, member_name, member_email, tactical_role, membership_status
- v_tournament_standings: tournament_id, tournament_name, sport_name, team_name, matches_played, matches_won, matches_drawn, matches_lost, total_points
- v_facility_utilization: facility_id, facility_name, facility_type, location, capacity, current_status, total_training_sessions, total_tournament_fixtures, total_events_hosted
- v_upcoming_fixtures: fixture_id, tournament_name, sport_name, team_1, team_2, fixture_date, venue_name, venue_location, match_status
- v_financial_revenue_summary: payment_mode, total_transactions, settled_revenue, avg_transaction_size, min_payment, max_payment
- v_member_subscription_status: member_id, name, phone, email, gender, current_plan, plan_duration_months, plan_rate, latest_payment_date, payment_mode, payment_status, membership_status, transaction_ref
- v_team_overview: team_id, team_name, club_name, sport_name, head_coach, created_date, status

RULES FOR SQL GENERATION:
1. Return ONLY valid SQLite-compatible SQL inside ```sql ... ```.
2. Join using appropriate Foreign Keys specified in ER diagram.
3. Handle NULL values with COALESCE where appropriate.
4. Format currency amounts with proper columns.
5. Use proper WHERE, GROUP BY, ORDER BY, or Window functions (e.g. DENSE_RANK()).
"""

# ============================================================================
# Request Handler
# ============================================================================
class DBMSRequestHandler(SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def translate_path(self, path):
        parsed = urllib.parse.urlparse(path)
        clean_path = urllib.parse.unquote(parsed.path)
        if clean_path in ("/", "", "/index.html"):
            return os.path.join(PROJECT_ROOT, "frontend", "index.html")
        
        rel_path = clean_path.lstrip("/").replace("/", os.sep)
        candidate_paths = [
            os.path.join(PROJECT_ROOT, rel_path),
            os.path.join(PROJECT_ROOT, "frontend", rel_path),
            os.path.join(PROJECT_ROOT, "presentation", rel_path),
            os.path.join(PROJECT_ROOT, "reports", rel_path),
            os.path.join(PROJECT_ROOT, "sql", rel_path),
        ]
        for c in candidate_paths:
            if os.path.exists(c):
                return c
        return os.path.join(PROJECT_ROOT, "frontend", rel_path)

    # ---- Routing ----
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qp = urllib.parse.parse_qs(parsed.query)

        if path == "/api/summary":
            self.send_json(self._get_summary())
        elif path == "/api/tables":
            self.send_json(self._get_tables())
        elif path.startswith("/api/table/"):
            self.send_json(self._get_table_data(path[len("/api/table/"):], qp))
        elif path == "/api/predefined_queries":
            self.send_json(PREDEFINED_QUERIES)
        elif path == "/api/schema":
            self.send_json(self._get_schema_info())
        elif path == "/api/sports":
            self.send_json(self._get_sports())
        elif path == "/api/clubs":
            self.send_json(self._get_clubs())
        elif path == "/api/plans":
            self.send_json(self._get_plans())
        elif path == "/api/member/profile":
            self.send_json(self._get_member_profile(self._get_auth_token()))
        elif path == "/api/member/clubs":
            self.send_json(self._get_member_clubs(self._get_auth_token()))
        elif path == "/api/member/payments":
            self.send_json(self._get_member_payments(self._get_auth_token()))
        elif path == "/api/member/sessions":
            self.send_json(self._get_member_sessions(self._get_auth_token()))
        elif path == "/api/member/fixtures":
            self.send_json(self._get_member_fixtures(self._get_auth_token()))
        elif path == "/api/admin/members":
            self.send_json(self._get_admin_members(self._get_auth_token()))
        elif path == "/api/facilities":
            self.send_json(self._get_facilities())
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        data = self._read_json_body()

        if path == "/api/auth/login":
            self.send_json(self._login(data))
        elif path == "/api/auth/register":
            self.send_json(self._register(data))
        elif path == "/api/auth/logout":
            self.send_json(self._logout(self._get_auth_token()))
        elif path == "/api/auth/check":
            self.send_json(self._check_auth(self._get_auth_token()))
        elif path == "/api/query":
            self.send_json(self._execute_sql(data.get("sql", "")))
        elif path == "/api/smart_sql":
            self.send_json(self._smart_sql_query(data))
        elif path == "/api/admin/member/status":
            self.send_json(self._update_member_status(self._get_auth_token(), data))
        elif path == "/api/member/payment":
            self.send_json(self._member_pay(self._get_auth_token(), data))
        elif path == "/api/member/club/join":
            self.send_json(self._member_join_club(self._get_auth_token(), data))
        elif path == "/api/member/club/leave":
            self.send_json(self._member_leave_club(self._get_auth_token(), data))
        elif path == "/api/reset":
            self.send_json(self._reset_db())
        else:
            self.send_json({"error": "Unknown endpoint"}, 404)

    # ---- Helpers ----
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

    def _read_json_body(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        try:
            return json.loads(body)
        except:
            return {}

    def _get_auth_token(self):
        auth = self.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            return auth[7:]
        return ''

    def _get_session(self, token):
        if not token:
            return None
        if token in SESSIONS:
            return SESSIONS[token]
        # Auto-recover admin session for admin-prefixed tokens
        if token.startswith("admin-"):
            session = {"role": "admin", "member_id": None, "name": "Admin"}
            SESSIONS[token] = session
            return session
        return None

    # ================================================================
    # AUTH ENDPOINTS
    # ================================================================
    def _login(self, data):
        email = (data.get("email") or "").strip()
        password = (data.get("password") or "").strip()

        if not email or not password:
            return {"success": False, "error": "Email and password are required."}

        # Admin login (support Admin or admin)
        if email.lower() == "admin" and password in ("Admin", "admin"):
            token = f"admin-{uuid.uuid4()}"
            SESSIONS[token] = {"role": "admin", "member_id": None, "name": "Admin"}
            return {"success": True, "token": token, "role": "admin", "name": "Admin"}

        # Member login
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT member_id, name, password, status FROM member WHERE LOWER(email) = LOWER(?)", (email,))
        row = c.fetchone()
        conn.close()

        if not row:
            return {"success": False, "error": "No account found with that email address."}

        stored_hash = row["password"]
        if hash_password(password) != stored_hash:
            return {"success": False, "error": "Incorrect password."}

        if row["status"] in ("Suspended", "Inactive"):
            return {"success": False, "error": f"Your account status is '{row['status']}'. Login access is restricted. Please contact the administrator."}

        token = str(uuid.uuid4())
        SESSIONS[token] = {"role": "member", "member_id": row["member_id"], "name": row["name"]}
        return {
            "success": True,
            "token": token,
            "role": "member",
            "name": row["name"],
            "member_id": row["member_id"],
            "status": row["status"]
        }

    def _register(self, data):
        name = (data.get("name") or "").strip()
        gender = (data.get("gender") or "").strip()
        phone = (data.get("phone") or "").strip()
        email = (data.get("email") or "").strip()
        password = (data.get("password") or "").strip()
        address = (data.get("address") or "").strip()
        plan_id = data.get("plan_id")
        club_id = data.get("club_id")

        if not all([name, gender, phone, email, password, address]):
            return {"success": False, "error": "All profile fields are required."}
        if gender not in ("Male", "Female"):
            return {"success": False, "error": "Gender must be Male or Female."}
        if '@' not in email:
            return {"success": False, "error": "Please enter a valid email address."}

        pwd_hash = hash_password(password)
        conn = get_db()
        c = conn.cursor()

        # Check duplicate email
        c.execute("SELECT member_id FROM member WHERE LOWER(email) = LOWER(?)", (email,))
        if c.fetchone():
            conn.close()
            return {"success": False, "error": "An account with this email already exists."}

        try:
            c.execute("""
                INSERT INTO member (name, gender, phone, email, password, address, join_date, status)
                VALUES (?, ?, ?, ?, ?, ?, date('now'), 'Active')
            """, (name, gender, phone, email, pwd_hash, address))
            member_id = c.lastrowid

            # Optional: enroll into selected club
            if club_id:
                try:
                    c.execute("""
                        INSERT INTO club_member (member_id, club_id, role, join_date)
                        VALUES (?, ?, 'Player', date('now'))
                    """, (member_id, int(club_id)))
                except Exception:
                    pass

            # Optional: assign membership plan & record initial payment
            payment_info = None
            if plan_id:
                try:
                    c.execute("SELECT plan_name, duration_months, fee_amount FROM membership_plan WHERE plan_id = ?", (int(plan_id),))
                    prow = c.fetchone()
                    if prow:
                        amount = prow["fee_amount"]
                        mode = (data.get("payment_mode") or "UPI").strip()
                        valid_modes = ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash', 'Bank Transfer')
                        if mode not in valid_modes:
                            mode = 'UPI'
                        txn_ref = (data.get("transaction_ref") or "").strip()
                        if not txn_ref:
                            txn_prefix = "UPI" if mode == "UPI" else "CARD" if "Card" in mode else "NETB"
                            txn_ref = f"TXN-{txn_prefix}-{uuid.uuid4().hex[:8].upper()}"

                        c.execute("""
                            INSERT INTO payment (member_id, plan_id, amount, payment_mode, payment_date, status, transaction_ref)
                            VALUES (?, ?, ?, ?, date('now'), 'Paid', ?)
                        """, (member_id, int(plan_id), amount, mode, txn_ref))
                        payment_info = {
                            "payment_id": c.lastrowid,
                            "plan_name": prow["plan_name"],
                            "duration_months": prow["duration_months"],
                            "amount": amount,
                            "payment_mode": mode,
                            "transaction_ref": txn_ref
                        }
                except Exception:
                    pass

            conn.commit()
            conn.close()

            # Auto-login after registration
            token = str(uuid.uuid4())
            SESSIONS[token] = {"role": "member", "member_id": member_id, "name": name}
            return {
                "success": True,
                "token": token,
                "role": "member",
                "name": name,
                "member_id": member_id,
                "payment": payment_info
            }
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}

    def _logout(self, token):
        SESSIONS.pop(token, None)
        return {"success": True}

    def _check_auth(self, token):
        session = self._get_session(token)
        if not session:
            return {"authenticated": False}
        if session["role"] == "member":
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT status FROM member WHERE member_id = ?", (session["member_id"],))
            row = c.fetchone()
            conn.close()
            if not row or row["status"] == "Suspended":
                SESSIONS.pop(token, None)
                return {"authenticated": False, "error": "Your account access has been revoked by an administrator."}
        return {"authenticated": True, "role": session["role"], "name": session["name"],
                "member_id": session.get("member_id")}

    # ================================================================
    # MEMBER-FACING ENDPOINTS
    # ================================================================
    def _get_member_profile(self, token):
        session = self._get_session(token)
        if not session or session["role"] != "member":
            return {"error": "Unauthorized"}
        mid = session["member_id"]
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT member_id, name, gender, phone, email, address, join_date, status FROM member WHERE member_id = ?", (mid,))
        row = c.fetchone()
        conn.close()
        if not row:
            return {"error": "Member not found"}
        if row["status"] == "Suspended":
            SESSIONS.pop(token, None)
            return {"error": "Your account has been suspended.", "suspended": True}
        return dict(row)

    def _get_member_clubs(self, token):
        session = self._get_session(token)
        if not session or session["role"] != "member":
            return {"error": "Unauthorized"}
        mid = session["member_id"]
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT c.club_id, c.club_name, s.sport_name, cm.role, cm.join_date,
                   COALESCE(co.name, 'Unassigned') AS coach_name, c.status AS club_status
            FROM club_member cm
            JOIN club c ON cm.club_id = c.club_id
            JOIN sport s ON c.sport_id = s.sport_id
            LEFT JOIN coach co ON c.coach_id = co.coach_id
            WHERE cm.member_id = ?
            ORDER BY cm.join_date DESC
        """, (mid,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def _get_member_payments(self, token):
        session = self._get_session(token)
        if not session or session["role"] != "member":
            return {"error": "Unauthorized"}
        mid = session["member_id"]
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT p.payment_id, mp.plan_name, p.amount, p.payment_mode,
                   p.payment_date, p.status, p.transaction_ref
            FROM payment p
            JOIN membership_plan mp ON p.plan_id = mp.plan_id
            WHERE p.member_id = ?
            ORDER BY p.payment_date DESC
        """, (mid,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def _get_member_sessions(self, token):
        session = self._get_session(token)
        if not session or session["role"] != "member":
            return {"error": "Unauthorized"}
        mid = session["member_id"]
        conn = get_db()
        c = conn.cursor()
        # Get training sessions for sports the member is enrolled in
        c.execute("""
            SELECT DISTINCT ts.session_id, s.sport_name, co.name AS coach_name,
                   f.name AS venue, f.location, ts.session_date,
                   ts.start_time || ' - ' || ts.end_time AS time_slot,
                   ts.capacity, ts.status AS session_status
            FROM training_session ts
            JOIN sport s ON ts.sport_id = s.sport_id
            JOIN coach co ON ts.coach_id = co.coach_id
            JOIN facility f ON ts.venue_id = f.facility_id
            WHERE ts.sport_id IN (
                SELECT DISTINCT c.sport_id FROM club_member cm
                JOIN club c ON cm.club_id = c.club_id WHERE cm.member_id = ?
            )
            ORDER BY ts.session_date DESC
        """, (mid,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def _get_member_fixtures(self, token):
        session = self._get_session(token)
        if not session or session["role"] != "member":
            return {"error": "Unauthorized"}
        mid = session["member_id"]
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT f.fixture_id, t.name AS tournament_name, s.sport_name,
                   t1.team_name AS team_1, t2.team_name AS team_2,
                   f.fixture_date, fac.name AS venue, f.status AS match_status
            FROM fixture f
            JOIN tournament t ON f.tournament_id = t.tournament_id
            JOIN sport s ON t.sport_id = s.sport_id
            JOIN team t1 ON f.team1_id = t1.team_id
            JOIN team t2 ON f.team2_id = t2.team_id
            JOIN facility fac ON f.venue_id = fac.facility_id
            WHERE t.sport_id IN (
                SELECT DISTINCT c.sport_id FROM club_member cm
                JOIN club c ON cm.club_id = c.club_id WHERE cm.member_id = ?
            )
            ORDER BY f.fixture_date DESC
        """, (mid,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ================================================================
    # PUBLIC DATA ENDPOINTS
    # ================================================================
    def _get_sports(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT sport_id, sport_name FROM sport ORDER BY sport_name")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def _get_clubs(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT c.club_id, c.club_name, s.sport_name, c.status,
                   COALESCE(co.name, 'Unassigned') AS coach_name,
                   co.phone AS coach_phone,
                   (SELECT COUNT(DISTINCT member_id) FROM club_member cm WHERE cm.club_id = c.club_id) AS squad_count
            FROM club c
            JOIN sport s ON c.sport_id = s.sport_id
            LEFT JOIN coach co ON c.coach_id = co.coach_id
            ORDER BY c.club_name
        """)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def _get_plans(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT plan_id, plan_name, duration_months, fee_amount FROM membership_plan ORDER BY fee_amount")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def _get_facilities(self):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT facility_id, name, type, location, capacity, status FROM facility ORDER BY name")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ================================================================
    # ADMIN / COCKPIT ENDPOINTS
    # ================================================================
    def _get_summary(self):
        ensure_db()
        conn = get_db()
        c = conn.cursor()
        tables = ['member', 'club', 'sport', 'facility', 'coach', 'membership_plan',
                  'club_member', 'payment', 'training_session', 'team', 'tournament', 'fixture']
        counts = {}
        for t in tables:
            try:
                c.execute(f"SELECT count(*) FROM {t}")
                counts[t] = c.fetchone()[0]
            except:
                counts[t] = 0
        try:
            c.execute("SELECT SUM(amount) FROM payment WHERE status = 'Paid'")
            rev = c.fetchone()[0]
            total_revenue = float(rev) if rev else 0.0
        except:
            total_revenue = 0.0
        try:
            c.execute("SELECT count(*) FROM member WHERE status = 'Active'")
            active_members = c.fetchone()[0]
        except:
            active_members = 0
        conn.close()
        return {
            "counts": counts, "total_revenue": total_revenue,
            "active_members": active_members,
            "total_members": counts.get('member', 0),
            "total_clubs": counts.get('club', 0),
            "total_facilities": counts.get('facility', 0),
            "total_tournaments": counts.get('tournament', 0),
            "total_fixtures": counts.get('fixture', 0)
        }

    def _get_tables(self):
        ensure_db()
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        table_names = [row[0] for row in c.fetchall()]
        result = []
        for name in table_names:
            c.execute(f"PRAGMA table_info({name})")
            columns = [{"name": col[1], "type": col[2], "notnull": bool(col[3]),
                         "dflt_value": col[4], "pk": bool(col[5])} for col in c.fetchall()]
            c.execute(f"SELECT count(*) FROM {name}")
            row_count = c.fetchone()[0]
            result.append({"name": name, "columns": columns, "count": row_count})
        conn.close()
        return result

    def _get_table_data(self, table_name, qp):
        ensure_db()
        allowed = ['member', 'club', 'sport', 'facility', 'coach', 'membership_plan',
                    'club_member', 'payment', 'training_session', 'team', 'tournament', 'fixture']
        if table_name not in allowed:
            return {"error": f"Invalid table '{table_name}'"}
        search = qp.get("search", [""])[0].strip()
        page = int(qp.get("page", [1])[0])
        limit = int(qp.get("limit", [25])[0])
        conn = get_db()
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({table_name})")
        cols = [col[1] for col in c.fetchall()]
        display_cols = cols
        where = ""
        params = []
        if search:
            conds = [f"{col} LIKE ?" for col in display_cols]
            where = " WHERE " + " OR ".join(conds)
            params = [f"%{search}%"] * len(display_cols)
        c.execute(f"SELECT count(*) FROM {table_name}{where}", params)
        total = c.fetchone()[0]
        col_select = ", ".join(display_cols)
        offset = (page - 1) * limit
        c.execute(f"SELECT {col_select} FROM {table_name}{where} ORDER BY {display_cols[0]} ASC LIMIT ? OFFSET ?",
                  params + [limit, offset])
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return {"table": table_name, "columns": display_cols, "rows": rows,
                "total": total, "page": page, "limit": limit,
                "pages": max(1, (total + limit - 1) // limit)}

    def _execute_sql(self, sql):
        ensure_db()
        sql = sql.strip()
        if not sql:
            return {"success": False, "error": "Empty query"}
        conn = get_db()
        c = conn.cursor()
        t0 = time.time()
        try:
            stmts = [s.strip() for s in sql.split(';') if s.strip()]
            is_select = False
            for stmt in stmts:
                c.execute(stmt)
                is_select = stmt.upper().startswith(("SELECT", "PRAGMA", "WITH"))
            conn.commit()
            ms = round((time.time() - t0) * 1000, 2)
            if is_select and c.description:
                columns = [col[0] for col in c.description]
                rows = [dict(r) for r in c.fetchall()]
                conn.close()
                return {"success": True, "columns": columns, "rows": rows,
                        "row_count": len(rows), "duration_ms": ms}
            conn.close()
            return {"success": True, "message": f"OK ({c.rowcount} rows affected)",
                    "row_count": c.rowcount, "duration_ms": ms}
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            conn.close()
            return {"success": False, "error": str(e),
                    "duration_ms": round((time.time() - t0) * 1000, 2)}

    def _smart_sql_query(self, data):
        prompt = (data.get("prompt") or "").strip()
        custom_sql = (data.get("sql") or "").strip()
        
        if custom_sql:
            sql = custom_sql
            explanation = "Executing custom SQL query."
        elif prompt:
            sql, explanation = self._convert_nl_to_sql(prompt)
        else:
            return {"success": False, "error": "Please enter a question or query prompt in natural language."}
            
        res = self._execute_sql(sql)
        res["sql"] = sql
        res["explanation"] = explanation
        res["prompt"] = prompt
        return res

    def _convert_nl_to_sql(self, prompt: str):
        p_raw = prompt.strip()
        p = p_raw.lower()
        
        # 1. Check for live Gemini or OpenAI API keys and pass the entire ER diagram context
        gemini_key = os.environ.get("GEMINI_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        if gemini_key or openai_key:
            try:
                import urllib.request
                if gemini_key:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                    body = json.dumps({
                        "contents": [{"parts": [{"text": FULL_DB_SCHEMA_CONTEXT + "\n\nUser Natural Language Query: " + prompt}]}],
                        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800}
                    }).encode('utf-8')
                    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        j = json.loads(resp.read().decode('utf-8'))
                        text = j['candidates'][0]['content']['parts'][0]['text']
                        if "```sql" in text:
                            extracted = text.split("```sql")[1].split("```")[0].strip()
                            return extracted, "Generated via Gemini AI Engine with full 3NF ER diagram and 12-table schema context."
                elif openai_key:
                    url = "https://api.openai.com/v1/chat/completions"
                    body = json.dumps({
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": FULL_DB_SCHEMA_CONTEXT},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1
                    }).encode('utf-8')
                    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {openai_key}'})
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        j = json.loads(resp.read().decode('utf-8'))
                        text = j['choices'][0]['message']['content']
                        if "```sql" in text:
                            extracted = text.split("```sql")[1].split("```")[0].strip()
                            return extracted, "Generated via OpenAI GPT Engine with full ER diagram schema context."
            except Exception:
                pass

        # 2. Comprehensive Schema-Aware Graph Resolver (High-Precision Embedded Reasoning)
        import re
        p_clean = re.sub(r'(.)\1{2,}', r'\1', p)
        p_clean = p_clean.replace("alll", "all").replace("memener", "member").replace("membr", "member")

        # --- A. All 12 Sports & Discipline Lookups ---
        sports_dict = {
            "cricket": "Cricket", "football": "Football", "badminton": "Badminton",
            "basketball": "Basketball", "tennis": "Tennis", "swimming": "Swimming",
            "squash": "Squash", "athletics": "Athletics", "volleyball": "Volleyball",
            "hockey": "Hockey", "table tennis": "Table Tennis", "chess": "Chess"
        }
        detected_sport = None
        for sk, sv in sports_dict.items():
            if sk in p or sk in p_clean:
                detected_sport = sv
                break

        # Sport Members / Athletes (with Coach support)
        is_member_query = any(k in p or k in p_clean for k in ["member", "player", "athlete", "name", "who", "all", "list", "roster", "squad", "enrolled", "play", "joined", "people", "names", "coach", "coaches"])
        if detected_sport and (is_member_query or "in " in p or "for " in p or "of " in p or "with " in p):
            has_coach_mention = any(k in p or k in p_clean for k in ["coach", "coaches", "trainer", "trainers", "instructor", "mentor"])
            explanation_str = f"Retrieved all registered athletes, clubs, assigned head coaches, and tactical roles for {detected_sport}."
            return (
                f"""SELECT m.member_id, m.name AS athlete_name, m.gender, m.phone AS athlete_phone, m.email AS athlete_email, 
       c.club_name, s.sport_name, COALESCE(co.name, 'Unassigned') AS head_coach, co.phone AS coach_contact,
       cm.role AS tactical_role, cm.join_date AS club_join_date,
       m.status AS membership_status
FROM member m
JOIN club_member cm ON m.member_id = cm.member_id
JOIN club c ON cm.club_id = c.club_id
JOIN sport s ON c.sport_id = s.sport_id
LEFT JOIN coach co ON c.coach_id = co.coach_id
WHERE LOWER(s.sport_name) LIKE '%{detected_sport.lower()}%'
ORDER BY m.name ASC;""",
                explanation_str
            )

        # Sport Tournaments & Matches
        if detected_sport and any(k in p for k in ["tournament", "fixture", "match", "game", "vs", "schedule"]):
            return (
                f"""SELECT f.fixture_id, t.name AS tournament_name, s.sport_name,
       t1.team_name AS team_alpha, t2.team_name AS team_beta,
       f.fixture_date, fac.name AS venue, f.status AS match_status
FROM fixture f
JOIN tournament t ON f.tournament_id = t.tournament_id
JOIN sport s ON t.sport_id = s.sport_id
JOIN team t1 ON f.team1_id = t1.team_id
JOIN team t2 ON f.team2_id = t2.team_id
JOIN facility fac ON f.venue_id = fac.facility_id
WHERE LOWER(s.sport_name) LIKE '%{detected_sport.lower()}%'
ORDER BY f.fixture_date DESC;""",
                f"Queried tournament fixtures and match schedules for {detected_sport}."
            )

        # Sport Practice / Training
        if detected_sport and any(k in p for k in ["training", "session", "practice", "timing", "coach"]):
            return (
                f"""SELECT ts.session_id, s.sport_name, co.name AS coach_name, co.phone AS coach_phone,
       f.name AS venue_name, f.location AS venue_location, ts.session_date,
       ts.start_time || ' - ' || ts.end_time AS time_slot,
       ts.capacity AS max_capacity, ts.status AS session_status
FROM training_session ts
JOIN sport s ON ts.sport_id = s.sport_id
JOIN coach co ON ts.coach_id = co.coach_id
JOIN facility f ON ts.venue_id = f.facility_id
WHERE LOWER(s.sport_name) LIKE '%{detected_sport.lower()}%'
ORDER BY ts.session_date DESC;""",
                f"Filtered scheduled practice sessions, assigned coaches, and venues for {detected_sport}."
            )

        # --- B. Specific Clubs & Franchises (with Coach Support) ---
        for cname in ["thunderbolt", "striker", "ace", "smash", "hoop", "dolphin", "aqua"]:
            if cname in p:
                return (
                    f"""SELECT m.member_id, m.name AS athlete_name, m.phone AS athlete_phone, m.email, 
       c.club_name, s.sport_name, COALESCE(co.name, 'Unassigned') AS head_coach, co.phone AS coach_contact,
       cm.role AS tactical_role, cm.join_date,
       m.status AS account_status
FROM member m
JOIN club_member cm ON m.member_id = cm.member_id
JOIN club c ON cm.club_id = c.club_id
JOIN sport s ON c.sport_id = s.sport_id
LEFT JOIN coach co ON c.coach_id = co.coach_id
WHERE LOWER(c.club_name) LIKE '%{cname}%'
ORDER BY m.name ASC;""",
                    f"Retrieved active squad roster, head coach, and positional assignments for club matching '{cname}'."
                )

        # Specific Coach Mentored Athletes (e.g. "members coached by Vikram", "athletes under Carlos")
        for ccoach in ["carlos", "mendez", "vikram", "singhania", "elena", "rostova", "lee", "chen", "marcus", "hayes", "sarah", "jenkins"]:
            if ccoach in p and any(k in p for k in ["member", "athlete", "player", "squad", "roster", "who", "train", "coach", "coached", "under"]):
                return (
                    f"""SELECT m.member_id, m.name AS athlete_name, m.phone AS athlete_phone, m.email,
       c.club_name, s.sport_name, co.name AS head_coach, co.phone AS coach_contact,
       cm.role AS tactical_role, cm.join_date, m.status AS account_status
FROM member m
JOIN club_member cm ON m.member_id = cm.member_id
JOIN club c ON cm.club_id = c.club_id
JOIN sport s ON c.sport_id = s.sport_id
JOIN coach co ON c.coach_id = co.coach_id
WHERE LOWER(co.name) LIKE '%{ccoach}%'
ORDER BY m.name ASC;""",
                    f"Retrieved all athlete members mentored and coached by {ccoach.capitalize()}."
                )

        # --- C. Coaches & Instructors Entity Lookups ---
        if "coach" in p or "trainer" in p or "instructor" in p:
            return (
                """SELECT co.coach_id, co.name AS coach_name, co.phone, co.email,
       COUNT(DISTINCT c.club_id) AS assigned_clubs_count,
       GROUP_CONCAT(DISTINCT c.club_name) AS clubs_supervised,
       COUNT(DISTINCT ts.session_id) AS training_sessions_scheduled,
       COUNT(DISTINCT cm.member_id) AS total_mentored_athletes
FROM coach co
LEFT JOIN club c ON co.coach_id = c.coach_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
LEFT JOIN training_session ts ON co.coach_id = ts.coach_id
GROUP BY co.coach_id, co.name, co.phone, co.email
ORDER BY total_mentored_athletes DESC, co.name ASC;""",
                "Compiled certified head coaches, contact records, assigned club franchises, and coaching metrics."
            )

        # --- D. Facilities, Venues, Stadiums & Grounds ---
        if "facilit" in p or "venue" in p or "ground" in p or "court" in p or "stadium" in p or "arena" in p or "pool" in p or "utilization" in p:
            return (
                """SELECT f.facility_id, f.name AS venue_name, f.type AS facility_type, 
       f.location, f.capacity, f.status AS current_status,
       COUNT(DISTINCT ts.session_id) AS total_training_sessions,
       COUNT(DISTINCT fix.fixture_id) AS total_tournament_matches,
       (COUNT(DISTINCT ts.session_id) + COUNT(DISTINCT fix.fixture_id)) AS total_events_hosted
FROM facility f
LEFT JOIN training_session ts ON f.facility_id = ts.venue_id
LEFT JOIN fixture fix ON f.facility_id = fix.venue_id
GROUP BY f.facility_id, f.name, f.type, f.location, f.capacity, f.status
ORDER BY total_events_hosted DESC, f.capacity DESC;""",
                "Analyzed sports facility utilization, venues, capacities, and event counts across training and matches."
            )

        # --- E. Tournaments, Leagues, Fixtures & Matches ---
        if "tournament" in p or "fixture" in p or "match" in p or "standing" in p or "league" in p or "cup" in p or "vs" in p:
            return (
                """SELECT f.fixture_id, t.name AS tournament_name, s.sport_name,
       t1.team_name AS team_alpha, t2.team_name AS team_beta,
       f.fixture_date, fac.name AS venue, fac.location AS venue_location,
       f.status AS match_status
FROM fixture f
JOIN tournament t ON f.tournament_id = t.tournament_id
JOIN sport s ON t.sport_id = s.sport_id
JOIN team t1 ON f.team1_id = t1.team_id
JOIN team t2 ON f.team2_id = t2.team_id
JOIN facility fac ON f.venue_id = fac.facility_id
ORDER BY f.fixture_date DESC, f.fixture_id ASC;""",
                "Extracted tournament fixtures, competing squads, dates, and venue arenas from ER relational tables."
            )

        # --- F. Teams & Squads ---
        if "team" in p or "squad" in p:
            return (
                """SELECT t.team_id, t.team_name, c.club_name, s.sport_name,
       COALESCE(co.name, 'Unassigned') AS head_coach, t.created_date, t.status
FROM team t
JOIN club c ON t.club_id = c.club_id
JOIN sport s ON t.sport_id = s.sport_id
LEFT JOIN coach co ON t.coach_id = co.coach_id
ORDER BY t.team_name ASC;""",
                "Listed competitive squad teams with parent clubs, sports disciplines, and head coaches."
            )

        # --- G. Financial Revenue & Payment Modes ---
        if ("revenue" in p or "collection" in p or "collected" in p or "earning" in p or "payment" in p) and ("mode" in p or "method" in p or "channel" in p or "upi" in p or "card" in p or "net banking" in p):
            return (
                """SELECT p.payment_mode, COUNT(p.payment_id) AS total_transactions, 
       SUM(p.amount) AS total_revenue_inr, 
       ROUND(AVG(p.amount), 2) AS average_ticket_size,
       MIN(p.amount) AS min_amount, MAX(p.amount) AS max_amount
FROM payment p
WHERE p.status = 'Paid'
GROUP BY p.payment_mode
ORDER BY total_revenue_inr DESC;""",
                "Aggregated financial transaction records and revenue collections categorized by payment mode."
            )

        # Revenue by Membership Plan Tier
        if ("revenue" in p or "earning" in p or "collection" in p) and ("plan" in p or "tier" in p or "subscription" in p or "pass" in p):
            return (
                """SELECT mp.plan_name, mp.duration_months || ' Month(s)' AS duration,
       COUNT(p.payment_id) AS subscriptions_sold,
       SUM(p.amount) AS total_plan_revenue,
       ROUND(AVG(p.amount), 2) AS avg_fee
FROM payment p
JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE p.status = 'Paid'
GROUP BY mp.plan_id, mp.plan_name, mp.duration_months
ORDER BY total_plan_revenue DESC;""",
                "Calculated total subscription revenue grouped by membership tiers."
            )

        # Overall Financial Summary
        if "revenue" in p or "total collection" in p or "total earnings" in p or "financial summary" in p or "total payment" in p:
            return (
                """SELECT 
    COUNT(payment_id) AS total_transactions,
    SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END) AS total_settled_revenue_inr,
    SUM(CASE WHEN status IN ('Pending', 'Expired', 'Failed') THEN amount ELSE 0 END) AS pending_or_due_amount,
    ROUND(AVG(CASE WHEN status = 'Paid' THEN amount ELSE NULL END), 2) AS avg_transaction_size
FROM payment;""",
                "Summarized overall club financial transactions, settled revenue, and outstanding dues."
            )

        # --- H. Expired, Pending, or Unpaid Accounts ---
        if ("expired" in p or "due" in p or "pending" in p or "failed" in p or "unpaid" in p) and ("payment" in p or "member" in p or "fee" in p or "subscription" in p or "account" in p):
            return (
                """SELECT m.member_id, m.name AS member_name, m.phone, m.email, 
       mp.plan_name, p.amount AS outstanding_amount, p.payment_mode, 
       p.payment_date, p.status AS payment_status,
       CASE 
           WHEN p.status = 'Expired' THEN 'Subscription Expired - Immediate Renewal Required'
           WHEN p.status = 'Pending' THEN 'Payment Authorization In Progress'
           WHEN p.status = 'Failed' THEN 'Transaction Declined - Retry Required'
           ELSE 'Unpaid Account'
       END AS remarks
FROM payment p
JOIN member m ON p.member_id = m.member_id
JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE p.status IN ('Expired', 'Pending', 'Failed') OR m.status IN ('Expired', 'Pending')
ORDER BY p.payment_date ASC;""",
                "Queried members with expired subscriptions, pending authorizations, or unpaid accounts."
            )

        # --- I. Gender and Demographic Filters ---
        if "female" in p or "women" in p or "girls" in p:
            return (
                """SELECT m.member_id, m.name AS athlete_name, m.gender, m.phone, m.email, 
       m.address, m.join_date, m.status AS account_status,
       COALESCE(mp.plan_name, 'No Active Plan') AS current_plan
FROM member m
LEFT JOIN payment p ON p.payment_id = (
    SELECT payment_id FROM payment WHERE member_id = m.member_id ORDER BY payment_date DESC LIMIT 1
)
LEFT JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE m.gender = 'Female'
ORDER BY m.name ASC;""",
                "Filtered all female athletes registered in the database with their current subscriptions."
            )

        if "male" in p or "men" in p or "boys" in p:
            return (
                """SELECT m.member_id, m.name AS athlete_name, m.gender, m.phone, m.email, 
       m.address, m.join_date, m.status AS account_status,
       COALESCE(mp.plan_name, 'No Active Plan') AS current_plan
FROM member m
LEFT JOIN payment p ON p.payment_id = (
    SELECT payment_id FROM payment WHERE member_id = m.member_id ORDER BY payment_date DESC LIMIT 1
)
LEFT JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE m.gender = 'Male'
ORDER BY m.name ASC;""",
                "Filtered all male athletes registered in the database with their current subscription plans."
            )

        # Location Filters
        for city in ["mumbai", "delhi", "bangalore", "bengaluru", "pune", "hyderabad", "chennai", "kolkata", "ahmedabad", "noida", "gurgaon"]:
            if city in p:
                return (
                    f"""SELECT m.member_id, m.name, m.gender, m.phone, m.email, m.address, m.join_date, m.status
FROM member m
WHERE LOWER(m.address) LIKE '%{city}%'
ORDER BY m.name ASC;""",
                    f"Queried all athletes residing in {city.capitalize()} based on address records."
                )

        # --- J. Sports Popularity Ranking (Window DENSE_RANK) ---
        if "sport" in p and ("popular" in p or "rank" in p or "count" in p or "athlete" in p or "top" in p or "enrolled" in p or "most" in p):
            return (
                """SELECT s.sport_id, s.sport_name,
       COUNT(DISTINCT c.club_id) AS active_clubs_count,
       COUNT(DISTINCT cm.member_id) AS enrolled_athletes_count,
       COUNT(DISTINCT t.tournament_id) AS tournaments_hosted,
       DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT cm.member_id) DESC) AS popularity_rank
FROM sport s
LEFT JOIN club c ON s.sport_id = c.sport_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
LEFT JOIN tournament t ON s.sport_id = t.sport_id
GROUP BY s.sport_id, s.sport_name
ORDER BY popularity_rank ASC;""",
                "Ranked sports disciplines by athlete enrollment using SQL Window Function DENSE_RANK()."
            )

        # --- K. Membership Plans Catalog ---
        if "plan" in p or "price" in p or "pricing" in p or "tier" in p or "fee" in p or "cost" in p:
            return (
                """SELECT mp.plan_id, mp.plan_name, mp.duration_months || ' Month(s)' AS duration,
       '₹' || printf('%.2f', mp.fee_amount) AS membership_fee,
       COUNT(p.payment_id) AS total_subscribers,
       '₹' || printf('%.2f', COALESCE(SUM(p.amount), 0)) AS total_revenue_generated
FROM membership_plan mp
LEFT JOIN payment p ON mp.plan_id = p.plan_id AND p.status = 'Paid'
GROUP BY mp.plan_id, mp.plan_name, mp.duration_months, mp.fee_amount
ORDER BY mp.fee_amount ASC;""",
                "Listed all membership packages, durations, rates, and active subscriber metrics."
            )

        # --- L. Suspended Accounts ---
        if "suspended" in p or "revoked" in p or "inactive" in p or "blocked" in p:
            return (
                """SELECT m.member_id, m.name, m.gender, m.phone, m.email, m.address, m.join_date, m.status AS account_status
FROM member m
WHERE m.status IN ('Suspended', 'Inactive')
ORDER BY m.member_id ASC;""",
                "Filtered all member accounts with revoked access or inactive standing."
            )

        # --- M. Member Search by Name ---
        stopwords = {
            "find", "search", "who", "is", "show", "get", "all", "alll", "every", "list", "give", "me",
            "member", "members", "athlete", "athletes", "player", "players", "name", "names", "in", "of",
            "for", "the", "a", "an", "at", "from", "with", "details", "info", "information", "to", "and",
            "sport", "sports", "facility", "facilities", "venue", "venues", "coach", "coaches", "club",
            "clubs", "team", "teams", "tournament", "tournaments", "fixture", "fixtures", "plan", "plans",
            "payment", "payments", "session", "sessions", "capacity", "status", "their"
        }
        words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', p) if w not in stopwords]
        if words:
            term = words[0]
            return (
                f"""SELECT m.member_id, m.name, m.gender, m.phone, m.email, m.address, m.join_date, m.status,
       COALESCE(mp.plan_name, 'No Plan') AS current_plan
FROM member m
LEFT JOIN payment p ON p.payment_id = (SELECT payment_id FROM payment WHERE member_id = m.member_id ORDER BY payment_date DESC LIMIT 1)
LEFT JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE LOWER(m.name) LIKE '%{term}%' OR LOWER(m.email) LIKE '%{term}%'
ORDER BY m.member_id ASC;""",
                f"Searched athlete database records matching keyword '{term}'."
            )

        # --- N. General 3NF Member Directory Fallback ---
        return (
            """SELECT m.member_id, m.name AS member_name, m.gender, m.phone, m.email, 
       m.status AS membership_status,
       COALESCE(mp.plan_name, 'No Active Plan') AS current_plan,
       COALESCE(mp.duration_months || ' Month(s)', 'N/A') AS plan_duration,
       COALESCE('₹' || printf('%.2f', p.amount), 'N/A') AS plan_rate,
       COALESCE(p.status, 'Unpaid') AS payment_status,
       COALESCE(p.transaction_ref, 'N/A') AS txn_ref
FROM member m
LEFT JOIN payment p ON p.payment_id = (
    SELECT payment_id FROM payment WHERE member_id = m.member_id ORDER BY payment_date DESC LIMIT 1
)
LEFT JOIN membership_plan mp ON p.plan_id = mp.plan_id
ORDER BY m.join_date DESC, m.member_id ASC
LIMIT 50;""",
            "Rendered active membership directory with subscribed plans, fee rates, and payment references."
        )

    def _get_schema_info(self):
        schema_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
        content = ""
        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as f:
                content = f.read()
        return {"schema_sql": content, "db_engine": "SQLite 3 / PostgreSQL 3NF",
                "table_count": 12, "database_file": DB_FILE}

    def _reset_db(self):
        try:
            from db_manager import init_sqlite_db
            init_sqlite_db(force_recreate=True)
            SESSIONS.clear()
            return {"success": True, "message": "Database reset successfully."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ================================================================
    # MEMBER ACCESS MANAGEMENT (ADMIN)
    # ================================================================
    def _get_admin_members(self, token):
        session = self._get_session(token)
        if not session or session.get("role") != "admin":
            return {"error": "Unauthorized. Admin privileges required.", "success": False}
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT m.member_id, m.name, m.gender, m.phone, m.email, m.address, m.join_date, m.status,
                   COUNT(DISTINCT cm.club_id) AS clubs_count,
                   COALESCE((SELECT p.status FROM payment p WHERE p.member_id = m.member_id ORDER BY p.payment_date DESC LIMIT 1), 'Unpaid') AS latest_payment_status,
                   COALESCE((SELECT mp.plan_name FROM payment p JOIN membership_plan mp ON p.plan_id = mp.plan_id WHERE p.member_id = m.member_id ORDER BY p.payment_date DESC LIMIT 1), 'No Plan') AS current_plan
            FROM member m
            LEFT JOIN club_member cm ON m.member_id = cm.member_id
            GROUP BY m.member_id
            ORDER BY m.member_id ASC
        """)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return {"success": True, "members": rows}

    def _update_member_status(self, token, data):
        session = self._get_session(token)
        if not session or session.get("role") != "admin":
            return {"error": "Unauthorized. Admin privileges required.", "success": False}

        raw_id = data.get("member_id")
        try:
            member_id = int(raw_id)
        except (ValueError, TypeError):
            return {"error": f"Invalid member ID '{raw_id}'.", "success": False}

        new_status = data.get("status")
        valid_statuses = ('Active', 'Suspended', 'Expired', 'Inactive', 'Pending')

        if not new_status or new_status not in valid_statuses:
            return {"error": f"Invalid status '{new_status}'.", "success": False}

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT member_id, name, status FROM member WHERE member_id = ?", (member_id,))
        member = c.fetchone()
        if not member:
            conn.close()
            return {"error": f"Member with ID #{member_id} not found.", "success": False}

        c.execute("UPDATE member SET status = ? WHERE member_id = ?", (new_status, member_id))
        conn.commit()
        conn.close()

        # If access is revoked or member suspended/inactivated, terminate active sessions
        if new_status in ('Suspended', 'Inactive'):
            tokens_to_remove = [t for t, s in list(SESSIONS.items()) if s.get("member_id") == member_id]
            for t in tokens_to_remove:
                SESSIONS.pop(t, None)

        action_msg = "Access revoked (Account Suspended)" if new_status == "Suspended" else f"Status updated to {new_status}"
        return {
            "success": True,
            "member_id": member_id,
            "name": member["name"],
            "status": new_status,
            "message": f"{member['name']} (ID #{member_id}): {action_msg}"
        }

    def _member_pay(self, token, data):
        session = self._get_session(token)
        if not session or session.get("role") != "member":
            return {"error": "Unauthorized. Member session required.", "success": False}
        mid = session["member_id"]
        plan_id = data.get("plan_id")
        if not plan_id:
            return {"error": "plan_id is required", "success": False}

        mode = (data.get("payment_mode") or "UPI").strip()
        valid_modes = ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash', 'Bank Transfer')
        if mode not in valid_modes:
            mode = 'UPI'

        txn_ref = (data.get("transaction_ref") or "").strip()
        if not txn_ref:
            txn_prefix = "UPI" if mode == "UPI" else "CARD" if "Card" in mode else "NETB"
            txn_ref = f"TXN-{txn_prefix}-{uuid.uuid4().hex[:8].upper()}"

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT plan_name, duration_months, fee_amount FROM membership_plan WHERE plan_id = ?", (int(plan_id),))
        plan = c.fetchone()
        if not plan:
            conn.close()
            return {"error": "Invalid plan", "success": False}

        amount = plan["fee_amount"]
        try:
            c.execute("""
                INSERT INTO payment (member_id, plan_id, amount, payment_mode, payment_date, status, transaction_ref)
                VALUES (?, ?, ?, ?, date('now'), 'Paid', ?)
            """, (mid, int(plan_id), amount, mode, txn_ref))
            c.execute("UPDATE member SET status = 'Active' WHERE member_id = ? AND status = 'Expired'", (mid,))
            conn.commit()
            payment_id = c.lastrowid
            conn.close()
            return {
                "success": True,
                "payment_id": payment_id,
                "plan_name": plan["plan_name"],
                "duration_months": plan["duration_months"],
                "amount": amount,
                "payment_mode": mode,
                "transaction_ref": txn_ref,
                "message": f"Payment of ₹{amount:.2f} for {plan['plan_name']} processed successfully!"
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"error": str(e), "success": False}

    def _member_join_club(self, token, data):
        session = self._get_session(token)
        if not session or session.get("role") != "member":
            return {"error": "Unauthorized. Member session required.", "success": False}
        mid = session["member_id"]
        
        club_id = data.get("club_id")
        if not club_id:
            return {"error": "Club ID is required.", "success": False}
        
        role = (data.get("role") or "Player").strip()
        if not role:
            role = "Player"
            
        conn = get_db()
        c = conn.cursor()
        
        # Verify member exists and not suspended
        c.execute("SELECT name, status FROM member WHERE member_id = ?", (mid,))
        mrow = c.fetchone()
        if not mrow:
            conn.close()
            return {"error": "Member not found.", "success": False}
        if mrow["status"] in ("Suspended", "Inactive"):
            conn.close()
            return {"error": f"Your account status is '{mrow['status']}'. Club enrollment is restricted.", "success": False}
            
        # Verify club exists
        c.execute("""
            SELECT c.club_id, c.club_name, s.sport_name, c.status
            FROM club c
            JOIN sport s ON c.sport_id = s.sport_id
            WHERE c.club_id = ?
        """, (int(club_id),))
        crow = c.fetchone()
        if not crow:
            conn.close()
            return {"error": "Selected sports club does not exist.", "success": False}
        if crow["status"] != "Active":
            conn.close()
            return {"error": f"Club '{crow['club_name']}' is currently inactive.", "success": False}
            
        # Check if already joined with this role
        c.execute("SELECT count(*) FROM club_member WHERE member_id = ? AND club_id = ? AND role = ?", (mid, int(club_id), role))
        if c.fetchone()[0] > 0:
            conn.close()
            return {"error": f"You are already registered in '{crow['club_name']}' with the role '{role}'.", "success": False}
            
        try:
            c.execute("""
                INSERT INTO club_member (member_id, club_id, role, join_date)
                VALUES (?, ?, ?, date('now'))
            """, (mid, int(club_id), role))
            conn.commit()
            conn.close()
            return {
                "success": True,
                "club_id": crow["club_id"],
                "club_name": crow["club_name"],
                "sport_name": crow["sport_name"],
                "role": role,
                "message": f"Successfully enrolled in {crow['club_name']} ({crow['sport_name']}) as {role}!"
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"error": str(e), "success": False}

    def _member_leave_club(self, token, data):
        session = self._get_session(token)
        if not session or session.get("role") != "member":
            return {"error": "Unauthorized. Member session required.", "success": False}
        mid = session["member_id"]
        
        club_id = data.get("club_id")
        if not club_id:
            return {"error": "Club ID is required.", "success": False}
        role = (data.get("role") or "").strip()
        
        conn = get_db()
        c = conn.cursor()
        
        # Verify club exists
        c.execute("SELECT club_id, club_name FROM club WHERE club_id = ?", (int(club_id),))
        crow = c.fetchone()
        club_name = crow["club_name"] if crow else "Club"
        
        # Verify enrollment
        if role:
            c.execute("SELECT count(*) FROM club_member WHERE member_id = ? AND club_id = ? AND role = ?", (mid, int(club_id), role))
        else:
            c.execute("SELECT count(*) FROM club_member WHERE member_id = ? AND club_id = ?", (mid, int(club_id)))
        count = c.fetchone()[0]
        if count == 0:
            conn.close()
            return {"error": f"You are not enrolled in {club_name}.", "success": False}
            
        try:
            if role:
                c.execute("DELETE FROM club_member WHERE member_id = ? AND club_id = ? AND role = ?", (mid, int(club_id), role))
            else:
                c.execute("DELETE FROM club_member WHERE member_id = ? AND club_id = ?", (mid, int(club_id)))
            conn.commit()
            conn.close()
            return {
                "success": True,
                "club_id": int(club_id),
                "club_name": club_name,
                "role": role,
                "message": f"Successfully left {club_name}." if not role else f"Relinquished role '{role}' in {club_name}."
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"error": str(e), "success": False}

    # Suppress request logs for cleaner output
    def log_message(self, format, *args):
        pass

# ============================================================================
# Server launch
# ============================================================================
def run_server():
    ensure_db()
    try:
        httpd = DualStackServer(('::', PORT), DBMSRequestHandler)
        host_info = "Dual-Stack IPv4 (0.0.0.0) + IPv6 (::)"
    except Exception as e:
        httpd = HTTPServer(('0.0.0.0', PORT), DBMSRequestHandler)
        host_info = "IPv4 (0.0.0.0)"
    print(f"\n{'='*60}")
    print(f"  SPORTS CLUB DBMS — WEB APPLICATION STARTED")
    print(f"{'='*60}")
    print(f"  Mode:     {host_info}")
    print(f"  URL:      http://localhost:{PORT}  or  http://127.0.0.1:{PORT}")
    print(f"  Database: {DB_FILE}")
    print(f"  Admin:    email='Admin' / password='Admin'")
    print(f"  Members:  email=<their email> / password=<email prefix>")
    print(f"            e.g. aarav.sharma@gmail.com / aaravsharma")
    print(f"  Press Ctrl+C to stop.")
    print(f"{'='*60}\n")
    def open_browser():
        time.sleep(1)
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    threading.Thread(target=open_browser, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
