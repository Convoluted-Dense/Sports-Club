# Sports Club Membership and Tournament Management System (DBMS)

Relational Database Management System (RDBMS) normalized to Third Normal Form (3NF) for managing sports clubs, memberships, training facilities, tournaments, match fixtures, and payments.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Embedded%20RDBMS-lightblue.svg)](https://www.sqlite.org/)
[![Flask](https://img.shields.io/badge/Flask-REST%20API-black.svg)](https://palletsprojects.com/p/flask/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## Project Overview

The Sports Club Management System is a database management project engineered to streamline athletic club administration. It eliminates data redundancy and guarantees relational integrity across complex sports club operations including multi-tier memberships, trainer allocations, facility reservations, multi-stage tournament scheduling, and payment accounting.

---

## Architecture and Key Features

- Strict Third Normal Form (3NF): Engineered schema with 10 relational tables, foreign key cascades, and check constraints preventing functional dependencies and deletion anomalies.
- RESTful Backend API: Built with Python and Flask (backend/app.py), providing endpoints for CRUD operations, member lookups, and tournament statistics.
- Interactive Web Management Dashboard: Responsive web frontend (frontend/index.html) featuring analytical data cards, membership rosters, and facility schedules.
- Interactive CLI Management Utility: Terminal-based management interface (backend/cli.py) for administrative queries, member registration, and batch SQL execution.
- Analytical Views and Automated Triggers: Pre-compiled database views for tournament standings and membership revenue reporting, paired with triggers enforcing payment state validation.

---

## Database Schema & Table Dictionary

```
+-------------------------------------------------------------------------+
|                              SPORTS CLUB DB                             |
+-------------------------------------------------------------------------+
|  Members       ---> Memberships  ---> Payments                         |
|  Trainers      ---> Training_Sessions                                  |
|  Facilities    ---> Bookings                                           |
|  Tournaments   ---> Matches      ---> Match_Participants               |
+-------------------------------------------------------------------------+
```

### Relational Tables
1. Members: Core member profiles (ID, name, email, phone, emergency contact, join date).
2. Membership_Types: Tier catalog (Bronze, Silver, Gold, Platinum, fees, duration, facility access rights).
3. Memberships: Active and historical member subscriptions with expiry tracking.
4. Trainers: Certified coaches, specializations, hourly billing rates, and contact details.
5. Training_Sessions: Individual and group coaching appointments linking members, trainers, and time slots.
6. Facilities: Sports infrastructure (Tennis courts, Swimming pools, Gymnasiums, Pitch rentals).
7. Bookings: Facility reservations with slot conflict prevention and status tracking.
8. Tournaments: Athletic events, start/end dates, entry fees, and prize distribution.
9. Matches: Tournament fixtures, rounds, dates, and official match outcomes.
10. Payments: Transaction ledger tracking membership renewals, bookings, invoices, and payment methods.

---

## Repository Structure

```
Sports-Club/
├── backend/
│   ├── app.py                   # Flask REST API server and routing
│   ├── cli.py                   # Administrative command-line management interface
│   └── db_manager.py            # SQLite connection manager and SQL query execution helper
├── frontend/
│   ├── index.html               # Web management portal
│   ├── er_diagram.html          # Interactive visual Entity-Relationship diagram
│   ├── presentation.html        # Academic project presentation slides
│   └── er.jpeg                  # Schema ER diagram graphic
├── sql/
│   ├── schema.sql               # DDL schema definition with 3NF constraints and indexes
│   ├── populate_data.sql        # Realistic sample data seed script
│   ├── queries.sql              # Complex analytical queries, joins, and aggregations
│   └── setup_database.ps1       # Automated PowerShell database initialization script
├── start.bat                    # One-click Windows startup script
└── README.md                    # Project documentation
```

---

## Setup & Execution

### Option A: Quickstart with SQLite (Zero Configuration)

1. Clone the repository:
```bash
git clone https://github.com/Convoluted-Dense/Sports-Club.git
cd Sports-Club
```

2. Install Python dependencies:
```bash
pip install flask
```

3. Initialize the database and launch the application:
```bash
# Using the Windows batch script
start.bat

# Or manually:
python -m backend.app
```

4. Open http://localhost:5000 or load frontend/index.html in your browser.

---

### Option B: Interactive Command-Line Tool

Launch the administrative CLI:
```bash
python backend/cli.py
```
Provides quick menus to register members, schedule training sessions, book facilities, and view tournament leaderboards.

---

## License

This project is licensed under the MIT License.
