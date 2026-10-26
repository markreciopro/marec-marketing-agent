import sqlite3
import os
import requests
import json
from datetime import datetime

# Path to relational v2 database
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "leads.db")
GROK_API_KEY = os.getenv("GROK_API_KEY")

def get_pending_leads():
    """Fetches leads from V2 relational schema that are in 'New Leads' stage."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT l.id, c.first_name, c.last_name, c.title, c.email, comp.name, comp.country
        FROM leads_v2 l
        JOIN contacts c ON l.contact_id = c.id
        JOIN companies comp ON c.company_id = comp.id
        WHERE l.stage = 'New Leads'
    """)
    leads = cursor.fetchall()
    conn.close()
    return leads

def generate_grok_draft(first_name, company, title, country):
    """Generates personalized consultative outreach copy using Grok 4.7 API."""
    if not GROK_API_KEY:
        print("Notice: GROK_API_KEY environment variable not detected. Using fallback draft template.")
        return f"Hello {first_name},\n\nI noticed {company}'s operations in {country}. At MAREC Insights, we help resort and hospitality leaders optimize workforce scheduling, labor-cost visibility, and decision intelligence.\n\nBest regards,\nMark Recio"

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Write a brief, compelling B2B consultative email (under 120 words) from Mark Recio at MAREC Insights to {first_name}, who is the {title} at {company} (located in {country}).
    Focus on resort workforce analytics, labor scheduling efficiency, and custom Power BI / Python decision models.
    Keep the tone professional, direct, and conversational.
    """

    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are an executive outreach expert for hospitality business intelligence and workforce analytics."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"Grok API returned status code {response.status_code}. Using template.")
    except Exception as e:
        print(f"Error connecting to Grok API: {e}")

    return f"Hello {first_name},\n\nI wanted to connect regarding workforce analytics and decision models at {company}."

def stage_drafts_for_review():
    """Processes new leads, drafts personalized emails, and stages them for human approval."""
    leads = get_pending_leads()
    if not leads:
        print("No new pending leads found in 'New Leads' stage.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for lead_id, first, last, title, email, company, country in leads:
        print(f"Generating review draft for {first} {last} ({company})...")
        location_str = country if country else "your region"
        draft_content = generate_grok_draft(first, company, title, location_str)

        # 1. Store draft in outreach_activities table with status='draft'
        cursor.execute("""
            INSERT INTO outreach_activities (lead_id, activity_type, subject, content, status)
            VALUES (?, 'Email Draft', ?, ?, 'draft')
        """, (lead_id, f"Workforce Analytics & Labor Intelligence for {company}", draft_content))

        # 2. Advance lead stage to 'Researched'
        cursor.execute("UPDATE leads_v2 SET stage = 'Researched' WHERE id = ?", (lead_id,))
        print(f"-> Draft saved for Lead ID {lead_id}. Pipeline stage updated to 'Researched'.")

    conn.commit()
    conn.close()
    print("\n✓ Processing complete! All new leads have been staged into review drafts.")

if __name__ == "__main__":
    stage_drafts_for_review()