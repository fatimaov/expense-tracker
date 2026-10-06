# Layer 3 — Analytics and Awareness

## Purpose and user value

Help users explore patterns instead of only viewing a transaction list. Analytics and the Companion must always make the selected period and filtered subset clear.

## Scope

## Included core features

- Month, quarter, year, custom-range, and all-history selection.
- Headline metrics, charts, category breakdowns, comparisons, and deterministic insights.
- Search and filters across transaction type, category, B/U/C, reflective context, and date.
- Savings and reserve trends.
- Companion exploration over the exact visible period and filters.
- Reviewable proposals for selected record changes.

## Depends on

- Layers 1 and 2, including transaction data, context fields, and deterministic cashflow services.
- Shared rules in [context](../context.md) and [architecture](../architecture.md).

## Existing capabilities used

## Data model

## Backend

## Frontend

## Business rules and calculations

Analytics distinguishes recorded expenses from expected recurring commitments and estimated variable payments. Available balance and current goal progress are current-state values, not historical period totals. Empty periods are not presented as zero-value financial results.

Filters update the records, metrics, charts, and insights together. A filtered result must identify itself as a subset. Records without a selected context are excluded from context-specific breakdowns rather than placed in an invented classification.

## Companion capabilities

The Companion can summarize selected records, explain charts and deterministic insights, compare periods, find matching records, identify missing context or estimated values, and answer questions about category, B/U/C, and reflective-context patterns.

## Manual user flows

## AI action proposals and confirmation

When explicitly requested, it can prepare proposals to edit or delete selected transactions or add, change, or remove their context. Searching, filtering, and explanation are read-only. Any record mutation requires review and confirmation.

## Effects on other layers

## Testing

## Out of scope

## Acceptance criteria

- Users can search, filter, and compare periods.
- Metrics and charts match the selected data.
- The Companion states the period and whether it is using a filtered subset.
- The Companion does not invent classifications or treat missing context as a financial result.
- Record proposals show affected records and fields before confirmation.
