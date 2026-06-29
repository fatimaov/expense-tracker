# Deployment Guide

This guide covers local development and the production architecture: a React
frontend on Vercel, a Flask API on Render, and PostgreSQL on Supabase. Run
commands from the repository root unless a section says otherwise.

## 1. Prerequisites

- Python `3.13.0` (defined in `backend/.python-version`)
- Node.js `20.19+` or `22.12+` (required by Vite 8)
- PostgreSQL
- Pipenv
- npm (included with Node.js)

Confirm the tools are available:

```bash
python --version
node --version
npm --version
pipenv --version
psql --version
```

## 2. Environment Variables

Never commit real `.env` files or secrets. Use the tracked `.env.example` files
as templates.

### Backend

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes | Secret used to sign JWT access tokens |
| `CORS_ORIGINS` | Yes in production | Comma-separated allowed frontend origins |
| `FLASK_ENV` | No | Defaults to `production` |
| `FLASK_DEBUG` | No | Use `1` locally and `0` in production |

Local `backend/.env` example:

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
JWT_SECRET_KEY=replace-with-a-local-secret
FLASK_ENV=development
FLASK_DEBUG=1
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Production backend example:

```dotenv
DATABASE_URL=postgresql://postgres.PROJECT_REF:DB_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
JWT_SECRET_KEY=replace-with-a-long-random-production-secret
FLASK_ENV=production
FLASK_DEBUG=0
CORS_ORIGINS=https://expense-tracker-liart-three-87.vercel.app
```

Copy the Session Pooler connection string from **Supabase Dashboard > Connect**
and replace its password placeholder with the database password. Keep the real
connection string and password only in Render environment variables.

### Frontend

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Yes | Backend base URL including the `/api` prefix |

Local `frontend/.env` example:

```dotenv
VITE_API_BASE_URL=http://localhost:5000/api
```

Vercel example:

```dotenv
VITE_API_BASE_URL=https://expense-tracker-api-8aad.onrender.com/api
```

Vite embeds this value at build time. Redeploy the frontend after changing it.

## 3. Local Development Setup

### Backend and database

Create the PostgreSQL database with a role that matches `DATABASE_URL`:

```bash
createdb expense_tracker
```

Then install the locked dependencies and configure the environment:

```bash
cd backend
pipenv install --deploy
cp .env.example .env
pipenv run flask --app run:app db upgrade
pipenv run python run.py
```

In PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

The API runs at `http://localhost:5000`. Verify it at
`http://localhost:5000/api/health`.

If `createdb` is unavailable, create a database named `expense_tracker` using
`psql` or a PostgreSQL administration tool, then update `DATABASE_URL`.

### Frontend

In a second terminal:

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

In PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

Open the URL printed by Vite, normally `http://localhost:5173`.

## 4. Database Migrations

Run migration commands from `backend`. Flask-Migrate uses Alembic underneath,
and generated revisions are stored in `backend/migrations/versions`.

Create a migration after changing SQLAlchemy models:

```bash
pipenv run flask --app run:app db migrate -m "describe the change"
```

Review the generated migration before applying it. Apply pending migrations
locally with:

```bash
pipenv run flask --app run:app db upgrade
```

Apply migrations in production from the Render Shell. The command connects to
Supabase through the Render service's `DATABASE_URL`:

```bash
pipenv run flask --app run:app db upgrade
```

Run the production command after the first deployment and whenever new
migration files are deployed.

## 5. Production Database on Supabase

Supabase provides the managed PostgreSQL database while authentication and
application APIs remain in Flask. This keeps the existing SQLAlchemy and
Alembic architecture unchanged while separating database hosting from the
Render web service.

### Direct Connection and Session Pooler

| Connection | Host pattern | Use case |
| --- | --- | --- |
| Direct Connection | `db.PROJECT_REF.supabase.co:5432` | IPv6 environments or projects with the Supabase IPv4 add-on |
| Session Pooler | `aws-0-REGION.pooler.supabase.com:5432` | Persistent application servers that need an IPv4-compatible endpoint |

Supabase Direct Connection uses IPv6 by default. The Render service therefore
uses the Session Pooler URL, which provides IPv4 compatibility and preserves
session-style PostgreSQL behavior suitable for Gunicorn, SQLAlchemy, `psql`,
and Alembic migrations.

This deployment uses Session Pooler mode on port `5432`, not Transaction
Pooler mode on port `6543`.

### Configure the database

1. Create a Supabase project and save its database password securely.
2. Open **Connect** in the Supabase dashboard.
3. Select and copy the **Session Pooler** connection string.
4. Replace the password placeholder and set the complete URL as `DATABASE_URL`
   on the Render Web Service.

Expected format:

