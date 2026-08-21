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

`.github/workflows/demo-reset.yml` resets the public demo data on a schedule to keep the shared environment clean and prevent real financial data from being stored.

The workflow:

- Deletes all users except the demo account
- Uses database cascade deletes to remove related expenses
- Restores the default demo expenses

⚠️ **Important for contributors:** If you connect this project to your own database, disable or remove this workflow unless you understand that it deletes user data. It is intended only for the public demo environment.

### Supabase Free-Tier Keep-Alive

`.github/workflows/supabase-keep-alive.yml` is an optional maintenance workflow for developers using their own Supabase database. Because inactive Supabase Free Tier projects may be paused after several days, the workflow connects to Supabase with `psql`, creates the `keep_alive_logs` table if it does not already exist, and inserts a maintenance record.

It can be started manually through `workflow_dispatch` and runs automatically every day at 08:00 and 19:00 UTC. The workflow requires a GitHub Actions secret named `SUPABASE_DATABASE_URL` containing the PostgreSQL connection string for your Supabase database. Review and adapt the workflow, database secret, and schedule for your deployment. This is a database maintenance helper, not application business logic.

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
