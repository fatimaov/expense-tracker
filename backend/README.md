# Backend development and tests

Install the backend dependencies from this directory with `pipenv sync --dev`.
Run the backend test suite with:

```powershell
pipenv run pytest
```

The normal API tests use an isolated in-memory SQLite database. The migration
integration test requires PostgreSQL and intentionally refuses to run against
a database that already contains tables. Create a new, disposable database for
the test, then set `V2_MIGRATION_TEST_DATABASE_URL` to its connection string
before running pytest. For example:

```powershell
$env:V2_MIGRATION_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/expense_tracker_migration_test"
pipenv run pytest
```

The migration test first upgrades that empty database through the existing
MVP schema, inserts title-only and title-plus-notes expense fixtures, then
upgrades to head and verifies identifiers, amounts, dates, categories, creation
timestamps, notes mapping, the seven category seeds, and removal of the legacy
`expenses` table. Use a fresh disposable database each time; do not point this
variable at application or production data.
