# Expense Tracker

Expense Tracker is a full-stack personal expense tracker and reusable starter project. Explore the code, try the live demo, or clone and adapt it with your own database, environment variables, and deployment setup.

## Features

- Register, log in, and log out
- Create, edit, and delete expenses
- Track amount, title, date, category, and optional notes
- View expenses from newest to oldest
- Keep expense data separate for each user
- Use a mobile-first responsive interface

## Live Demo

- App: [expense-tracker-liart-three-87.vercel.app](https://expense-tracker-liart-three-87.vercel.app/)
- API health check: [expense-tracker-api-8aad.onrender.com/api/health](https://expense-tracker-api-8aad.onrender.com/api/health)

The backend runs on Render's free tier, so its first request may take 30–60 seconds.

### Demo Account

- Email: `demo@email.com`
- Password: `12345678`

### Public Demo Maintenance

`.github/workflows/demo-reset.yml` resets the public demo database every week. It runs `.github/scripts/demo_reset.py` using dependencies from `.github/scripts/requirements.txt`.

The workflow:

- Deletes all users except the demo account
- Uses database cascade deletes to remove related expenses
- Restores the default demo expenses

⚠️ **Important for contributors:** If you connect this project to your own database, disable or remove this workflow unless you understand that it deletes user data. It is intended only for the public demo environment.

### Supabase Free-Tier Maintenance

The optional `.github/workflows/supabase-keep-alive.yml` workflow is for personal Supabase databases. It runs twice daily and uses `.github/scripts/keep_alive.py` to create `keep_alive_logs` if needed, add a keep-alive record, and send a confirmation email through [Resend](https://resend.com). It uses dependencies from `.github/scripts/requirements.txt`.

`.github/workflows/keep-alive-cleanup.yml` runs monthly and uses `.github/scripts/keep_alive_cleanup.py` to delete keep-alive logs and send a confirmation email. Use `DRY_RUN=false` for normal cleanup and `true` when testing or adjusting the script.

Required GitHub Actions secrets are `SUPABASE_DATABASE_URL`, `RESEND_API_KEY`, `EMAIL_FROM`, and `EMAIL_TO`; the cleanup workflow also requires `DRY_RUN`.

## Project Purpose

This public repository lets you:

- Explore the implementation and test the live project
- Clone or fork it as a starting point for your own expense tracker
- Follow future improvements and releases

## Tech Stack

- **Frontend:** React, Vite, React Router, Bootstrap
- **Backend:** Flask, SQLAlchemy, Flask-Migrate/Alembic, Gunicorn
- **Database:** PostgreSQL
- **Authentication:** JWT
- **Deployment:** Vercel, Render, Supabase
- **Package management:** npm, Pipenv

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd expense-tracker
```

### 2. Install dependencies

Backend:

```bash
cd backend
pipenv install --deploy
```

Frontend:

```bash
cd frontend
npm install
```

### 3. Configure environment variables

Copy the example files:

```text
backend/.env.example  →  backend/.env
frontend/.env.example →  frontend/.env
```

See `docs/DEPLOYMENT.md` for additional configuration details.

### 4. Set up PostgreSQL

Create a PostgreSQL database, update the backend environment variables, and run:

```bash
cd backend
pipenv run flask --app run:app db upgrade
```

### 5. Run the project

Backend:

```bash
cd backend
pipenv run python run.py
```

Frontend:

```bash
cd frontend
npm run dev
```

Default local URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api`

## Project Structure

```text
frontend/   React application
backend/    Flask API and database migrations
docs/       Project, API, deployment, and development documentation
```

For more information, see the documentation in `docs/`.
