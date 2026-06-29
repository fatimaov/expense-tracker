# Expense Tracker

A simple, mobile-first web app for recording and reviewing personal expenses.

## Features

- Email and password authentication
- Create, view, edit, and delete expenses
- Expenses ordered from newest to oldest
- Fixed categories: Transport, Accommodation, Food, Activities, and Other
- Private expense data for each user

## Tech Stack

- React, Vite, React Router, and Bootstrap
- Flask, SQLAlchemy, and Flask-Migrate
- PostgreSQL
- JSON Web Tokens (JWT)

## Render Backend Deployment

Create a Render **Web Service** from this repository with these settings:

- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `pip install pipenv && pipenv install --deploy`
- Start Command: `pipenv run gunicorn run:app`
- Health Check Path: `/api/health`

The `run:app` target uses the Flask application created in `backend/run.py`.
Render supplies the Gunicorn bind configuration for the service port.

Configure these backend environment variables in Render:

- `DATABASE_URL`: the Render PostgreSQL connection string
- `JWT_SECRET_KEY`: a long, random secret value
- `CORS_ORIGINS`: the deployed frontend origin, for example
  `https://your-app.vercel.app`

`FLASK_ENV` defaults to `production`, and `FLASK_DEBUG` should remain unset or
set to `0` in production.

After the first deployment, and whenever a new migration is added, run this
command from the Render Shell:

```bash
pipenv run flask --app run:app db upgrade
```
