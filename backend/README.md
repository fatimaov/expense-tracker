# Backend development and tests

Install the backend dependencies from this directory with `pipenv sync --dev`.
Run the backend test suite with:

```powershell
pipenv run python -m pytest
```

The normal API tests use an isolated in-memory SQLite database. The migration
integration test requires PostgreSQL and intentionally refuses to run against
a database that already contains tables. Create a new, disposable database for
the test, then set `V2_MIGRATION_TEST_DATABASE_URL` to its connection string
before running pytest. For example:

```powershell
$env:V2_MIGRATION_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/expense_tracker_migration_test"
pipenv run python -m pytest
```

## AI provider boundary (Layer 1)

The application has no AI HTTP endpoint in this layer. Internal callers build
deterministic transaction evidence first, reserve a per-user provider start,
then call the provider-neutral JSON generator. The generator accepts text,
application evidence, and a JSON response schema; it does not have database
access. Prompts, provider responses, credentials, and transaction data are not
written to the request-start table or application logs.

For local development, install [LM Studio](https://lmstudio.ai/), download and
load a text model that supports JSON-schema output, and start its local server.
Set `AI_PROVIDER=lm_studio`, `LM_STUDIO_BASE_URL` (usually
`http://localhost:1234/v1`), and `LM_STUDIO_MODEL` to the model identifier shown
by the server. The local adapter uses the OpenAI-compatible endpoint with one
request attempt and a 30-second timeout.

Production may set `AI_PROVIDER=gemini`, `GEMINI_API_KEY`, and `GEMINI_MODEL`.
Store the key in the deployment's server-side secret manager; never expose it
to frontend configuration. The Gemini adapter requests JSON-schema output,
uses a 30-second timeout, and disables retries. `AI_REQUEST_TIMEOUT_SECONDS`
is fixed at `30` for this layer.

Provider selection and adapter tests inject fake clients. They do not require
LM Studio, a Gemini key, or network access. The per-user database guard permits
ten request starts in a rolling 15-minute window; started requests count even
if a provider later fails or times out.

To run the PostgreSQL concurrent-guard integration test, point
`AI_RATE_GUARD_TEST_DATABASE_URL` at a separate, empty, disposable PostgreSQL
database. The test creates its schema and removes it when finished.

The migration test first upgrades that empty database through the existing
MVP schema, inserts title-only and title-plus-notes expense fixtures, then
upgrades to head and verifies identifiers, amounts, dates, categories, creation
timestamps, notes mapping, the seven category seeds, and removal of the legacy
`expenses` table. Use a fresh disposable database each time; do not point this
variable at application or production data.
