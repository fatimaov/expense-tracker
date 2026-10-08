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

## Financial data, time, and lifecycle

- V2 supports one currency only: EUR. Amounts use fixed-precision decimal values, never binary floating-point values. Backend services use Python `Decimal`; PostgreSQL stores amounts as `NUMERIC(14,2)`; and API payloads represent amounts as decimal strings such as `"12.34"`.
- V2 uses the fixed IANA timezone `Europe/Madrid` for current-month selection, calendar-month boundaries, due dates, and recurring-occurrence generation. It observes daylight-saving time automatically. V2 does not use device location and does not let users change this timezone.
- A transaction belongs to the calendar month determined by its transaction date, even when the transaction is added or changed later.
- Ordinary transactions are soft-deleted. Deletion must preserve the historical audit record and trigger the same recalculation path as an edit.
- Each recurring occurrence is a persisted record with a unique `(recurring_commitment_id, scheduled_date)` pair and one of the states `expected`, `generated`, or `suppressed`. Deleting a generated or upcoming occurrence changes it to `suppressed`; a later occurrence-generation run must not recreate it, while future occurrences continue normally.
- A financial mutation, including a create, edit, soft delete, transfer, or recurring-occurrence change, must trigger deterministic recalculation of the affected period and all later derived balances, including Money left to spend and goal allocations. The backend commits the record change and recalculation as one workflow, then returns `201 Created` or `200 OK` with the affected period range. The frontend treats that successful response as the signal to invalidate its relevant cached financial queries and refetch the normal dashboard and history responses. It never derives replacement financial values itself. Real-time server push is not required for V2.
- The backend, not the frontend clock, determines whether the active calendar month has advanced. Before serving financial state or applying a financial mutation, a backend service must ensure that prior months have been closed. After an inactive period, it processes every elapsed month in chronological order, first generating due recurring occurrences and then applying month-close calculations.
- Month close persists a closure record for the calendar month and its derived calculations. Closing must be atomic and idempotent: repeating the check cannot duplicate allocations, balance movements, or generated occurrences. A closed month is not reopened. Users may create, edit, or soft-delete transactions in a closed month after receiving a recalculation warning; the backend recalculates and updates that month's derived close values and every following balance, while retaining an audit trail of the correction.

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

Layer 5 may add a curated external-knowledge retrieval step for general financial education and healthy financial habits. Retrieval-augmented generation is not part of Layer 1 AI-assisted transaction entry: that flow uses the user's supplied input and permitted application data to prepare a reviewable draft. Layer 5 retrieval remains separate from application evidence, is identifiable in the response, and never overrides deterministic application calculations. Live account data, market data, and unreviewed web content are outside this boundary until a later decision defines their source, freshness, privacy, and safety requirements.

Action proposals are untrusted input. The application validates them again when the user confirms. Proposals need an operation type, target entity, affected fields, evidence/reference context, proposal version or timestamp, and an idempotency key or equivalent duplicate-submission protection.

## Shared financial vocabulary

The product uses **B/U/C** as the canonical spending-context model: **Bill**, **Usage**, and **Choice**. These are the only stored values for this field. Any expanded explanatory labels in the interface must map to these same values and must not create alternative API or database enums.

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
