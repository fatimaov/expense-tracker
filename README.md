# Expense Tracker

Expense Tracker is a full-stack personal finance-awareness tool. It helps users record income and expenses, understand what they have left to spend each month, and build a habit of saving money.

The repository currently contains the working MVP for personal expense tracking. V2 is the next product direction and is being defined on top of that foundation.

## V2 Direction

V2 expands the MVP into a broader personal finance tool organized around calendar months. The core experience helps users record income and expenses, understand their monthly cashflow and balances, and review their transaction history.

Users can add savings goals, recurring commitments, richer spending context, and an optional AI Companion as they need them. They can also create transaction drafts from natural-language input, receipt images, or voice input, but every AI-generated draft must be reviewed and approved before it is saved. The product remains useful for basic tracking without requiring users to use every capability.

The existing MVP behavior remains part of V2: users can register, log in, and manage their own expenses with a responsive interface.

See the [V2 documentation](./docs/V2/README.md) for product context, architecture, implementation layers, and roadmap.

See the [V2 five-week roadmap](./docs/V2/roadmap.md) for the implementation sequence and first AI Companion slice.

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
