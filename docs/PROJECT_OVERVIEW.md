# Expense Tracker

## Purpose

Expense Tracker is a private personal finance-awareness tool. It helps people record their income and expenses, understand how they use their money, and make more conscious financial decisions.

The app is intended for individuals who want to take more responsibility for their spending habits. It is not designed to automate financial decisions or replace the user's judgment. Recording and confirming a transaction is part of the value: each entry gives the user a clearer view of how much money they have available and how their choices affect it.

## Vision

The long-term vision is to help users build a consistent habit of checking in with their finances. Expense Tracker should make it easy to record transactions while keeping the user's financial situation visible and understandable.

The app should help users answer practical questions such as:

- How much money do I have available for the rest of this period?
- Where is my money going?
- How much am I spending on each category?
- How much did a trip, event, or other activity cost?
- How much can I set aside for savings?
- Am I staying within the limits I set for myself?

## Product direction

The product will gradually develop from a simple expense log into a personal cash-flow and financial-awareness tool.

Users should be able to record both income and expenses, including recurring items such as salary, rent, subscriptions, or other regular payments. They should also be able to define a savings target as a fixed amount or percentage of their income.

A user's financial position for a period can then be understood through a simple calculation:

```text
Income - savings allocation - recurring commitments - recorded expenses = available balance
```

The app should show this calculation clearly rather than hide it behind automation. The available balance should be updated as the user confirms new transactions, giving them an ongoing reason to stay aware of their spending.

To reduce the effort required to record an expense, the app may support assisted input such as natural-language text, receipt uploads, and voice recordings. These features can help prepare the expense details, but the user must always review and confirm the information before it is saved.

As more structured data is collected, the app can provide useful summaries and analytics by period, category, and tag. Tags can group expenses belonging to trips, events, projects, or other personal contexts. Future features may include budgets, recurring expense generation, savings goals, and optional AI-generated interpretations of spending patterns.

## Long-term goal

The long-term goal is to help users improve their financial awareness, control their spending, and save money through consistent small decisions. The app should make financial information easier to understand without becoming a complex accounting system or a source of financial advice.

Expense Tracker is intentionally not intended to be:

- A company finance or accounting system.
- A bank-connected transaction tracker.
- An investment or tax management tool.
- A shared household finance platform.
- A system that makes financial decisions on the user's behalf.

The user remains in control of their data and confirms the financial records created by the app.

## Current MVP

The MVP focuses on personal expense tracking. Users can register, log in, and manage their own expenses by adding, viewing, editing, and deleting records.

Each expense includes:

- Amount in euros.
- Title or description.
- Expense date.
- Category.
- Optional notes.

The MVP includes five fixed categories: Transport, Accommodation, Food, Activities, and Other. It also includes user data isolation, JWT authentication, a responsive interface, loading and error states, an empty state for users without expenses, and a newest-first expense list.

The detailed MVP specification, API reference, deployment guide, and development roadmap are available in [docs/MVP/](./MVP/).
