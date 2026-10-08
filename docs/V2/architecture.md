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
- Each non-idempotent financial command, including transaction creation, reserve transfer, and proposal confirmation, requires a client-generated `Idempotency-Key`. The backend retains the key and its successful result for 24 hours; a repeat request with the same key returns that original result without creating another financial effect. An edit also includes the record's `updated_at` value. If it no longer matches the stored record, the backend returns `409 Conflict` and the frontend refreshes before the user retries.
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

AI-provider access must sit behind a provider adapter selected by deployment configuration. The adapter must support commercial providers and an OpenAI-compatible local endpoint such as LM Studio without exposing provider-specific types to services or routes. V2 starts with a per-user limit of 10 AI requests per 15 minutes, a 30-second provider timeout, and no automatic retry after a provider request has started. Provider errors return a safe, actionable error and do not block manual flows.

Action proposals are untrusted input. The application validates them again when the user confirms. Proposals need an operation type, target entity, affected fields, evidence/reference context, proposal version or timestamp, and an idempotency key or equivalent duplicate-submission protection.

## Shared financial vocabulary

The product uses **B/U/C** as the canonical spending-context model: **Bill**, **Usage**, and **Choice**. These are the only stored values for this field. Any expanded explanatory labels in the interface must map to these same values and must not create alternative API or database enums.

## Security and privacy

- Every query and mutation is scoped to the authenticated user.
- V2 uses a 24-hour JWT stored in browser local storage and sent in an `Authorization: Bearer` header. This is a deliberate simplicity trade-off: a successful cross-site-scripting attack can expose the token. Cookie authentication, refresh tokens, email verification, and general token denylisting are out of scope for V2.
- Passwords are never stored in plain text and use the existing Werkzeug password-hashing helpers. Password changes require the current password. Changing a password, soft-deleting an account, or disabling an account increments an account token version so existing JWTs are rejected immediately.
- Logout removes the JWT from the browser. Because V2 does not use cookie authentication, it does not require CSRF tokens. CORS must allow only the configured frontend origin.
- AI context must contain only data the user is authorized to view.
- Prompts, responses, and logs should avoid unnecessary sensitive raw data.
- Receipt images and voice recordings are private, transient request inputs. V2 accepts JPEG, PNG, and WebP images, plus MP3, WAV, and M4A audio, with a maximum upload size of 10 MB and a maximum audio duration of two minutes. The browser retains a selected file only until upload completes. The backend processes the multipart upload through private temporary storage or a controlled spool, forwards it to the configured provider, and deletes its temporary copy in a cleanup path whether the provider request succeeds or fails. V2 does not offer a media library or retain uploaded files for later review.
- The application cannot control an external provider's retention once it has received an input. A commercial provider may retain inputs according to its service terms and account configuration; a local provider such as LM Studio keeps processing within the configured local environment. A deployment may enable only providers whose data-handling terms are acceptable for this product.
- Users may soft-delete their account. A deleted account cannot authenticate or access private data. V2 does not include data export.
- Companion conversations, unconfirmed AI drafts, and action proposals are not persisted in the application database. The frontend holds them only for the active interaction; confirmation sends the proposed fields to the normal backend command, which validates them again. Application logs must not contain raw prompts, model responses, or uploaded-file contents.
- Confirmation endpoints must validate ownership again rather than trusting the proposal creator.
- Provider failures must not block manual entry or management flows.
- Unsupported or ambiguous actions must result in a clarification or safe refusal, not a guessed mutation.

## API conventions

Use the `/api/v2` prefix, authenticated routes for private data, consistent JSON error responses, ownership checks, and migration-backed schema changes. New endpoints should be thin transport layers that call services. Response shapes should distinguish recorded values, estimates, projections, and proposals.

- Collections use `page` and `page_size` query parameters, with a default page size of 25 and a maximum of 100. A collection response uses `data` for records and `meta` for pagination information.
- Dates use `YYYY-MM-DD`; timestamps use ISO 8601; and monetary amounts are decimal strings. For example, `GET /api/v2/transactions?month=2026-10&page=1` lists one month of transactions, and `POST /api/v2/transactions` returns `201 Created` after recalculation succeeds.
- Validation errors use the form `{"error":{"code":"validation_error","message":"Invalid transaction.","fields":{"amount":"Must be greater than zero."}}}`. A stale edit returns `409 Conflict`; authentication failures use `401`; ownership failures use `403`; and an exceeded request limit uses `429`.

## Deployment and operations

- V2 has local-development and production environments. Preview deployments are permitted only when they use isolated data and never production credentials or database access.
- Production migrations run as an explicit release step before the new backend version serves traffic. Corrections use new forward migrations rather than automatic rollback against production data.
- `GET /api/v2/health` provides a minimal health check without returning personal or financial data.
- V2 relies on the configured managed PostgreSQL provider's backup capability. It does not implement a separate application-level backup system.

## Testing expectations

Each layer needs service tests for formulas and edge cases, API tests for ownership and validation, and frontend verification for loading, empty, error, confirmation, and manual fallback states. CI must also run the frontend production build and a migration upgrade test against a fresh PostgreSQL database. Companion tests use fixed evidence fixtures and mocked provider responses; tests must never call a live AI provider.
