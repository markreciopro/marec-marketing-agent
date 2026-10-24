import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Standardized MAREC Insights Signature Block
OFFICIAL_SIGNATURE = """Best regards,

Mark Anthony Recio, MBA
Strategic Lead & Principal Consultant | MAREC Insights
Direct: (702) 763-2573
Email: mark.recio@marec.site
Web: https://marec.site"""


def generate_grok_email(first_name, title="Leadership", company="your property"):
    """
    Generates a personalized consultative outreach email using Grok AI via direct API.
    Handles both positional arguments (first_name, title, company) or a dictionary lead object.
    Guarantees that the official MAREC Insights contact signature block is appended.
    """
    # If a dictionary was passed as the first argument
    if isinstance(first_name, dict):
        lead_data = first_name
        first_name = lead_data.get("first_name", "Valued Executive")
        company = lead_data.get("company", "your property")
        title = lead_data.get("role", lead_data.get("title", "Leadership"))

    api_key = os.getenv("XAI_API_KEY")

    prompt = f"""
You are an expert executive sales copywriter for MAREC Insights, a high-end business intelligence and data analytics consulting firm specializing in luxury hospitality workforce operations.

Draft a short, highly professional, direct cold outreach email to {first_name}, who is a {title} at {company}.

Tone & Style:
- Warm, executive, professional, and consultative.
- Address common industry pain points: operating in data silos across PMS, LMS, HRIS, CRM, and POS platforms.
- Mention how MAREC Insights builds hybrid ETL architectures (using Python and R) to unify data into executive Power BI and Tableau dashboards to optimize scheduling, reduce labor leakage, and capture high-margin revenue.
- End with a low-friction call to action asking for a brief 10-minute introductory call next week.
- End the main body right before the closing sign-off.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You write concise, high-converting B2B consultative outreach emails for luxury hospitality executives."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        if api_key:
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                raw_text = data["choices"][0]["message"]["content"].strip()
                
                # Strip any AI-generated closing and attach the official signature block
                for signoff in ["Best regards", "Warm regards", "Sincerely", "Regards"]:
                    if signoff in raw_text:
                        raw_text = raw_text.split(signoff)[0].strip()

                full_text = f"{raw_text}\n\n{OFFICIAL_SIGNATURE}"
                subject = f"Optimizing Hospitality Decision Intelligence at {company}"
                html_body = full_text.replace("\n\n", "</p><p>").replace("\n", "<br>")

                return {
                    "subject": subject,
                    "text": full_text,
                    "html": f'<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333333;"><p>{html_body}</p></div>'
                }

    except Exception as e:
        print(f"⚠️ Grok API call encountered an error ({e}), utilizing structured fallback template.")

    # Fallback template with guaranteed MAREC Insights contact signature
    fallback_text = f"""Hi {first_name},

Hope your week is going well.

Luxury hospitality leaders at {company} often face the challenge of operating in data silos across PMS, LMS, HRIS, CRM, and POS platforms.

At MAREC Insights, we engineer hybrid ETL architectures using Python and R to ingest and unify cross-departmental data into executive Power BI and Tableau decision dashboards. By connecting workforce intelligence with property performance metrics, we help operators optimize scheduling, reduce labor leakage, and capture high-margin revenue opportunities.

Would you be open to a brief 10-minute introductory call next week to explore how this applies to your operations?

{OFFICIAL_SIGNATURE}"""

    fallback_html = fallback_text.replace("\n\n", "</p><p>").replace("\n", "<br>")

    return {
        "subject": f"Optimizing Hospitality Decision Intelligence at {company}",
        "text": fallback_text,
        "html": f'<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333333;"><p>{fallback_html}</p></div>'
    }