import os

def fetch_leads():
    """
    Fetches leads for outreach processing.
    Checks for TARGET_OVERRIDE_EMAIL environment variable for immediate testing.
    """
    # Check if a custom target email was passed for testing
    override_email = os.getenv("TARGET_OVERRIDE_EMAIL")
    
    if override_email:
        return [
            {
                "email": override_email,
                "first_name": "Mark",
                "role": "Director of Hospitality",
                "company": "Aria Resort & Casino Las Vegas"
            }
        ]

    # Default lead list for standard pipeline execution
    return [
        {
            "email": "mark.recio@marec.site",
            "first_name": "Mark",
            "role": "Director of Hospitality",
            "company": "Aria Resort & Casino Las Vegas"
        }
    ]