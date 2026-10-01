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

1. **Transaction tracking:** users record income and one-time expenses using general categories. This creates the raw history of their financial activity.
2. **Monthly cashflow and reserve:** the application groups transactions by calendar month, shows the active month's money left to spend, and lets the user switch a maximum monthly savings allocation on or off before updating the available balance and savings reserve.
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
- As a user, I want to see how each month's surplus or deficit affects my available balance and how my goal contributions grow my savings reserve.
- As a user, I want to distinguish one-time expenses from recurring commitments so that I can see which costs continue into future months.
- As a user, I want to create savings goals with deadlines so that I can give part of my savings a clear purpose and direction.
- As a user, I want to review my spending by selected month or date range and category so that I can notice patterns and make better choices.
- As a user, I want to reflect on what matters to me so that my spending and savings support my priorities.
- As a user, I want to ask an AI Companion questions about my financial activity so that I can understand it and think through possible goals without giving up control of my decisions.


## Key concepts

These concepts should be used consistently across the product and its documentation.

- **Income/Ingresos:** money received during a specific period.
- **One-time expense/Gasto puntual:** an individual transaction entered through the quick expense flow.
- **Transaction history/Historial de transacciones:** the complete record of income and one-time expenses across months.
- **Recurring commitment/Pago recurrente:** a repeated financial obligation, such as a subscription, rent, utility, loan, or installment.
- **Fixed commitment/Pago fijo:** a recurring obligation with a predictable amount.
- **Variable commitment/Pago variable:** a recurring obligation whose amount changes, such as electricity or water.
- **Cashflow/Flujo de caja:** the movement of money into and out of the user's finances during a selected month or date range.
- **B/U/C classification:** Bill, Usage, or Choice spending.
- **Expense category:** a descriptive group such as Food, Health, Travel, Transport, or Entertainment.
- **Reflective context tags/Etiquetas de contexto:** optional Need, Love, Like, or Want tags that add personal meaning and emotional context to an expense.
- **Month:** a selected calendar month, with the current month shown by default.
- **Available balance/Saldo disponible:** unallocated money carried forward for ordinary spending. It can start with a user-provided opening amount, changes when a month closes, and can become negative after the savings reserve is exhausted.
- **Money left to spend/Dinero restante para gastar:** the current month's cashflow after income, expenses, and commitments. In Layer 2, it is income minus expenses; when an intentional Goal allocation is enabled in a later layer, that allocation is also deducted. It can be negative even when the user has an available balance from previous months.
- **Monthly result/Resultado mensual:** the positive or negative cashflow produced by a month from its income, expenses, and commitments. It shows the month's underlying surplus or deficit before any savings are set aside.
- **Monthly savings allocation/Asignación mensual de ahorro:** the positive monthly result that Layer 2 may direct to the savings reserve at month close. It is flexible during the month and decreases as new expenses reduce the monthly result. Later, Savings Goals can replace this with an intentional planned Goal allocation that is deducted from Money left to spend.
- **Savings goal/Objetivo de ahorro:** a named purpose with a target amount, time horizon, deadline, and contribution plan.
- **Goal allocation/Asignación al objetivo:** the desired amount to reserve for an active Savings goal during the selected month. It can be €0, the planned monthly amount, or the maximum supported by the month's cashflow. It does not use the Available balance unless the user makes a separate transfer.
- **Reserved goal amount/Importe reservado para el objetivo:** the amount actually set aside for a Savings goal from income recorded during the selected month. It can remain €0 until income is recorded and cannot exceed the available income.
- **Savings reserve/Reserva de ahorro:** money intentionally set aside and kept separate from ordinary spending. It includes unassigned reserve money, monthly savings allocations, Goal allocations, and explicit transfers from the available balance.
- **Unassigned reserve/Reserva no asignada:** the portion of the Savings reserve that is not assigned to a Savings goal. It can cover an exhausted Available balance or be assigned to a goal through an explicit user action.
- **Financial reflection/Reflexión financiera:** reviewing spending patterns and priorities to make more intentional decisions.
- **Money dial/Dial del dinero:** an area where the user finds meaningful value in spending and may intentionally choose to spend more.
- **AI Companion/Asistente de IA:** an optional conversational assistant that explains recorded data, supports reflection, and helps users brainstorm goals.

