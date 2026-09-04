import os
import psycopg
import requests

def get_required_env(name):
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value

def connect_to_database(database_url):
    return psycopg.connect(database_url)

def send_confirmation_email(api_key, email_from, email_to, subject, message):
    response = requests.post(
        "https://api.resend.com/emais",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-type": "application/json"
        },
        json={
            "from": email_from,
            "to": [email_to],
            "subject": subject,
            "html": message,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()