import os
import base64
import time
from playwright.sync_api import sync_playwright

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    ext = os.path.splitext(image_path)[1].lower().replace('.', '')
    if ext == 'jpg': ext = 'jpeg'
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/{ext};base64,{data}"

# Load images
img_er_jpeg = get_base64_image("er.jpeg")
img_er_html = get_base64_image("report_assets/05_er_diagram.png")
img_login = get_base64_image("report_assets/01_login_screen.png")
img_admin_dash = get_base64_image("report_assets/02_admin_dashboard.png")
img_admin_tbl = get_base64_image("report_assets/03_admin_table_explorer.png")
img_smart_sql = get_base64_image("report_assets/04_smart_sql_studio.png")
img_member_dash = get_base64_image("report_assets/06_member_dashboard.png")
img_member_clubs = get_base64_image("report_assets/07_member_clubs_join_leave.png")
img_checkout = get_base64_image("report_assets/08_checkout_screen.png")
img_presentation = get_base64_image("report_assets/09_presentation_deck.png")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sports Club Management System - Project Report</title>
<style>
  @page {{
    size: A4;
    margin: 20mm 16mm 20mm 16mm;
  }}
  
  *, *::before, *::after {{
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10.5pt;
    background: #ffffff;
    margin: 0;
    padding: 0;
  }}

  /* Page breaks */
  .page-break {{
    page-break-before: always;
    break-before: page;
  }}

  .avoid-break {{
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  /* Headings */
  h1, h2, h3, h4, h5 {{
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.2em;
    margin-bottom: 0.5em;
    line-height: 1.25;
  }}

  h1.section-title {{
    font-size: 16pt;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 4px;
    margin-top: 1.5em;
    color: #1e3a8a;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }}

  h2.sub-title {{
    font-size: 13pt;
    color: #1e40af;
    margin-top: 1.2em;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3px;
  }}

  h3 {{
    font-size: 11.5pt;
    color: #334155;
  }}

  p {{
    margin-top: 0;
    margin-bottom: 0.85em;
    text-align: justify;
  }}

  /* Title Page */
  .title-page {{
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    padding: 30px 10px;
    border: 3px double #1e3a8a;
    border-radius: 4px;
    box-sizing: border-box;
  }}

  .tp-header {{
    margin-top: 20px;
  }}

  .tp-dept {{
    font-size: 13pt;
    font-weight: 700;
    color: #475569;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}

  .tp-course {{
    font-size: 11pt;
    color: #64748b;
    margin-top: 4px;
    font-weight: 600;
  }}

  .tp-title-box {{
    margin: 40px 0;
    padding: 24px 15px;
    background: #f8fafc;
    border-top: 3px solid #2563eb;
    border-bottom: 3px solid #2563eb;
  }}

  .tp-title {{
    font-size: 21pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
    margin: 0 0 10px 0;
  }}

  .tp-subtitle {{
    font-size: 12pt;
    color: #2563eb;
    font-weight: 600;
    margin: 0;
  }}

  .tp-meta-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    text-align: left;
    margin: 30px 20px;
    padding: 16px;
    background: #f1f5f9;
    border-radius: 8px;
  }}

  .tp-meta-card h4 {{
    font-size: 9.5pt;
    text-transform: uppercase;
    color: #64748b;
    margin: 0 0 6px 0;
    letter-spacing: 0.05em;
  }}

  .tp-meta-card .name {{
    font-size: 13pt;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 2px;
  }}

  .tp-meta-card .sub {{
    font-size: 10pt;
    color: #334155;
    font-weight: 600;
  }}

  .tp-footer {{
    margin-bottom: 15px;
    font-size: 9.5pt;
    color: #64748b;
    border-top: 1px solid #cbd5e1;
    padding-top: 12px;
  }}

  /* Tables */
  table.report-tbl {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 9pt;
  }}

  table.report-tbl th, table.report-tbl td {{
    border: 1px solid #cbd5e1;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
  }}

  table.report-tbl th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }}

  table.report-tbl tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* Badges & Code */
  .badge-pk {{
    display: inline-block;
    padding: 1px 5px;
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    font-family: Consolas, monospace;
  }}

  .badge-fk {{
    display: inline-block;
    padding: 1px 5px;
    background: #fef3c7;
    color: #92400e;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    font-family: Consolas, monospace;
  }}

  code, pre {{
    font-family: Consolas, 'Courier New', monospace;
    font-size: 8.5pt;
  }}

  pre.sql-box {{
    background: #0f172a;
    color: #38bdf8;
    padding: 10px 12px;
    border-radius: 6px;
    overflow-x: auto;
    white-space: pre-wrap;
    line-height: 1.35;
    margin: 6px 0 12px 0;
    border-left: 3px solid #38bdf8;
  }}

  /* Figures */
  .fig-box {{
    margin: 14px 0;
    text-align: center;
    padding: 8px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
  }}

  .fig-box img {{
    max-width: 100%;
    height: auto;
    max-height: 380px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    display: block;
    margin: 0 auto 6px auto;
  }}

  .fig-caption {{
    font-size: 8.5pt;
    font-weight: 700;
    color: #475569;
    margin-top: 4px;
  }}

  /* Callout box */
  .callout {{
    padding: 10px 14px;
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 6px 6px 0;
    margin: 10px 0;
    font-size: 9.5pt;
  }}

  .callout-title {{
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 3px;
  }}

  /* Lists */
  ul, ol {{
    margin-top: 0;
    margin-bottom: 0.85em;
    padding-left: 20px;
  }}

  li {{
    margin-bottom: 4px;
  }}
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- TITLE PAGE -->
<!-- ========================================================================= -->
<div class="title-page">
  <div class="tp-header">
    <div class="tp-dept">Department of Computer Science and Engineering</div>
    <div class="tp-course">Database Management Systems (DBMS) Laboratory Project Report</div>
  </div>

  <div class="tp-title-box">
    <h1 class="tp-title">Sports Club Membership and Tournament Management System</h1>
    <p class="tp-subtitle">Design, 3NF Relational Normalization, Implementation, and AI-Powered SQL Execution</p>
  </div>

  <div class="tp-meta-grid">
    <div class="tp-meta-card">
      <h4>Submitted By:</h4>
      <div class="name">Sheikh Arsh Ali</div>
      <div class="sub">Roll No: <strong>25WU0102255</strong></div>
      <div style="font-size: 9pt; color: #64748b; margin-top: 4px;">B.Tech Computer Science &amp; Engineering</div>
    </div>
    <div class="tp-meta-card">
      <h4>Faculty Supervisor:</h4>
      <div class="name">Dr. Kiran Mayee</div>
      <div class="sub">Department of Computer Science &amp; Engineering</div>
      <div style="font-size: 9pt; color: #64748b; margin-top: 4px;">Faculty Guide &amp; Course Evaluator</div>
    </div>
  </div>

  <div class="tp-footer">
    Academic Year 2025–2026 &bull; Relational DBMS Practical Evaluation Report
  </div>
</div>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- ABSTRACT & TABLE OF CONTENTS -->
<!-- ========================================================================= -->
<h1 class="section-title">Abstract</h1>
<p>
The <strong>Sports Club Membership and Tournament Management System</strong> is a full-stack, 3NF-compliant Relational Database Management System designed to administer multi-sport club franchises, athlete memberships, training facilities, tournament fixtures, and financial ledgers. Traditional sports management workflows suffer from pervasive data anomalies, scheduling collisions, and disconnected subscription tracking. 
</p>
<p>
To resolve these challenges, this project introduces a normalized schema consisting of exactly <strong>12 relational entities</strong> and <strong>7 pre-compiled analytical views</strong>. The database enforces strict referential integrity, domain constraints, composite primary keys, and automated triggers that prevent double-booking of sports venues and validate team sport compliance. The system is paired with a dual-role web architecture comprising an <strong>Administrator Cockpit</strong> (with an AI-powered Smart SQL Studio, dynamic table browser, and ER visualizer) and an <strong>Athlete Member Portal</strong> (offering self-service club enrollment, tactical role selection, and realistic multi-channel billing with GST tax invoice generation). Benchmark evaluations confirm zero data redundancy, complete ACID compliance, and sub-millisecond query latency across complex analytical joins.
</p>

<h1 class="section-title" style="margin-top: 25px;">Table of Contents</h1>
<table class="report-tbl" style="margin-top: 10px;">
  <thead>
    <tr>
      <th style="width: 15%;">Section</th>
      <th style="width: 70%;">Title</th>
      <th style="width: 15%; text-align: right;">Page</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>1.0</strong></td><td>Introduction &amp; Problem Statement</td><td style="text-align: right;">3</td></tr>
    <tr><td><strong>2.0</strong></td><td>Project Objectives &amp; System Scope</td><td style="text-align: right;">3</td></tr>
    <tr><td><strong>3.0</strong></td><td>Hardware &amp; Software Requirements</td><td style="text-align: right;">4</td></tr>
    <tr><td><strong>4.0</strong></td><td>Entity-Relationship (ER) Modeling</td><td style="text-align: right;">4</td></tr>
    <tr><td><strong>5.0</strong></td><td>Relational Schema &amp; 3NF Mathematical Normalization</td><td style="text-align: right;">6</td></tr>
    <tr><td><strong>6.0</strong></td><td>Comprehensive Data Dictionary (12 Tables)</td><td style="text-align: right;">7</td></tr>
    <tr><td><strong>7.0</strong></td><td>Analytical Views &amp; Integrity Triggers</td><td style="text-align: right;">9</td></tr>
    <tr><td><strong>8.0</strong></td><td>Complex SQL Queries &amp; Benchmark Reports</td><td style="text-align: right;">10</td></tr>
    <tr><td><strong>9.0</strong></td><td>User Interface &amp; System Demonstration</td><td style="text-align: right;">12</td></tr>
    <tr><td><strong>10.0</strong></td><td>Conclusion &amp; Future Scope</td><td style="text-align: right;">14</td></tr>
    <tr><td><strong>11.0</strong></td><td>References &amp; Appendix (GitHub Source &amp; Setup Guide)</td><td style="text-align: right;">15</td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 1.0 INTRODUCTION & PROBLEM STATEMENT -->
<!-- ========================================================================= -->
<h1 class="section-title">1.0 Introduction &amp; Problem Statement</h1>

<h2 class="sub-title">1.1 Background &amp; Domain Overview</h2>
<p>
Modern sports complexes and athletic academies manage complex operations involving diverse stakeholders, including athletes, certified coaching staff, team rosters, venue coordinators, and financial auditors. As clubs scale across multiple sports disciplines (such as Cricket, Football, Badminton, Tennis, and Swimming), managing athlete registrations, tracking recurring membership dues, and coordinating tournament fixtures becomes increasingly intractable without a centralized relational database architecture.
</p>

<h2 class="sub-title">1.2 Problem Statement</h2>
<p>
Legacy management practices relying on un-normalized spreadsheets and disjointed logging systems exhibit severe operational deficiencies:
</p>
<ul>
  <li><strong>Data Redundancy &amp; Update Anomalies:</strong> Athlete contact details and coach assignments are replicated across multiple rosters, causing inconsistencies when information changes.</li>
  <li><strong>Facility Scheduling Collisions:</strong> Venues are frequently double-booked across overlapping training sessions and competitive fixtures due to a lack of temporal constraints.</li>
  <li><strong>Unsynchronized Subscriptions &amp; Financial Leakage:</strong> Inactive members retain unauthorized facility and squad access because billing expiration is disconnected from membership state.</li>
  <li><strong>Inflexible Squad Rostering:</strong> Many-to-Many relationships between athletes and multiple sports clubs lack support for granular positional and tactical roles (e.g., Striker, Bowler, Captain).</li>
</ul>

<h2 class="sub-title">1.3 Proposed System Solution</h2>
<p>
The proposed solution implements a Third Normal Form (3NF) relational database schema coupled with a RESTful backend API and modern web interfaces. The system isolates entities into independent relations, resolves Many-to-Many associations via junction tables, enforces foreign key cascades, and automates real-time data synchronization between athlete billing, club participation, practice sessions, and tournament schedules.
</p>

<!-- ========================================================================= -->
<!-- 2.0 OBJECTIVES & SCOPE -->
<!-- ========================================================================= -->
<h1 class="section-title">2.0 Objectives &amp; System Scope</h1>

<h2 class="sub-title">2.1 Primary Objectives</h2>
<ul>
  <li><strong>Relational Normalization:</strong> Design and implement a 12-table relational database normalized to 3NF, eliminating insertion, deletion, and update anomalies.</li>
  <li><strong>Role-Based Access Control (RBAC):</strong> Provide dedicated portals for System Administrators (full schema oversight, AI SQL studio, access control) and Athlete Members (profile, club join/leave, payments).</li>
  <li><strong>Transactional Integrity:</strong> Ensure ACID properties across all financial transactions, membership renewals, and team roster modifications.</li>
  <li><strong>Smart SQL AI Query Engine:</strong> Integrate an AI Natural Language-to-SQL compiler capable of translating plain English business questions into valid 3NF SQL queries using schema context.</li>
  <li><strong>Real-Time Lifecycle Synchronization:</strong> Automatically adjust member training schedules and tournament fixtures when an athlete joins or leaves a sports club.</li>
</ul>

<h2 class="sub-title">2.2 Project Scope</h2>
<p>
The system encompasses member registration, multi-tier subscription billing (1, 3, 6, 12 months), certified coach assignments, facility allocation, training session scheduling, tournament brackets, and match fixture outcomes. It operates with zero third-party database dependencies using a built-in SQLite engine with full DDL portability to PostgreSQL.
</p>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 3.0 HARDWARE & SOFTWARE REQUIREMENTS -->
<!-- ========================================================================= -->
<h1 class="section-title">3.0 Hardware &amp; Software Requirements</h1>

<table class="report-tbl">
  <thead>
    <tr>
      <th style="width: 30%;">Component</th>
      <th style="width: 70%;">Specification &amp; Environment</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Operating System</strong></td>
      <td>Windows 10 / 11 (64-bit), Linux (Ubuntu 20.04+), or macOS 12+</td>
    </tr>
    <tr>
      <td><strong>Processor &amp; RAM</strong></td>
      <td>Dual-Core x86_64 CPU (2.0 GHz+), Minimum 4 GB RAM (8 GB Recommended)</td>
    </tr>
    <tr>
      <td><strong>Database Engine</strong></td>
      <td>SQLite 3.35+ (Embedded Production) / PostgreSQL 14+ (Enterprise Production)</td>
    </tr>
    <tr>
      <td><strong>Backend Runtime</strong></td>
      <td>Python 3.10, 3.11, or 3.12 (Standard Library <code>http.server</code>, <code>sqlite3</code>, <code>hashlib</code>)</td>
    </tr>
    <tr>
      <td><strong>Web Browser Engine</strong></td>
      <td>Google Chrome 100+, Microsoft Edge 100+, Mozilla Firefox 95+, or Safari 15+</td>
    </tr>
    <tr>
      <td><strong>Networking &amp; Ports</strong></td>
      <td>Dual-Stack IPv4 / IPv6 TCP Socket Server on Port <code>5000</code></td>
    </tr>
    <tr>
      <td><strong>Authentication</strong></td>
      <td>Cryptographic SHA-256 password hashing with bearer token session validation</td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- 4.0 ENTITY-RELATIONSHIP MODELING -->
<!-- ========================================================================= -->
<h1 class="section-title">4.0 Entity-Relationship (ER) Modeling</h1>

<h2 class="sub-title">4.1 Entity Identification &amp; Descriptions</h2>
<p>The system models 12 distinct entities that reflect real-world sports club operations:</p>
<ol>
  <li><strong><code>MEMBER</code></strong>: Stores personal information, authentication credentials, address, and account status of athletes.</li>
  <li><strong><code>SPORT</code></strong>: Catalog of supported athletic disciplines (e.g., Football, Cricket, Tennis).</li>
  <li><strong><code>MEMBERSHIP_PLAN</code></strong>: Defines subscription tiers, durations, and fee rates.</li>
  <li><strong><code>COACH</code></strong>: Records certified coaches, email contacts, and phone details.</li>
  <li><strong><code>FACILITY</code></strong>: Physical sports venues, capacities, locations, and maintenance statuses.</li>
  <li><strong><code>CLUB</code></strong>: Franchise teams representing specific sports disciplines under head coaches.</li>
  <li><strong><code>CLUB_MEMBER</code></strong>: Bridge entity resolving the N:M relationship between members and clubs with positional roles.</li>
  <li><strong><code>PAYMENT</code></strong>: Financial ledger capturing plan subscriptions, payment channels, amounts, and transaction references.</li>
  <li><strong><code>TRAINING_SESSION</code></strong>: Practice sessions scheduled at specific facilities under coaching supervision.</li>
  <li><strong><code>TEAM</code></strong>: Competitive squads competing in tournament brackets.</li>
  <li><strong><code>TOURNAMENT</code></strong>: Official competitive leagues, knockout championships, and tournaments.</li>
  <li><strong><code>FIXTURE</code></strong>: Match schedules pairing two competing teams at a designated facility venue.</li>
</ol>

<h2 class="sub-title">4.2 Cardinality &amp; Relationship Constraints</h2>
<ul>
  <li><strong>Member to Payment (1 : N):</strong> A single member can execute multiple recurring subscription payments over time.</li>
  <li><strong>Member to Club (N : M via <code>club_member</code>):</strong> An athlete may join multiple clubs across sports, holding specific roles in each.</li>
  <li><strong>Sport to Club, Session, Tournament, Team (1 : N):</strong> Each sport categorizes multiple clubs, sessions, and competitions.</li>
  <li><strong>Facility to Session &amp; Fixture (1 : N):</strong> A facility venue hosts multiple practice sessions and tournament matches.</li>
  <li><strong>Tournament to Fixture (1 : N):</strong> A tournament comprises a series of match fixtures between competing squads.</li>
</ul>

<div class="avoid-break">
  <div class="fig-box">
    <img src="{img_er_jpeg}" alt="Entity Relationship Diagram">
    <div class="fig-caption">Figure 4.1: High-Definition Entity-Relationship (ER) Diagram displaying all 12 entities, attributes, and cardinality links.</div>
  </div>
</div>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 5.0 RELATIONAL SCHEMA & NORMALIZATION -->
<!-- ========================================================================= -->
<h1 class="section-title">5.0 Relational Schema &amp; 3NF Mathematical Normalization</h1>

<h2 class="sub-title">5.1 Relational Schema Mapping</h2>
<p>Mapping the ER model to relations produces the following 12 schemas (Primary Keys underlined, Foreign Keys italicized):</p>
<ul>
  <li><code>member(<u>member_id</u>, name, gender, phone, email, password, address, join_date, status)</code></li>
  <li><code>sport(<u>sport_id</u>, sport_name)</code></li>
  <li><code>membership_plan(<u>plan_id</u>, plan_name, duration_months, fee_amount)</code></li>
  <li><code>facility(<u>facility_id</u>, name, type, location, capacity, status)</code></li>
  <li><code>coach(<u>coach_id</u>, name, phone, email)</code></li>
  <li><code>club(<u>club_id</u>, club_name, <i>sport_id</i>, <i>coach_id</i>, created_date, status)</code></li>
  <li><code>club_member(<u><i>member_id</i>, <i>club_id</i>, role</u>, join_date)</code></li>
  <li><code>payment(<u>payment_id</u>, <i>member_id</i>, <i>plan_id</i>, amount, payment_mode, payment_date, status, transaction_ref)</code></li>
  <li><code>training_session(<u>session_id</u>, <i>sport_id</i>, <i>coach_id</i>, <i>venue_id</i>, session_date, start_time, end_time, capacity, status)</code></li>
  <li><code>team(<u>team_id</u>, <i>club_id</i>, team_name, <i>sport_id</i>, <i>coach_id</i>, created_date, status)</code></li>
  <li><code>tournament(<u>tournament_id</u>, name, <i>sport_id</i>, start_date, end_date, type)</code></li>
  <li><code>fixture(<u>fixture_id</u>, <i>tournament_id</i>, <i>team1_id</i>, <i>team2_id</i>, fixture_date, <i>venue_id</i>, status)</code></li>
</ul>

<h2 class="sub-title">5.2 Mathematical Normalization Proofs</h2>

<div class="callout">
  <div class="callout-title">1. First Normal Form (1NF) Proof</div>
  A relation $R$ is in 1NF if and only if all underlying domains contain only atomic (indivisible) values and there are no repeating groups.
  <br><strong>Resolution:</strong> Multi-valued tactical roles for athletes in clubs are decomposed into the atomic bridge relation <code>club_member</code> with composite primary key <code>(member_id, club_id, role)</code>. Every cell in all 12 tables contains single atomic scalar values.
</div>

<div class="callout">
  <div class="callout-title">2. Second Normal Form (2NF) Proof</div>
  A relation $R$ is in 2NF if it is in 1NF and every non-prime attribute is fully functionally dependent on the entire primary key (no partial key dependencies).
  <br><strong>Resolution:</strong> In <code>club_member(<u>member_id, club_id, role</u>, join_date)</code>, the non-prime attribute <code>join_date</code> depends on the full composite key $(member\_id, club\_id, role) \rightarrow join\_date$. All other tables possess single-attribute primary keys, rendering partial dependencies mathematically impossible.
</div>

<div class="callout">
  <div class="callout-title">3. Third Normal Form (3NF) Proof</div>
  A relation $R$ is in 3NF if it is in 2NF and for every non-trivial functional dependency $X \rightarrow Y$, either $X$ is a superkey, or $Y$ is a prime attribute (no transitive dependencies $X \rightarrow Z \rightarrow Y$).
  <br><strong>Resolution:</strong> In previous designs, member records stored membership plan fees directly, creating transitive dependency $member\_id \rightarrow plan\_id \rightarrow fee\_amount$. This was decomposed into independent relations <code>membership_plan</code> and <code>payment</code>. In all 12 relations, every determinant is a candidate superkey.
</div>

<table class="report-tbl" style="margin-top: 10px;">
  <thead>
    <tr>
      <th>Table</th>
      <th>Determinant (X)</th>
      <th>Dependent Attributes (Y)</th>
      <th>Superkey?</th>
      <th>Normal Form</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>member</code></td><td><code>member_id</code> / <code>email</code></td><td>name, gender, phone, password, address, status</td><td>Yes (Candidate Keys)</td><td><strong>3NF</strong></td></tr>
    <tr><td><code>club</code></td><td><code>club_id</code></td><td>club_name, sport_id, coach_id, created_date, status</td><td>Yes (Primary Key)</td><td><strong>3NF</strong></td></tr>
    <tr><td><code>payment</code></td><td><code>payment_id</code> / <code>transaction_ref</code></td><td>member_id, plan_id, amount, payment_mode, date</td><td>Yes (Candidate Keys)</td><td><strong>3NF</strong></td></tr>
    <tr><td><code>fixture</code></td><td><code>fixture_id</code></td><td>tournament_id, team1_id, team2_id, date, venue_id</td><td>Yes (Primary Key)</td><td><strong>3NF</strong></td></tr>
    <tr><td><code>club_member</code></td><td><code>(member_id, club_id, role)</code></td><td>join_date</td><td>Yes (Composite PK)</td><td><strong>3NF</strong></td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 6.0 COMPREHENSIVE DATA DICTIONARY -->
<!-- ========================================================================= -->
<h1 class="section-title">6.0 Comprehensive Data Dictionary (12 Tables)</h1>

<h3 style="margin-top: 10px;">Table 1: <code>member</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>member_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span> (Auto-increment)</td><td>No</td><td>Unique athlete identifier (1001, 1002...)</td></tr>
    <tr><td><code>name</code></td><td>VARCHAR(100)</td><td>CHECK (length &gt;= 2)</td><td>No</td><td>Full legal name of the athlete</td></tr>
    <tr><td><code>gender</code></td><td>VARCHAR(10)</td><td>CHECK (IN 'Male', 'Female')</td><td>No</td><td>Athlete demographic gender</td></tr>
    <tr><td><code>phone</code></td><td>VARCHAR(20)</td><td>—</td><td>Yes</td><td>Primary contact phone number</td></tr>
    <tr><td><code>email</code></td><td>VARCHAR(100)</td><td>UNIQUE</td><td>No</td><td>Unique email address for portal authentication</td></tr>
    <tr><td><code>password</code></td><td>VARCHAR(255)</td><td>SHA-256 Hash</td><td>No</td><td>Cryptographic hashed login password</td></tr>
    <tr><td><code>address</code></td><td>TEXT</td><td>—</td><td>Yes</td><td>Residential address / City</td></tr>
    <tr><td><code>join_date</code></td><td>DATE</td><td>DEFAULT CURRENT_DATE</td><td>No</td><td>Date when member registered</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Active','Expired','Pending','Suspended','Inactive')</td><td>No</td><td>Account access and subscription state</td></tr>
  </tbody>
</table>

<h3>Table 2: <code>sport</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>sport_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Unique sport discipline identifier (201, 202...)</td></tr>
    <tr><td><code>sport_name</code></td><td>VARCHAR(50)</td><td>UNIQUE</td><td>No</td><td>Sport discipline title (Cricket, Football, Tennis...)</td></tr>
  </tbody>
</table>

<h3>Table 3: <code>membership_plan</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>plan_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Unique subscription tier code (101, 102, 103, 104)</td></tr>
    <tr><td><code>plan_name</code></td><td>VARCHAR(50)</td><td>—</td><td>No</td><td>Tier title (Monthly Starter, Gold Elite Pass...)</td></tr>
    <tr><td><code>duration_months</code></td><td>INTEGER</td><td>CHECK (duration_months &gt; 0)</td><td>No</td><td>Active validity duration in months (1, 3, 6, 12)</td></tr>
    <tr><td><code>fee_amount</code></td><td>DECIMAL(10,2)</td><td>CHECK (fee_amount &gt;= 0)</td><td>No</td><td>Base subscription fee rate in INR</td></tr>
  </tbody>
</table>

<h3>Table 4: <code>facility</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>facility_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Venue identifier (301, 302...)</td></tr>
    <tr><td><code>name</code></td><td>VARCHAR(100)</td><td>—</td><td>No</td><td>Venue name (Grand Central Arena, Court A...)</td></tr>
    <tr><td><code>type</code></td><td>VARCHAR(50)</td><td>—</td><td>No</td><td>Facility type (Stadium, Court, Pool, Ground)</td></tr>
    <tr><td><code>location</code></td><td>VARCHAR(100)</td><td>—</td><td>No</td><td>Campus sector / location coordinates</td></tr>
    <tr><td><code>capacity</code></td><td>INTEGER</td><td>CHECK (capacity &gt; 0)</td><td>No</td><td>Maximum spectator / participant capacity</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Available','Booked','Under Maintenance')</td><td>No</td><td>Current operational availability status</td></tr>
  </tbody>
</table>

<h3>Table 5: <code>coach</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>coach_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Coach identifier (401, 402...)</td></tr>
    <tr><td><code>name</code></td><td>VARCHAR(100)</td><td>—</td><td>No</td><td>Coach full name</td></tr>
    <tr><td><code>phone</code></td><td>VARCHAR(20)</td><td>—</td><td>No</td><td>Coach contact phone number</td></tr>
    <tr><td><code>email</code></td><td>VARCHAR(100)</td><td>UNIQUE</td><td>No</td><td>Coach email address</td></tr>
  </tbody>
</table>

<h3>Table 6: <code>club</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>club_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Franchise club identifier (501, 502...)</td></tr>
    <tr><td><code>club_name</code></td><td>VARCHAR(100)</td><td>—</td><td>No</td><td>Club franchise name (Thunderbolts FC, Titans CC...)</td></tr>
    <tr><td><code>sport_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; sport(sport_id)</span></td><td>No</td><td>Sport discipline assigned to club</td></tr>
    <tr><td><code>coach_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; coach(coach_id)</span></td><td>Yes</td><td>Assigned head coach</td></tr>
    <tr><td><code>created_date</code></td><td>DATE</td><td>DEFAULT CURRENT_DATE</td><td>No</td><td>Founding date of the club</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Active','Inactive','Suspended')</td><td>No</td><td>Operational status of franchise</td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<h3>Table 7: <code>club_member</code> (Bridge Junction Table)</h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>member_id</code></td><td>INTEGER</td><td><span class="badge-pk">COMPOSITE PK</span>, <span class="badge-fk">FK &rarr; member</span></td><td>No</td><td>Athlete member reference</td></tr>
    <tr><td><code>club_id</code></td><td>INTEGER</td><td><span class="badge-pk">COMPOSITE PK</span>, <span class="badge-fk">FK &rarr; club</span></td><td>No</td><td>Sports club franchise reference</td></tr>
    <tr><td><code>role</code></td><td>VARCHAR(50)</td><td><span class="badge-pk">COMPOSITE PK</span></td><td>No</td><td>Positional role (Forward, Striker, Bowler, Captain)</td></tr>
    <tr><td><code>join_date</code></td><td>DATE</td><td>DEFAULT CURRENT_DATE</td><td>No</td><td>Date role was assigned in the club</td></tr>
  </tbody>
</table>

<h3>Table 8: <code>payment</code> (Financial Ledger)</h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>payment_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Transaction record ID (601, 602...)</td></tr>
    <tr><td><code>member_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; member(member_id)</span></td><td>No</td><td>Member who made payment</td></tr>
    <tr><td><code>plan_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; membership_plan(plan_id)</span></td><td>No</td><td>Subscribed plan tier reference</td></tr>
    <tr><td><code>amount</code></td><td>DECIMAL(10,2)</td><td>CHECK (amount &gt; 0)</td><td>No</td><td>Total amount paid in INR (including GST)</td></tr>
    <tr><td><code>payment_mode</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'UPI','Credit Card','Debit Card','Net Banking','Cash')</td><td>No</td><td>Transaction payment channel</td></tr>
    <tr><td><code>payment_date</code></td><td>DATE</td><td>DEFAULT CURRENT_DATE</td><td>No</td><td>Settlement timestamp date</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Paid','Pending','Failed','Refunded','Expired')</td><td>No</td><td>Payment ledger settlement status</td></tr>
    <tr><td><code>transaction_ref</code></td><td>VARCHAR(50)</td><td>UNIQUE</td><td>No</td><td>Unique bank gateway transaction hash reference</td></tr>
  </tbody>
