import os
import requests

def generate_email(lead_name, company_name, title, trend_briefing=None):
    """
    Generates a personalized B2B executive outreach email for MAREC Insights.
    Uses xAI (Grok) API if XAI_API_KEY is available, with an automatic
    fail-safe fallback template.
    """
    api_key = os.getenv("XAI_API_KEY")
    
    # 1. High-Converting Fallback Template
    briefing_context = f"\n\nRecent Market Insight:\n{trend_briefing}" if trend_briefing else ""
    fallback_email = (
        f"Hi {lead_name},\n\n"
        f"As {title} at {company_name}, optimizing operational throughput and workforce utilization "
        f"is critical to protecting margins in today's dynamic hospitality market.\n\n"
        f"At MAREC Insights, we help luxury hospitality and gaming executives transform raw workforce "
        f"and operations data into predictive decision intelligence.{briefing_context}\n\n"
        f"Would you be open to a brief 10-minute strategy chat next week to explore how we can optimize "
        f"labor efficiency and operational yields for {company_name}?\n\n"
        f"Best regards,\n\n"
        f"Mark Recio\n"
        f"Founder & Principal Consultant | MAREC Insights\n"
        f"mark.recio@marec.site | (702) 763-2573"
    )

    # 2. Attempt xAI Grok Generation if Key Exists
    if api_key:
        try:
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            prompt = (
                f"You are a strategic B2B marketing advisor for MAREC Insights, an independent analytics "
                f"and workforce operations consultancy run by Mark Recio.\n"
                f"Write a concise, compelling 3-paragraph executive cold outreach email to {lead_name}, who is "
                f"the {title} at {company_name}.\n"
                f"Focus on how MAREC Insights delivers data-driven workforce optimization, decision intelligence, "
                f"and revenue management for hospitality and enterprise operations.\n"
            )
            if trend_briefing:
                prompt += f"Seamlessly incorporate this recent industry trend briefing into the body: {trend_briefing}\n"
            
            prompt += "Keep the tone professional, direct, and consultative. End with a polite call to action for a 10-minute strategy conversation. Do not include subject line or placeholders."

            payload = {
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": "You write high-converting executive B2B outreach emails for MAREC Insights."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 350
            }

            response = requests.post(url, headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                if content:
                    return content
            else:
                print(f"⚠️ xAI API returned status code {response.status_code}. Using fail-safe fallback template.")
        except Exception as e:
            print(f"⚠️ xAI API generation notice: {e}. Using fail-safe fallback template.")

    return fallback_email

if __name__ == "__main__":
    # Test script locally
    test_email = generate_email(
        lead_name="Alexander Vance",
        company_name="Bellagio Las Vegas",
        title="VP of Hotel Operations",
        trend_briefing="Increasing resort labor costs are prompting executive teams to deploy real-time digital twin analytics."
    )
    print("--- GENERATED OUTREACH TEST ---")
    print(test_email)