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

import requests

from utils import get_required_env, connect_to_database, send_confirmation_email

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
            subject="Expense Tracker keep-alive successful"
            message=f"""
                <p>The Supabase keep-alive workflow ran successfully.</p>
                <p>Inserted log ID: {log_id}</p>
            """

            email_response = send_confirmation_email(
                resend_api_key, 
                email_from, 
                email_to, 
                subject,
                message
            )
            print(f"Confirmation email sent successfully: {email_response}")

            mark_log_as_notified(conn, log_id)
            print(f"Keep-alive log {log_id} marked as notified.")

        except requests.RequestException as error:
            print(f"Confirmation email failed: {error}")

if __name__ == "__main__":
    main()


