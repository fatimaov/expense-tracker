# Layer 1 — Transaction Foundation

## Purpose and user value

Give users a reliable transaction history and several ways to record or correct one-time income and expenses. The user should be able to maintain their history manually, use assisted entry when useful, and remain in control of every record saved to the application.

Layer 1 establishes the canonical transaction contract used by later layers. It preserves the existing MVP expense data and extends the application to support income, fixed shared categories, optional expense context, and reviewable assisted-entry drafts.

## Scope

### Included core features

- One-time income CRUD for today and past dates.
- One-time expense CRUD for today and past dates.
- Migration of existing MVP expenses into the Layer 1 transaction model.
- A transaction history containing income and expenses, ordered newest first.
- A current-calendar-month default view with access to the complete history.
- Simple category totals.
- Seven fixed, shared application categories: five expense categories and two income categories.
- Optional B/U/C classification for expenses.
- Optional Need/Love/Like/Want reflective context for expenses.
- Manual entry.
- Natural-language entry with a reviewable AI-filled form.
- Receipt-image entry with a reviewable AI-filled form.
- Voice entry converted to text and passed through the same assisted-entry flow.
- Gemini and LM Studio provider integrations behind an application service boundary.
- Companion questions about transaction history.
- Confirmed transaction proposals.
- Soft deletion for all transactions.
- OpenAPI documentation for the Layer 1 API.

### Not included in Layer 1

- Recurring commitment rules or automatic scheduled generation.
- Transaction search or advanced filtering.
- Pagination or infinite scrolling.
- User-created, edited, or deleted categories.
- Saved incomplete drafts.
- Automatic B/U/C or reflective-context classification.
- Undo after deletion; the data model should support future restoration, but the temporary undo interaction may be implemented later.
- Cashflow, reserve, savings-goal, or recurring-commitment calculations owned by later layers.
- A persistent Companion conversation history.
- A database-backed pending-proposal workflow.

## Depends on

- Existing authentication and user ownership boundaries.
- Existing MVP expense data and manual expense flows.
- Shared rules in [context](../context.md) and [architecture](../architecture.md).

## Existing capabilities used

- JWT authentication and authenticated user routes.
- User ownership checks in backend services.
- Existing expense form, list, edit, and delete flows.
- Existing PostgreSQL database and Alembic migrations.
- Existing category values as the source for the initial expense-category migration.

## Data model

### Canonical transaction entity

Layer 1 uses one `transactions` table for one-time income and one-time expenses. The amount is always stored as a positive decimal. The transaction type determines whether the amount contributes to income or expense totals.

```text
transactions
- id
- user_id
- transaction_type: income | expense
- amount: positive decimal
- transaction_date: date
- category_id
- notes: optional text
- b_u_c: optional, expense only
- reflective_context: optional, expense only
- created_at: UTC timestamp
- updated_at: UTC timestamp
- deleted_at: nullable UTC timestamp
```

The model does not require a title or name for one-time income or expenses. Users can use the notes field for additional description, especially when selecting `Other`.

`transaction_date` is the date on which the financial activity took place. `created_at` and `updated_at` describe when the application record was created or changed. They must not be used as substitutes for `transaction_date` in financial calculations or period selection.

Existing MVP expenses are migrated into this table as `transaction_type = expense`. The migration should preserve existing record identifiers where practical and retain the original amount, date, category, and notes.

### Categories

Categories are global, shared application data. Users cannot create, rename, deactivate, or delete them.

The category model should support:

```text
categories
- id
- key
- label
- transaction_type: income | expense
```

Layer 1 seeds five fixed expense categories and two fixed income categories. The exact labels should preserve the current expense categories where applicable. Each transaction can reference only a category belonging to its transaction type. An `Other` category is available for both types.

Categories must remain readable for historical transactions because they cannot be removed or renamed by users.

### Recurring commitments boundary

Recurring commitments are not transaction records and are not implemented in Layer 1. They belong to a later layer as configuration/rules that can generate ordinary transaction records.

The planned relationship is:

```text
recurring_commitments
  -> generates one or more transactions
```

Later layers may add source metadata and a nullable `recurring_commitment_id` to generated transactions. This allows the transaction history to contain both manual and generated expenses without storing commitment rules in the Layer 1 transaction table or implementing scheduling prematurely.

## Backend

- Replace or adapt the MVP expense persistence around the canonical transaction model.
- Add income and expense transaction services while preserving existing expense behavior during migration.
- Add a migration for the transaction table, category data, and existing expense records.
- Keep amount, date, category, transaction-type, optional-context, ownership, and soft-deletion validation in backend services.
- Scope every read and mutation to the authenticated user.
- Exclude soft-deleted records from normal history, totals, and Companion evidence.
- Provide deterministic current-month and complete-history queries.
- Provide deterministic category-total services.
- Expose stable API responses for transactions, category totals, and assisted-entry drafts/proposals.
- Keep Gemini and LM Studio calls behind an application service/provider boundary.
- Use LM Studio as the default development provider and a commercial Gemini provider in production through the same provider interface.
- Ensure provider failures do not block manual transaction entry.
- Document the Layer 1 API with OpenAPI and expose a usable Swagger UI or equivalent API reference.

