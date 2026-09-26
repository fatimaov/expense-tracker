# Expense Tracker V2 — Product Requirements Document

## Purpose

Expense Tracker is a private personal finance-awareness tool. It helps users record income and expenses, understand their spending, and build a habit of saving money.

V2 should make expense capture faster while keeping the user responsible for reviewing and confirming every transaction. It should also show how much money is left to spend in the current month and how the user's savings are growing over time.

The app is not a bank account, accounting system, investment tool, or source of professional financial advice.

## Main concepts

| Term | Meaning |
| --- | --- |
| **Month** | A calendar month, from its first day to its last day. |
| **Income** | Money recorded for a month, such as salary, freelance pay, or a manual amount. |
| **Expense** | Money the user has spent. |
| **Regular payment** | A repeated payment, such as rent, a subscription, or a membership. |
| **Savings goal** | The amount or percentage the user wants to set aside during a month. |
| **Money left to spend** | The amount available for the rest of the current month. |
| **Monthly result** | The amount the month adds to, or takes from, the savings reserve. |
| **Savings reserve** | The accumulated savings result from past and current months. |
| **Category** | What an expense was for, such as Food or Transport. |
| **Tag** | A label that groups expenses by context, such as a trip or event. |
| **Expense draft** | An expense prepared for the user to check before saving. |
| **Assisted entry** | Using text, a receipt, or voice to prepare an expense draft. |

## Calendar months

V2 works with calendar months. The application knows the current date and automatically shows the current month:

```text
1 April → 30 April
1 May → 31 May
1 June → 30 June
```

Every income and expense belongs to the month of its date. A month can start with no income, so the money left to spend starts at €0. Expenses can still be recorded and the balance can become negative.

Custom period start days are outside the initial V2 scope.

## Money left to spend

The current month's money left to spend is calculated as:

```text
Income recorded for the month
+ money moved from the savings reserve
- savings goal
- regular payments due in the month
- recorded expenses
= money left to spend
```

Income added during the month increases that month's money left to spend immediately. A user who wants to record money without a traditional source can create an income record with a title such as “Manual amount.”

Money from the savings reserve is never used automatically. The user must explicitly move it into the current month.

The current month's money left to spend and the savings reserve are shown separately. The reserve is not automatically added to the current month's spending money.

## Savings reserve

The savings reserve represents the user's accumulated savings progress. It is not a bank balance.

The savings goal is money reserved from the month, not an expense. It is excluded from the money left to spend during the month. The user can see the goal, but ordinary expenses should not use it by default.

The monthly result is based on the month's income, regular payments, and expenses. If the user stays within the money available for ordinary spending, the savings goal remains protected and is added to the savings reserve. If the user overspends, the overspending reduces or consumes part of the savings goal. A larger deficit can also reduce the existing savings reserve.

For example:

```text
Savings goal: €300
Money left at the end of the month: €200
Monthly savings result: €500
```

If the month ends €100 over budget, that deficit reduces the monthly result. The savings reserve updates while the month is active and becomes final when the month closes.

The user can view:

- The current month's money left to spend.
- The current month's savings result.
- The total savings reserve.
- Monthly savings results over time.

The reserve can be filtered by a range of months. Future versions may allow users to divide the reserve into savings goals such as a trip, car, phone, or emergency fund.

## Income and regular payments

Users can record income such as salary, freelance work, or a manual amount. Each income record includes an amount, title or source, date, and optional notes. Its date determines the month it affects. Income can be one-time or recurring.

Users can register regular payments such as rent, subscriptions, and memberships. Each regular payment includes:

- Name.
- Amount.
- Category.
- Payment day.
- Frequency, such as monthly or every few months.
- Start date.
- Active status.

The application checks which regular payments are due in each month and includes them in that month's money-left-to-spend calculation. They are shown separately from recorded expenses so the user can see what is planned and what has already been recorded.

In V2, regular payments can remain calculation-based. The application does not need to create an expense automatically on the payment date. Automatic expense creation can be added later, but planned payments and actual expenses must never be counted twice.

If a regular payment is added later with a start date in an earlier month, the affected past months are recalculated. The user should be able to review and confirm that change.

## Expense capture

The manual form remains the fallback and most reliable method. An expense includes:

- Amount.
- Title or merchant.
- Date.
- Category.
- Optional notes.
- Optional tags.

V2 adds assisted entry for expenses only:

- Natural-language text, such as “I spent €24.50 on dinner yesterday.”
- Receipt upload.
- Voice recording.

These methods create an expense draft. They do not save an expense automatically.

```text
Input → AI processing → expense draft → user review → confirmation → saved expense
```

The user must be able to correct every extracted field before confirming it. Incomplete or uncertain results must be shown for review.

## Categories, tags, and analytics

Categories describe what an expense was for. V2 can keep the existing fixed categories and add more later. Custom user-created categories are a future improvement.

Tags describe the context of an expense. An expense can have multiple tags, such as “Spain trip” and “Weekend.” Users can search or filter by tag and see how much they spent in that group.

The app should provide summaries for:

- Income by month and source.
- Expenses by month.
- Money left to spend.
- Savings goals and monthly results.
- Savings reserve over time.
- Spending by category.
- Spending by tag.
- The expenses behind each total.

A future version may allow a tag, such as a trip, to have its own budget. That budget could be funded by monthly money or the savings reserve, but this is not required for the initial V2 scope.

## Main application areas

- Dashboard: current month, money left to spend, savings goal, monthly result, savings reserve, regular payments, income, and recent expenses.
- Spending: expense history, filters, totals, categories, tags, and expense creation.
- Income: income history and income creation.
- Savings and analytics: monthly results, reserve history, and longer-term summaries.
- Settings: personal preferences.

The frontend should use shared Context and reducer patterns for authentication, expenses, income, the current month, filters, and request status. Local form state should remain local when it does not need to be shared.

## Past months

Users can add, edit, or delete dated expenses, income, and regular payments from past months. The affected monthly result and savings reserve are recalculated.

This allows users to correct their history without moving a transaction into the current month.

## Data model direction

V2 requires at least three meaningful models. The expected models are:

- `User`: owns private data.
- `Expense`: a confirmed outgoing transaction.
- `Income`: a recorded incoming amount.
- `FinancialMonth`: a calendar month and its calculated result.
- `RecurringItem`: a regular income or payment rule.
- `Tag`: a user-owned expense label.
- `SavingsGoal` or `Budget`: a future way to plan money for a purpose or category.
- `ReserveEntry`: a monthly result or a move to or from the savings reserve.

Analytics should be calculated from transaction data rather than stored as duplicated totals.

## Privacy and boundaries

- Users can access only their own data.
- Assisted expense drafts require explicit confirmation.
- AI assistance is limited to expense capture in V2.
- The app does not connect to banks or import transactions automatically.
- The app does not provide financial advice or make decisions for the user.
- Shared household finances, investments, tax reporting, and native mobile apps are outside the scope.

## Definition of success

V2 is successful when:

- The application automatically identifies the current calendar month.
- Users can record income and expenses for that month.
- Users can set a savings goal and understand their money left to spend.
- Users can register regular payments with a frequency and start date.
- Users can add an expense manually or through at least one assisted entry method.
- Assisted expenses require review and confirmation.
- The monthly result and savings reserve update as transactions change.
- Users can review savings and spending by month, category, and tag.
- The existing MVP expense-tracking behavior remains available and stable.
