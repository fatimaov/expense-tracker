# Layer 1 — Transaction Foundation

## Purpose

Layer 1 gives a user a reliable history of one-time income and expenses. They can add a record manually or with assisted entry, correct it later, soft-delete it, review it in a dedicated history page, and use a dedicated Companion page for grounded transaction questions and reviewable change proposals.

It establishes the transaction contract used by later layers. It does not add cashflow, savings, recurring commitments, search, analytics, or user-managed categories.

## Dependencies and shared rules

Layer 1 depends on the existing authentication and ownership boundaries and on the shared rules in [context](../context.md) and [architecture](../architecture.md). In particular, those documents define money representation, the `Europe/Madrid` time boundary, soft deletion, idempotency, stale edits, API conventions, provider safety, privacy, and testing expectations.

Layer 1 replaces the MVP expense persistence with the canonical transaction model while preserving existing expense data. Existing manual expense use remains available through the new transaction flows.

## Scope

### Included

- One-time income and one-time expense creation, editing, and soft deletion.
- Migration of all MVP expenses to the transaction model.
- Fixed shared categories: five for expenses and two for income.
- Optional B/U/C and Need/Love/Like/Want values for expenses.
- A dedicated transaction-history page that shows the current calendar month by default and lets the user view complete history.
- Server-side pagination and simple pagination controls in the history page.
- Deterministic transaction summaries and category totals for the displayed or requested dataset.
- Four entry methods: manual form, natural-language text, receipt image, and voice.
- A dedicated, stateless Companion page for supported transaction-history questions and transaction change proposals.
- OpenAPI documentation for the Layer 1 API.
- Bootstrap 5.3 default layout and components. Custom visual design is deferred.

### Not included

- Recurring commitments, cashflow, balances, reserves, savings goals, or budgeting.
- Search, advanced filters, analytics, charts, or user-created categories.
- Persistent drafts, Companion conversation history, or a database-backed proposal workflow.
- Companion proposals to create transactions. The normal and assisted-entry forms already provide creation.
- Automatic B/U/C or reflective-context classification.
- Undo after deletion, bank imports, or stored receipt images and voice recordings.

## Transaction and category contracts

### Transaction

`transactions` stores one-time income and one-time expenses.

```text
transactions
- id
- user_id
- transaction_type: income | expense
- amount: positive decimal
- transaction_date: date
- category_id
- notes: optional text
- b_u_c: optional; expense only
- reflective_context: optional; expense only
- created_at: UTC timestamp
- updated_at: UTC timestamp
- deleted_at: nullable UTC timestamp
```

Transaction type determines whether the positive amount is income or an expense. A transaction date may be today or in the past; the backend rejects future dates using the application time boundary. A transaction's type is fixed after creation. Editing may change the amount, date, category, notes, and applicable optional context.

`notes` is the only free-text transaction field. New Layer 1 transactions do not have a separate title.

### MVP expense migration

Each MVP expense becomes an expense transaction with its original identifier where practical, amount, date, category, creation time, and notes preserved. Its required MVP title is prepended to `notes`:

- when the old notes are empty, the new notes value is the trimmed title;
- when the old notes are present, the new notes value is `<trimmed title>\n\n<trimmed old notes>`.

The migration must not discard either value. It must normalize a blank resulting value to `null` and have automated tests for title-only and title-plus-notes records.

### Categories

Categories are shared application data. Users can list them but cannot create, rename, deactivate, or delete them. The application seeds exactly these categories:

| Key | Label | Type |
| --- | --- | --- |
| `expense_transport` | Transport | expense |
| `expense_accommodation` | Accommodation | expense |
| `expense_food` | Food | expense |
| `expense_activities` | Activities | expense |
| `expense_other` | Other | expense |
| `income_salary` | Salary | income |
| `income_other` | Other | income |

Each transaction must use a category with the same transaction type. Historical records continue to display their category because these seed categories are never removed.

### Optional expense context

An expense may have zero or one value from each set:

- B/U/C: `bill`, `usage`, or `choice`;
- reflective context: `need`, `love`, `like`, or `want`.

Income cannot have either field. Neither field is inferred from a category, notes, text prompt, receipt, or voice input.

## Manual history and entry experience

The frontend has two dedicated authenticated pages: Transaction History and Companion. Transaction History presents income and expenses in descending `transaction_date` order, with creation time as the stable tie-breaker. It opens on the current calendar month and provides access to every history page.

