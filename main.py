import os
from lead_finder import fetch_leads
from report_generator import generate_daily_trend_briefing
from ai_generator import generate_email
from db_client import save_lead, init_db, is_lead_processed
from sender import send_email

def run_marketing_pipeline():
    print("🚀 Initializing MAREC Insights Marketing Agent Pipeline...")
    
    init_db()
    leads = fetch_leads()
    
    if not leads:
        print("No leads retrieved.")
        return

    processed_count = 0
    skipped_count = 0
    dispatched_leads = []

    for lead in leads:
        name = lead.get("name", "Valued Partner")
        company = lead.get("company", "Aria Resort & Casino Las Vegas")
        email = lead.get("email")
        title = lead.get("title", "Luxury Hospitality Leader")

        if email and is_lead_processed(email):
            print(f"⏩ Lead already processed, skipping: {email}")
            skipped_count += 1
            continue

        print(f"\n📊 1. Generating daily research trend briefing for {company}...")
        # Generate dynamic today's date & cited research trend
        trend_briefing = generate_daily_trend_briefing(company_name=company, role=title)

        print(f"📧 2. Crafting personalized email with daily trend brief...")
        # Pass trend_briefing into email generator
        email_content = generate_email(
            lead_name=name,
            company_name=company,
            title=title,
            trend_briefing=trend_briefing
        )

        if email:
            print(f"📤 3. Dispatching email to {email}...")
            subject = f"Optimizing Hospitality Analytics & Workforce Intelligence for {company}"
            send_email(to_email=email, subject=subject, body=email_content)
            save_lead(name=name, company=company, email=email, status="sent")
            processed_count += 1
            dispatched_leads.append(f"{name} ({company}) - {email}")
        else:
            print(f"⚠️ No email address found for {name}.")

    print(f"\n✅ Run Complete! Sent: {processed_count} | Skipped: {skipped_count}")

if __name__ == "__main__":
    run_marketing_pipeline()