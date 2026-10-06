# 🏆 Sports Club Membership and Tournament Management System (DBMS)

An enterprise-grade **Relational Database Management System (RDBMS)** normalized to **Third Normal Form (3NF)** for multi-sport complexes, club franchises, athlete memberships, training venues, tournaments, and financial billing.

Includes a **Full Web Management Cockpit & Smart SQL Studio**, **Athlete Member Portal**, interactive **ER Diagram Visualizer**, and **Slide Presentation Deck**.

---

## 📌 Project Overview
The **Sports Club Management System** streamlines operations across multiple athletic disciplines by providing strict relational data integrity (ACID transactions), role-based access control, automated membership life-cycle tracking, and AI-assisted SQL query execution.

### Key Highlights
- **12 Relational Tables & 7 Analytical Views** normalized to 3NF.
- **Role-Based Web Portals**: Dedicated interfaces for **System Administrators** and **Athlete Members**.
- **Smart SQL Studio (AI NL-to-SQL)**: Converts natural language questions into executable 3NF SQL queries using schema context.
- **Club Membership & Role Management**: Real-time club enrollment and relinquishment with tactical role assignments (e.g., *Forward, Midfielder, Batsman, Bowler, Shuttler*).
- **Realistic Multi-Channel Checkout**: Realistic payment simulation for **UPI/QR**, **Credit/Debit Cards**, and **Net Banking** with instant GST tax invoice generation.
- **Security & Integrity**: Password hashing (SHA-256), composite primary keys, foreign key cascades, and real-time account suspension/activation.

---

## 🗄️ Database Relational Schema & Table Dictionary

```
[MEMBERSHIP_PLAN] 1 ──── N [PAYMENT] N ──── 1 [MEMBER] 
                                                │
                                                └──── N [CLUB_MEMBER] N ──── 1 [CLUB] N ──── 1 [COACH]
                                                                                │                 │
[FACILITY] 1 ──── N [TRAINING_SESSION] N ──── 1 [SPORT] 1 ──── N [CLUB]         │ 1               │ 1
    │                                              │                            │                 │
    │                                              │ 1                          ▼ N               ▼ N
    │                                              │                       [TEAM] ◄───────────────┘
    │                                              │                          │
    │                                              │ N                        │ N (Participates In)
    │                                              │                          │
    └─────────────────────────────────────────► [FIXTURE] ◄───────────────────┘
                                           (Team 1 vs Team 2)
```

### Complete 12-Table Entity & Attribute Reference

| Table Name | Primary Key | Foreign Keys | Key Attributes & Data Types | Description & Business Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **`member`** | `member_id` | — | `name` (VARCHAR), `gender` (VARCHAR), `phone` (VARCHAR), `email` (VARCHAR UNIQUE), `password` (VARCHAR/HASH), `address` (TEXT), `join_date` (DATE), `status` (VARCHAR) | Core athlete demographic and account security table. Status: `Active`, `Expired`, `Pending`, `Suspended`, `Inactive`. |
| **`sport`** | `sport_id` | — | `sport_name` (VARCHAR UNIQUE) | Sports discipline catalog (Cricket, Football, Tennis, Badminton, Basketball, Swimming, etc.). |
| **`membership_plan`** | `plan_id` | — | `plan_name` (VARCHAR), `duration_months` (INT > 0), `fee_amount` (DECIMAL >= 0) | Subscription tiers (e.g., Monthly Starter, Quarterly Pro, Annual Gold Elite Pass). |
| **`facility`** | `facility_id` | — | `name` (VARCHAR), `type` (VARCHAR), `location` (VARCHAR), `capacity` (INT > 0), `status` (VARCHAR) | Sports grounds, courts, and stadiums. Status: `Available`, `Booked`, `Under Maintenance`. |
| **`coach`** | `coach_id` | — | `name` (VARCHAR), `phone` (VARCHAR), `email` (VARCHAR UNIQUE) | Certified athletic coaches assigned to clubs, teams, and training sessions. |
| **`club`** | `club_id` | `sport_id` &rarr; `sport`, `coach_id` &rarr; `coach` | `club_name` (VARCHAR), `created_date` (DATE), `status` (VARCHAR) | Franchise sports clubs. Linked to exactly 1 sport and 1 head coach. |
| **`club_member`** | `(member_id, club_id, role)` | `member_id` &rarr; `member`, `club_id` &rarr; `club` | `role` (VARCHAR), `join_date` (DATE) | Bridge table resolving N:M athlete-to-club relationship with tactical role assignments. |
| **`payment`** | `payment_id` | `member_id` &rarr; `member`, `plan_id` &rarr; `membership_plan` | `amount` (DECIMAL > 0), `payment_mode` (VARCHAR), `payment_date` (DATE), `status` (VARCHAR), `transaction_ref` (VARCHAR UNIQUE) | Financial ledger recording subscription transactions (`UPI`, `Credit Card`, `Debit Card`, `Net Banking`). |
| **`training_session`** | `session_id` | `sport_id` &rarr; `sport`, `coach_id` &rarr; `coach`, `venue_id` &rarr; `facility` | `session_date` (DATE), `start_time` (TIME), `end_time` (TIME > start_time), `capacity` (INT > 0), `status` (VARCHAR) | Scheduled training practice sessions with venue allocations. |
| **`team`** | `team_id` | `club_id` &rarr; `club`, `sport_id` &rarr; `sport`, `coach_id` &rarr; `coach` | `team_name` (VARCHAR), `created_date` (DATE), `status` (VARCHAR) | Competitive tournament squads formed under sports clubs. |
| **`tournament`** | `tournament_id` | `sport_id` &rarr; `sport` | `name` (VARCHAR), `start_date` (DATE), `end_date` (DATE >= start_date), `type` (VARCHAR) | Competitive leagues and tournaments (`Knockout`, `Round Robin`, `League`). |
| **`fixture`** | `fixture_id` | `tournament_id` &rarr; `tournament`, `team1_id` &rarr; `team`, `team2_id` &rarr; `team`, `venue_id` &rarr; `facility` | `fixture_date` (DATETIME), `status` (VARCHAR) | Match fixtures between two teams (`CHECK (team1_id <> team2_id)`). |

