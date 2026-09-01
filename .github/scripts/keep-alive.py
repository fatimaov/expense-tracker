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
# GMAIL_ADDRESS
# GMAIL_APP_PASSWORD
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

def main():
    print("Starting Supabase keep-alive workflow...")

    database_url = get_required_env("SUPABASE_DATABASE_URL")
    gmail_address = get_required_env("GMAIL_ADDRESS")
    gmail_app_password = get_required_env("GMAIL_APP_PASSWORD")
    email_to = get_required_env("EMAIL_TO")

    print("Environment variables loaded successfully.")

    with connect_to_database(database_url) as conn:
        print("Database connection successful.")

        create_keep_alive_table(conn)
        print("keep_alive_logs table is ready.")

        log_id = insert_keep_alive_log(conn)
        print(f"Keep-alive log inserted successfully with id: {log_id}")

if __name__ == "__main__":
    main()


