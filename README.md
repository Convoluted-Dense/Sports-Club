# Sports Club Membership and Tournament Management System (DBMS)

A Relational Database Management System (RDBMS) normalized to Third Normal Form (3NF) for managing sports clubs, memberships, training facilities, tournaments, match fixtures, and payments.

Includes a Web Management Dashboard, Smart SQL Query Studio, Member Portal, interactive ER Diagram, and Presentation Slides.

---

## Project Overview

The Sports Club Management System manages operations across multiple athletic disciplines using relational database principles, role-based access, membership life-cycle tracking, and SQL query execution.

### Key Features
- 12 Relational Tables and 7 Analytical Views normalized to 3NF.
- Role-Based Web Portals: Separate interfaces for System Administrators and Athlete Members.
- Smart SQL Studio: Converts natural language questions into 3NF SQL queries using database schema context.
- Club Membership and Role Management: Club enrollment and departure with tactical role assignments (e.g., Forward, Midfielder, Batsman, Bowler, Shuttler).
- Multi-Channel Payment Simulation: Payment processing for UPI/QR, Credit/Debit Cards, and Net Banking with GST tax invoice generation.
- Security and Data Integrity: Password hashing (SHA-256), composite primary keys, foreign key constraints, and account suspension/activation controls.

---

## Database Schema and Table Dictionary

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

### Table and Attribute Reference

| Table Name | Primary Key | Foreign Keys | Key Attributes & Data Types | Description & Business Rules |
| :--- | :--- | :--- | :--- | :--- |
| **`member`** | `member_id` | — | `name` (VARCHAR), `gender` (VARCHAR), `phone` (VARCHAR), `email` (VARCHAR UNIQUE), `password` (VARCHAR/HASH), `address` (TEXT), `join_date` (DATE), `status` (VARCHAR) | Athlete demographic and authentication records. Status: `Active`, `Expired`, `Pending`, `Suspended`, `Inactive`. |
| **`sport`** | `sport_id` | — | `sport_name` (VARCHAR UNIQUE) | Sports disciplines catalog (Cricket, Football, Tennis, Badminton, Basketball, Swimming, etc.). |
| **`membership_plan`** | `plan_id` | — | `plan_name` (VARCHAR), `duration_months` (INT > 0), `fee_amount` (DECIMAL >= 0) | Subscription tiers (e.g., Monthly Starter, Quarterly Pro, Annual Gold Pass). |
| **`facility`** | `facility_id` | — | `name` (VARCHAR), `type` (VARCHAR), `location` (VARCHAR), `capacity` (INT > 0), `status` (VARCHAR) | Grounds, courts, and stadiums. Status: `Available`, `Booked`, `Under Maintenance`. |
| **`coach`** | `coach_id` | — | `name` (VARCHAR), `phone` (VARCHAR), `email` (VARCHAR UNIQUE) | Certified coaches assigned to clubs, teams, and training sessions. |
| **`club`** | `club_id` | `sport_id` -> `sport`, `coach_id` -> `coach` | `club_name` (VARCHAR), `created_date` (DATE), `status` (VARCHAR) | Sports clubs linked to one sport and one head coach. |
| **`club_member`** | `(member_id, club_id, role)` | `member_id` -> `member`, `club_id` -> `club` | `role` (VARCHAR), `join_date` (DATE) | Bridge table resolving N:M relationship between members and clubs with tactical roles. |
| **`payment`** | `payment_id` | `member_id` -> `member`, `plan_id` -> `membership_plan` | `amount` (DECIMAL > 0), `payment_mode` (VARCHAR), `payment_date` (DATE), `status` (VARCHAR), `transaction_ref` (VARCHAR UNIQUE) | Ledger recording subscription payments (UPI, Credit Card, Debit Card, Net Banking). |
| **`training_session`** | `session_id` | `sport_id` -> `sport`, `coach_id` -> `coach`, `venue_id` -> `facility` | `session_date` (DATE), `start_time` (TIME), `end_time` (TIME > start_time), `capacity` (INT > 0), `status` (VARCHAR) | Scheduled practice sessions with venue allocations. |
| **`team`** | `team_id` | `club_id` -> `club`, `sport_id` -> `sport`, `coach_id` -> `coach` | `team_name` (VARCHAR), `created_date` (DATE), `status` (VARCHAR) | Competitive tournament squads formed under sports clubs. |
| **`tournament`** | `tournament_id` | `sport_id` -> `sport` | `name` (VARCHAR), `start_date` (DATE), `end_date` (DATE >= start_date), `type` (VARCHAR) | Tournaments and leagues (Knockout, Round Robin, League). |
| **`fixture`** | `fixture_id` | `tournament_id` -> `tournament`, `team1_id` -> `team`, `team2_id` -> `team`, `venue_id` -> `facility` | `fixture_date` (DATETIME), `status` (VARCHAR) | Match schedules between two teams (team1_id != team2_id). |