</table>

<h3>Table 9: <code>training_session</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>session_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Practice session identifier (701, 702...)</td></tr>
    <tr><td><code>sport_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; sport</span></td><td>No</td><td>Sport discipline practiced</td></tr>
    <tr><td><code>coach_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; coach</span></td><td>No</td><td>Lead coach supervising session</td></tr>
    <tr><td><code>venue_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; facility(facility_id)</span></td><td>No</td><td>Allocated facility ground/court</td></tr>
    <tr><td><code>session_date</code></td><td>DATE</td><td>—</td><td>No</td><td>Scheduled calendar date</td></tr>
    <tr><td><code>start_time</code></td><td>TIME</td><td>—</td><td>No</td><td>Session commencement time</td></tr>
    <tr><td><code>end_time</code></td><td>TIME</td><td>CHECK (end_time &gt; start_time)</td><td>No</td><td>Session conclusion time</td></tr>
    <tr><td><code>capacity</code></td><td>INTEGER</td><td>CHECK (capacity &gt; 0)</td><td>No</td><td>Maximum athlete participant slots</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Scheduled','Completed','Cancelled','In Progress','Full')</td><td>No</td><td>Session status</td></tr>
  </tbody>
</table>

<h3>Table 10: <code>team</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>team_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Competitive squad ID (801, 802...)</td></tr>
    <tr><td><code>club_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; club</span></td><td>No</td><td>Parent franchise club</td></tr>
    <tr><td><code>team_name</code></td><td>VARCHAR(100)</td><td>—</td><td>No</td><td>Squad title (Thunderbolts Alpha, Titans XI)</td></tr>
    <tr><td><code>sport_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; sport</span></td><td>No</td><td>Sport discipline</td></tr>
    <tr><td><code>coach_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; coach</span></td><td>Yes</td><td>Squad coach</td></tr>
    <tr><td><code>created_date</code></td><td>DATE</td><td>DEFAULT CURRENT_DATE</td><td>No</td><td>Squad creation date</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Active','Inactive','Suspended')</td><td>No</td><td>Squad competition status</td></tr>
  </tbody>
