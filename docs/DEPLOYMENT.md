# Deployment Guide

This guide covers local development and production deployment of the Flask API
to Render and the React frontend to Vercel. Run commands from the repository
root unless a section says otherwise.

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

Render example:

```dotenv
DATABASE_URL=postgresql://render-user:password@render-host/expense_tracker
JWT_SECRET_KEY=replace-with-a-long-random-production-secret
FLASK_ENV=production
FLASK_DEBUG=0
CORS_ORIGINS=https://your-app.vercel.app
```

Use the internal connection string supplied by Render PostgreSQL rather than
typing `DATABASE_URL` manually.

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
VITE_API_BASE_URL=https://your-api.onrender.com/api
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

Run migration commands from `backend`.

Create a migration after changing SQLAlchemy models:

```bash
pipenv run flask --app run:app db migrate -m "describe the change"
```

Review the generated migration before applying it. Apply pending migrations
locally with:

```bash
pipenv run flask --app run:app db upgrade
```

Apply migrations in production from the Render Shell:

```bash
pipenv run flask --app run:app db upgrade
```

Run the production command after the first deployment and whenever new
migration files are deployed.

## 5. Backend Deployment on Render

### PostgreSQL

1. Create a Render PostgreSQL database.
2. Keep the database and web service in the same region when possible.
3. Copy its internal connection string into the web service's `DATABASE_URL`.

### Web service

Create a Render Web Service from the repository with:

- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `pip install pipenv && pipenv install --deploy`
- Start Command: `pipenv run gunicorn run:app`
- Health Check Path: `/api/health`

The production entry point is the `app` object in `backend/run.py`. Render
supplies Gunicorn's bind configuration for the service port.

Set these environment variables:

- `DATABASE_URL`: Render PostgreSQL internal connection string
- `JWT_SECRET_KEY`: long, random production secret
- `CORS_ORIGINS`: deployed Vercel frontend origin without a trailing slash
- `FLASK_ENV=production` (optional because it is the default)
- `FLASK_DEBUG=0` (optional but recommended explicitly)

For the first deployment:

1. Deploy the web service.
2. Open its Render Shell.
3. Run `pipenv run flask --app run:app db upgrade`.
4. Verify `https://your-api.onrender.com/api/health`.

Run the migration command again after deployments that contain new migration
files.

## 6. Frontend Deployment on Vercel

Import the same repository into Vercel and configure:

- Root Directory: `frontend`
- Framework Preset: Vite
- Install Command: `npm ci`
- Build Command: `npm run build`
- Output Directory: `dist`

Add this production environment variable before building:

```dotenv
VITE_API_BASE_URL=https://your-api.onrender.com/api
```

To support React Router URLs on refresh, create `frontend/vercel.json` with:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

After Vercel assigns the frontend URL, set the Render service's
`CORS_ORIGINS` to that exact origin and redeploy the backend. Preview deployments
use different origins; add them explicitly as comma-separated values only when
they need API access.

## 7. Post-Deployment Smoke Test

1. Open `https://your-api.onrender.com/api/health`; expect an `ok` response.
2. Open the Vercel frontend and register a new account.
3. Log in if registration does not leave the session active.
4. Create an expense and verify it appears in the list.
5. Edit the expense and verify the changes.
6. Delete the expense and verify it disappears.
7. Log out and confirm protected pages return to login.
8. Log in again and confirm saved expenses persist.
9. Refresh `/expenses`, `/expenses/new`, and an edit URL to verify SPA routing.

## 8. Troubleshooting

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

- Use Render's internal PostgreSQL connection string for the Render service.
- Confirm the database is available and in the expected region.
- Check that local PostgreSQL is running and the local credentials are correct.

### Environment variable issues

- Confirm variable names match exactly and contain no accidental quotes.
- Ensure `VITE_API_BASE_URL` includes `/api`.
- Redeploy Vercel after changing a `VITE_` variable.
- Keep `JWT_SECRET_KEY` stable; changing it invalidates existing tokens.

### React Router pages return 404 on refresh

Add the SPA rewrite shown in the Vercel section as `frontend/vercel.json`, then
redeploy the frontend.
