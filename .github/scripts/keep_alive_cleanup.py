import requests
import os

from utils import get_required_env, connect_to_database, send_confirmation_email

def delete_keep_alive_logs(conn, dry_run):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM keep_alive_logs;")
        print(f"Rows affected: {cur.rowcount}")

    if dry_run:
        conn.rollback()
        print("Dry run enabled. No records were deleted.")
    else:
        conn.commit()
        print("Cleanup committed. Records were deleted.")


def main():
    print("Starting Supabase keep-alive cleanup workflow...")

    database_url = get_required_env("SUPABASE_DATABASE_URL")
    resend_api_key = get_required_env("RESEND_API_KEY")
    email_from = get_required_env("EMAIL_FROM")
    email_to = get_required_env("EMAIL_TO")
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    print("Environment variables loaded successfully.")

    with connect_to_database(database_url) as conn:
        print("Database connection successful.")

        delete_keep_alive_logs(conn, dry_run)

        try:
            subject="Expense Tracker keep-alive cleanup completed"
            message="""
                <p>The monthly keep-alive logs cleanup ran successfully.</p>
                <p>Old keep-alive log records were deleted from the database.</p>
            """
        
            email_response = send_confirmation_email(
                resend_api_key, 
                email_from, 
                email_to, 
                subject,
                message
            )
            print(f"Confirmation email sent successfully: {email_response}")
        
        except requests.RequestException as error:
            print(f"Confirmation email failed: {error}")


if __name__ == "__main__":
    main()