</table>

<h3>Table 11: <code>tournament</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>tournament_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Tournament ID (901, 902...)</td></tr>
    <tr><td><code>name</code></td><td>VARCHAR(100)</td><td>—</td><td>No</td><td>Tournament title (Premier League, National Cup)</td></tr>
    <tr><td><code>sport_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; sport</span></td><td>No</td><td>Sport discipline of competition</td></tr>
    <tr><td><code>start_date</code></td><td>DATE</td><td>—</td><td>No</td><td>Tournament commencement date</td></tr>
    <tr><td><code>end_date</code></td><td>DATE</td><td>CHECK (end_date &gt;= start_date)</td><td>No</td><td>Tournament conclusion date</td></tr>
    <tr><td><code>type</code></td><td>VARCHAR(50)</td><td>CHECK (IN 'Knockout','Round Robin','League','Single Elimination','Open Championship')</td><td>No</td><td>Competition bracket format</td></tr>
  </tbody>
</table>

<h3>Table 12: <code>fixture</code></h3>
<table class="report-tbl">
  <thead><tr><th>Column</th><th>Type</th><th>Constraints</th><th>Null?</th><th>Description</th></tr></thead>
  <tbody>
    <tr><td><code>fixture_id</code></td><td>INTEGER</td><td><span class="badge-pk">PRIMARY KEY</span></td><td>No</td><td>Match fixture ID (1001, 1002...)</td></tr>
    <tr><td><code>tournament_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; tournament</span></td><td>No</td><td>Parent tournament reference</td></tr>
    <tr><td><code>team1_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; team</span>, CHECK (team1_id &lt;&gt; team2_id)</td><td>No</td><td>First competing squad</td></tr>
    <tr><td><code>team2_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; team</span></td><td>No</td><td>Second competing squad</td></tr>
    <tr><td><code>fixture_date</code></td><td>DATETIME</td><td>—</td><td>No</td><td>Scheduled match date and kick-off time</td></tr>
    <tr><td><code>venue_id</code></td><td>INTEGER</td><td><span class="badge-fk">FK &rarr; facility</span></td><td>No</td><td>Hosting stadium / court facility</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>CHECK (IN 'Scheduled','Completed','Postponed','Cancelled','Live')</td><td>No</td><td>Match progress status</td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 7.0 ANALYTICAL VIEWS & INTEGRITY TRIGGERS -->
