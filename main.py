import os
import sys
from dotenv import load_dotenv
from core.lead_finder import fetch_leads
from core.ai_generator import generate_grok_email
from core.sender import send_email
from database.db_client import init_db, is_lead_sent, mark_lead_sent

load_dotenv(override=True)

def run_marketing_pipeline():
    print("🚀 Initializing MAREC Insights Marketing Agent Pipeline...")
    init_db()
    
    leads = fetch_leads()
    if not leads:
        print("ℹ️ No leads retrieved.")
        return

    sent_count = 0
    skipped_count = 0

    for lead in leads:
        email = lead.get("email")
        first_name = lead.get("first_name", "Executive")
        title = lead.get("role", lead.get("title", "Director of Hospitality"))
        company = lead.get("company", "Aria Resort & Casino Las Vegas")

        if is_lead_sent(email):
            print(f"⏩ Skipping {email} (already processed in database).")
            skipped_count += 1
            continue

        print(f"🧠 Generating Grok AI email content for {first_name} at {company}...")
        content = generate_grok_email(first_name, title, company)

        print(f"📧 Dispatching outreach message to {email}...")
        
        # Pass parameters cleanly matching core/sender.py signature
        success = send_email(
            email,
            content["subject"],
            content["text"],
            content["html"]
        )

        if success:
            mark_lead_sent(email, first_name, company, title)
            sent_count += 1
            print(f"✅ Successfully sent to {email}")
        else:
            print(f"❌ Failed to dispatch email to {email}")

    print(f"\n📊 Summary: {sent_count} Sent, {skipped_count} Skipped.")

if __name__ == "__main__":
    run_marketing_pipeline()