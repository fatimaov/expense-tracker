# Expense Tracker

## Overview

Expense Tracker is a mobile-first full-stack application for securely recording
and reviewing personal expenses. The MVP provides authentication, private
per-user data, fixed expense categories, and complete expense CRUD workflows.

## Live Demo

- Frontend: [expense-tracker-liart-three-87.vercel.app](https://expense-tracker-liart-three-87.vercel.app/)
- Backend health check: [expense-tracker-api-8aad.onrender.com/api/health](https://expense-tracker-api-8aad.onrender.com/api/health)

## Features

- Email and password registration, login, and logout
- JWT-based authentication with protected frontend routes and API endpoints
- Create, view, edit, and permanently delete expenses
- Private expense data scoped to the authenticated user
- Expenses ordered from newest to oldest
- Fixed categories: Transport, Accommodation, Food, Activities, and Other
- Optional notes, loading and error feedback, and an empty-state call to action
- Responsive Bootstrap layout for mobile and desktop

## Tech Stack

- Frontend: React, Vite, React Router, Bootstrap
- Backend: Flask, SQLAlchemy, Flask-Migrate/Alembic, Gunicorn
- Database: Supabase PostgreSQL
- Authentication: JSON Web Tokens
- Hosting: Vercel, Render Web Service, Supabase
- Dependency management: npm and Pipenv

## Project Structure

```text
expense-tracker/
├── backend/
│   ├── app/              # Models, routes, services, serializers, and config
│   ├── migrations/       # Alembic database migrations
│   ├── Pipfile           # Python dependencies
│   └── run.py            # Flask and Gunicorn entry point
├── frontend/
│   ├── src/              # Pages, components, context, services, and router
│   └── vercel.json       # React Router SPA rewrites
└── docs/                 # Product, API, roadmap, and deployment documentation
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for local setup, environment
variables, migrations, production deployment, and smoke testing.

## Current Architecture

```text
Browser
  -> Vercel (React + Vite frontend)
  -> Render (Flask API served by Gunicorn)
  -> Supabase PostgreSQL (Session Pooler)
```

## Current Status

The MVP is deployed and functional in production. Registration, authentication,
expense CRUD, data persistence, responsive layout, client-side routing, and
hosting integration are working end to end.

## Future Improvements

- Tags for grouping expenses by trips or events
- Spending analytics and reports
- Budgets and spending limits
- Bank or card transaction imports
- Receipt scanning and assisted expense entry
