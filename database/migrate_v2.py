import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Starting database migration to Schema v2...")

    # 1. Companies Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        website TEXT,
        category TEXT,
        country TEXT,
        island TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Contacts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        title TEXT,
        email TEXT NOT NULL UNIQUE,
        is_verified INTEGER DEFAULT 0,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    );
    """)

    # 3. Leads & Sales Pipeline Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER NOT NULL,
        stage TEXT DEFAULT 'New Leads',
        potential_need TEXT,
        lead_score INTEGER DEFAULT 50,
        lead_source TEXT DEFAULT 'Hunter.io',
        next_followup DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    );
    """)

    # 4. Outreach Activities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outreach_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER NOT NULL,
        activity_type TEXT NOT NULL,
        subject TEXT,
        content TEXT,
        status TEXT DEFAULT 'sent',
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lead_id) REFERENCES leads_v2(id)
    );
    """)

    # 5. Opportunities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        estimated_value REAL DEFAULT 0.0,
        probability INTEGER DEFAULT 20,
        stage TEXT DEFAULT 'Discovery',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lead_id) REFERENCES leads_v2(id)
    );
    """)

    # 6. Tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        title TEXT NOT NULL,
        due_date DATE,
        is_completed INTEGER DEFAULT 0,
        FOREIGN KEY (lead_id) REFERENCES leads_v2(id)
    );
    """)

    # --- MIGRATE EXISTING LEADS SAFELY ---
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads';")
    if cursor.fetchone():
        # Check actual columns in the old leads table
        cursor.execute("PRAGMA table_info(leads);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Existing 'leads' columns found: {columns}")

        cursor.execute("SELECT * FROM leads;")
        old_rows = cursor.fetchall()

        for row in old_rows:
            # Map based on available columns or use safe defaults
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            
            first = row_dict.get("first_name", "Valued")
            last = row_dict.get("last_name", "Executive")
            comp_name = row_dict.get("company", "Independent Resort")
            title = row_dict.get("title", "Operations Leader")
            email = row_dict.get("email", f"contact_{id(row)}@example.com")
            status = row_dict.get("status", "pending")

            # Insert Company if not exists
            cursor.execute("INSERT OR IGNORE INTO companies (name) VALUES (?)", (comp_name,))
            cursor.execute("SELECT id FROM companies WHERE name = ?", (comp_name,))
            comp_res = cursor.fetchone()
            if comp_res:
                comp_id = comp_res[0]

                # Insert Contact
                cursor.execute("""
                    INSERT OR IGNORE INTO contacts (company_id, first_name, last_name, title, email, is_verified)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (comp_id, first, last, title, email))
                
                cursor.execute("SELECT id FROM contacts WHERE email = ?", (email,))
                contact_res = cursor.fetchone()
                if contact_res:
                    contact_id = contact_res[0]
                    stage = 'Contacted' if status == 'contacted' else 'New Leads'
                    cursor.execute("""
                        INSERT OR IGNORE INTO leads_v2 (contact_id, stage, lead_source)
                        VALUES (?, ?, 'Legacy Migration')
                    """, (contact_id, stage))

    conn.commit()
    conn.close()
    print("Migration complete! Relational v2 schema is ready.")

if __name__ == "__main__":
    migrate_database()