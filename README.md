# Expense Tracker

Expense Tracker is a full-stack personal expense tracker built as a live demo and a reusable starter project.

You can explore the codebase, test the deployed app, or clone the repository and adapt it with your own database, environment variables, and deployment setup.

## Features
- User registration, login, and logout
- Create, edit, and delete expenses
- Track amount, title, date, category, and optional notes
- View expenses ordered by newest first
- User-specific expense data
- Mobile-first responsive interface

## Live Demo

* App: [expense-tracker-liart-three-87.vercel.app](https://expense-tracker-liart-three-87.vercel.app/)
* Backend health check: [expense-tracker-api-8aad.onrender.com/api/health](https://expense-tracker-api-8aad.onrender.com/api/health)

The backend runs on Render's free tier, so the first request may take 30–60 seconds.

### Demo Account

* Email: `demo@email.com`
* Password: `12345678`

### Public Demo Maintenance

This repository includes the scheduled GitHub Actions workflow in `.github/workflows/demo-reset.yml`. It resets the public demo data to keep the shared demo environment clean and prevent unwanted data from being left in the demo account. The workflow:

* Deletes all users except the demo account.
* Relies on database cascade deletes to remove related expenses.
* Restores the default demo expense records.

This is intentional because the project is a public demo environment and should not store real user financial data.

⚠️ **Important for contributors:** If you clone this repository and connect it to your own database, disable or remove this workflow unless you understand that it deletes user data. It is intended only for the public demo environment.

### Supabase Free Tier Keep-Alive

This repository also includes an optional GitHub Actions workflow in `.github/workflows/supabase-keep-alive.yml` for developers who clone the project and deploy their own Supabase database. Supabase Free Tier projects with no activity for several days may be paused, so the workflow provides a simple maintenance mechanism by connecting directly to Supabase and creating/inserting a maintenance record.

The workflow currently runs manually with `workflow_dispatch`. To enable automatic execution, uncomment the `schedule` section in the YAML file and configure the desired cron schedule. Review and adapt the workflow, including its database secret and schedule, to your deployment setup. It is not part of the application business logic; it is only an optional database maintenance helper.

## Project Purpose

This repository is public so you can:

* Explore the implementation and test the live project.
* Clone or fork it and use it as a base for your own expense tracker.
* Follow future improvements and new versions of the project.

## Tech Stack

* **Frontend:** React, Vite, React Router, Bootstrap
* **Backend:** Flask, SQLAlchemy, Flask-Migrate/Alembic, Gunicorn
* **Database:** PostgreSQL
* **Authentication:** JWT
* **Deployment:** Vercel, Render, Supabase
* **Package management:** npm, Pipenv

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

Create local env files from the provided examples:

```text
backend/.env.example  →  backend/.env
frontend/.env.example →  frontend/.env
```

See `docs/DEPLOYMENT.md` for additional configuration details.

### 4. Set up PostgreSQL

Create a PostgreSQL database and update the backend environment variables, then run:

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

* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:5000/api`

## Project Structure

```text
frontend/   React application
backend/    Flask API and database migrations
docs/       Project, API, deployment, and development documentation
```

For more details, see the documentation in `docs/`.
