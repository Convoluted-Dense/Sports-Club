import sqlite3
import os
import sys

DB_FILE = os.path.join(os.path.dirname(__file__), "sports_club.db")

def print_table(cursor, title=None):
    if title:
        print(f"\n=== {title} ===")
    
    if not cursor.description:
        print("Empty or non-query result.")
        return
        
    cols = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    
    if not rows:
        print("No rows found.")
        return

    # Calculate max column widths
    col_widths = [len(c) for c in cols]
    for row in rows:
        for idx, val in enumerate(row):
            val_str = str(val) if val is not None else "NULL"
            col_widths[idx] = max(col_widths[idx], len(val_str))

    # Format header
    header = " | ".join(cols[i].ljust(col_widths[i]) for i in range(len(cols)))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(cols)))
    
    print(header)
    print(separator)
    for row in rows:
        row_str = " | ".join((str(val) if val is not None else "NULL").ljust(col_widths[i]) for i, val in enumerate(row))
        print(row_str)
    print(f"({len(rows)} rows)\n")

def list_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in cursor.fetchall()]
    print("\n--- Available Tables ---")
    for idx, t in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f" {idx:2d}. {t.ljust(20)} ({count} rows)")
    print("------------------------\n")

def main():
    if not os.path.exists(DB_FILE):
        print(f"Database file not found. Initializing...")
        from db_manager import init_sqlite_db
        init_sqlite_db()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if len(sys.argv) > 1:
        # One-shot command or table name
        arg = " ".join(sys.argv[1:]).strip()
        if arg.lower() == "tables":
            list_tables(cursor)
        elif arg.lower().startswith("select") or arg.lower().startswith("pragma"):
            try:
                cursor.execute(arg)
                print_table(cursor)
            except Exception as e:
                print(f"Error: {e}")
        else:
            # Assume table name
            try:
                cursor.execute(f"SELECT * FROM {arg} LIMIT 30")
                print_table(cursor, title=f"Table: {arg}")
            except Exception as e:
                print(f"Error: {e}")
        conn.close()
        return

    # Interactive loop
    print("==========================================================")
    print(" SPORTS CLUB DBMS - INTERACTIVE TERMINAL VIEWER")
    print("==========================================================")
    print(" Commands:")
    print("   .tables               - List all tables with row counts")
    print("   .view <table_name>    - View rows from a table")
    print("   <SQL query>;          - Execute any SQL statement")
    print("   .exit or quit         - Exit terminal viewer")
    print("==========================================================\n")

    list_tables(cursor)

    while True:
        try:
            cmd = input("DBMS> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not cmd:
            continue
        if cmd.lower() in [".exit", "exit", "quit", ".quit"]:
            break
        elif cmd.lower() in [".tables", "tables"]:
            list_tables(cursor)
        elif cmd.lower().startswith(".view "):
            tbl = cmd.split(maxsplit=1)[1].strip().strip(';')
            try:
                cursor.execute(f"SELECT * FROM {tbl} LIMIT 30")
                print_table(cursor, title=f"Table: {tbl}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            try:
                cursor.execute(cmd)
                if cmd.strip().upper().startswith(("SELECT", "PRAGMA", "EXPLAIN")):
                    print_table(cursor)
                else:
                    conn.commit()
                    print(f"Executed successfully. ({cursor.rowcount} rows affected)\n")
            except Exception as e:
                print(f"SQL Error: {e}\n")

    conn.close()

if __name__ == "__main__":
    main()
