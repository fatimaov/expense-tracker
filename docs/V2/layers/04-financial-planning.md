# Layer 4 — Financial Planning

## Purpose and user value

Help users connect current cashflow with future priorities and obligations. This layer contains two core features: Savings Goal management and Recurring Commitment management. The Companion assists with both, while their management pages remain complete manual alternatives.

## Scope

## Included core features

- Savings Goal creation, editing, contribution plans, allocation, progress, withdrawal, and lifecycle.
- Recurring Commitment creation, scheduling, generated records, expected impact, variable estimates, and lifecycle.
- Goal and commitment calculations grounded in Layers 1–3.
- Companion questions, estimates, reflections, and confirmed proposals for both features.

## Depends on

- Layer 1 transaction, category, B/U/C, and reflective-context models.
- Layer 2 Available balance, Savings reserve, and monthly calculation services.
- Layer 3 period, search, filter, and analytics services.
- Shared rules in [context](../context.md) and [architecture](../architecture.md).

## Existing capabilities used

## Data model

## Backend

## Frontend

## Business rules and calculations

### Savings Goals

A goal can have a target and deadline, a target with a fixed monthly amount, a target with a percentage-of-income plan, or no target/deadline as an open-ended goal. Target-and-deadline goals calculate planned contribution as remaining target divided by months remaining. Goals without deadlines can show an estimated completion time when their contribution plan and data support it.

The active month can use €0, the total planned allocation, or the maximum supported by cashflow. Goal contributions, direct transfers, withdrawals, target changes, deadline changes, and lifecycle actions remain visible and user-controlled.

### Recurring Commitments

Commitments can be fixed or variable and include name, expected amount, frequency, schedule, optional Coverage period, category, optional context, lifecycle dates, and notes. Expected records affect planning before payment, while generated records are linked to the commitment and must not be double-counted.

## Manual user flows

The user can edit, cancel, or confirm a Savings goal proposal, or perform the same task manually from Savings Goals.

The user can edit, cancel, or confirm a Recurring Commitment proposal, or perform the same task manually from Recurring Commitments.

## Companion capabilities

The Companion can explain progress, affordability, contribution plans, deadlines, completion estimates, and the relationship with the Savings reserve. It can reflect on a possible goal using transaction and income history, explain assumptions, compare contribution scenarios, and prepare a plan with name, target, deadline, contribution amount or percentage, and estimated timeline.

The Companion can explain upcoming payments, monthly and yearly impact, schedules, coverage, fixed versus variable amounts, estimated payments, missed occurrences, and expected versus recorded expenses.

## AI action proposals and confirmation

Goal proposals must distinguish estimates from commitments and show all fields and expected effects. The Companion can prepare proposals to create, edit, pause, reactivate, cancel, archive, contribute to, withdraw from, or change the allocation of a Savings goal.

The Companion can prepare proposals to create, edit, pause, reactivate, cancel, archive, or confirm a variable amount for a Recurring Commitment. It must not infer a commitment from a one-time transaction.

Goal and commitment proposals are untrusted input. Confirmation rechecks ownership, permissions, required values, balances, goal limits, schedules, current generated records, duplicate occurrences, and stale data. Only the normal validated command applies the change. The UI reports success or failure after confirmation.

## Effects on other layers

## Testing

## Out of scope

## Acceptance criteria

- Users can manage goals and commitments manually from their dedicated views.
- The Companion can answer supported questions and explain assumptions.
- The Companion can prepare goal plans and commitment proposals from permitted application data.
- No goal, commitment, allocation, transfer, or generated record changes before confirmation.
- Expected, estimated, and recorded values remain visibly distinct.
- Goal and commitment calculations integrate correctly with the Layer 2 cashflow services.
