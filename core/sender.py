import os
import resend
from dotenv import load_dotenv

load_dotenv(override=True)

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to_email, subject, text_body="", html_body=""):
    """
    Sends an email using the Resend API.
    Flexibly accepts text/text_body and html/html_body.
    """
    try:
        sender_email = os.getenv("SENDER_EMAIL", "mark.recio@marec.site")
        
        params = {
            "from": f"Mark Recio <{sender_email}>",
            "to": [to_email],
            "subject": subject,
            "text": text_body,
            "html": html_body if html_body else f"<p>{text_body}</p>"
        }

        response = resend.Emails.send(params)
        return bool(response and getattr(response, "id", None) or isinstance(response, dict))
    except Exception as e:
        print(f"⚠️ Resend dispatch error: {e}")
        return False