```dotenv
DATABASE_URL=postgresql://postgres.PROJECT_REF:DB_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

Percent-encode special characters in the password when placing it inside a
URL.

Connect manually with the same Session Pooler URL:

```bash
psql "postgresql://postgres.PROJECT_REF:DB_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres"
```

Apply the existing schema from the Render Shell after configuring
`DATABASE_URL`:

```bash
pipenv run flask --app run:app db upgrade
```

## 6. Backend Deployment on Render

Create a Render Web Service from the repository with:

- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `pip install pipenv && pipenv install --deploy`
- Start Command: `pipenv run gunicorn run:app`
- Health Check Path: `/api/health`

The production entry point is the `app` object in `backend/run.py`. Render
supplies Gunicorn's bind configuration for the service port.

Set these environment variables:

- `DATABASE_URL`: Supabase Session Pooler connection string
- `JWT_SECRET_KEY`: long, random production secret
- `CORS_ORIGINS`: `https://expense-tracker-liart-three-87.vercel.app`
- `FLASK_ENV=production` (optional because it is the default)
- `FLASK_DEBUG=0` (optional but recommended explicitly)

For the first deployment:

1. Deploy the web service.
2. Open its Render Shell.
3. Run `pipenv run flask --app run:app db upgrade`.
4. Verify
   `https://expense-tracker-api-8aad.onrender.com/api/health`.

Run the migration command again after deployments that contain new migration
files.

## 7. Frontend Deployment on Vercel

Import the same repository into Vercel and configure:

- Root Directory: `frontend`
- Framework Preset: Vite
- Install Command: `npm ci`
- Build Command: `npm run build`
- Output Directory: `dist`

Add this production environment variable before building:

```dotenv
VITE_API_BASE_URL=https://expense-tracker-api-8aad.onrender.com/api
```

The repository includes `frontend/vercel.json` to support React Router URLs on
refresh and direct access:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "redirects": [
    {
      "source": "/login",
      "destination": "/",
      "permanent": false
    }
  ],
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

The application uses `/` as its login route, so Vercel redirects `/login` to
`/`. The rewrite then serves `index.html` for all application routes and lets
React Router select the correct page in the browser.

After Vercel assigns the frontend URL, set the Render service's
`CORS_ORIGINS` to that exact origin and redeploy the backend. Preview deployments
use different origins; add them explicitly as comma-separated values only when
they need API access.

## 8. Production Deployment Workflow

1. Create the Supabase project and copy its Session Pooler URL.
2. Create the Render Web Service and configure `DATABASE_URL`,
   `JWT_SECRET_KEY`, and `CORS_ORIGINS`.
3. Deploy the backend and apply Alembic migrations from the Render Shell.
4. Verify the Render health endpoint.
5. Deploy the Vercel frontend with `VITE_API_BASE_URL` pointing to Render.
6. Set Render's `CORS_ORIGINS` to the final Vercel origin and redeploy it.
7. Complete the smoke test below.

## 9. Post-Deployment Smoke Test

1. Open
   `https://expense-tracker-api-8aad.onrender.com/api/health`; expect an `ok`
   response.
2. Open `https://expense-tracker-liart-three-87.vercel.app/` and register a new
   account.
3. Log in if registration does not leave the session active.
4. Create an expense and verify it appears in the list.
5. Edit the expense and verify the changes.
6. Delete the expense and verify it disappears.
7. Log out and confirm protected pages return to login.
8. Log in again and confirm saved expenses persist.
9. Refresh `/register`, `/expenses`, `/expenses/new`, and an edit URL to verify
   SPA routing. Open `/login` and confirm it redirects to `/`.

## 10. Troubleshooting

### CORS errors

- Confirm `CORS_ORIGINS` exactly matches the Vercel origin, including `https`.
- Do not include paths such as `/api` in `CORS_ORIGINS`.
- Redeploy the backend after changing Render environment variables.

### Missing tables or columns

Run from the Render Shell:

```bash
pipenv run flask --app run:app db upgrade
```

Confirm that `DATABASE_URL` points to the intended database.

### Database connection errors

- Confirm Render uses the Supabase Session Pooler URL on port `5432`.
- Verify the Supabase project is active and the database password is correct.
- Percent-encode special characters in the password inside `DATABASE_URL`.
- Check that local PostgreSQL is running and the local credentials are correct.

### Environment variable issues

- Confirm variable names match exactly and contain no accidental quotes.
- Ensure `VITE_API_BASE_URL` includes `/api`.
- Redeploy Vercel after changing a `VITE_` variable.
- Keep `JWT_SECRET_KEY` stable; changing it invalidates existing tokens.

### React Router pages return 404 on refresh

Confirm `frontend/vercel.json` is included in the deployment and that Vercel's
Root Directory is `frontend`, then redeploy.
