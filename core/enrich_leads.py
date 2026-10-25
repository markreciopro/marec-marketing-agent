import os
import requests
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Path to database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "leads.db")

def find_verified_emails(domain: str, company_name: str):
    """
    Queries Hunter.io API to discover verified corporate executive emails.
    Requires HUNTER_API_KEY environment variable.
    """
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        logging.warning("HUNTER_API_KEY not found. Skipping lead enrichment.")
        return []

    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        leads = []
        if "data" in data and "emails" in data["data"]:
            for item in data["data"]["emails"]:
                first_name = item.get("first_name") or "Valued"
                last_name = item.get("last_name") or "Executive"
                email = item.get("value")
                title = item.get("position") or "Operations Leader"
                
                # Filter for high accuracy emails (>70% confidence)
                if email and item.get("confidence", 0) >= 70:
                    leads.append((first_name, last_name, company_name, title, email))
        
        return leads
    except Exception as e:
        logging.error(f"Error fetching leads for {domain}: {e}")
        return []

def save_leads_to_db(leads):
    """Inserts newly discovered leads into database/leads.db."""
    if not leads:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executemany("""
        INSERT OR IGNORE INTO leads (first_name, last_name, company, title, email)
        VALUES (?, ?, ?, ?, ?)
    """, leads)
    
    conn.commit()
    conn.close()
    logging.info(f"Inserted {len(leads)} verified leads into leads.db.")

if __name__ == "__main__":
    # Define target enterprise resort/hospitality domains
    target_list = [
        {"domain": "mgmresorts.com", "company": "MGM Resorts International"},
        {"domain": "wynnlasvegas.com", "company": "Wynn Las Vegas"},
        {"domain": "caesars.com", "company": "Caesars Entertainment"}
    ]

    for target in target_list:
        found_leads = find_verified_emails(target["domain"], target["company"])
        save_leads_to_db(found_leads)