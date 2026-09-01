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

# Get the environment variables
def get_required_env(name):
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value

def main():
    print("Starting Supabase keep-alive workflow...")

    database_url = get_required_env("SUPABASE_DATABASE_URL")
    gmail_address = get_required_env("GMAIL_ADDRESS")
    gmail_app_password = get_required_env("GMAIL_APP_PASSWORD")
    email_to = get_required_env("EMAIL_TO")

    print("Environment variables loaded successfully.")

if __name__ == "__main__":
    main()


