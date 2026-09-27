# Expense Tracker

## Purpose

Expense Tracker is a private personal finance-awareness tool. It helps people record income and expenses, understand their spending, and build a habit of saving money.

The app is designed for users who want to stay aware of their expenses and make better decisions with the money they have available. Adding an expense should be quick, but the user should still review and confirm it.

## How it works

The application works with calendar months. It knows the current date and automatically shows the current month.

Income and expenses belong to the month of their date. A month can start with no income, so the money left to spend starts at €0. The user can add income during the month, including an income record titled “Manual amount” when they want to record money without a traditional source.

The current month's money left to spend is calculated as:

```text
Income
- savings goal
- regular payments
- expenses
= money left to spend
```

The dashboard shows the current month, money left to spend, savings goal, monthly result, savings reserve, regular payments, income, and recent expenses.

## Saving money

The main direction of the product is to help users save money and build better financial habits.

The user can set a monthly savings goal as an amount or a percentage of income. Money left unspent can increase the monthly result, while overspending reduces it.

The savings reserve represents the user's accumulated savings progress. It updates as the user adds income and expenses, and it can be viewed as a total or by month. It is separate from the money left to spend and cannot be used for ordinary spending in V2. A monthly deficit reduces the reserve instead.

Over time, the reserve can support goals such as a trip, a car, a phone, or an emergency fund.

## Income and regular payments

Users can record different kinds of income, such as salary, freelance work, or a manual amount. They can also register regular payments such as rent, subscriptions, and memberships, including their amount, frequency, payment day, and start date.

The application includes regular payments in the months where they are due. These payments are shown separately from expenses already recorded. Users can correct past transactions, and the affected monthly results and savings reserve are recalculated.

## Assisted expense entry

The manual form remains available for every expense. The app may also help prepare an expense through:

- Natural-language text.
- Receipt uploads.
- Voice recordings.

These methods create an expense draft. The user reviews and confirms the information before it is saved.

## Analytics and future direction

Users can review income, expenses, savings, categories, and tags by month. Tags can group expenses by context, such as a trip or event, and show how much that group cost.

Future features may include budgets for tags or categories, savings goals, and optional AI-generated explanations of spending patterns.

Expense Tracker is not intended to be a company finance system, accounting platform, investment tool, bank-connected service, or source of professional financial advice. The user remains in control of their data and financial decisions.

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