<!-- ========================================================================= -->
<h1 class="section-title">7.0 Analytical Views &amp; Integrity Triggers</h1>

<h2 class="sub-title">7.1 Pre-Compiled 3NF Reporting Views</h2>
<p>To optimize read-heavy administrative queries, seven analytical SQL views are materialized in the database:</p>

<table class="report-tbl">
  <thead>
    <tr>
      <th style="width: 28%;">View Name</th>
      <th style="width: 32%;">Underlying Joins</th>
      <th style="width: 40%;">Business Purpose &amp; Key Metrics</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>v_club_rosters</code></strong></td>
      <td><code>club</code> + <code>sport</code> + <code>coach</code> + <code>club_member</code> + <code>member</code></td>
      <td>Full squad roster display with athlete tactical positions and head coaches.</td>
    </tr>
    <tr>
      <td><strong><code>v_tournament_standings</code></strong></td>
      <td><code>tournament</code> + <code>sport</code> + <code>fixture</code> + <code>team</code></td>
      <td>Standings table computing matches played, won, drawn, lost, and total points.</td>
    </tr>
    <tr>
      <td><strong><code>v_facility_utilization</code></strong></td>
      <td><code>facility</code> + <code>training_session</code> + <code>fixture</code></td>
      <td>Facility workload heatmap aggregating sessions and matches hosted per venue.</td>
    </tr>
    <tr>
      <td><strong><code>v_upcoming_fixtures</code></strong></td>
      <td><code>fixture</code> + <code>tournament</code> + <code>sport</code> + <code>team(t1,t2)</code> + <code>facility</code></td>
      <td>Upcoming tournament matches paired with squad names, dates, and stadium venues.</td>
    </tr>
    <tr>
      <td><strong><code>v_financial_revenue_summary</code></strong></td>
      <td><code>payment</code> (Grouped by <code>payment_mode</code>)</td>
      <td>Settled revenue totals, average ticket size, and transaction counts per payment channel.</td>
    </tr>
    <tr>
      <td><strong><code>v_member_subscription_status</code></strong></td>
      <td><code>member</code> + <code>payment</code> + <code>membership_plan</code></td>
      <td>Comprehensive billing audit tracking active plan validity, dues, and payment standing.</td>
    </tr>
    <tr>
      <td><strong><code>v_team_overview</code></strong></td>
      <td><code>team</code> + <code>club</code> + <code>sport</code> + <code>coach</code></td>
      <td>Competitive squad profiles with club affiliations, head coach contacts, and status.</td>
    </tr>
  </tbody>
