# Expense Tracker V2 — Product Requirements Document

## Product summary

Expense Tracker is a private personal finance-awareness application for a single user. It helps users understand their cashflow, make more conscious decisions with their money, and work toward a life that reflects their priorities.

The application combines income, expenses, recurring commitments, monthly spending availability, savings goals, and personal reflection. It is more than a record of transactions: it helps users understand what their money is doing and what they want it to support.

V2 builds this direction on top of the completed expense-tracking MVP. The existing MVP behaviour remains available and stable.

## Target audience

V2 is for people who want a clear and calm way to manage their personal finances without maintaining a restrictive, complicated budget. It is especially useful for users who want to understand their monthly spending capacity, notice recurring commitments, build savings for meaningful goals, and reflect on whether their financial choices match what matters to them.

The product is designed for individual personal finances, not shared household accounts, business accounting, or professional financial management.

## Product direction and principles

The product asks two connected questions:

> “Where did my money go?”

and:

> “What is my money helping me do?”

Expense Tracker should make the financial picture visible first and help the user interpret it second. It should connect cashflow, everyday choices, and personal priorities without judging the user or making decisions on their behalf.

The experience should follow these principles:

- **Clarity before advice:** calculations should be understandable and based on the user's recorded information.
- **Awareness without shame:** a deficit, unfinished goal, or expensive month is information to work with, not a moral judgment.
- **Money follows meaning:** saving is easier to sustain when it is connected to a purpose.
- **Spend consciously, not perfectly:** the goal is intentional spending, not eliminating every enjoyable expense.
- **Small systems beat willpower:** the product should favour repeatable habits such as capturing transactions, reviewing commitments, reserving savings, and checking progress.

## V2 goals

V2 should help users:

- understand their income, spending, and monthly cashflow;
- know how much money is available to spend during a selected month;
- see recurring commitments separately from one-time expenses;
- build and track multiple savings goals;
- understand how each month affects their savings reserve;
- review their financial history through filters, metrics, and visual summaries;
- reflect on spending, priorities, and future plans;
- use an AI companion to explore their data and think through goals without receiving prescriptive financial advice.

## Key concepts

These concepts should be used consistently across the product and its documentation.

- **Income:** money received during a specific period.
- **One-time expense:** an individual transaction entered through the quick expense flow.
- **Recurring commitment:** a repeated financial obligation, such as a subscription, rent, utility, loan, or installment.
- **Fixed commitment:** a recurring obligation with a predictable amount.
- **Variable commitment:** a recurring obligation whose amount changes, such as electricity or water.
- **B/U/C classification:** Bill, Usage, or Choice spending.
- **Expense category:** a descriptive group such as Food, Health, Travel, Transport, or Entertainment.
- **Reflection label:** optional Need, Love, Like, or Want context for understanding the user's relationship with spending.
- **Month:** a selected calendar month, with the current month shown by default.
- **Money left to spend:** the amount available after income, commitments, expenses, and planned savings are considered.
- **Savings goal:** a named purpose with a target amount, time horizon, deadline, and contribution plan.
- **Savings reserve:** accumulated savings progress kept separate from money available for ordinary spending.
- **Financial reflection:** reviewing spending patterns and priorities to make more intentional decisions.
- **AI Companion:** an optional conversational assistant that explains recorded data, supports reflection, and helps users brainstorm goals.

The B/U/C lens is used as follows:

- **Bill:** fixed commitments such as rent, a mortgage, or an installment payment.
- **Usage:** expenses that change according to consumption, such as electricity, water, gas, or mobile data.
- **Choice:** spending the user can increase, reduce, replace, or stop, such as entertainment, shopping, eating out, or flexible subscriptions.

Need/Love/Like/Want is optional reflective context. It does not replace normal expense categories or act as a moral score.

## Core features

### Income and expense tracking

Users can record and manage income and expenses for different dates and months. The quick-entry flow is designed for one-time expenses and should remain fast and simple.

### Expense categories and reflection

Users can organize expenses with standard or personal categories, classify them with B/U/C, and optionally add Need/Love/Like/Want context for later reflection and analysis.

### Monthly cashflow

The application calculates and explains the selected month's income, commitments, expenses, savings allocation, and money left to spend. A month can show a surplus or deficit, and the result remains visible rather than being hidden.

