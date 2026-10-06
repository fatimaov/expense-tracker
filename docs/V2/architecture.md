# V2 Shared Architecture

This document contains technical decisions shared by all implementation layers. Layer-specific architecture belongs in the relevant file under `layers/`.

## Current stack

- Frontend: React, Vite, JavaScript, React Router, Bootstrap, and shared CSS.
- Backend: Python, Flask, SQLAlchemy, Flask-Migrate/Alembic, and Gunicorn.
- Database: PostgreSQL.
- Authentication: JWT.
- Deployment: Vercel for the frontend, Render for the backend, and Supabase PostgreSQL.

The existing MVP structure is the starting point. TypeScript, OpenAPI/Swagger, additional AI providers, and containerization remain possible V2 decisions and must be evaluated before adoption.

## Repository boundaries

- `frontend/` contains routes, views, components, client services, auth state, and presentation logic.
- `backend/app/models/` contains persisted entities and relationships.
- `backend/app/routes/` contains HTTP transport and authentication boundaries.
- `backend/app/services/` contains business rules, calculations, validation, and orchestration.
- `backend/app/serializers/` contains API response shaping.
- `backend/migrations/` contains schema changes.
- `docs/V2/layers/` is the implementation reference, not runtime code.

Business calculations belong in backend services and should be exposed to the frontend through stable API responses. The frontend should not independently reimplement financial rules.

## Layer dependency rule

Layers are additive. A later layer may consume models, services, API contracts, and UI patterns from an earlier layer, but it must not silently change an earlier layer's meaning. Changes that affect previous calculations require explicit compatibility review, tests, and migration planning.

Every layer file must state:

- what it depends on;
- what it adds to the data model and services;
- what it exposes to the frontend;
- what Companion evidence and actions it adds; and
- how previous manual flows continue to work.

## Deterministic calculation boundary

The backend calculation services produce structured evidence containing the selected period, source records or aggregates, formulas, current-state values, assumptions, exclusions, and data-quality warnings. The Companion receives this evidence and explains it. The model must not query the database directly or independently calculate financial values.

## Companion integration boundary

The Companion integration should have three stages:

1. Authenticate and authorize the user.
2. Build a layer-specific evidence/context object from deterministic services and permitted records.
3. Return either a grounded response or a typed action proposal for the normal application flow.

Action proposals are untrusted input. The application validates them again when the user confirms. Proposals need an operation type, target entity, affected fields, evidence/reference context, proposal version or timestamp, and an idempotency key or equivalent duplicate-submission protection.

## Security and privacy

- Every query and mutation is scoped to the authenticated user.
- AI context must contain only data the user is authorized to view.
- Prompts, responses, and logs should avoid unnecessary sensitive raw data.
- Confirmation endpoints must validate ownership again rather than trusting the proposal creator.
- Provider failures must not block manual entry or management flows.
- Unsupported or ambiguous actions must result in a clarification or safe refusal, not a guessed mutation.

## API conventions

Use the existing `/api` prefix, authenticated routes for private data, consistent JSON error responses, ownership checks, and migration-backed schema changes. New endpoints should be thin transport layers that call services. Response shapes should distinguish recorded values, estimates, projections, and proposals.

## Testing expectations

Each layer needs service tests for formulas and edge cases, API tests for ownership and validation, and frontend verification for loading, empty, error, confirmation, and manual fallback states. Companion tests should use fixed evidence fixtures so answers and proposals can be evaluated without relying on live model behaviour alone.
