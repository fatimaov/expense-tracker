# Layer 2 — Cashflow and Reserve

## Purpose and user value

Turn Layer 1 records into a monthly financial position the user can understand: Monthly result, Money left to spend, Available balance, Savings reserve, and Unassigned reserve.

## Scope

## Included core features

- Calendar-month grouping.
- Monthly result and Money left to spend.
- Starting Available balance and starting Savings reserve.
- Savings allocation on/off behaviour.
- Month-close rules and past-change recalculation.
- Explicit transfers between Available balance and Unassigned reserve.
- Companion explanations, what-if questions, and confirmed Layer 2 proposals.

## Depends on

- Layer 1 transaction, category, context, user, and ownership models.
- Layer 1 transaction CRUD and deterministic period queries.
- Shared rules in [context](../context.md) and [architecture](../architecture.md).

## Existing capabilities used

## Data model

## Backend

## Frontend

## Business rules and calculations

- Monthly result is income minus expenses for the selected month.
- Positive result can increase Unassigned reserve when savings allocation is on.
- Deficits reduce Available balance, then Unassigned reserve, and may leave Available balance negative.
- Savings allocation is not a configurable goal allocation yet; Savings Goals belong to Layer 4.
- Editing or deleting a past transaction recalculates the affected month and following balances.
- Transfers are not income, expenses, or transaction-history records.

## Companion capabilities

The Companion can explain monthly calculations, current balances, reserve changes, active versus closed periods, and the effect of a transaction change. It can answer what-if questions without changing data.

## Manual user flows

## AI action proposals and confirmation

When explicitly requested, it can prepare proposals to change starting balances, switch savings allocation, or transfer money between Available balance and Unassigned reserve. Proposals show before/after balances, source and destination, assumptions, and recalculation effects. Confirmation revalidates current balances and stale state.

## Effects on other layers

## Testing

## Out of scope

## Acceptance criteria

- Dashboard and Companion agree for positive, negative, zero, and changed-income cases.
- Current-state values are distinguished from selected-period totals.
- Confirmed proposals update only the intended balance or setting.
- Cancelled, stale, or invalid proposals change nothing.
- Manual balance and transfer flows remain available without AI.
