import os
import sqlite3

# Define database file path
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "leads.db")

def initialize_database():
    """
    Initializes the SQLite database schema and populates sample executive lead records.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create target leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            company TEXT,
            title TEXT,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Create processed leads tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_leads (
            email TEXT PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Clear out old test entries if needed
    cursor.execute("DELETE FROM leads")
    cursor.execute("DELETE FROM processed_leads")

    # 4. Insert targeted executive prospect leads
    # (Replace email addresses with your actual target corporate contacts)
    target_leads = [
        ("Aria Operations", "Team", "Aria Resort & Casino Las Vegas", "Director of Operations", "operations@aria.com"),
        ("Bellagio Analytics", "Lead", "Bellagio Hotel & Casino", "VP of Revenue & Workforce", "analytics@bellagio.com"),
        ("Wynn Leadership", "Group", "Wynn Las Vegas", "Chief Commercial Officer", "leadership@wynnlasvegas.com"),
    ]

    cursor.executemany("""
        INSERT INTO leads (first_name, last_name, company, title, email)
        VALUES (?, ?, ?, ?, ?)
    """, target_leads)

    conn.commit()
    conn.close()
    print(f"✅ Successfully initialized {DB_PATH} with updated schema and prospect records!")

if __name__ == "__main__":
    initialize_database()