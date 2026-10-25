import os
import sys

# Ensure root directory and database folder are in system path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "database"))

# Direct imports from root and database folders
try:
    from lead_finder import fetch_leads
    from report_generator import generate_daily_trend_briefing
    from ai_generator import generate_email
    from sender import send_email, send_executive_report
except ImportError:
    # Fallback if files are inside a core/ directory
    from core.lead_finder import fetch_leads
    from core.report_generator import generate_daily_trend_briefing
    from core.ai_generator import generate_email
    from core.sender import send_email, send_executive_report

try:
    from database.db_client import save_lead, init_db, is_lead_processed
except ImportError:
    from db_client import save_lead, init_db, is_lead_processed

def run_marketing_pipeline():
    print("=" * 60)
    print("🚀 INITIALIZING MAREC INSIGHTS B2B MARKETING PIPELINE")
    print("=" * 60)
    
    # 1. Initialize Database
    try:
        init_db()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"⚠️ Database initialization notice: {e}")

    # 2. Fetch Prospects
    try:
        leads = fetch_leads()
    except Exception as e:
        print(f"❌ Error fetching leads: {e}")
        leads = []

    if not leads:
        print("⚠️ No leads retrieved from source. Sending execution summary...")
        try:
            send_executive_report(evaluated_count=0, dispatched_count=0, skipped_count=0, dispatched_logs=[])
        except Exception as e:
            print(f"❌ Failed to dispatch report: {e}")
        return

    total_evaluated = len(leads)
    processed_count = 0
    skipped_count = 0
    dispatched_logs = []

    print(f"📊 Evaluated {total_evaluated} target prospects from roster...\n")

    for idx, lead in enumerate(leads, 1):
        name = lead.get("name", "Valued Partner")
        company = lead.get("company", "Aria Resort & Casino Las Vegas")
        email = lead.get("email")
        title = lead.get("title", "Luxury Hospitality Leader")

        print(f"[{idx}/{total_evaluated}] Target: {name} | {company} ({email})")

        # Duplicate Prevention Check
        if email and is_lead_processed(email):
            print(f"   ⏩ Lead already in leads.db — Skipping to prevent duplicate outreach.")
            skipped_count += 1
            continue

        # Fetch xAI Research Briefing
        print(f"   🔎 Generating daily research briefing via xAI Grok Agent...")
        try:
            trend_briefing = generate_daily_trend_briefing(company_name=company, role=title)
        except Exception as e:
            print(f"   ⚠️ Trend generator fallback: {e}")
            trend_briefing = None

        # Assemble Email Body
        print(f"   ✍️ Assembling personalized outreach message...")
        email_content = generate_email(
            lead_name=name,
            company_name=company,
            title=title,
            trend_briefing=trend_briefing
        )

        # Dispatch Email
        if email:
            print(f"   📤 Dispatching outreach via Resend API to {email}...")
            subject = f"Optimizing Hospitality Analytics & Workforce Intelligence for {company}"
            
            try:
                success = send_email(to_email=email, subject=subject, body=email_content)
                if success:
                    save_lead(name=name, company=company, email=email, status="sent")
                    processed_count += 1
                    dispatched_logs.append(f"{name} ({company}) — {email}")
                    print(f"   ✅ Successfully sent and logged in database.")
                else:
                    print(f"   ❌ Resend API dispatch failed.")
            except Exception as e:
                print(f"   ❌ Dispatch error: {e}")
        else:
            print(f"   ⚠️ Missing email address for lead: {name}")

    print("\n" + "=" * 60)
    print(f"✅ PIPELINE RUN COMPLETE | Sent: {processed_count} | Skipped: {skipped_count} | Total: {total_evaluated}")
    print("=" * 60)

    # 3. Dispatch Executive Summary Report
    print("📧 Dispatching Executive Marketing Report to mark.recio@marec.site...")
    try:
        send_executive_report(
            evaluated_count=total_evaluated,
            dispatched_count=processed_count,
            skipped_count=skipped_count,
            dispatched_logs=dispatched_logs
        )
    except Exception as e:
        print(f"❌ Could not send Executive Report: {e}")

if __name__ == "__main__":
    run_marketing_pipeline()