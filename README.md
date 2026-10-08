# Expense Tracker

Expense Tracker is a full-stack personal finance-awareness tool. It helps users record income and expenses, understand what they have left to spend each month, and build a habit of saving money.

The repository currently contains the working MVP for personal expense tracking. V2 extends that foundation in small, user-visible layers while keeping the basic tracker useful when AI is unavailable.

## V2 Direction

V2 adds:

- Complete income and expense history with fixed categories and optional spending context.
- Monthly cashflow, available balance, savings reserve, savings goals, and recurring commitments.
- Search, filters, comparisons, charts, and financial-planning views.
- An optional AI Companion for grounded answers and reviewable transaction or planning proposals.
- Assisted entry from natural-language text, receipt images, and voice input, always requiring user review before saving.

See the [V2 documentation](./docs/V2/README.md) for product context, architecture, implementation layers, and roadmap.

See the [V2 five-week roadmap](./docs/V2/roadmap.md) for the implementation sequence and the first AI Companion slice. The roadmap describes delivery order; the [product context](./docs/V2/context.md) and [shared architecture](./docs/V2/architecture.md) define the product and technical rules.

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

- Explore the current MVP implementation and test the live project
- Follow the transition from the MVP to V2
- Clone or fork the project as a starting point for your own finance tracker

## Tech Stack and V2 Implementation

Current stack:

- **Frontend:** React, Vite, JavaScript, React Router, Bootstrap
- **Backend:** Flask, SQLAlchemy, Flask-Migrate/Alembic, Gunicorn
- **API:** Flask JSON API
- **Database:** PostgreSQL
- **Authentication:** JWT
- **Deployment:** Vercel, Render, Supabase
- **Package management:** npm, Pipenv

Planned or under consideration for V2:

- **Frontend:** migrate the application to TypeScript and implement the complete V2 UI design
- **API documentation:** add OpenAPI documentation and Swagger UI
- **AI providers:** add a cloud AI provider and a local AI provider for assisted entry and the AI Companion; specific models are still to be decided
- **Containerization:** Dockerize the project if it fits the deployment and development workflow

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

See `docs/MVP/DEPLOYMENT.md` for additional configuration details.

### 4. Set up PostgreSQL and run migrations

Create a PostgreSQL database named `expense_tracker`, update `backend/.env` with its connection string and a local JWT secret, and run:

```bash
cd backend
pipenv run upgrade
```

The backend uses the locked Python dependencies from `backend/Pipfile.lock`.

### 5. Run the project

Backend:

```bash
cd backend
pipenv run start
```

Frontend:

```bash
cd frontend
npm run dev
```

Default local URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api`

Verify the backend with `http://localhost:5000/api/health`. For frontend checks, run `npm run lint` and `npm run build` from `frontend/`.

## Project Structure

```text
frontend/   React application
backend/    Flask API and database migrations
docs/       Project, API, deployment, and development documentation
```

For more information, see the documentation in `docs/`.