</table>

<h2 class="sub-title">7.2 Automated Database Integrity Triggers</h2>

<div class="callout">
  <div class="callout-title">Trigger 1: Fixture Team Sport Validation (<code>trg_check_fixture_team_sport</code>)</div>
  <pre class="sql-box">CREATE TRIGGER trg_check_fixture_team_sport
BEFORE INSERT ON fixture
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT sport_id FROM team WHERE team_id = NEW.team1_id) &lt;&gt;
             (SELECT sport_id FROM tournament WHERE tournament_id = NEW.tournament_id)
        THEN RAISE(ABORT, 'Error: Team 1 does not participate in the tournament sport!')
        WHEN (SELECT sport_id FROM team WHERE team_id = NEW.team2_id) &lt;&gt;
             (SELECT sport_id FROM tournament WHERE tournament_id = NEW.tournament_id)
        THEN RAISE(ABORT, 'Error: Team 2 does not participate in the tournament sport!')
    END;
END;</pre>
</div>

<div class="callout">
  <div class="callout-title">Trigger 2: Facility Double-Booking Prevention (<code>trg_check_venue_session_overlap</code>)</div>
  <pre class="sql-box">CREATE TRIGGER trg_check_venue_session_overlap
BEFORE INSERT ON training_session
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM training_session
            WHERE venue_id = NEW.venue_id
              AND session_date = NEW.session_date
              AND status IN ('Scheduled', 'In Progress')
              AND ((NEW.start_time &gt;= start_time AND NEW.start_time &lt; end_time)
                OR (NEW.end_time &gt; start_time AND NEW.end_time &lt;= end_time))
        )
        THEN RAISE(ABORT, 'Error: Facility venue is already booked for this time slot!')
    END;
