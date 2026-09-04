# main()
# ↓
# read local env vars / GitHub secrets
# ↓
# connect to PostgreSQL with psycopg
# ↓
# delete all users except demo@email.com
# ↓
# delete demo user expenses
# ↓
# insert the 4 fresh demo expenses again
# ↓
# try to send confirmation email
# ↓
# if reset succeeds, sends confirmation email through Resend
# ↓
# if email succeeds, workflow ends normally
# ↓
# if email fails, reset still stays done but email error is logged

import requests

from utils import get_required_env, connect_to_database, send_confirmation_email

demo_email = "demo@email.com"

def delete_non_demo_users(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM users
            WHERE email != %s;
            """,
            (demo_email,),
        )
    conn.commit()

def clear_demo_expenses(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM expenses
            WHERE user_id = (
              SELECT id
              FROM users
              WHERE email = %s
            );
            """,
            (demo_email,),
        )
    conn.commit()


def main():
    print("Starting demo-reset workflow...")

    database_url = get_required_env("SUPABASE_DATABASE_URL")
    resend_api_key = get_required_env("RESEND_API_KEY")
    email_from = get_required_env("EMAIL_FROM")
    email_to = get_required_env("EMAIL_TO")

    print("Environment variables loaded successfully.")

    with connect_to_database(database_url) as conn:
        print("Database connection successful.")

        delete_non_demo_users(conn)
        print("All users except demo@email.com deleted successfully.")

        clear_demo_expenses(conn)
        print("Demo user expenses deleted successfully.")
        


if __name__ == "__main__":
    main()
