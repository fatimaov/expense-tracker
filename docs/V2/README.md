# Expense Tracker V2 Documentation

This folder is the working reference for implementing V2. It is intentionally small and organized around the way the product is built.

## Document authority

Use the active GitHub issue and its acceptance criteria to determine the requested work. Use the target layer file for feature-specific behaviour, `context.md` for shared product rules, and `architecture.md` for shared technical rules. The roadmap defines delivery order, not feature behaviour. Treat the PRD as background unless it has been reconciled with these documents. If two sources conflict, raise the conflict and update the applicable source of truth before implementing a new interpretation.

## Reading order for implementation

1. Read [context](./context.md) for product rules, terminology, boundaries, and AI behaviour.
2. Read [architecture](./architecture.md) for shared technical decisions and conventions.
3. Read [roadmap](./roadmap.md) for implementation order and current delivery goals.
4. Read the target layer file in `layers/`.
5. Read any dependency layers named in the target layer's `Depends on` section.
6. Inspect the existing code before changing it, and keep the layer's acceptance criteria visible while implementing.

## Current code baseline

V2 extends the working MVP; do not assume its current implementation already follows every V2 decision.

- The frontend starts at `frontend/src/main.jsx`, with routes in `frontend/src/router/`, API client code in `frontend/src/services/`, and client configuration in `frontend/src/config.js`.
- The backend application starts at `backend/run.py`. Models, routes, services, serializers, and Alembic migrations follow the boundaries described in `architecture.md`.
- Environment-variable templates are `frontend/.env.example` and `backend/.env.example`. The root [README](../../README.md) documents dependency installation, PostgreSQL setup, and local start commands.
- Frontend commands are defined in `frontend/package.json`: `npm run dev`, `npm run build`, and `npm run lint`. Backend commands are defined in `backend/Pipfile`, including `pipenv run start` and Alembic migration commands.
- The MVP does not establish a visible automated test suite or test command. A V2 layer that adds tests must document its test command and run it; the shared V2 test expectations are in `architecture.md`.
- The current frontend environment example still points at the MVP `/api` prefix. V2 endpoints use `/api/v2`; update the configuration as part of the relevant V2 API migration rather than assuming the MVP default is correct.

## Documents

### Shared context

- [context.md](./context.md) — product direction, scope, terminology, AI rules, and decisions that apply to every layer.
- [architecture.md](./architecture.md) — shared stack, project boundaries, security, AI integration, and data/API conventions.

### Implementation layers

- [Layer 1 — Transaction foundation](./layers/01-transaction-foundation.md)
- [Layer 2 — Cashflow and reserve](./layers/02-cashflow-and-reserve.md)
- [Layer 3 — Analytics and awareness](./layers/03-analytics-and-awareness.md)
- [Layer 4 — Financial planning](./layers/04-financial-planning.md)
- [Layer 5 — Companion expansion](./layers/05-companion-expansion.md)

The layer files are implementation briefs. Each one describes the user value, included core features, dependencies, data and calculations, manual flows, Companion capabilities, confirmation rules, and acceptance criteria for that layer.