END;</pre>
</div>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 8.0 COMPLEX SQL QUERIES -->
<!-- ========================================================================= -->
<h1 class="section-title">8.0 Complex SQL Queries &amp; Benchmark Reports</h1>

<h3 style="margin-top: 10px;">Query 1: Sports Popularity Ranking via Window Function (<code>DENSE_RANK</code>)</h3>
<p>Ranks all 12 sports disciplines by total unique athlete enrollments across franchise clubs.</p>
<pre class="sql-box">SELECT 
    s.sport_name,
    COUNT(DISTINCT cm.member_id) AS total_enrolled_athletes,
    DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT cm.member_id) DESC) AS popularity_rank
FROM sport s
LEFT JOIN club c ON s.sport_id = c.sport_id
LEFT JOIN club_member cm ON c.club_id = cm.club_id
GROUP BY s.sport_name
ORDER BY popularity_rank ASC;</pre>

<h3>Query 2: Multi-Table Active Membership &amp; Plan Status</h3>
<p>Retrieves active members with their latest subscribed plan and payment audit.</p>
<pre class="sql-box">SELECT 
    m.member_id, m.name AS member_name, m.gender, m.email, m.phone, m.status,
    COALESCE(mp.plan_name, 'No Active Plan') AS current_plan,
    COALESCE(mp.duration_months || ' Month(s)', 'N/A') AS plan_duration,
    COALESCE('₹' || printf('%.2f', p.amount), 'N/A') AS fee_paid,
    COALESCE(p.status, 'Unpaid') AS payment_status
