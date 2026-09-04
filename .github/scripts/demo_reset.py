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
