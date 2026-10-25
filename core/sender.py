import os
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def send_outreach_email(to_email: str, subject: str, body_text: str) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "mark.recio@marec.site")

    if not api_key:
        logging.error("RESEND_API_KEY environment variable is missing.")
        return False

    if not to_email:
        logging.error("No target recipient email specified.")
        return False

    payload = {
        "from": f"Mark Recio <{sender_email}>",
        "to": [to_email],
        "subject": subject,
        "text": body_text
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.resend.com/emails", json=payload, headers=headers)
        if response.status_code in [200, 201, 202]:
            logging.info(f"Successfully delivered email to: {to_email}")
            return True
        else:
            logging.error(f"Resend API error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        logging.error(f"Failed to transmit email: {e}")
        return False