The B/U/C lens is used as follows:

- **Bill/Factura:** fixed commitments such as rent, a mortgage, or an installment payment.
- **Usage/Consumo:** expenses that change according to consumption, such as electricity, water, gas, or mobile data.
- **Choice/Elección:** spending the user can increase, reduce, replace, or stop, such as entertainment, shopping, eating out, or flexible subscriptions.

The reflective context tags are optional. They do not replace normal expense categories or act as a moral score. They are used as follows:

- **Need/Necesidad:** necessary for basic wellbeing or functioning.
- **Love/Amor:** creates lasting value or joy.
- **Like/Gusto:** creates temporary enjoyment.
- **Want/Deseo:** mainly immediate gratification.

## Core features

### Layer 1: Transaction tracking

Layer 1 establishes the transaction history that the rest of the application builds on. Users can create and manage income and expense records for the current or past months using general categories. Records may be entered manually or through optional AI-assisted methods, with the user remaining responsible for reviewing and approving each record before it is saved. [Read more](#layer-1-extended-transaction-tracking).

### Layer 2: Monthly cashflow and savings reserve

The application groups transactions by calendar month and focuses the dashboard on the active month. It shows the month's income, expenses, monthly result, money left to spend, available balance, and savings reserve. The user can switch the maximum monthly savings allocation on or off. At month close, the positive result can increase the unassigned reserve, while overspending reduces the unassigned reserve after the available balance is exhausted. This layer works without configurable savings goals. [Read more](#layer-2-extended-monthly-cashflow-and-savings-reserve).

### Layer 3: Analytics and awareness

The application turns the raw transaction history into useful information. Users can review the full history through metrics, graphics, categories, filters, and search. Analytics also displays the savings reserve and how it changes across months.

### Layer 4: Savings goals

Users can create multiple short-, medium-, and long-term Savings goals with targets, deadlines, and contribution plans. For the active month, they can choose no Goal allocation, the planned allocation, or the maximum amount supported by the month's cashflow. The Reserved goal amount is taken from that month's income, increases the goal and the Savings reserve, and reduces Money left to spend. Users can also transfer money from the Available balance to a goal or the Unassigned reserve. Goal progress, withdrawals, and changes to the plan remain visible and user-controlled. [Read more](#layer-4-extended-savings-goals).

### Layer 5: Recurring commitments

Users can optionally create and manage repeated financial commitments separately from one-time expenses. These may be fixed or variable and may represent subscriptions, memberships, essential bills, utilities, loans, or installment purchases. The application shows their expected monthly and yearly impact and avoids double-counting when an actual payment is recorded.

### Layer 6: Richer spending context

Users can add more meaning to their records through expense categories, B/U/C classification, and optional reflective context tags. They can also identify their personal Money dials: the areas where spending creates meaningful value for them. This layer enriches analytics and supports reflection but is not required for basic tracking.

### Layer 7: AI Companion

The AI Companion is an optional conversational tool that uses the user's application data to answer questions, explain patterns, compare periods, brainstorm savings goals, and support reflection. It should distinguish facts from suggestions, explain the period and data behind an answer, and never change records or make decisions without explicit user action.

The AI Companion is not required for the application to work. AI-assisted income and expense entry belongs to Layer 1 and must not block the manual entry flow.

## Main application views

### Monthly Dashboard

The default private-area view for the active calendar month. It displays income, one-time expenses, recurring commitments, Money left to spend, Available balance, the total Savings reserve, and recent records. It also shows whether the Goal allocation is active, the desired Goal allocation for the month, and the amount actually reserved from income so far. The Monthly result and monthly savings allocation remain calculation values rather than primary dashboard metrics.

The desired Goal allocation can be €0 when switched off, the amount defined by the Savings goal plan, or the maximum amount supported by the month's cashflow. The reserved amount can remain €0 until income is recorded and updates as income is added. Selecting the total Savings reserve opens the Savings Goals view with the individual goals and their progress. The dashboard provides quick access to add one-time expenses and income manually or through AI-assisted entry methods, including natural-language, receipt image, and voice input.

### Transactions and Analytics

A full-history view for exploring records across any selected period. It combines search, filters, metrics, categories, richer spending context, and visual summaries so users can compare Monthly results, spending patterns, and the Savings reserve over time. Users can edit or delete manually entered records here, with a notice when a change may recalculate a past month and following balances.

### Recurring Commitments

A management view for adding, editing, pausing, cancelling, and archiving recurring commitments. It shows their current status and expected monthly or yearly impact.

### Savings Goals

A management and progress view for creating, editing, pausing, completing, cancelling, or archiving Savings goals. It shows each goal's progress, contribution plan, deadline, Goal allocation, and relationship to the Savings reserve. Users can change the active month's Goal allocation, make direct transfers, and withdraw from a goal without silently changing its future plan.

### AI Companion

A conversational view for asking questions about financial activity, exploring patterns, reflecting on priorities, and brainstorming goals.

### Settings

A place for personal preferences, categories, starting Available balance, starting Savings reserve, transfers between the Available balance and the Unassigned reserve, and other account-level configuration.

## Detailed layer explanations

### Layer 1 extended: Transaction tracking

Layer 1 provides the raw transaction history and should be useful on its own. Users can add, view, edit, and delete income and expense records for the current or past months. Records can be created manually or through an AI-assisted entry flow, but every AI-assisted record must be reviewed and explicitly approved by the user before it is saved.

Each record includes an amount, category, date, and optional notes. Income and expense forms may use different labels and categories, but both belong to the same transaction history. Named records such as Spotify or Mortgage belong to recurring commitments introduced in a later layer.

Layer 1 supports three AI-assisted entry methods in addition to the manual form:

- **Natural-language entry:** the user describes an income or expense in their own words. The AI identifies whether it is income or an expense and proposes the amount, category, date, and notes for the matching form.
- **Receipt image entry:** the user takes or uploads a picture of a receipt. The AI interprets the receipt and proposes a one-time expense in the matching form, including the amount, date, category, and useful notes when they are available.
- **Voice entry:** the user records a voice message through browser-supported voice input. The application converts the message to text, and the AI interprets that text and proposes the fields for the matching income or expense form.

The AI should show the proposed transaction clearly, preserve uncertainty where the input is incomplete or ambiguous, and let the user correct any field before approval. It must not save a record, create a recurring commitment, or silently choose a category or date without the user's approval. The manual form remains available at all times and is the fallback when AI entry is unavailable or the user prefers to enter the record directly.

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

The quick-add experience should make one-time expense recording easy, whether the user enters the fields manually or approves an AI-generated draft. The initial forms do not include B/U/C classification, recurring-commitment management, fixed or variable commitment types, or reflective context tags. Those concepts, along with specialized transaction types, monthly calculations, analytics, savings goals, and richer context, belong to later layers. AI-assisted entry is available in Layer 1, while the broader AI Companion remains an optional later-layer experience.

### Layer 2 extended: Monthly cashflow and savings reserve

The rules for this layer are:

- **Calendar month:** each transaction belongs to the month selected in its date, even if it is added or changed later.
- **Monthly result:** income minus expenses for the selected month. It can be positive or negative and shows the month's underlying cashflow.
- **Savings allocation on:** when enabled, a positive monthly result is set aside for the savings reserve at month close. The amount is flexible during the month and decreases as new expenses reduce the monthly result. It is €0 when the monthly result is zero or negative.
- **Savings allocation off:** no monthly result is set aside, so the full monthly result remains available to update the available balance.
- **Money left to spend:** during Layer 2, this is the monthly result: income minus expenses. The savings allocation does not reduce this value during the active month because it is not an intentional spending restriction yet.
- **Income changes:** if income is added later in the month, the monthly result, monthly savings allocation, and money left to spend update accordingly.
- **Savings goals:** this layer does not use a planned Goal allocation. That configurable amount and its current-month editing belong to Layer 4.
- **Month close:** if savings allocation is on, a positive monthly result increases the Unassigned reserve. If the monthly result is negative, it first reduces the Available balance; once the Available balance reaches zero, the Unassigned reserve covers the remaining amount. If the reserve also reaches zero, the Available balance becomes negative. If savings allocation is off, the full monthly result updates the Available balance.
- **Starting position:** users may provide an initial Available balance and an initial Savings reserve separately. In Layer 2, the initial Savings reserve is automatically treated as Unassigned reserve.
- **Reserve transfer:** a user can explicitly transfer money between the Available balance and the Unassigned reserve. This is not recorded as income or an expense.
- **Past changes:** editing or deleting a past transaction recalculates that month's Monthly result, monthly savings allocation, and the balances for following months.

### Layer 4 extended: Savings goals

The rules for this layer are:

- **Savings goal:** a named purpose with a target amount, deadline, and contribution plan. Users can create multiple goals.
- **Goal allocation:** the desired amount to reserve for a Savings goal during the active month.
- **Current-month choices:** the user can set the Goal allocation to €0, use the planned allocation, or save the maximum positive amount supported by that month's cashflow. The Reserved goal amount is €0 until income is recorded and cannot exceed the available income for the month.
- **Scope of changes:** changing the Goal allocation affects only the active month. It does not change the Savings goal's planned allocation for future months unless the user explicitly changes that plan.
- **Progress:** the goal's saved amount, remaining amount, deadline, and progress update according to the actual Reserved goal amount.
- **Direct transfer:** the user can move money from the Available balance to a Savings goal or the Unassigned reserve. This is separate from monthly income and expenses.
- **Reserve ownership:** existing Unassigned reserve remains unassigned until the user explicitly assigns it to a Savings goal or transfers it to the Available balance. It is not automatically used to complete a goal.
- **Deficit recovery:** once Savings goals are in use, the application does not automatically use the Unassigned reserve or withdraw money from a Savings goal. The user chooses whether to transfer Unassigned reserve money to the Available balance or explicitly withdraw money from a specific goal. A goal withdrawal reduces its progress and increases the remaining amount.
- **Withdrawal:** after a goal withdrawal, the application recalculates the suggested contribution needed to meet the original deadline.
- **Goal changes:** the user can pause, cancel, archive, or replace a goal. Past contribution history remains intact, and the application does not change the target or deadline silently.
- **Realistic planning:** when the recalculated contribution is not realistic, the application can show alternatives such as extending the deadline, lowering the target, or pausing contributions.

## Boundaries

V2 is a personal finance tool for individual users. It covers income and expense tracking, monthly cashflow, the Available balance, the Savings reserve, analytics, Savings goals, recurring commitments, richer spending context, and the optional AI Companion. It also supports AI-generated transaction drafts from natural-language descriptions, receipt images, and voice input. Users must review and approve these drafts before they are saved.

V2 does not include bank or card connections, automatic transaction imports, shared household finances, business accounting, investment execution, tax reporting, or professional financial advice. Debt and installment commitments may be represented for visibility, but detailed payoff planning is outside the initial V2 scope.

AI features are optional and must remain explainable and user-controlled. AI may interpret input, explain recorded data, and suggest possibilities, but it must not make changes or decisions without explicit user action. The data model, transaction fields, technical architecture, browser API choices, and entity relationships belong in the architecture document rather than this PRD.

## Definition of success

V2 is successful when an individual user can maintain a reliable transaction history for income and expenses, understand their selected month's cashflow and balances, and review spending patterns through analytics. They should also be able to manage recurring commitments and Savings goals that support their priorities.
