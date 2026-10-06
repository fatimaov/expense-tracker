# Layer 1 — Transaction Foundation

## Purpose and user value

Give users a reliable transaction history and several ways to record or correct income and one-time expenses. Introduce the first useful Companion so users can ask about their history and prepare transaction changes without losing control.

## Scope

## Included core features

- Income and one-time expense CRUD for current and past months.
- Transaction history search and record selection.
- General expense and income categories, including add and deactivate management.
- Optional B/U/C classification and Need/Love/Like/Want reflective context on expenses.
- Manual entry.
- Natural-language, receipt-image, and voice-entry boundaries with reviewable drafts.
- Companion questions and confirmed transaction proposals.

## Depends on

- Existing authentication, user ownership, expense model, routes, services, and frontend MVP flows.
- Shared rules in [context](../context.md) and [architecture](../architecture.md).

## Existing capabilities used

## Data model

Layer 1 establishes the transaction contract used by every later layer. Each record has amount, category, date, and optional notes. Expenses may also have one B/U/C classification and one reflective context tag. These fields are optional and never inferred automatically.

Categories can be added or deactivated without making historical records unreadable. Deactivated categories are not offered for new records.

## Backend

- Add or adapt income and transaction persistence while preserving MVP expense behaviour.
- Keep validation and ownership checks in backend services.
- Provide deterministic period and category summary services.
- Add stable API responses for records, summaries, and typed proposals.
- Keep AI provider calls behind an application service boundary.

## Frontend

## Business rules and calculations

## Manual user flows

## Companion capabilities

The Companion can answer what was spent in a period, find records matching a description, summarize a category, and identify records missing optional context.

## AI action proposals and confirmation

Entry proposals must preserve uncertainty and include all fields proposed for the form. When explicitly asked, the Companion can prepare proposals to create, edit, delete, or update a transaction's context fields. The user can edit, cancel, or confirm. The manual form remains complete when AI is unavailable.

## Effects on other layers

## Testing

## Out of scope

## Acceptance criteria

- Users can create, view, edit, and delete income and one-time expenses manually.
- Users can manage categories and preserve historical category readability.
- Users can add, edit, or remove optional context manually.
- The Companion answers transaction-history questions using visible evidence.
- AI-created or AI-edited records do not change until explicitly confirmed.
- The app remains usable when AI entry or the Companion is unavailable.