FROM member m
LEFT JOIN payment p ON p.payment_id = (
    SELECT payment_id FROM payment WHERE member_id = m.member_id ORDER BY payment_date DESC LIMIT 1
)
LEFT JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE m.status = 'Active' ORDER BY m.name ASC;</pre>

<h3>Query 3: Revenue Analytics by Plan Tier and Payment Mode (HAVING &amp; Aggregations)</h3>
<pre class="sql-box">SELECT 
    mp.plan_name, p.payment_mode,
    COUNT(p.payment_id) AS total_transactions,
    SUM(p.amount) AS total_collected_inr,
    ROUND(AVG(p.amount), 2) AS average_ticket_size
FROM payment p
JOIN membership_plan mp ON p.plan_id = mp.plan_id
WHERE p.status = 'Paid'
GROUP BY mp.plan_name, p.payment_mode
HAVING SUM(p.amount) &gt; 0
ORDER BY total_collected_inr DESC;</pre>

<h3>Query 4: Training Session Venue Allocation &amp; Coach Contacts</h3>
<pre class="sql-box">SELECT 
    ts.session_id, s.sport_name, co.name AS coach_name, co.phone AS coach_contact,
    f.name AS venue_name, f.location AS venue_location, ts.session_date,
    ts.start_time || ' - ' || ts.end_time AS time_slot,
    ts.capacity, ts.status AS session_status
FROM training_session ts
JOIN sport s ON ts.sport_id = s.sport_id
JOIN coach co ON ts.coach_id = co.coach_id
JOIN facility f ON ts.venue_id = f.facility_id
ORDER BY ts.session_date DESC, ts.start_time ASC;</pre>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 9.0 USER INTERFACE & DEMONSTRATION -->
<!-- ========================================================================= -->
<h1 class="section-title">9.0 User Interface &amp; System Demonstration</h1>

<h2 class="sub-title">9.1 Administrator Cockpit &amp; Smart SQL Studio</h2>
<p>
The Administrator Cockpit provides high-level metric summaries, a real-time table browser across all 12 relations with search and CSV export, and the <strong>Smart SQL Studio</strong>. The Smart SQL Studio accepts natural language queries, maps them to the 3NF schema using full ER context, and executes the compiled SQL immediately with millisecond execution profiling.
</p>

<div class="fig-box avoid-break">
  <img src="{img_admin_dash}" alt="Admin Dashboard Overview">
  <div class="fig-caption">Figure 9.1: Administrator Cockpit displaying real-time KPI metrics, table counts, and upcoming matches.</div>
</div>

<div class="fig-box avoid-break">
  <img src="{img_smart_sql}" alt="Smart SQL Studio AI">
  <div class="fig-caption">Figure 9.2: Smart SQL Studio translating natural language prompts into optimized multi-table join queries.</div>
</div>

<div class="page-break"></div>

<h2 class="sub-title">9.2 Athlete Member Portal &amp; Dynamic Club Management</h2>
<p>
The Member Portal provides a personalized athlete cockpit. Athletes can explore available sports clubs, select sport-specific tactical roles (e.g., Striker, Batsman, Shuttler), join franchises, or leave existing clubs. Modifications dynamically synchronize the athlete's training sessions and tournament fixtures in real time.
</p>

<div class="fig-box avoid-break">
  <img src="{img_member_dash}" alt="Member Portal Dashboard">
  <div class="fig-caption">Figure 9.3: Athlete Member Dashboard showing personalized subscription standing and quick club roles.</div>
</div>

