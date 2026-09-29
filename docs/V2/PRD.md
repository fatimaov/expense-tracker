# Expense Tracker V2 — Product Requirements Document

## Product summary

Expense Tracker is a personal money companion that helps users turn everyday financial activity into a clearer sense of control and progress. It brings income, expenses, monthly availability, savings, and financial priorities into one place so users can understand where their money is going, know what they can safely spend, and gradually direct more of their money toward the life they want. The experience starts as a simple and useful tracking tool, then becomes more powerful as users add savings goals, recurring commitments, richer spending context, and guided reflection.

V2 builds this direction on top of the completed expense-tracking MVP. The existing MVP behaviour remains available and stable.

## Target audience

Expense Tracker is for people managing their own personal finances who want a clearer and more intentional relationship with money. This includes students, people beginning to manage their finances independently, and anyone who wants to understand their cashflow, build better habits, reduce financial stress, or make progress toward meaningful goals.

The audience may have different levels of financial knowledge and different situations: regular or irregular income, little or substantial savings, debt or no debt, and short-term or long-term goals. The common motivation is to understand the numbers, know what is available to spend, make more conscious choices, and use money to support priorities such as safety, travel, learning, health, family, freedom, or retirement.

The experience should be approachable for people who feel overwhelmed by money or traditional budgeting. It should encourage awareness and consistency without shame, guilt, or the expectation that users must manage their finances perfectly.

The current product is for individual use only. Shared household finances, couples contributing to common goals, and connected accounts may be considered in the future, but they are outside the current scope. The product is also not intended for business accounting, investment management, tax reporting, or professional financial advice.

## Product vision and layered experience

The application is designed to work without requiring every feature. Each layer adds more context and support to the one before it:

1. **Transaction tracking:** users record one-time income and one-time expenses using general categories. This creates the raw history of their financial activity.
2. **Monthly cashflow and reserve:** the application groups transactions by calendar month, shows the active month's money left to spend, and carries the month's final positive or negative result into the savings reserve when the month closes.
3. **Analytics and awareness:** users explore the full transaction history through metrics, graphics, categories, filters, and search, while also reviewing the savings reserve over time.
4. **Savings goals:** users can give their savings a purpose by creating short-, medium-, and long-term goals with progress and deadlines.
5. **Recurring commitments:** users can make subscriptions, bills, utilities, loans, and installment payments visible and easier to manage.
6. **Richer spending context:** B/U/C, Need/Love/Like/Want, expense categories, and Money dial reflections help users describe their choices more accurately and identify patterns.
7. **AI Companion:** an optional conversational tool can answer questions using the user's data, help interpret patterns, brainstorm goals, and support personal reflection.

The product should make the financial picture visible before offering interpretation. It should be calm and non-judgmental, explain its calculations, and keep the user in control of their records, goals, and decisions.

## User journey

1. The user opens the application and sees the current monthly dashboard.
2. They record income and quickly add one-time expenses as they happen.
3. They review their available money, monthly result, and savings reserve.
4. They explore their full history through search, filters, and analytics.
5. If useful, they add recurring commitments and savings goals.
6. They use classifications, reflection, or the AI Companion to understand patterns and priorities.
7. They adjust their commitments and goals as their circumstances change.

## User stories

- As a user, I want to know how much money I have left to spend this month so that I can make decisions with a clear picture of my cashflow.
- As a user, I want to see how each month's surplus or deficit affects my savings reserve, even if I have no specific savings goal.
- As a user, I want to distinguish one-time expenses from recurring commitments so that I can see which costs continue into future months.
- As a user, I want to create savings goals with deadlines so that I can give part of my savings a clear purpose and direction.
- As a user, I want to review my spending by selected month or date range and category so that I can notice patterns and make better choices.
- As a user, I want to reflect on what matters to me so that my spending and savings support my priorities.
- As a user, I want to ask an AI Companion questions about my financial activity so that I can understand it and think through possible goals without giving up control of my decisions.


## Key concepts

These concepts should be used consistently across the product and its documentation.

- **Income:** money received during a specific period.
- **One-time expense:** an individual transaction entered through the quick expense flow.
- **Transaction history:** the complete record of income and one-time expenses across months.
- **Recurring commitment:** a repeated financial obligation, such as a subscription, rent, utility, loan, or installment.
- **Fixed commitment:** a recurring obligation with a predictable amount.
- **Variable commitment:** a recurring obligation whose amount changes, such as electricity or water.
- **Cashflow:** the movement of money into and out of the user's finances during a selected month or date range.
- **B/U/C classification:** Bill, Usage, or Choice spending.
- **Expense category:** a descriptive group such as Food, Health, Travel, Transport, or Entertainment.
- **Reflective context tags:** optional Need, Love, Like, or Want tags that add personal meaning and emotional context to an expense.
- **Month:** a selected calendar month, with the current month shown by default.
- **Money left to spend:** the amount available during a selected month after income, commitments, expenses, and any active goal allocation are considered.
- **Monthly result:** the final positive or negative amount produced by a month after its income, expenses, commitments, and active goal allocations are considered.
- **Savings goal:** a named purpose with a target amount, time horizon, deadline, and contribution plan.
- **Goal allocation:** the part of available money assigned to an active savings goal.
- **Savings reserve:** accumulated savings progress kept separate from money available for ordinary spending.
- **Financial reflection:** reviewing spending patterns and priorities to make more intentional decisions.
- **Money dial:** an area where the user finds meaningful value in spending and may intentionally choose to spend more.
- **AI Companion:** an optional conversational assistant that explains recorded data, supports reflection, and helps users brainstorm goals.

