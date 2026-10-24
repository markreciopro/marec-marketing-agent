import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")

def init_db():
    """Initializes the SQLite database table if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_leads (
            email TEXT PRIMARY KEY,
            first_name TEXT,
            company TEXT,
            title TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_lead_sent(email: str) -> bool:
    """Checks if a lead email has already been processed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_leads WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_lead_sent(email: str, first_name: str = "", company: str = "", title: str = ""):
    """Records a processed lead into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO processed_leads (email, first_name, company, title)
        VALUES (?, ?, ?, ?)
    """, (email, first_name, company, title))
    conn.commit()
    conn.close()