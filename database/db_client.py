import os
import sqlite3

# Define absolute path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "leads.db")

def get_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite leads database and create tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            company TEXT,
            email TEXT UNIQUE,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_lead_processed(email):
    """Check if an email address has already been processed in leads.db to prevent duplicate outreach."""
    if not email:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM leads WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_lead(name, company, email, status="sent"):
    """Insert or update a lead in the leads database."""
    if not email:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO leads (name, company, email, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                status=excluded.status,
                name=excluded.name,
                company=excluded.company
        """, (name, company, email, status))
        conn.commit()
        return True
    except Exception as e:
        print(f"⚠️ Error saving lead to database: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database client initialized successfully at:", DB_PATH)