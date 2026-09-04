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

def create_demo_expenses(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH demo_user AS (
                SELECT id
                FROM users
                WHERE email = %s
            )
            INSERT INTO expenses (
                user_id,
                amount,
                title,
                expense_date,
                category,
                notes
            )
            SELECT
                demo_user.id,
                demo_expenses.amount,
                demo_expenses.title,
                demo_expenses.expense_date,
                demo_expenses.category,
                demo_expenses.notes
            FROM demo_user
            CROSS JOIN (
                VALUES
                    (
                        4.80,
                        'Coffee & pastry',
                        '2026-08-09'::date,
                        'Food'::expense_category,
                        'Breakfast at a café before work ☕'
                    ),
                    (
                        18.50,
                        'Train ticket',
                        '2026-08-09'::date,
                        'Transport'::expense_category,
                        'Round trip to the city center'
                    ),
                    (
                        32.00,
                        'Museum tickets',
                        '2026-08-09'::date,
                        'Activities'::expense_category,
                        'Weekend visit with a friend'
                    ),
                    (
                        74.90,
                        'Hotel night',
                        '2026-08-09'::date,
                        'Accommodation'::expense_category,
                        'One-night stay during a short trip 🏨'
                    )
            ) AS demo_expenses (
                amount,
                title,
                expense_date,
                category,
                notes
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

        create_demo_expenses(conn)
        print("Demo user expenses created sucessfully.")



if __name__ == "__main__":
    main()