## Frontend

- Preserve the existing MVP expense flows while adapting them to the transaction model.
- Add income entry and editing using the appropriate income categories.
- Provide a transaction history view containing both income and expenses.
- Show the current calendar month by default while allowing the user to access the complete history.
- Order records newest first using `transaction_date`, then a stable creation-time tie-breaker.
- Display the transaction type and whether the amount increases or decreases the user's totals.
- Provide simple category totals.
- Add optional B/U/C and reflective-context fields to the expense form only.
- Keep the full edit form as the way to change optional context.
- Provide assisted-entry flows that populate the normal transaction form for review.
- Allow users to add B/U/C and reflective context manually during assisted-entry review.
- Require the user to confirm or discard each assisted-entry draft in the same session.
- Keep manual entry fully usable when AI or voice recognition is unavailable.
- Use Bootstrap defaults and the existing shared CSS patterns for Layer 1 presentation; custom visual design is deferred.

## Business rules and calculations

### Transaction rules

- A transaction is either an income or an expense.
- Amounts are positive values; transaction type determines their financial direction.
- One-time transactions may use today or any earlier date.
- Future transaction dates are rejected in Layer 1.
- A transaction has no required title/name.
- Notes are optional.
- Expense B/U/C and reflective context are each optional and allow at most one value.
- Income cannot have B/U/C or reflective context.
- Category must be valid for the transaction type.
- Soft-deleted transactions are excluded from normal reads and calculations.
- Deleting a transaction does not physically remove its database record.

### Date and time rules

- Financial period selection uses the user-selected `transaction_date`.
- `created_at` and `updated_at` are stored as UTC timestamps.
- The frontend may use the browser's local date to default a new transaction to today.
- The backend must not derive the transaction date from `created_at`.
- A user timezone setting is not required for Layer 1. It should be considered before implementing recurring commitment scheduling or server-side date generation.

### Layer 1 summaries

Layer 1 keeps summaries intentionally small. The backend may provide category totals for the selected current-month or complete-history dataset. Empty periods must remain distinguishable from periods whose total is genuinely zero.

Cashflow, reserve, savings allocation, and future recurring-commitment effects are defined by later layers.

## Manual user flows

### Add transaction

1. The user chooses to add income or an expense.
2. The form defaults the transaction date to today.
3. The user enters the amount, date, category, and optional notes.
4. For an expense, the user may optionally select one B/U/C value and one reflective-context value.
5. The application validates and saves the transaction.
6. The history and applicable totals update after successful creation.

### Review transaction history

1. The user opens the transaction history.
2. The application shows the current calendar month by default.
3. The user can access the complete history.
4. Records are ordered newest first.
5. Income and expenses are visually distinguishable.

### Edit transaction

1. The user selects a transaction.
2. The application displays the complete editable form.
3. The user can change the amount, date, category, notes, and—when applicable—optional context.
4. The application validates ownership and all values again before saving.

### Delete transaction

1. The user selects delete.
2. The application asks for confirmation.
3. After confirmation, the transaction is soft-deleted.
4. The transaction disappears from normal history and totals.

An expiring undo action may be added later without changing the soft-deletion contract.

## Assisted entry

Natural-language, receipt-image, and voice entry all produce the same normalized review form. Assisted entry is not a separate persistence path.

The provider may propose:

- transaction type: income or expense;
- amount;
- transaction date;
- category;
- notes.

The provider must not infer B/U/C or Need/Love/Like/Want. These fields remain blank unless the user selects them manually during review.

The review form must make uncertainty and missing values visible. The user can edit every proposed field before confirming or discard the draft. Incomplete drafts are not saved for later.

### Voice entry

The initial browser voice-entry implementation may use the Web Speech API `SpeechRecognition` interface to convert speech to text. The feature must handle unsupported browsers, permission errors, recognition errors, interim results, and final results. The typed/manual entry flow remains available as a fallback.

The resulting transcript is passed into the same natural-language parsing pipeline used for typed input.

## Companion capabilities

The Layer 1 Companion can:

- explain how much was spent in the selected period;
- summarize income or expenses by category;
- find records matching a supported description or visible history subset;
- identify records missing optional expense context;
- prepare an edit, delete, or context-change proposal when explicitly asked.

Layer 1 uses stateless, one-request Companion interactions. A user sends a prompt and receives a response; conversation history and multi-turn memory are deferred.

The Companion has access to the user's complete non-deleted transaction history in Layer 1, subject to the authenticated ownership boundary. It must identify the relevant period and data subset used in each response.

The application exposes structured deterministic summaries and evidence to the Companion, rather than allowing the model to calculate totals independently. These summaries may include total income, total expenses, net result, category totals, matching records, and records missing optional context. The model may explain that evidence, but it must not query the database or independently calculate financial values.

