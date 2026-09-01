# main()
# ↓
# read local env vars / GitHub secrets
# ↓
# connect to PostgreSQL with psycopg
# ↓
# create keep_alive_logs table if missing
# ↓
# insert new row
# ↓
# store returned row id in a Python variable
# ↓
# try to send confirmation email
# ↓
# if email succeeds:
#     update notified_at for that row id
# ↓
# if email fails:
#     log the error
#     leave notified_at as NULL

# psycopg → database
# os → read secrets/env vars
# smtplib/email.message → send email

# ENV VARS
# SUPABASE_DATABASE_URL
# RESEND_API_KEY
# EMAIL_FROM
# EMAIL_TO
# get_required_env()

#  DATABASE FUNCTIONS
# create_keep_alive_table(connection)
# insert_keep_alive_log(connection)
# mark_log_as_notified(connection, log_id)

# EMAIL FUNCTIONS
# send_confirmation_email()

import os 
import psycopg
import requests

# Get the environment variables
def get_required_env(name):
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value

def connect_to_database(database_url):
    return psycopg.connect(database_url)

def create_keep_alive_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS keep_alive_logs (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                source TEXT NOT NULL,
                note TEXT,
                notified_at TIMESTAMPTZ DEFAULT NULL
            );
            """
        )

    conn.commit()

def insert_keep_alive_log(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO keep_alive_logs (source, note)
            VALUES (%s, %s)
            RETURNING id;
            """,
            ("github-actions", "Scheduled keep-alive ping"),
        )

        log_id = cur.fetchone()[0]

    conn.commit()
    return log_id

def send_confirmation_email(api_key, email_from, email_to, log_id):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-type": "application/json"
        },
        json={
            "from": email_from,
            "to": [email_to],
            "subject": "Expense Tracker keep-alive successful",
            "html": f"""
                <p>The Supabase keep-alive workflow ran successfully.</p>
                <p>Inserted log ID: {log_id}</p>
            """,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()

def mark_log_as_notified(conn, log_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE keep_alive_logs
            SET notified_at = NOW()
            WHERE id = %s;
            """,
            (log_id,),
        )

    conn.commit()

def main():
    print("Starting Supabase keep-alive workflow...")

    database_url = get_required_env("SUPABASE_DATABASE_URL")
    resend_api_key = get_required_env("RESEND_API_KEY")
    email_from = get_required_env("EMAIL_FROM")
    email_to = get_required_env("EMAIL_TO")

    print("Environment variables loaded successfully.")

    with connect_to_database(database_url) as conn:
        print("Database connection successful.")

        create_keep_alive_table(conn)
        print("keep_alive_logs table is ready.")

        log_id = insert_keep_alive_log(conn)
        print(f"Keep-alive log inserted successfully with id: {log_id}")

        try:
            email_response = send_confirmation_email(
                resend_api_key, 
                email_from, 
                email_to, 
                log_id
            )
            print(f"Confirmation email sent successfully: {email_response}")

            mark_log_as_notified(conn, log_id)
            print(f"Keep-alive log {log_id} marked as notified.")
            
        except requests.RequestException as error:
            print(f"Confirmation email failed: {error}")

if __name__ == "__main__":
    main()