---

### 📊 Pre-Built 3NF Analytical Views

1. **`v_club_rosters`**: Aggregates athlete rosters, tactical positions, clubs, and head coaches.
2. **`v_tournament_standings`**: Computes matches played, wins, draws, losses, and tournament points.
3. **`v_facility_utilization`**: Measures training sessions and tournament matches hosted per sports facility.
4. **`v_upcoming_fixtures`**: Joins tournament matches with team names, sport disciplines, and venue locations.
5. **`v_financial_revenue_summary`**: Summarizes collections, transactions, and average ticket sizes by payment mode.
6. **`v_member_subscription_status`**: Provides active plan, renewal date, and payment standing for every member.
7. **`v_team_overview`**: Competitive squad overview with founding dates and coaching staff.

---

## ⚡ Automated Integrity Triggers & Business Rules

1. **Tournament Team Sport Validation (`trg_check_fixture_team_sport`)**:
   - Asserts that both competing squads (`team1_id` and `team2_id`) participate in the exact sport registered for that tournament.
2. **Facility Double-Booking Prevention (`trg_check_venue_session_overlap`)**:
   - Rejects overlapping training sessions scheduled at the same facility on the same date and time slot.
3. **Account Status Club Restraints**:
   - Prevents suspended or inactive athlete accounts from enrolling in club rosters.
4. **Duplicate Role Prevention**:
   - Prevents duplicate role registration in the same club via composite key `(member_id, club_id, role)`.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Database Engine** | **SQLite 3 / PostgreSQL Compatible** (Foreign key constraints, 3NF schema, indexes, views, triggers) |
| **Backend Server** | **Python HTTP Server** (`app.py`), dual-stack IPv4/IPv6 networking, SHA-256 password security, REST API |
| **Frontend UI** | **Vanilla HTML5 / Modern CSS / JavaScript** (`index.html`) with glassmorphism styling, Lucide icons, responsive layout |
| **AI Integration** | **Smart SQL Studio** (Schema-aware Natural Language-to-SQL compiler with full ERD context) |
| **Visual Documentation** | Interactive **ER Diagram Viewer** (`er_diagram.html`) and **Slide Presentation Deck** (`presentation.html`) |

---

## ⚡ Quick Start (1-Click Run)

### Option A: Launch Interactive Web Cockpit (Zero Config)
Double-click `start.bat` (Windows) or execute in your terminal:

```bash
python app.py
```
*The server automatically initializes `sports_club.db` and launches the application at [http://127.0.0.1:5000](http://127.0.0.1:5000)*.

#### Default Demo Credentials
- **Administrator**: `Admin` / `Admin`
- **Athlete Member**: `aarav.sharma@gmail.com` / `aaravsharma` (or any registered member email with prefix)

---

### Option B: PostgreSQL Setup (Production Script)
If you have PostgreSQL installed locally:

```powershell
.\setup_database.ps1
```

Or execute manually via `psql`:
```cmd
psql -U postgres -d postgres -c "CREATE DATABASE sports_club_db;"
psql -U postgres -d sports_club_db -f schema.sql
psql -U postgres -d sports_club_db -f populate_data.sql
```

---

## 📁 Repository Structure

```
├── app.py                 # Backend REST API server and static web host
├── index.html             # Single-Page App (Admin Cockpit & Member Portal)
├── db_manager.py          # Database initializer and SQLite builder
├── schema.sql             # 3NF relational schema DDL (12 tables, views, triggers)
├── populate_data.sql      # Comprehensive mock dataset and fixtures
├── queries.sql            # 10 advanced DBMS SQL queries
├── er_diagram.html        # Interactive visual ER diagram
├── er.jpeg                # High-resolution ER diagram image
├── presentation.html      # Interactive slide presentation deck
├── cli.py                 # Interactive terminal CLI tool for DBMS operations
├── start.bat / start.ps1  # Quick launcher scripts
└── README.md              # Project documentation and schema dictionary
```