---

### Analytical Views

1. **`v_club_rosters`**: Athlete rosters, tactical positions, clubs, and head coaches.
2. **`v_tournament_standings`**: Matches played, wins, draws, losses, and tournament points.
3. **`v_facility_utilization`**: Training sessions and tournament matches hosted per facility.
4. **`v_upcoming_fixtures`**: Tournament matches with team names, sports, and venues.
5. **`v_financial_revenue_summary`**: Total collections, transaction count, and average payment amount by payment mode.
6. **`v_member_subscription_status`**: Active plan details, renewal dates, and payment standing for members.
7. **`v_team_overview`**: Squad information with founding dates and coaches.

---

## Integrity Constraints and Business Rules

1. **Tournament Team Sport Validation (`trg_check_fixture_team_sport`)**:
   - Ensures competing teams (`team1_id` and `team2_id`) participate in the sport registered for that tournament.
2. **Facility Booking Conflict Prevention (`trg_check_venue_session_overlap`)**:
   - Rejects overlapping training sessions scheduled at the same venue on the same date and time.
3. **Account Status Validation**:
   - Prevents suspended or inactive accounts from enrolling in club rosters.
4. **Duplicate Role Prevention**:
   - Prevents duplicate role registration within the same club using composite primary key `(member_id, club_id, role)`.

---

## Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Database Engine** | **SQLite 3 / PostgreSQL Compatible** (Foreign keys, 3NF schema, indexes, views, triggers) |
| **Backend Server** | **Python HTTP Server** (`app.py`), IPv4/IPv6 socket handling, SHA-256 password hashing, REST API |
| **Frontend UI** | **HTML5 / CSS / JavaScript** (`index.html`), Lucide icons, responsive layout |
| **AI Integration** | **Smart SQL Studio** (Schema-aware Natural Language-to-SQL compiler with ERD context) |
| **Documentation** | Interactive **ER Diagram** (`er_diagram.html`) and **Slide Presentation** (`presentation.html`) |

---

## Setup and Execution

### Option A: Running the Application (SQLite / Zero Config)
Double-click `start.bat` (Windows) or run in terminal:

```bash
python backend/app.py
```
*The server initializes `sql/sports_club.db` automatically and opens [http://127.0.0.1:5000](http://127.0.0.1:5000)*.

#### Default Demo Logins
- **Administrator**: `Admin` / `Admin`
- **Member**: `aarav.sharma@gmail.com` / `aaravsharma` (or any registered member email with prefix)

---

### Option B: PostgreSQL Setup
If using PostgreSQL:

```powershell
.\sql\setup_database.ps1
```

Or manually using `psql`:
```cmd
psql -U postgres -d postgres -c "CREATE DATABASE sports_club_db;"
psql -U postgres -d sports_club_db -f sql/schema.sql
psql -U postgres -d sports_club_db -f sql/populate_data.sql
```

---

## Repository Organization

```
Sports-Club/
├── backend/
│   ├── app.py                 # REST API server & multi-directory static host
│   ├── db_manager.py          # Database builder & SQLite initializer
│   └── cli.py                 # Interactive terminal CLI tool
├── frontend/
│   ├── index.html             # Single-Page Web App (Admin Cockpit & Member Portal)
│   ├── er_diagram.html        # Interactive visual ER diagram studio
│   ├── presentation.html      # Interactive slide presentation deck (Full System)
│   ├── presentation1.html     # Interactive slide deck (Phase 1: Conceptual Design)
│   └── er.jpeg                # High-definition ER diagram graphic
├── sql/
│   ├── schema.sql             # 3NF relational schema DDL (12 tables, views, triggers)
│   ├── populate_data.sql      # Mock dataset and seed fixtures
│   ├── queries.sql            # 10 advanced analytical DBMS SQL queries
│   ├── sports_club.db         # SQLite relational database instance
│   └── setup_database.ps1     # Automated PostgreSQL setup script
├── presentation/
│   ├── presentation1.pdf      # Phase 1 Conceptual Design & Architecture Slide Deck (PDF)
│   └── presentation2.pdf      # High-definition widescreen full slide deck (PDF)
├── reports/
│   └── Sports_Club_DBMS_Project_Report.pdf # Academic Project Report (A4 PDF)
├── .gitignore                 # Git ignore rules
├── start.bat                  # Windows batch launcher
├── start.ps1                  # PowerShell launcher
└── README.md                  # Documentation and database schema dictionary
```