The B/U/C lens is used as follows:

- **Bill:** fixed commitments such as rent, a mortgage, or an installment payment.
- **Usage:** expenses that change according to consumption, such as electricity, water, gas, or mobile data.
- **Choice:** spending the user can increase, reduce, replace, or stop, such as entertainment, shopping, eating out, or flexible subscriptions.

The reflective context tags are optional. They do not replace normal expense categories or act as a moral score. They are used as follows:

- **Need:** necessary for basic wellbeing or functioning.
- **Love:** creates lasting value or joy.
- **Like:** creates temporary enjoyment.
- **Want:** mainly immediate gratification.

## Core features

### Layer 1: Transaction tracking

Users can record one-time income and one-time expenses using general categories. This is the raw transaction history that the rest of the application builds on. The quick-entry flow is designed for everyday one-time expenses and should remain fast and simple. [Read more](#layer-1-extended-transaction-tracking).

### Layer 2: Monthly cashflow and savings reserve

The application groups transactions by calendar month and focuses the dashboard on the active month. It shows income, expenses, and money left to spend during the active month. When a month closes, its final positive or negative result is added to the savings reserve. This layer works without specific savings goals.

### Layer 3: Analytics and awareness

The application turns the raw transaction history into useful information. Users can review the full history through metrics, graphics, categories, filters, and search. Analytics also displays the savings reserve and how it changes across months.

### Layer 4: Savings goals

Users can optionally create multiple short-, medium-, and long-term goals and assign part of their savings progress to them. Goals provide purpose, deadlines, recommended contributions, and visible progress. If a goal is paused, cancelled, archived, or replaced, its past contribution history remains intact.

### Layer 5: Recurring commitments

Users can optionally create and manage repeated financial commitments separately from one-time expenses. These may be fixed or variable and may represent subscriptions, memberships, essential bills, utilities, loans, or installment purchases. The application shows their expected monthly and yearly impact and avoids double-counting when an actual payment is recorded.

### Layer 6: Richer spending context

Users can add more meaning to their records through expense categories, B/U/C classification, and optional reflective context tags. They can also identify their personal Money dials: the areas where spending creates meaningful value for them. This layer enriches analytics and supports reflection but is not required for basic tracking.

### Layer 7: AI Companion

The AI Companion is an optional conversational tool that uses the user's application data to answer questions, explain patterns, compare periods, brainstorm savings goals, and support reflection. It should distinguish facts from suggestions, explain the period and data behind an answer, and never change records or make decisions without explicit user action.

The AI Companion is not required for the application to work. AI-assisted one-time expense entry is a future enhancement and must not block the manual quick-entry flow.

## Main application views

### Monthly Dashboard

The default private-area view. It focuses only on the selected month and displays the month’s income, one-time expenses, recurring commitments, money left to spend, active goal allocation, savings reserve, goal progress, and recent records.

The dashboard provides quick access to add a one-time expense and add income. Selecting the savings reserve opens a summary of savings-goal progress.

### Transactions and Analytics

A full-history view for exploring records across any selected period. It combines search, filters, metrics, and visual summaries so users can compare months and understand spending patterns.

### Recurring Commitments

A management view for adding, editing, pausing, cancelling, and archiving recurring commitments. It shows their current status and expected monthly or yearly impact.

### Savings Goals

A management and progress view for creating, editing, pausing, completing, cancelling, or archiving goals. It shows progress, contribution plans, deadlines, and the overall savings reserve.

### AI Companion

A conversational view for asking questions about financial activity, exploring patterns, reflecting on priorities, and brainstorming goals.

### Settings

A place for personal preferences, categories, and other account-level configuration.

## Boundaries

V2 does not include bank or card connections, automatic transaction imports, shared finances, business accounting, investment execution, tax reporting, or professional financial advice.

Debt and installment commitments can be represented at a basic visibility level, but detailed payoff planning is outside the initial V2 scope. AI features must remain explainable, optional, and user-controlled.

The data model, transaction fields, technical architecture, technology choices, and relationships between entities belong in the architecture document, not in this PRD.

## Definition of success

V2 is successful when a user can record income and expenses, understand their selected month's available money, review their history and analytics, and see monthly progress accumulate in a savings reserve. Recurring commitments, savings goals, reflection tools, and the AI Companion should add value without being required for the core experience to work.

## Detailed layer explanations

### Layer 1 extended: Transaction tracking

Layer 1 provides the raw transaction history and should be useful on its own. Users can add, view, edit, and delete one-time income and expense records for the current or past months.

Each record includes an amount, title, category, date, and optional notes. Income and expense forms may use different labels and categories, but both belong to the same transaction history.

The application should start with general expense categories such as:

- Food and groceries;
- Housing and bills;
- Transport and fuel;
- Health;
- Travel and accommodation;
- Education;
- Entertainment;
- Shopping and personal care;
- Other.

It should also provide general income categories such as:

- Salary or wages;
- Freelance or contract work;
- Business income;
- Scholarship or study support;
- Benefits or pension;
- Gift or family support;
- Interest or other income;
- Other.

Users should be able to add, rename, or deactivate categories later. Existing transaction history should remain understandable if a category is changed or deactivated.

The quick-add experience should make one-time expense recording easy. The initial forms do not include B/U/C classification, recurring-commitment management, fixed or variable commitment types, or reflective context tags. Those concepts, along with specialized transaction types, monthly calculations, analytics, savings goals, richer context, and AI support, belong to later layers.