### Recurring commitments

Users can create and manage recurring financial commitments separately from one-time expenses. Commitments can be fixed or variable and may represent subscriptions, memberships, essential bills, utilities, loans, or installment purchases.

The application should show the expected monthly and yearly impact of active commitments and avoid counting an expected payment twice when the user records the actual expense.

### Savings goals and reserve

Users can create multiple short-, medium-, and long-term savings goals. The application shows recommended contributions, progress, deadlines, and the effect of changes to a goal. Past contributions remain part of the user's history if a goal is paused, cancelled, archived, or replaced.

The savings reserve shows accumulated savings progress separately from money left to spend.

### History and analytics

Users can review their full financial history over a selected period. They can search and filter records and view summaries by month, category, recurring status, B/U/C classification, income, expenses, savings, and other useful measures.

### Personal priorities and reflection

The application helps users identify what matters to them, such as safety, travel, health, learning, family, freedom, or retirement. Users can reflect on what they want to spend more on, what they are willing to reduce, and whether their financial activity supports their priorities.

Users can also identify their personal “money dials”: the areas where spending creates meaningful value for them. The application should support the complementary reflection of what they want to spend more freely on and what they are willing to reduce.

### AI Companion

The AI Companion can answer questions about the user's recorded information, explain patterns, compare periods, help brainstorm savings goals, and guide reflection. It should distinguish facts from suggestions, explain the period and data behind an answer, and never change records or make decisions without explicit user action.

The AI Companion is deferred if it would compromise the reliability of the core cashflow, commitment, savings, or history features.

## Main application views

### Monthly Dashboard

The default private-area view. It focuses only on the selected month and displays the month’s income, one-time expenses, recurring commitments, money left to spend, savings allocation, savings reserve, goal progress, and recent records.

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

## User journey

1. The user opens the application and sees the current monthly dashboard.
2. They record income and quickly add one-time expenses as they happen.
3. They add recurring commitments so the monthly picture includes ongoing obligations.
4. They create savings goals connected to personal priorities and future plans.
5. They review how much money is left to spend and how much is being reserved.
6. At the end of a month, they review the result and compare it with previous periods.
7. They use history, analytics, or the AI Companion to understand patterns and decide what to adjust.
8. They update commitments and savings goals as their circumstances change.

## User stories

- As a user, I want to know how much money I have left to spend this month so that I can make decisions with a clear picture of my cashflow.
- As a user, I want to distinguish one-time expenses from recurring commitments so that I can see which costs continue into future months.
- As a user, I want to create savings goals with deadlines so that my saving has a clear purpose and direction.
- As a user, I want to review my spending by period and category so that I can notice patterns and make better choices.
- As a user, I want to reflect on what matters to me so that my spending and savings support my priorities.
- As a user, I want to ask an AI companion questions about my financial activity so that I can understand it and think through possible goals without giving up control of my decisions.

## Boundaries

V2 does not include bank or card connections, automatic transaction imports, shared finances, business accounting, investment execution, tax reporting, or professional financial advice.

Debt and installment commitments can be represented at a basic visibility level, but detailed payoff planning is outside the initial V2 scope. AI features must remain explainable, optional, and user-controlled.

The data model, transaction fields, technical architecture, technology choices, and relationships between entities belong in the architecture document, not in this PRD.

## Existing MVP foundation

The completed MVP provides registration, login, user data isolation, and personal expense management. Users can add, view, edit, and delete expenses with an amount, title or description, date, category, and optional notes.

The MVP includes the original fixed categories of Transport, Accommodation, Food, Activities, and Other, along with responsive layout, loading and error states, and a newest-first expense list. V2 extends this foundation without redefining or removing the existing expense-tracking behaviour.

## Long-term direction

Beyond V2, Expense Tracker can grow into a personal money companion that helps users understand their patterns, build reserves, fund meaningful goals, and make financial decisions with more confidence. It should remain smaller than a bank, accounting system, investment platform, or professional financial-advice service. The user stays in control of their data, goals, and decisions.

## Definition of success

V2 is successful when a user can record income and expenses, understand their selected month's available money, manage recurring commitments, track multiple savings goals, review their history and analytics, and use reflection tools to connect their financial choices with their personal priorities.