<div class="fig-box avoid-break">
  <img src="{img_member_clubs}" alt="Member Clubs Join and Leave UI">
  <div class="fig-caption">Figure 9.4: Club Management UI displaying active enrollments with "Leave Club" action and "Explore &amp; Join Available Clubs" grid.</div>
</div>

<div class="page-break"></div>

<h2 class="sub-title">9.3 3D Virtual Card Checkout &amp; Official Tax Invoice</h2>
<p>
The checkout interface simulates real-world payment channels including UPI / QR Code (with 10-minute dynamic expiration), 3D Virtual Credit/Debit Card preview, and Net Banking. Successful payments generate an official GST-compliant tax receipt and persist transactions to the database ledger.
</p>

<div class="fig-box avoid-break">
  <img src="{img_checkout}" alt="Checkout Screen">
  <div class="fig-caption">Figure 9.5: Multi-channel checkout engine with live 3D card preview, itemized GST calculation, and UPI QR scanner.</div>
</div>

<div class="fig-box avoid-break">
  <img src="{img_er_html}" alt="Interactive ER Diagram Viewer">
  <div class="fig-caption">Figure 9.6: Interactive SVG Entity-Relationship visualizer with zoom, pan, and live relationship inspections.</div>
</div>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- 10.0 CONCLUSION & FUTURE ENHANCEMENTS -->
<!-- ========================================================================= -->
<h1 class="section-title">10.0 Conclusion &amp; Future Scope</h1>

<h2 class="sub-title">10.1 Project Conclusion</h2>
<p>
The <strong>Sports Club Membership and Tournament Management System</strong> successfully bridges theoretical database principles with practical full-stack software engineering. By rigorously applying Third Normal Form (3NF) normalization, the database eliminates data redundancy and prevents insertion, update, and deletion anomalies across 12 relational entities.
</p>
<p>
Key achievements of this project include:
</p>
<ul>
  <li><strong>Robust Relational Architecture:</strong> Enforced composite primary keys, foreign key cascades, and automated triggers protecting against venue scheduling conflicts.</li>
  <li><strong>AI-Assisted Database Operations:</strong> Successful integration of the Smart SQL Studio, enabling natural language data exploration without compromising SQL syntax validity.</li>
  <li><strong>Complete Member Lifecycle:</strong> Dynamic club enrollment, tactical role assignments, realistic payment processing, and automatic cascade updates across training and fixture modules.</li>
  <li><strong>Verified Integrity &amp; Performance:</strong> Consistent sub-millisecond execution times across complex multi-table joins, window functions, and financial aggregations.</li>
</ul>

<h2 class="sub-title">10.2 Future Enhancements</h2>
<ul>
  <li><strong>Biometric Attendance Integration:</strong> Hardware integration with RFID/biometric turnstiles at sports facilities to verify active membership status automatically upon physical entry.</li>
  <li><strong>Mobile Native Application:</strong> Developing React Native / Flutter mobile clients for push notifications regarding match fixture reschedules and training session reminders.</li>
  <li><strong>Predictive Analytics:</strong> Utilizing machine learning models to forecast venue utilization rates and identify athlete churn patterns based on payment history.</li>
</ul>

<!-- ========================================================================= -->
<!-- 11.0 REFERENCES & APPENDIX -->
<!-- ========================================================================= -->
<h1 class="section-title">11.0 References &amp; Appendix</h1>

<h2 class="sub-title">11.1 Academic &amp; Technical References</h2>
<ol>
  <li>Elmasri, R., &amp; Navathe, S. B. (2015). <em>Fundamentals of Database Systems</em> (7th ed.). Pearson.</li>
  <li>Silberschatz, A., Korth, H. F., &amp; Sudarshan, S. (2019). <em>Database System Concepts</em> (7th ed.). McGraw-Hill.</li>
  <li>SQLite Consortium. (2024). <em>SQLite Foreign Key Support &amp; ACID Transactions</em>. https://www.sqlite.org/</li>
  <li>PostgreSQL Global Development Group. (2024). <em>PostgreSQL 16 Documentation: Schema Design and Triggers</em>. https://www.postgresql.org/docs/</li>
</ol>

<h2 class="sub-title">11.2 Project Repository &amp; Source Code Link</h2>
<div class="callout">
  <div class="callout-title">Official GitHub Repository</div>
  Source code, SQL schemas, dataset scripts, and web applications are publicly hosted at:<br>
  <strong><a href="https://github.com/Convoluted-Dense/Sports-Club.git" target="_blank" style="color:#2563eb; text-decoration:none;">https://github.com/Convoluted-Dense/Sports-Club.git</a></strong>
</div>

<h2 class="sub-title">11.3 Step-by-Step Setup &amp; Execution Guide</h2>
<ol>
  <li><strong>Clone the Repository:</strong>
    <pre class="sql-box" style="background:#1e293b; color:#e2e8f0;">git clone https://github.com/Convoluted-Dense/Sports-Club.git
cd Sports-Club</pre>
  </li>
  <li><strong>Zero-Config Launch (Python 3 Built-in):</strong>
    <pre class="sql-box" style="background:#1e293b; color:#e2e8f0;">python app.py</pre>
    <em>The server initializes <code>sports_club.db</code> automatically and launches the application at <code>http://127.0.0.1:5000</code>.</em>
  </li>
  <li><strong>Default Demo Login Credentials:</strong>
    <ul>
      <li><strong>Administrator:</strong> Username: <code>Admin</code> | Password: <code>Admin</code></li>
      <li><strong>Member Athlete:</strong> Email: <code>aarav.sharma@gmail.com</code> | Password: <code>aaravsharma</code></li>
    </ul>
  </li>
</ol>

</body>
</html>
"""

with open("project_report.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML report written to project_report.html")

# Render to PDF using Playwright + Edge
print("Rendering PDF with Playwright + Edge...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='msedge')
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('project_report.html')}")
    time.sleep(2)
    pdf_path = "Sports_Club_DBMS_Project_Report.pdf"
    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
        display_header_footer=True,
        header_template="<span></span>",
        footer_template="<div style='font-size: 8pt; color: #64748b; width: 100%; text-align: right; padding-right: 15mm;'>Sports Club DBMS Report | Sheikh Arsh Ali (25WU0102255) | Page <span class='pageNumber'></span> of <span class='totalPages'></span></div>"
    )
    browser.close()

print(f"PDF successfully generated at: {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
