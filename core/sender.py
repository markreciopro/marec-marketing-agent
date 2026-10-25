import os
import requests

def send_email(to_email, subject, body):
    """
    Dispatches a single B2B outreach email using the Resend API.
    """
    resend_api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "mark.recio@marec.site")

    if not resend_api_key:
        print("⚠️ Missing RESEND_API_KEY environment variable. Dispatch aborted.")
        return False

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {resend_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": f"Mark Recio <{sender_email}>",
        "to": [to_email],
        "subject": subject,
        "text": body
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ Successfully dispatched outreach email to {to_email}")
            return True
        else:
            print(f"❌ Resend API Error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Network or dispatch exception: {e}")
        return False

def send_executive_report(evaluated_count, dispatched_count, skipped_count, dispatched_logs=None):
    """
    Dispatches the daily Executive Operations & Leads Briefing directly to mark.recio@marec.site.
    """
    resend_api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "mark.recio@marec.site")
    recipient_email = "mark.recio@marec.site"

    if not resend_api_key:
        print("⚠️ Missing RESEND_API_KEY. Skipping Executive Marketing Report dispatch.")
        return False

    logs_formatted = "\n".join([f"• {log}" for log in dispatched_logs]) if dispatched_logs else "• No outreach emails dispatched in this cycle."

    subject = f"📊 MAREC Insights Executive Briefing: Pipeline Execution Summary"
    body = (
        f"MAREC Insights — Executive Marketing Agent Summary\n"
        f"{'='*55}\n\n"
        f"Pipeline Execution Metrics:\n"
        f"• Total Prospects Evaluated : {evaluated_count}\n"
        f"• Outreach Emails Dispatched: {dispatched_count}\n"
        f"• Skipped (Duplicate Check): {skipped_count}\n\n"
        f"Dispatched Activity Log:\n"
        f"{logs_formatted}\n\n"
        f"{'='*55}\n"
        f"Automated System Notification | MAREC Insights Platform"
    )

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {resend_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": f"MAREC Agent <{sender_email}>",
        "to": [recipient_email],
        "subject": subject,
        "text": body
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ Executive Marketing Report sent to {recipient_email}")
            return True
        else:
            print(f"❌ Resend API Error on Executive Report ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Network exception on Executive Report: {e}")
        return False

if __name__ == "__main__":
    send_executive_report(evaluated_count=5, dispatched_count=1, skipped_count=4, dispatched_logs=["Test Prospect — test@example.com"])