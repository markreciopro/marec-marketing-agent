import os
import sqlite3
import logging
from typing import List, Dict, Any

# Setup basic logging for lead retrieval tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "leads.db")

def get_unprocessed_leads(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetches up to `limit` leads from the database that have not yet been processed.
    Ensures leads already present in `processed_leads` are completely excluded.
    """
    if not os.path.exists(DB_PATH):
        logging.error(f"Database file not found at: {DB_PATH}")
        return []

    leads = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()

        # Ensure processed_leads table exists to prevent SQL errors on clean DBs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_leads (
                email TEXT PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Fetch up to `limit` leads not in `processed_leads`
        query = """
            SELECT * FROM leads 
            WHERE email NOT IN (SELECT email FROM processed_leads WHERE email IS NOT NULL)
            LIMIT ?
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

        for row in rows:
            leads.append(dict(row))

        conn.close()
        logging.info(f"Retrieved {len(leads)} unprocessed lead(s) for pipeline execution.")

    except sqlite3.Error as e:
        logging.error(f"SQLite error while fetching leads: {e}")

    return leads

def mark_lead_as_processed(email: str) -> None:
    """
    Records a lead's email into `processed_leads` upon successful engagement/email delivery.
    """
    if not email:
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO processed_leads (email) VALUES (?)
        """, (email,))
        conn.commit()
        conn.close()
        logging.info(f"Marked lead as processed: {email}")
    except sqlite3.Error as e:
        logging.error(f"Failed to record processed lead ({email}): {e}")

if __name__ == "__main__":
    # Test script locally
    unprocessed = get_unprocessed_leads(limit=100)
    print(f"Found {len(unprocessed)} unprocessed leads ready for batching.")