## AI action proposals and confirmation

The Companion may prepare proposals to:

- edit a transaction;
- soft-delete a transaction;
- add, change, or remove expense context fields.

A proposal is not a data change. It must show the proposed operation and all affected transaction fields, including uncertainty or missing information. The user can edit, cancel, or explicitly confirm it.

Layer 1 proposals are transient request/response objects and are not persisted as pending records. The frontend sends the complete proposal back to the normal application command when the user confirms it. A proposal identifier, version/timestamp, and idempotency key may be included to prevent duplicate submissions and to detect stale proposals, but the proposal itself does not become an application record.

Only the normal validated application command may apply the change. Confirmation must recheck ownership, required fields, supported categories, allowed dates, transaction type, current record state, and duplicate-submission protection. The UI must report success only after the application confirms that the mutation succeeded.

Assisted entry is separate from Companion record-editing proposals. Natural-language, receipt, and voice inputs produce a transaction form draft, and the user explicitly confirms that form before the normal create command persists a new transaction.

## Effects on other layers

- Layer 2 consumes Layer 1 income and expense transactions to calculate monthly cashflow, available balance, and reserve behavior.
- Layer 3 consumes Layer 1 history, categories, and optional context for search, filters, analytics, comparisons, and deterministic insights.
- Layer 4 adds recurring commitment rules that may generate linked transaction records and consumes Layer 1 categories and context fields.
- Later layers must not reinterpret the meaning of `transaction_date`, transaction type, positive amounts, soft deletion, or missing optional context without an explicit compatibility review.

## Implementation approach

Layer 1 should be delivered as feature slices. Each slice begins with the backend data model, migration, service rules, and API contract, then adds the frontend flow and verification for that feature. The intended order is:

1. Transaction and category foundation, including MVP expense migration.
2. Manual income and expense CRUD with soft deletion.
3. Transaction history, current-month default, complete-history access, and category totals.
4. Optional expense context.
5. OpenAPI documentation and API verification.
6. Natural-language, receipt-image, and voice-assisted entry with review and confirmation.
7. Stateless Companion summaries and edit/delete/context proposals.

The complete transaction foundation, including assisted entry, Companion integration, API documentation, and manual fallback behavior, is the Layer 1 completion target.

## Testing

Layer 1 should include:

- service tests for income and expense validation;
- tests for positive amount handling and transaction direction;
- tests for today/past-date validation and future-date rejection;
- tests for category/type compatibility;
- tests for optional context restrictions and one-value limits;
- tests for migration of existing MVP expenses;
- tests proving soft-deleted records are excluded from normal reads and totals;
- API tests for authentication, ownership, validation, and isolation;
- API tests for category totals and current-month/history responses;
- OpenAPI contract verification for Layer 1 endpoints;
- frontend verification for loading, empty, error, manual fallback, review, confirmation, and deletion states;
- assisted-entry tests using fixed provider outputs and deterministic evidence fixtures;
- tests proving unconfirmed assisted-entry drafts do not mutate transaction data;
- tests proving transient Companion proposals do not mutate transaction data until confirmed;
- tests proving stale or duplicate proposal confirmations are rejected safely.

## Out of scope

- Recurring commitment creation, scheduling, generation, or duplicate-occurrence prevention.
- Bank or card connections and automatic imports.
- User-created or user-managed categories.
- Search, advanced filters, pagination, and analytics dashboards.
- Savings goals, reserves, budgets, and cashflow planning.
- Automatic classification of B/U/C or reflective context.
- Professional financial advice or external financial-account data.
- Persistent Companion conversations or conversation memory.

## Acceptance criteria

- Users can create, view, edit, and soft-delete one-time income and expenses manually.
- Existing MVP expenses remain available after migration into the transaction model.
- Transactions accept only today or past dates.
- Amounts are stored as positive values and transaction type determines their direction.
- Income and expenses use the correct fixed shared categories.
- Users cannot create, modify, deactivate, or delete categories.
- Users can add, edit, and remove optional expense context manually.
- The default history view shows the current calendar month, with access to the complete history.
- Transaction history is ordered newest first and includes both income and expenses.
- Category totals are deterministic and match the displayed transaction dataset.
- Soft-deleted transactions no longer appear in normal history or totals.
- Natural-language, receipt-image, and voice entry produce reviewable transaction forms.
- Assisted entry does not infer B/U/C or reflective context.
- AI-created or AI-edited records do not change until explicitly confirmed.
- Manual entry remains usable when Gemini, LM Studio, receipt processing, or voice recognition is unavailable.
- The Layer 1 API is documented through OpenAPI and can be inspected through the project API documentation interface.
- The Layer 1 UI uses Bootstrap defaults and remains usable without a custom design system.
- Layer 1 Companion interactions are stateless and use structured deterministic summaries grounded in the user's complete transaction history.