The history API follows the shared collection contract (`page` and `page_size`); the frontend offers simple Previous and Next navigation. The category totals returned for a view must describe exactly the same non-deleted records as that view.

The manual form supports both income and expense creation. Required fields are transaction type, amount, transaction date, and a category valid for that type. Notes and expense context are optional. The form defaults the date to today, but the backend remains authoritative.

Users can open a complete edit form from history. Deletion requires confirmation and performs a soft deletion. Deleted records disappear from normal history, totals, and Companion evidence.

Use standard Bootstrap 5.3 containers, navigation, form controls and validation feedback, tables or list groups, buttons, alerts, and confirmation modals. No custom design system is part of this layer.

## Assisted entry

All assisted entry produces the same unsaved draft for the normal transaction form. The user can correct every field, add optional expense context manually, confirm the normal create form, or discard the draft. A draft never writes a transaction itself.

| Entry method | Input | Output |
| --- | --- | --- |
| Manual | Form fields | Normal create command |
| Natural language | Typed text | Reviewable transaction draft |
| Receipt | One allowed transient image upload | Reviewable transaction draft |
| Voice | Browser speech transcript | The natural-language draft flow |

The provider may propose transaction type, amount, date, category, and notes. It must leave B/U/C and reflective context unset. Missing or uncertain values must be visible in the review form. Provider, upload, or voice-recognition failures must leave the manual form usable.

## Companion

The Companion is stateless: one prompt produces one response, and the application does not store a conversation. It receives structured deterministic evidence from application services, never direct database access.

### Supported answers

For a stated or inferred period, the Companion can answer only these Layer 1 questions:

- income, expense, or net total for the period;
- income or expense breakdown by category;
- records matching a supported description within the permitted history;
- records missing B/U/C or reflective context.

Every answer identifies its period and data subset, distinguishes application facts from suggestions, and acknowledges incomplete data. If a request is ambiguous, unsupported, or identifies several possible target records, the Companion asks for clarification instead of guessing.

### Response and proposal boundary

The provider must return one validated response kind:

```text
answer
- message
- evidence: period, included records or aggregates, exclusions, and warnings

clarification
- message
- missing or ambiguous information

proposal
- operation: edit_transaction | soft_delete_transaction | change_transaction_context
- target_transaction_id
- affected_fields
- evidence: current record and relevant period or subset
- uncertainty and expected effect when calculable
- proposal_version or created_at
```

An answer is read-only. A proposal is produced only for an explicit supported change request; it is not a data change. For a clear supported edit, deletion, or expense-context command, the backend may build the proposal directly from the user's instruction and the verified selected record. Other requests may use the provider. Both paths produce the same proposal shape and pass through the same backend validation before the proposal reaches the frontend.

The user can edit, cancel, or confirm a proposal. Confirmation sends the relevant normal update or delete command with the required idempotency and stale-record protections. It rechecks ownership, target state, fields, category compatibility, date, and all other normal validation. The UI reports success only after that command succeeds.

## Acceptance criteria

- MVP expenses migrate without losing amount, date, category, title, notes, or creation-time information.
- Users can manually create, view, edit, and soft-delete one-time income and expenses.
- Transactions require a valid type, positive amount, today-or-past date, and matching fixed category.
- Income has only the two income categories; expenses have only the five expense categories.
- Users cannot manage categories.
- Users can add, change, and remove optional expense context, and cannot assign it to income.
- Transaction History is a dedicated page, defaults to the current calendar month, provides paginated complete-history access, and orders records newest first.
- A history view's category totals match exactly the records included in that view.
- Soft-deleted records are absent from normal history, totals, and Companion evidence.
- Natural-language, receipt, and voice entry create only reviewable drafts; the normal create command persists a confirmed draft.
- Assisted entry never infers expense context, and manual entry remains usable when an AI or voice capability fails.
- Companion is a dedicated stateless page whose answers are grounded in deterministic evidence and identify their period and subset.
- Companion supports only the listed answers and edit/delete/context proposals; ambiguous and unsupported requests do not mutate data.
- A cancelled, unconfirmed, stale, invalid, or duplicate proposal confirmation changes no transaction.
- Layer 1 endpoints are documented in OpenAPI, and the UI uses only Bootstrap defaults and existing shared CSS patterns.
