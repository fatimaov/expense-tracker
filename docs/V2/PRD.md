# Expense Tracker V2 — Product Requirements Document

## Product summary

Expense Tracker is a personal money companion that helps users turn everyday financial activity into a clearer sense of control and progress. It brings income, expenses, monthly availability, savings, and financial priorities into one place so users can understand where their money is going, know what they can safely spend, and gradually direct more of their money toward the life they want. The experience starts as a simple and useful tracking tool, then becomes more powerful as users add savings goals, recurring commitments, richer spending context, and guided reflection.

V2 builds this direction on top of the completed expense-tracking MVP. The existing MVP behaviour remains available and stable.

## Product delivery strategy: AI from the beginning

The AI Companion is a product capability from the first V2 implementation, not a feature that is postponed until every financial feature is complete. We will build it through small, grounded vertical slices so that each new data capability immediately gives the user a clearer explanation, reflection, or reviewable action.

The implementation must keep two responsibilities separate:

- **Deterministic financial logic** calculates balances, periods, totals, comparisons, and other values that must be correct and reproducible.
- **The AI Companion** explains those values, answers questions about the available data, identifies limitations, supports reflection, and can prepare proposed actions. It must not become the source of truth or execute an action without the user's explicit confirmation.

Every slice should ship a usable user outcome. A slice is complete only when the underlying data, the user-facing view, the relevant deterministic calculations, and at least one Companion question or explanation work together. The manual flow must remain useful if an AI provider is unavailable.

The first implementation target is therefore an AI-ready transaction foundation and a small grounded Companion, rather than a full chat experience added at the end. Later layers expand the Companion's evidence base and its reviewable action proposals as monthly cashflow, analytics, goals, commitments, and spending context become available.

### Proposed actions and confirmation

The Companion may prepare an action proposal when the user asks it to do something the application supports. Examples include drafting a Savings goal, drafting a Recurring commitment, preparing an income or expense record, or proposing a change to an existing record. A proposal is not an application change.

Every proposal must show the exact operation, all affected fields, the source or reasoning used, important uncertainty, and the expected financial effect when it can be calculated. The user must be able to edit, cancel, or explicitly confirm the proposal. Only the application's normal validated command or form may apply the change after confirmation. The Companion must never bundle unrelated changes, infer consent from a conversational reply that is ambiguous, or report a change as completed before the application confirms success.

The same confirmation model applies across transactions, Savings goals, Recurring commitments, classifications, tags, transfers, and other future actions. Read-only questions do not require confirmation; actions that mutate data always do.

## Target audience

Expense Tracker is for people managing their own personal finances who want a clearer and more intentional relationship with money. This includes students, people beginning to manage their finances independently, and anyone who wants to understand their cashflow, build better habits, reduce financial stress, or make progress toward meaningful goals.

The audience may have different levels of financial knowledge and different situations: regular or irregular income, little or substantial savings, debt or no debt, and short-term or long-term goals. The common motivation is to understand the numbers, know what is available to spend, make more conscious choices, and use money to support priorities such as safety, travel, learning, health, family, freedom, or retirement.

The experience should be approachable for people who feel overwhelmed by money or traditional budgeting. It should encourage awareness and consistency without shame, guilt, or the expectation that users must manage their finances perfectly.

The current product is for individual use only. Shared household finances, couples contributing to common goals, and connected accounts may be considered in the future, but they are outside the current scope. The product is also not intended for business accounting, investment management, tax reporting, or professional financial advice.

## User journey

1. The user opens the application and sees the current monthly dashboard with their main balances and activity.
2. They add income and expenses manually or use an AI-assisted method, then review and approve any proposed record.
3. They review their Money left to spend, Monthly result, Available balance, Savings reserve, and Savings goal progress.
4. When needed, they use Settings to add starting balances, adjust the active month's Goal allocation, or manage transfers and preferences.
5. They explore their transaction history and analytics, then add recurring commitments or Savings goals as their needs grow.
6. They use spending context or the AI Companion to understand their patterns and adjust their records, commitments, and goals over time.

## User stories

- As a user, I want to record income and expenses in the way that is easiest for me so that keeping my transaction history up to date feels simple.
- As a user, I want to review and approve AI-assisted entries so that I remain in control of what is saved.
- As a user, I want to understand my monthly cashflow, Money left to spend, Available balance, and Savings reserve so that I can make informed spending decisions.
- As a user, I want to review my transaction history and analytics so that I can understand my spending patterns over time.
- As a user, I want to create Savings goals and manage their contributions so that my savings have a clear purpose and visible progress.
- As a user, I want to add recurring commitments and see their financial impact so that I can plan for costs that continue over time.
- As a user, I want to reflect on my spending and ask the AI Companion questions so that I can make choices that support my priorities.

## Key concepts

These concepts should be used consistently across the product and its documentation.

- **Income/Ingresos:** money received during a specific period.
- **One-time expense/Gasto puntual:** an individual transaction entered through the quick expense flow.
- **Transaction history/Historial de transacciones:** the complete record of income, one-time expenses, and recorded recurring-commitment payments across months.
- **Recurring commitment/Pago recurrente:** a repeated financial obligation, such as a subscription, rent, utility, loan, or installment.
- **Fixed commitment/Pago fijo:** a recurring obligation with a predictable amount.
- **Variable commitment/Pago variable:** a recurring obligation whose amount changes, such as electricity or water.
- **Payment frequency/Frecuencia de pago:** how often a Recurring commitment is paid, such as monthly, every X months, or yearly.
- **Coverage period/Periodo cubierto:** the period of service or access provided by one payment. In V2, it normally matches the Payment frequency. It is useful for subscriptions, memberships, insurance, and other prepaid services, but may not apply to commitments such as rent or utilities.
- **Cashflow/Flujo de caja:** the movement of money into and out of the user's finances during a selected month or date range.
- **B/C/U classification:** Bill, Cash/Choice, or Usage/Utilities spending.
- **Expense category:** a descriptive group such as Food, Health, Travel, Transport, or Entertainment.
- **Reflective context tags/Etiquetas de contexto:** an optional Need, Love, Like, or Want tag that adds personal meaning and emotional context to an expense. An expense can have at most one reflective context tag.
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
- **AI Companion/Asistente de IA:** an optional conversational assistant that explains recorded data, supports reflection, and helps users brainstorm goals.

### B/C/U spending model

The B/C/U model is a simple way to understand spending by the amount of control the user has over it. **B — Bills** are fixed obligations that must be paid, such as rent, a mortgage, loan payments, or other commitments where non-payment can create serious consequences. **C — Cash/Choice** covers spending the user can choose to increase, reduce, replace, or stop, such as eating out, entertainment, shopping, grooming, or flexible subscriptions. **U — Usage/Utilities** covers costs that fluctuate with consumption, such as electricity, water, gas, or mobile data.

The model is descriptive, not judgmental, and it does not replace normal expense categories. Its purpose is to help the user see where money is going and decide what kind of problem they may have: if most spending is in Bills or Usage, the issue may be that income is not sufficient for essential costs; if most spending is in Cash/Choice, the user may have more opportunities to adjust spending. The AI Companion can explain this lens and summarize recorded classifications, but it must not assign classifications or treat them as moral judgments.

### Need/Love/Like/Want reflective model

Need/Love/Like/Want is an optional reflective model for adding personal meaning to an expense that has already been recorded. It is separate from both the expense category and the B/C/U classification. **Need** means the expense was necessary for the user's wellbeing or functioning. **Love** means it is expected to create lasting value or joy. **Like** means it creates temporary enjoyment. **Want** means it is mainly about immediate gratification.

The model is a reflection prompt, not a ranking of good and bad spending. A user may apply one optional tag to an existing expense, change it later, or leave it blank. The meaning of a tag is personal: the same type of expense may be a Need, Love, Like, or Want for different users or in different circumstances.

The AI Companion may explain the four tags, summarize patterns among expenses that already have them, and help the user reflect on how spending relates to their priorities. It must not infer, assign, recommend, or silently change a tag. It should describe the selected period and acknowledge when untagged expenses are excluded from a reflective summary. It must never use the tags to shame the user, judge a purchase, or present one type of spending as universally more responsible than another.

## Core features

The application is organized into implementation layers. Each layer adds a complete, useful capability on top of the previous one. The AI Companion starts in Layer 1 with the transaction history and grows across the later layers as more financial context and supported actions become available. Users can continue using the manual product if AI is unavailable or not useful to them.

### Layer 1: Transaction history, entry methods, and the Companion foundation

Layer 1 establishes the complete transaction history that the rest of the application builds on. Users can create, view, edit, and delete income and one-time expense records for the current or past months. They can manage the initial general categories and the optional B/U/C classification and reflective context tag, enter records manually, or use natural-language, receipt, and voice entry methods. The AI Companion is already available in this layer: it can answer questions about the user's transaction history, find relevant records, prepare new transaction drafts, and prepare edits to existing records, including explicitly requested context changes. Every AI-proposed creation or edit is reviewed and explicitly confirmed before it changes the transaction history. [Read more](#layer-1-extended-transaction-history-entry-methods-and-the-companion-foundation).

### Layer 2: Monthly cashflow and savings reserve

The application groups transactions by calendar month and focuses the dashboard on the active month. It shows the month's income, expenses, monthly result, money left to spend, available balance, and savings reserve. The user can switch the maximum monthly savings allocation on or off. At month close, the positive result can increase the unassigned reserve, while overspending reduces the unassigned reserve after the available balance is exhausted. This layer works without configurable savings goals.

The Layer 2 Companion extends the Layer 1 transaction-history experience. It can explain the month's calculations, describe why balances or the reserve changed, answer what-if questions without changing data, and prepare confirmed proposals for Layer 2 actions such as changing a starting balance, switching savings allocation, or transferring money between the Available balance and the Unassigned reserve. [Read more](#layer-2-extended-monthly-cashflow-and-savings-reserve).

### Layer 3: Analytics and awareness

The application turns the raw transaction history into useful, descriptive information. The default view is the current calendar month, but users can select a specific month, quarter, year, custom date range, or all history. Users can review income, expenses, cashflow, savings, categories, B/U/C classifications, reflective context, and records through metrics, charts, filters, search, and short deterministic insight messages. Analytics also displays the Savings reserve and how it changes across months.

The Layer 3 Companion extends the Layer 1 and Layer 2 experiences over selected analytics data. It can search and summarize filtered records, explain charts and deterministic insights, compare periods, identify missing or estimated information, and answer questions about B/U/C and reflective-context patterns. It can also prepare reviewable proposals to update selected records' classifications or tags, but filtering and searching do not mutate data and every record change still requires confirmation. [Read more](#layer-3-extended-analytics-and-awareness).

### Layer 4: Savings goals

Users can create multiple Savings goals and define a target, deadline, and contribution plan for each one. Goals with a target and deadline receive an automatically calculated planned contribution. Goals without a deadline use a fixed monthly amount or a percentage of income and can show an estimated time to reach their target. For the active month, the user can choose no Goal allocation, the total planned allocation, or the maximum amount supported by the month's cashflow. At month close, the actual amount is distributed between goals by priority and increases the Savings reserve. Users can transfer money between the Available balance, the Unassigned reserve, and specific goals. Goal progress, withdrawals, and changes to the plan remain visible and user-controlled.

The Layer 4 Companion can answer questions about goal progress, affordability, contribution plans, deadlines, estimated completion dates, and the relationship between goals and the Savings reserve. It can reflect on a possible goal using the user's transaction and income history, explain assumptions, and prepare a Savings goal plan with a target, deadline, contribution amount or percentage, and estimated timeline. The user can accept, edit, or cancel the proposal, or complete the same task manually from the Savings Goals view. [Read more](#layer-4-extended-savings-goals).

### Layer 5: Recurring commitments

Users can optionally create and manage repeated financial commitments separately from one-time expenses. These may be fixed or variable and may represent subscriptions, memberships, essential bills, utilities, loans, or installment purchases. Active commitments appear as upcoming records in the current month, affect Money left to spend, and become linked expense records on their scheduled dates. The application supports an optional Coverage period aligned with the Payment frequency, shows the expected monthly and yearly impact, supports pausing, cancelling, and archiving, and avoids double-counting when an actual payment is recorded.

The Layer 5 Companion can answer questions about upcoming commitments, expected monthly and yearly impact, payment schedules, Coverage periods, fixed and variable amounts, estimated payments, and the difference between expected and recorded expenses. When explicitly asked, it can prepare a Recurring commitment proposal or a change to an existing commitment. The user can accept, edit, or cancel the proposal, or complete the same task manually from the Recurring Commitments view. [Read more](#layer-5-extended-recurring-commitments).

### Layer 6: Context-aware reflection

Layer 6 builds deeper reflective workflows on the B/U/C classifications and reflective context tags introduced in Layer 1 and used in Layer 3 analytics. It adds richer combinations, context-aware insights, and reflection prompts across one-time expenses and recurring commitments without making context mandatory or changing financial calculations. [Read more](#layer-6-extended-richer-spending-context).

### Layer 7: AI Companion expansion

Layer 7 completes the broader AI Companion experience across the product. It builds on the transaction-history Companion introduced in Layer 1 and adds richer explanations, cross-period reflection, Savings goal and Recurring commitment proposals, uncertainty handling, starter prompts, and the full set of trust and safety behaviours. It uses the user's application data, including B/U/C classifications and reflective context tags, to answer questions, explain patterns, compare periods, brainstorm Savings goals, and prepare supported actions for confirmation.

The Companion is optional, but its first useful version belongs to Layer 1 rather than being postponed until this layer. Layer 7 expands its coverage and action surface; it does not introduce AI for the first time. [Read more](#layer-7-extended-ai-companion-expansion).

### Implementation order

The layers above describe product capability, not the order in which the code must be built. V2 implementation follows a vertical-slice order: establish a trustworthy data contract, expose a small Companion experience, and expand both together.

1. **Transaction history and Companion foundation:** deliver the complete Layer 1 transaction history, entry methods, category management, and a Companion that can answer transaction questions and prepare reviewable transaction creations and edits.
2. **Cashflow, reserve, and Companion actions:** add monthly result, Money left to spend, Available balance, and Savings reserve, then let the Companion explain the formulas, answer what-if questions, and prepare confirmed proposals for Layer 2 balance and reserve actions.
3. **Analytics and awareness:** add period selection, comparisons, deterministic insights, search, filters, and analytics over the Layer 1 B/U/C and reflective context fields. The Companion can explain selected subsets, compare periods, identify missing context, and prepare confirmed record-context proposals.
4. **Planning data and Companion actions:** add Savings goal and Recurring commitment management. The Companion can explain progress, reflect on plans using transaction history, estimate timelines and impacts, and prepare goal or commitment proposals that the user can edit, cancel, or confirm. Every task remains available manually in its management view.
5. **Companion expansion:** consolidate the cross-layer experience around grounded answers, supported action proposals, starter prompts, uncertainty handling, evaluation cases, and reliable fallback behaviour.

The detailed five-week delivery plan lives in [V2 roadmap](./roadmap.md). If a week cannot deliver a complete slice, its scope must be reduced rather than hiding unfinished infrastructure behind a later AI milestone.

## Main application views

These views describe the main areas of the application from the user's perspective. They are a navigation and experience map, not an implementation sequence. Some views support multiple core features, and optional capabilities appear when the user chooses to use them.

### Monthly Dashboard

The default private-area view for the active calendar month. It displays Income, One-time expenses, expected Recurring commitments, recorded recurring-commitment payments, Money left to spend, Available balance, the total Savings reserve, and recent records. Expected commitments appear as low-opacity records from the beginning of the month, while generated expense records appear normally once their scheduled date arrives. Money left to spend includes expected commitments, including the expected amount for Variable commitments.

The dashboard also shows whether the Goal allocation is active, the desired Goal allocation for the month, and the amount actually reserved from income so far. The Monthly result and monthly savings allocation remain calculation values rather than primary dashboard metrics.

The desired Goal allocation can be €0 when switched off, the amount defined by the Savings goal plan, or the maximum amount supported by the month's cashflow. The reserved amount can remain €0 until income is recorded and updates as income is added. Selecting the total Savings reserve opens the Savings Goals view with the individual goals and their progress. The dashboard provides quick access to add One-time expenses and Income manually or through AI-assisted entry methods, including natural-language, receipt image, and voice input. Recurring commitments are added and managed from the separate Recurring Commitments view.

### Transactions and Analytics

A full-history view for exploring the Transaction history across any selected period. The current calendar month is selected by default, with options for a specific month, quarter, year, custom date range, or all history. It combines headline metrics, charts, category breakdowns, search, filters, and the transaction list so users can review income, expenses, Cashflow, Savings reserve changes, and Savings goal progress when available.

The view can compare the current month with the previous month and with the same month in the previous year. Comparisons use the current month's provisional Monthly result and the final Monthly result for closed months. Money left to spend is shown for the active month but is not used as a historical comparison metric. Expected Recurring commitments appear separately from recorded recurring-commitment payments, so they remain visible without being double-counted.

Analytics distinguishes recorded recurring-commitment payments from expected Recurring commitments. Variable commitment payments remain marked as Estimated until the user updates the generated record with the actual amount. Yearly or prepaid commitments can remain visible through a Coverage period note without creating new expenses during the covered months.

Filters and search update both the transaction list and the displayed metrics and charts. Users can filter by income or expense, One-time expense, Fixed commitment, Variable commitment, category, B/U/C classification, reflective context tag, and date. Selecting a B/U/C classification or reflective context tag excludes records without that selected context; without a context filter, all records remain visible. Text search can match a named recurring commitment, notes, category, or reflective context tag. Users can edit or delete records here, including adding, changing, or removing optional classifications and tags, with a warning when a change may recalculate a past month and following balances.

The view may include short, deterministic insight messages based on the selected data. These messages describe patterns without making recommendations. Context-based insights analyze only records that contain the relevant B/U/C classification or reflective context tag. Empty periods or breakdowns show a brief explanation rather than being presented as zero-value financial results.

### Recurring Commitments

A separate management view for adding and editing Recurring commitments. Users can set the Fixed commitment or Variable commitment type, expected amount, Payment frequency, schedule, optional Coverage period, category, B/U/C classification, reflective context tag, start date, end date, or payment limit. B/U/C classification and reflective context tags are optional, and users can add, change, or remove them later from the same view. The view shows each commitment's status, next payment occurrence, expected monthly and yearly impact, and active-coverage note when applicable.

Users can pause, reactivate, cancel, or archive Recurring commitments from this view. Changes affect future generated expense records only. Existing records remain in the Transaction history and can be edited or deleted there.

### Savings Goals

A management and progress view for creating, editing, pausing, completing, cancelling, and archiving Savings goals. Each goal appears with its saved amount, target, progress bar, remaining amount, deadline or estimated completion time, planned contribution, current status, and contribution for the active month. The view also separates money assigned to goals from the Unassigned reserve and shows their relationship to the total Savings reserve. Users can change the active month's Goal allocation, make direct transfers, review contribution history, and withdraw from a goal without silently changing its target or deadline.

### AI Companion

A conversational view for asking questions about financial activity, exploring patterns, reflecting on priorities, and preparing reviewable actions. The active calendar month is used by default, while the user can ask about another month, quarter, year, custom date range, or all available history. Each answer makes its period and relevant data subset clear.

The Companion uses the deterministic metrics and insight messages available in Transactions and Analytics, together with categories, B/U/C classifications, reflective context tags, Recurring commitments, the Available balance, the Savings reserve, and Savings goals. It can explain patterns such as Choice spending associated with a category, expenses with a Need reflective context tag during a selected period, estimated Variable commitment records, or records missing optional context. The experience is insight-first: it describes observed patterns before discussing possibilities, and it only offers suggestions when the user's question explicitly asks for them. Any suggestion must be grounded in the user's application data and capabilities.

The view may show starter questions such as “Summarize my spending this month,” “What patterns do you see in my Choice expenses?”, “Which Variable commitments still have estimated amounts?”, “What One-time expenses are missing a B/U/C classification?”, and “Create a Savings goal draft for a €1,000 emergency fund by December.” When the user requests an action, the Companion returns a structured proposal for the relevant review flow. It cannot apply the proposal, skip validation, or make a financial decision on the user's behalf. The underlying calculations remain deterministic and visible. Before the user starts a conversation, the view clearly warns that AI responses can be incomplete or incorrect, proposed actions must be reviewed before confirmation, and the Companion does not provide financial advice.

### Settings

An account-level view for setting up the user's starting position, managing categories, choosing personal preferences, and making explicit reserve transfers. Settings clearly distinguishes values that affect financial calculations from display preferences and actions that change balances without creating transaction records.

#### Starting balances and reserve

The user can provide or edit a starting Available balance and a starting Savings reserve. The starting Savings reserve is treated as Unassigned reserve until the user explicitly assigns money to a Savings goal. Settings shows the two starting values separately and explains how they relate to the Available balance, Savings reserve, and Unassigned reserve.

Changing a starting balance is an account-level correction. Before it is saved, Settings explains that it may recalculate the Available balance, Savings reserve, and following monthly results. It does not create an Income or One-time expense record. The view preserves the distinction between money available for ordinary spending and money intentionally kept in the Savings reserve, including when a later calculation makes the Available balance negative.

#### Reserve transfers

The user can explicitly transfer money between the Available balance and the Unassigned reserve. Settings supports both directions, shows the source and destination balances before confirmation, and prevents a transfer from exceeding the selected source balance. Transfers are separate from Income, One-time expenses, recorded Recurring-commitment payments, and Savings goal contributions. They do not appear in Transaction history and do not change a transaction's category or date.

After a transfer, Settings confirms the change and immediately shows the updated Available balance, Unassigned reserve, and total Savings reserve. Transfers to a specific Savings goal belong in Savings Goals, where the goal's saved amount and contribution history are visible.

#### Categories

Settings lists the active and deactivated general categories used by Income and One-time expense forms. The initial One-time expense categories are Food and groceries, Housing and bills, Transport and fuel, Health, Travel and accommodation, Education, Entertainment, Shopping and personal care, and Other. The initial Income categories are Salary or wages, Freelance or contract work, Business income, Scholarship or study support, Benefits or pension, Gift or family support, Interest or other income, and Other.

The user can add categories and deactivate existing categories, but cannot rename the existing categories. The fixed reflective context tags Need, Love, Like, and Want are managed by the product and cannot be edited in Settings. Deactivating a category does not remove it from Transaction history or make historical records unreadable. Deactivated categories are not offered for new records, while records that already use them remain editable and understandable.

#### Preferences and account configuration

Settings provides personal preferences that do not alter financial calculations, such as the default period used by Transactions and Analytics, display density, and confirmation preferences. It distinguishes these preferences from starting balances and reserve transfers, which do affect account calculations.

The view may include account-level actions such as signing out and managing account details. It does not expose controls for bank or card connections, shared household finances, investments, tax reporting, or professional financial advice, which are outside V2 scope. Any setting that is not yet connected to a persisted data service is labelled clearly and does not imply that it has changed application calculations.

#### Settings safeguards

Settings uses supportive, non-judgmental language and explains the effect of consequential changes before confirmation. Saving preferences and category changes does not silently modify transaction amounts, dates, notes, B/U/C classifications, reflective context tags, Recurring commitments, Savings goals, or historical records. Changes to starting balances and reserve transfers provide a clear confirmation or success state and remain visible through the resulting balance changes.

## Detailed layer explanations

### Layer 1 extended: Transaction history, entry methods, and the Companion foundation

Layer 1 provides the complete transaction history and should be useful on its own. Users can add, view, edit, and delete income and one-time expense records for the current or past months. They can manage the initial general categories, search and review their records, and use manual forms or AI-assisted entry methods. The first version of the AI Companion is delivered in this layer, alongside the transaction history rather than after the other layers.

Each record includes an amount, category, date, and optional notes. Expense records may also include one optional B/U/C classification and one optional Need/Love/Like/Want reflective context tag. Income and expense forms may use different labels and categories, but both belong to the same transaction history. Named records such as Spotify or Mortgage belong to recurring commitments introduced in a later layer.

Layer 1 defines the optional context fields without requiring them for entry. **B/U/C** describes the user's control over an expense: Bill, Usage, or Choice. **Need/Love/Like/Want** describes the personal meaning of an expense: Need, Love, Like, or Want. These fields are separate from the general category, can be left empty, and can be added, changed, or removed after a record is created. The product must not infer them from a category, receipt, voice input, or other transaction detail.

Layer 1 supports three AI-assisted entry methods in addition to the manual form:

- **Natural-language entry:** the user describes an income or expense in their own words. The AI identifies whether it is income or an expense and proposes the amount, category, date, and notes for the matching form.
- **Receipt image entry:** the user takes or uploads a picture of a receipt. The AI interprets the receipt and proposes a one-time expense in the matching form, including the amount, date, category, and useful notes when they are available.
- **Voice entry:** the user records a voice message through browser-supported voice input. The application converts the message to text, and the AI interprets that text and proposes the fields for the matching income or expense form.

The AI should show the proposed transaction clearly, preserve uncertainty where the input is incomplete or ambiguous, and let the user correct any field before approval. It must not save a record, create a recurring commitment, or silently choose a category or date without the user's approval. The manual form remains available at all times and is the fallback when AI entry is unavailable or the user prefers to enter the record directly.

The Layer 1 Companion can answer questions about the transaction history, such as what the user spent in a period, which records match a description, how much was spent in a category, or which records are missing context. When the user asks it to create a transaction or edit an existing one, it prepares a structured proposal containing the operation and all affected fields. This includes a B/U/C classification or reflective context tag only when the user explicitly requests that change; the Companion must not infer or assign context automatically. The user can review, edit, cancel, or confirm the proposal. Confirmation applies the change through the normal transaction validation flow. The Companion cannot delete a record or make any other change without the same explicit confirmation.

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

Users should be able to add or deactivate categories from the Layer 1 category-management flow. Existing transaction history should remain understandable if a category is deactivated, and deactivated categories should not be offered for new records. The Companion may answer questions about categories and prepare a category-management proposal only when the user explicitly requests a supported change; it must not rename or deactivate a category automatically.

The quick-add experience should make one-time expense recording easy, whether the user enters the fields manually or approves an AI-generated draft. Layer 1 forms and record editing support the optional B/U/C classification and reflective context tag. Recurring-commitment management, fixed or variable commitment types, monthly calculations, analytics, savings goals, and richer context workflows belong to later layers. The Companion foundation is part of Layer 1; later layers expand its evidence, questions, and supported proposals.

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

#### Layer 2 Companion capabilities

The Companion uses the same deterministic Layer 2 calculation service as the dashboard. It can:

- explain Income, expenses, Monthly result, Money left to spend, Available balance, Savings reserve, Unassigned reserve, and monthly savings allocation;
- identify the period and records behind an answer, including whether the month is active or closed;
- explain how adding, editing, or deleting a transaction would affect the current month and following balances without applying the change;
- answer what-if questions such as “What would my Available balance be if I spent €100 less this month?” without changing the transaction history; and
- prepare proposals for supported Layer 2 actions: changing a starting Available balance or Savings reserve, switching savings allocation on or off, and transferring money between the Available balance and the Unassigned reserve.

Each Layer 2 action proposal shows the operation, amount or setting, source and destination when relevant, the balances before and after, and any recalculation or month-close effect. The user can edit, cancel, or confirm it. Confirmation uses the normal Layer 2 validation flow, checks the current balances and calculation state again, and applies nothing if the proposal is stale or invalid. The Companion cannot directly change balances, reserves, allocation settings, or transactions.

### Layer 3 extended: Analytics and awareness

Layer 3 provides a descriptive view of the user's financial activity. Its calculations and factual insight messages remain available when the AI Companion is unavailable. The Companion is an additional interface over these deterministic results: it does not replace the calculations, assign moral meaning to spending, or change records without a confirmed proposal.

#### Periods and default view

- **Default period:** the current calendar month.
- **Available periods:** current month, a selected month, quarter, year, custom date range, and all history.
- **Selected period:** all period-based metrics, charts, comparisons, and filtered records use the selected period unless a metric is explicitly identified as a current-state value.
- **Current-state values:** Available balance, total Savings reserve, and current Savings goal progress describe the user's current position and are not treated as period totals.

#### Headline metrics

For the current month, analytics displays:

- Income;
- recorded expenses, including recorded recurring-commitment payments;
- Money left to spend;
- planned Goal allocation, when Savings goals are in use;
- Reserved goal amount so far, when applicable;
- Available balance;
- total Savings reserve; and
- savings rate.

For other selected periods, the view prioritizes the period's income, expenses, Monthly result, monthly savings allocation or Goal allocation, and savings rate. Available balance and current Savings goal progress remain current-state values rather than being presented as amounts produced by the selected historical period.

Expected recurring commitments are displayed separately from recorded expenses. They may contribute to a projected expense view but must not be added to recorded expenses before the payment is actually recorded. This prevents expected commitments from being double-counted.

#### Savings metrics

Analytics distinguishes money intentionally directed to the Savings reserve from positive money that remains in the Available balance.

- **Planned savings rate:** the planned Goal allocation divided by income for the selected month, when a planned Goal allocation exists.
- **Actual savings rate:** the amount actually added to the Savings reserve divided by income. For an active Savings goal, this uses the Reserved goal amount.
- **Maximum allocation:** when the user selects the maximum supported allocation, the expected amount is the current positive Monthly result: income minus expenses. The expected savings rate updates as income or expenses change.
- **Disabled allocation:** when savings allocation is disabled, the savings-rate value is shown as `—` with the note “No savings allocation”. A positive Monthly result may still increase the Available balance and is not counted as money saved to the Savings reserve.
- **Active but unfunded allocation:** when allocation is active but no money has been reserved yet, the actual savings rate is 0%.
- **Past periods:** analytics shows the planned allocation when one existed, the amount actually added to the Savings reserve or reserved for a Savings goal, and the resulting actual savings rate.

The view may also show positive Available-balance growth separately so that users can distinguish cash retained for ordinary spending from money intentionally saved.

#### Charts and breakdowns

The initial V2 analytics view includes:

- income versus expenses for the selected period, with monthly points when the range contains multiple months;
- income and expenses by category;
- each category's percentage of total income or total expenses for the selected period;
- the B/U/C breakdown for expenses when classifications are available;
- the Savings reserve trend across months; and
- Savings goal progress and planned versus actual contributions when Savings goals are available.

B/U/C classification and Need, Love, Like, and Want reflective context tags are optional Layer 1 fields. Layer 3 analytics uses them when they are present without requiring them for a transaction. If no records contain a classification or reflective context tag, the relevant breakdown shows an empty state and does not block the remaining analytics.

#### Comparisons and factual insights

Users can compare the current month with the previous month and with the same month in the previous year. Comparisons apply to the main month-level cashflow and savings metrics, including income, expenses, Monthly result, planned or actual savings amounts, and savings rate. For the active month, Monthly result is provisional and is calculated from the transactions recorded so far. For closed or historical months, Monthly result is the final result for that month. Money left to spend is an active-month value and is not used as a historical comparison metric. Available balance and Savings goal progress are not treated as period comparisons by default because they represent current-state values.

Analytics may show short, deterministic insight messages based directly on the selected data, such as “Food represents 34% of your expenses this month” or “Expenses are €120 higher than last month”. These messages are descriptive only. They do not recommend actions or judge spending. The Layer 3 Companion can explain the same metrics, comparisons, and patterns through conversation, but the underlying calculations remain deterministic and visible.

#### Search, filters, and records

Search and filters apply to both the transaction list and the metrics and charts generated from that list. The initial filter set should remain simple while supporting the data needed for later analysis:

- income or expense;
- expense type: One-time expense, Fixed commitment, or Variable commitment;
- category;
- B/U/C classification, when available;
- Need, Love, Like, or Want reflective context tag, when available;
- date or selected period; and
- named recurring commitment, notes, category, or reflective context tag through text search.

The filtered view makes clear that its metrics represent the filtered subset rather than the user's full finances. Users can edit or delete records from the transaction list. After confirmation, any affected analytics, monthly calculations, and following balances update consistently with the Layer 2 rules. Changes to past records should show the existing recalculation warning before they are applied.

#### Layer 3 Companion capabilities

The Companion uses the exact period, search query, filters, and deterministic result set shown in Transactions and Analytics. It can:

- summarize the selected records and state whether the answer represents all records or a filtered subset;
- answer questions about categories, B/U/C classifications, reflective context tags, income, expenses, savings, and comparisons;
- explain charts, headline metrics, deterministic insight messages, empty states, and missing or estimated data;
- find records that match a natural-language description and identify records missing a classification or reflective context tag;
- compare supported periods and explain the records and calculations behind the difference; and
- prepare proposals to edit or delete selected transactions, or to add, change, or remove a B/U/C classification or reflective context tag, when the user explicitly asks.

Search, filtering, chart exploration, and asking for an explanation are read-only interactions and do not require confirmation. Any proposal that changes a record must show the selected records and all affected fields, then pass through the existing review, validation, and confirmation flow. The Companion must not treat a filtered subset as the user's complete financial picture or apply a bulk change without an explicit, reviewable proposal.

#### Empty states and V2 boundaries

When a selected period or breakdown has insufficient data, the application shows an empty state with a short explanation of what is missing, such as “Add income or expenses to see this comparison.” Empty analytics states should not be treated as zero-value financial results.

Export is outside the initial Layer 3 V2 scope. Financial advice, autonomous recommendations, and unconfirmed AI-generated changes remain outside this layer.

### Layer 4 extended: Savings goals

Layer 4 adds purpose-based saving on top of the Savings reserve. Users manage goals from the separate Savings Goals view, while the Monthly Dashboard shows the total Goal allocation and lets the user control the active month's amount.

#### Goal setup and contribution plans

A Savings goal has a name and can be one of the following:

- **Target goal:** has a target amount and may have a deadline. It becomes Completed when its saved amount reaches the target.
- **Open-ended goal:** has no target or deadline and continues to accumulate, such as a general emergency fund.

Users can create multiple goals. A goal with a target can use either of these contribution plans when it does not have a deadline:

- a fixed monthly amount; or
- a percentage of the user's recorded monthly income.

For a goal with a target and deadline, the application calculates the planned contribution automatically:

`Remaining target amount ÷ months remaining`

The application can show the estimated number of months or estimated completion date for a goal without a deadline. The estimate uses the goal's current contribution plan and updates when the saved amount, contribution plan, or income changes.

When a percentage-based goal has no income history, the application does not estimate a completion time. It starts estimating after income is recorded. A goal without a recurring contribution plan can still receive direct transfers, but the application shows the remaining amount rather than an estimated completion time.

The contribution plan is a planning value. The actual Reserved goal amount can be lower when the user has insufficient cashflow, turns the Goal allocation off, or records a deficit.

#### Goal priority and monthly allocation

The total planned Goal allocation is the sum of the planned contributions for all active goals. The Monthly Dashboard displays this total for the active month.

For the active month, the user can choose:

- **€0:** no money is reserved for goals during the month;
- **planned allocation:** the application uses the total planned Goal allocation; or
- **maximum:** the application reserves the maximum positive amount supported by the month's cashflow.

The maximum supported amount is based on income, expenses, and expected Recurring commitments:

`Maximum Goal allocation = max(0, income − expenses − expected Recurring commitments)`

The Goal allocation is also limited by the money available from income for the month. It cannot create money or increase a deficit.

When several goals are active, the application distributes the actual Reserved goal amount in this order:

1. Goals with deadlines, ordered by the nearest deadline.
2. Goals without deadlines.

Within the same priority group, the application distributes money proportionally to each goal's planned contribution. For example, if two goals have planned contributions of €100 and €50, they receive two-thirds and one-third of the amount available to that group.

When the user chooses the maximum amount, money above the total planned allocation goes first to the most urgent incomplete goal. When that goal reaches its target, the remaining amount goes to the next incomplete goal.

Goals without deadlines receive their planned contribution when the user selects the planned allocation. They can also receive leftover money after deadline goals are funded when the user selects the maximum allocation. An open-ended goal without a target remains active and can continue receiving contributions.

#### Month close and reserve ownership

At month close, the actual Reserved goal amount is assigned to the applicable goals and increases both their saved amounts and the Savings reserve. The goal contribution history remains visible.

If there are no active Savings goals, positive money directed to savings goes to the Unassigned reserve. If active goals receive less than the available positive result, the remaining amount also goes to the Unassigned reserve. When the user sets the active month's Goal allocation to €0, the positive Monthly result remains in the Available balance instead.

The Unassigned reserve is not automatically assigned to a goal. The user can explicitly transfer it to a specific Savings goal or to the Available balance. Similarly, the user can transfer money from the Available balance to the Unassigned reserve or to a specific Savings goal. Transfers are separate from income, expenses, and goal contributions.

Direct transfers increase a goal's saved amount immediately. They do not change the goal's target, deadline, or future contribution plan. When a goal reaches its target through monthly contributions or direct transfers, it becomes Completed automatically.

#### Deficits and withdrawals

When a month closes with a negative result, the application covers the deficit in this order:

1. Available balance;
2. Unassigned reserve; and
3. a specific Savings goal only after the user explicitly chooses to withdraw from it.

The application does not automatically withdraw money from a goal. If the Available balance and Unassigned reserve are insufficient, the user can transfer money from the Unassigned reserve, withdraw from a selected goal, reduce or pause a future contribution, or leave the Available balance negative.

Withdrawing from a Savings goal reduces its saved amount and increases its remaining amount. The application recalculates the future contribution needed to meet the original deadline, but it does not change the target or deadline without the user's action. If the recalculated contribution is not realistic, the application shows alternatives such as extending the deadline, lowering the target, reducing the contribution, or pausing the goal.

#### Goal lifecycle

Users can pause, reactivate, complete, cancel, or archive goals:

- **Active:** the goal participates in planning and allocation.
- **Paused:** the goal remains visible but does not receive new planned contributions until reactivated.
- **Completed:** the goal has reached its target and remains visible with its progress at 100%. The user can archive it or withdraw money from it later.
- **Cancelled:** the goal stops receiving contributions and remains visible with its contribution history.
- **Archived:** the goal is hidden from the normal active list, while its history and financial effects remain available.

Completing a goal does not automatically move or spend its money. If the user later wants to use the money, they withdraw or transfer it to the Available balance and record the actual purchase as a normal expense. The expense is not automatically linked to the goal. Any remaining money stays assigned to the goal until the user transfers it elsewhere.

Changing a goal's target, deadline, or contribution plan affects future planning. Past contribution history remains intact, and the application does not change the target or deadline silently.

#### Layer 4 Companion capabilities

The Companion uses the deterministic Savings goal and cashflow calculations rather than creating its own financial model. It can:

- explain each goal's saved amount, target, remaining amount, progress, status, contribution history, planned contribution, and estimated completion time;
- reflect on a possible goal using recorded income, expenses, Available balance, Savings reserve, and previous savings patterns;
- estimate a feasible contribution, target date, or time to reach a target, while stating the period, assumptions, and limitations behind the estimate;
- compare possible contribution amounts or deadlines and explain how they would affect the estimated timeline; and
- prepare proposals to create, edit, pause, reactivate, complete, cancel, archive, contribute to, withdraw from, or change the allocation of a Savings goal when the user explicitly asks.

A goal proposal must show the goal name, target, deadline, contribution plan, proposed allocation, and estimated effect before confirmation. It must distinguish an estimate from a committed result and must not invent a user's priorities or treat a suggested goal as financial advice. The user can edit, cancel, or confirm the proposal. Confirmation uses the normal Savings Goals validation flow, checks current income, balances, goal status, and allocation limits again, and reports success or failure. The user can always open Savings Goals and perform the same task manually.

### Layer 5 extended: Recurring commitments

Layer 5 lets users define and manage Recurring commitments and see their expected effect before each payment is recorded. A Recurring commitment is managed separately from the quick One-time expense form. The user creates it from the Recurring Commitments view, and the application creates linked expense records in the Transaction history according to its schedule.

#### Commitment setup

Each Recurring commitment has an internal identifier that remains stable even when the user changes its name. This identifier links all generated expense records to the same commitment. Names do not need to be globally unique. Renaming a commitment updates the displayed name for its linked records without breaking their history.

The initial commitment fields are:

- name;
- fixed or variable commitment type;
- expected amount;
- Payment frequency;
- scheduled day or date;
- start date;
- optional Coverage period;
- optional end date or maximum number of payments;
- expense category;
- B/U/C classification;
- optional Need, Love, Like, or Want reflective context tag; and
- optional notes.

The initial Payment frequency options are monthly, every X months, and yearly. Yearly is a separate option from every X months, even though both may produce a twelve-month interval. The application uses the selected date as the basis for future payment occurrences.

Payment frequency determines when the application creates an expense record. When a Coverage period applies, it matches the Payment frequency. For example, a monthly subscription covers one month, a payment every three months covers three months, and a yearly membership covers twelve months. A commitment such as rent or electricity can have no Coverage period. Payment plans where the payment interval and coverage period differ are outside the initial V2 scope.

If a monthly commitment is scheduled for a day that does not exist in a particular month, the application uses the last day of that month. For example, a commitment scheduled for the 31st is applied on February 28th or 29th and April 30th. Future occurrences continue to use the original schedule rather than permanently changing the commitment's selected day.

The user can change the amount, date, Payment frequency, category, classification, context tag, notes, end date, or payment limit. When a Coverage period applies, it updates with the Payment frequency so the two remain aligned. Changes to the Recurring commitment affect future occurrences only. Existing generated records retain their current values and can be edited individually from the Transaction history.

#### Fixed and variable commitments

- **Fixed commitment:** the expected amount is known and is used for each occurrence until the user changes the commitment amount.
- **Variable commitment:** the user enters an expected amount. The application uses that amount for projections and calculations until the user edits the generated record with the actual amount.

A variable generated record remains visibly marked as **Estimated** until its amount is changed by the user. The user is responsible for keeping actual variable amounts accurate. Once the amount is confirmed, the record is displayed like a normal generated expense, although it remains linked to the recurring commitment and can still be edited later.

#### Scheduled and generated records

Active Recurring commitments produce linked expense records on their scheduled dates. If the application was not open on the scheduled date, it creates the missed record when the user next opens the application and preserves the original scheduled date.

The application also displays the current month's upcoming occurrences from the beginning of that month. These appear as low-opacity records marked **Upcoming** or **Expected**, so the user can see the commitments that will affect the month even before their scheduled dates arrive. Upcoming records use the expected amount, including the estimate for variable commitments.

When the scheduled date arrives, the upcoming record becomes a normal generated expense. The generated record is clearly identified as having been created automatically and contains a link to its recurring commitment.

If a commitment is created with a start date in the past, the application generates all applicable missed records from that start date. These records use the original scheduled dates. Variable missed records use the expected amount and remain marked as Estimated until the user corrects them. Creating past records may recalculate affected historical months and following balances, so the application shows the existing recalculation warning before applying the change.

A commitment paid in one transaction is recorded at its full actual amount in the month in which the payment occurs. If it has a Coverage period, the Recurring commitment remains visible during that period with a note such as “Paid until March 2027.” It does not create another expense or reduce Money left to spend until the next payment is due. This supports yearly memberships, quarterly subscriptions, and other prepaid services without treating the covered months as new expenses.

#### Calculations and double-counting

Expected recurring commitments are included in monthly planning before their payment date. Money left to spend is calculated as:

`Income − One-time expenses − recorded recurring-commitment payments − expected recurring commitments − Goal allocation`

Expected variable commitments use their current estimated amount. This means Money left to spend can be negative when commitments are expected but income has not yet been recorded for the month.

Expected Recurring commitments are shown separately from recorded expenses in analytics and must not be added to recorded expenses a second time after their payment becomes a generated record. Analytics distinguishes:

- recorded recurring-commitment payments;
- expected Recurring commitments;
- estimated Variable commitment payments; and
- total expected commitment amount.

The same commitment identifier prevents a generated record from being duplicated. If the user deletes an upcoming or generated occurrence, the application records that this specific occurrence was intentionally removed and does not recreate it. Future occurrences continue according to the commitment's schedule.

The One-time expense form does not include a commitment name field. Users can still enter notes such as “Spotify,” but the application does not automatically treat that One-time expense as part of a Recurring commitment. Users manage Recurring commitments only through the Recurring Commitments view.

#### Commitment status and lifecycle

- **Active:** the application displays expected occurrences, includes them in planning, and creates generated expense records according to the schedule.
- **Paused:** the application stops creating future generated expense records and removes future expected amounts from planning. Existing records remain visible. The user can reactivate the commitment later without losing its history.
- **Cancelled:** the application stops future generated expense records and future planning while keeping the commitment and its history visible.
- **Archived:** the commitment is hidden from the normal management list. Its historical records and financial effects remain available in transaction history and analytics.

Pausing or cancelling a Recurring commitment before its scheduled date prevents that occurrence from being created. Pausing or cancelling it after an occurrence has already been created does not remove that existing record. Reactivating a commitment resumes future occurrences according to its current schedule. The user can change the date or other schedule details when the external subscription or payment date changes; those changes affect future occurrences only.

An active commitment stops automatically when its optional end date is reached or its maximum number of payments has been generated. The user may also pause or cancel a commitment manually when they decide to stop or temporarily suspend it.

#### Recurring Commitments view

The Recurring Commitments view lists the user's commitments, their status, Payment frequency, Coverage period when applicable, expected amount, next payment occurrence, and expected monthly and yearly impact. It shows separate totals for expected Fixed commitments and Variable commitments.

Users can add, edit, pause, reactivate, cancel, and archive Recurring commitments from this view. They can also update the expected amount of a Variable commitment, manage its Payment frequency, and change its schedule. When a Coverage period applies, it stays aligned with the Payment frequency. Editing a commitment does not silently modify past generated records.

The view may show an active-coverage note for commitments paid in advance, such as “Paid until March 2027.” This note communicates that the commitment remains relevant without treating the covered months as new expenses.

#### Layer 5 Companion capabilities

The Companion uses the deterministic Recurring commitment schedule and planning calculations. It can:

- list and summarize active, paused, cancelled, and archived commitments;
- explain the next payment, Payment frequency, Coverage period, expected monthly and yearly impact, and the difference between expected, estimated, and recorded amounts;
- identify commitments with estimated Variable amounts, upcoming payments, missed occurrences, or possible double-counting concerns;
- explain how a commitment affects Money left to spend and a selected period without treating an expected payment as a recorded expense; and
- prepare proposals to create, edit, pause, reactivate, cancel, or archive a Recurring commitment, or to confirm the actual amount of a Variable commitment, when the user explicitly asks.

A commitment proposal must show the name, type, amount or estimate, schedule, category, optional context, Coverage period, lifecycle dates, and expected financial impact. The user can edit, cancel, or confirm it, or complete the same task manually in Recurring Commitments. Confirmation uses the normal commitment validation flow, checks the current schedule and existing generated records again, prevents duplicate occurrences, and reports success or failure. The Companion must not infer a recurring commitment from a one-time transaction or create one without an explicit user request and confirmation.

### Layer 6 extended: Context-aware reflection

Layer 6 deepens reflection on the optional context already available from Layer 1 and used by Layer 3 analytics. It helps users combine context with categories, commitments, goals, and priorities to identify patterns that are not visible through categories alone. The context is descriptive rather than judgmental. It does not change the cashflow, savings, or balance calculations, and it is not required to record an expense.

#### Categories remain required

Every income and expense record continues to use one general category from Layer 1. The category is the only required classification. Users can use **Other** when no available category describes the record. They can add new categories or deactivate existing categories from Settings, but they cannot rename the existing categories. Deactivating a category does not remove it from existing records or make their history unreadable.

Layer 6 does not replace the category with a more personal label. The B/U/C classification and reflective context tags introduced in Layer 1 add context alongside the general category.

#### B/U/C classification

An expense may optionally receive one B/U/C classification:

- **Bill:** a fixed commitment such as rent, a mortgage, or an installment payment;
- **Usage:** an expense that changes according to consumption, such as electricity, water, gas, or mobile data; or
- **Choice:** spending the user can increase, reduce, replace, or stop, such as entertainment, shopping, eating out, or flexible subscriptions.

The classification is optional and remains separate from the expense category. For example, an expense can be categorized as Food and classified as Choice. Users can add, change, or remove the classification when reviewing an existing expense.

#### Reflective context tags

An expense may optionally receive one reflective context tag. The available tags are fixed and cannot be renamed or edited by the user:

- **Need:** necessary for basic wellbeing or functioning;
- **Love:** creates lasting value or joy;
- **Like:** creates temporary enjoyment; or
- **Want:** mainly immediate gratification.

Reflective context tags add personal meaning to an expense. They do not replace the general category, represent a moral score, or determine whether the expense was right or wrong. Users can add, change, or remove a tag when reviewing an existing expense.

An expense can have both one B/U/C classification and one reflective context tag. For example, a Food expense can be classified as Choice and tagged Love. Records can also have only one of these optional fields or neither of them.

#### Entry and editing

The Layer 1 manual expense form and record editor include the optional B/U/C classification and reflective context tag, but the user can leave both fields empty. The AI-assisted entry methods interpret the required category and may include context only when the user explicitly requests it. They do not infer or silently assign B/U/C classifications or reflective context tags. The user can add, change, or remove those fields while reviewing a proposed record or later from the Transaction history.

Adding, changing, or removing context does not alter the amount, date, category, or cashflow calculations. If the user edits other fields on a past record at the same time, the existing recalculation warning applies.

#### Recurring commitments

Recurring commitments accept the same optional B/U/C classification and reflective context tag as one-time expenses. Users can set these fields when creating a commitment and add, change, or remove them later from the Recurring Commitments view.

When a Recurring commitment creates a generated expense record, the record receives the commitment's current category, B/U/C classification, and reflective context tag. Changes to a commitment affect future generated records only. Existing generated records retain their current values and can be edited from the Transaction history.

The AI-assisted entry methods must not infer or silently create or modify these classifications when proposing an income or expense. If the user explicitly requests a context change, the Companion may include it in a proposal, but the user remains responsible for reviewing and confirming the generated or manually entered record.

#### Filters and contextual analytics

Transactions and Analytics supports filters for B/U/C classification and reflective context tags. When the user selects a classification or tag filter, records without the selected context are excluded from the transaction list, metrics, charts, and insight messages. Without a context filter, records with and without optional context remain visible together.

Context-based breakdowns analyze only records that contain the relevant context. For example, the B/U/C breakdown uses expenses with a B/U/C classification, and the reflective-context breakdown uses expenses with a reflective context tag. Records without the relevant field are not placed into an “Unclassified” group and do not affect that breakdown. If no records in the selected period contain the relevant context, the view shows an empty state while the remaining analytics remain available.

The optional context fields can be combined with each other and with expense categories. Users can explore patterns such as Choice spending within Food, Need-tagged expenses within Health, or expenses that match a category, a B/U/C classification, and a reflective context tag at the same time. Filtered metrics and charts must make clear that they represent the selected subset rather than the user's full finances.

#### Deterministic insights and the AI Companion

The deterministic insight messages from Layer 3 expand to use B/U/C classifications and reflective context tags when the selected data contains them. These insights describe patterns without judging the user's choices or recommending a classification. They analyze only records containing the relevant context and do not treat missing tags as a financial result.

The AI Companion can use categories, B/U/C classifications, reflective context tags, and the user's other recorded data to explain patterns and support financial reflection. It may help the user think about priorities, compare contextual spending across periods, or explore what their records show. It must not infer or apply B/U/C classifications or reflective context tags. If the user explicitly asks for a supported classification or tag change, it may prepare a proposal, but the user must review and confirm it before the record changes.

#### Layer 6 boundaries

Layer 6 does not include customizable reflective tags, multiple B/U/C classifications per expense, automatic tag assignment, or Money dials. It does not make context mandatory and does not use B/U/C or reflective tags to judge spending, enforce budgets, or alter savings allocations. Recommendations and conversational interpretation remain responsibilities of the optional AI Companion, which begins in Layer 1 and expands through Layer 7.

### Layer 7 extended: AI Companion expansion

Layer 7 provides the expanded conversational interface for understanding and acting on the user's own financial data. The AI Companion was introduced in Layer 1 for transaction-history questions and reviewable transaction proposals. In this layer it becomes insight-first across the full product: it explains recorded activity, summarizes patterns, identifies incomplete or estimated information, and prepares supported proposals before the user confirms them. It uses the same deterministic metrics, calculations, B/U/C classifications, reflective context tags, Savings goals, Recurring commitments, and analytics that are visible elsewhere in the application. It does not create a separate financial model or replace the application's calculations.

#### Companion purpose and scope

The AI Companion helps the user understand what their Transaction history shows and reflect on how their spending relates to their priorities. It can:

- summarize Income, One-time expenses, recorded recurring-commitment payments, Cashflow, Money left to spend, Available balance, Savings reserve, and Savings goal progress;
- compare periods and explain meaningful changes between them;
- summarize One-time expenses by category, B/U/C classification, reflective context tag, or combinations of those fields;
- explain how the B/U/C model is intended to describe spending as Bill, Usage, or Choice;
- explain how Need, Love, Like, and Want tags are intended to add personal context without judging the user's choices;
- identify records that are incomplete, estimated, or missing optional context;
- explain how existing Income history, spending patterns, and Goal allocation settings relate to a possible Savings goal; and
- answer questions about the user's Transaction history using the application's available data.

The Companion does not search for external financial opportunities, recommend unrelated lifestyle changes, provide investment or tax guidance, or act as a general financial advisor. For example, it may discuss whether reducing recorded Choice expenses with a Want reflective context tag could help a Savings goal progress faster, but it must not tell the user to find cheaper housing or change a provider unless that information and functionality exist inside the application.

#### Data scope and periods

The Companion can access all application data available to the user, including Transaction history, categories, B/U/C classifications, reflective context tags, Recurring commitments, expected and actual amounts for Variable commitments, Savings goals, contribution history, the Available balance, the Savings reserve, reserve transfers, analytics, and deterministic insight values.

The active calendar month is the default period when the user does not specify one. The user can ask about another month, quarter, year, custom date range, or all available history. When a question concerns a selected period, the Companion uses the same period definitions and calculation rules as Transactions and Analytics.

Every answer that reports or interprets financial data must make its data scope clear. It should state the relevant period and, when material, the subset or exclusions used. For example, an answer may say that it is based on January through March 2026, or that a B/U/C summary excludes expenses without a B/U/C classification. It must not present a filtered subset as the user's complete financial picture.

#### Insight-first responses

The Companion describes observed facts and patterns before discussing possibilities. It does not proactively turn every pattern into advice. Suggestions are appropriate only when the user asks for them explicitly or uses wording that clearly requests them, such as “suggest,” “what could I change,” or “how could I reach this goal faster.”

Suggestions must be grounded in the user's recorded data, the application's analytics, its B/U/C classifications and reflective context tags, or an existing application capability. A suggestion may identify a possible effect, such as reducing Choice expenses with a Want reflective context tag, but must not present that possibility as a required action or a moral judgment. The Companion should acknowledge when the data is insufficient to support a meaningful suggestion.

The Companion may provide concise answers by default. If the user asks for details, it can explain the underlying records, formulas, comparisons, assumptions, and exclusions in more depth.

#### Questions and starter prompts

The AI Companion view may provide starter questions to help users understand what it can do. Initial examples include:

- “Summarize my spending this month.”
- “What patterns do you see in my Choice expenses?”
- “How much did I spend on expenses with a Want reflective context tag?”
- “Which Variable commitments still have estimated amounts?”
- “What One-time expenses are missing a B/U/C classification?”
- “How could my current spending affect my Savings goal?”

These prompts are examples, not a fixed limitation. The user can ask other questions as long as they relate to the data and capabilities available in the application.

#### Savings goal support

The Companion can help the user think through a potential Savings goal by using the application's goal rules and recorded data. It may explain an estimated time to reach a target, compare the target with previous income or savings patterns, identify a possible monthly contribution, or describe how different contribution amounts would affect the estimated timeline. If the user asks, it may prepare a Savings goal proposal with fields such as name, target, deadline, and contribution plan.

The Companion must not create, edit, pause, complete, cancel, archive, or contribute to a Savings goal without a confirmed proposal. It must not change a Goal allocation, transfer money, or update a transaction without the same explicit confirmation boundary. After receiving a proposal, the user remains responsible for reviewing the fields and confirming or rejecting it.

#### Action proposals and boundaries

The Companion can read the user's permitted application data and can prepare structured action proposals. It cannot directly save a record, modify a category, add or remove a B/U/C classification or reflective context tag, update a Recurring commitment, change a Savings goal, transfer money, or alter the Available balance or Savings reserve. A proposal may pre-fill the relevant application form or review surface, but the user must be able to inspect every field and explicitly confirm before the normal application command applies it.

The application must treat proposals as untrusted input. It validates ownership, permissions, required fields, supported values, dates, amounts, balance rules, and conflicts again at confirmation time. A stale proposal must be rechecked or rejected rather than applied against changed data. The UI should show a clear success or failure state after confirmation.

The Companion must not assign, infer as fact, or silently add a B/U/C classification or reflective context tag. It can summarize records that already contain those fields and can report which records are missing them. The user is responsible for adding, changing, or removing context in the appropriate application view.

#### Uncertainty and incomplete data

The Companion must clearly communicate uncertainty and data limitations. It should warn the user when an answer is affected by estimated Variable commitment amounts, missing B/U/C classifications, missing reflective context tags, incomplete transaction history, an empty or very small selected period, or goal information that is insufficient for a reliable estimate.

It may answer questions such as which records still need confirmation of their actual Variable commitment amount or which One-time expenses have no B/U/C classification. It should identify the relevant records and explain what is missing. If the user asks it to fill in a supported field, it may prepare a proposal, but it must not update the record automatically.

The Companion must distinguish recorded facts, calculations, interpretations, and possibilities. It should not invent missing transactions, assume that an expense without a reflective context tag belongs to a particular context, or describe an estimate as a confirmed result.

#### Conversation, language, and user trust

Conversations are temporary and stateless. The Companion does not retain conversational memory or use previous chats to build a user profile. Each conversation is grounded in the application data available at the time it is opened or asked a question.

The initial Companion experience is in English. Notes or records may contain other languages, but multilingual responses and a user-selectable language preference are outside the initial Layer 7 scope.

The tone is neutral and supportive. The Companion must avoid shame, guilt, moral judgments, pressure, and overconfident financial conclusions. Before the user starts a conversation, the AI Companion view must clearly explain that AI responses can be incomplete or incorrect, that users should review and double-check results, and that the Companion is not a financial advisor. This notice should remain easy to find while using the feature.

#### Layer 7 boundaries

Layer 7 does not include persistent chat history, user-specific memory, external financial research, bank or card data, investment or tax advice, automatic classification, automatic tagging, autonomous recommendations, or unconfirmed actions that change application data. It does include user-confirmed proposals for supported application actions. It does not replace deterministic calculations or the manual flows for managing transactions, commitments, balances, and Savings goals.

## Boundaries

V2 is a personal finance tool for individual users. It covers income and expense tracking, monthly cashflow, the Available balance, the Savings reserve, analytics, Savings goals, recurring commitments, richer spending context, and the optional AI Companion. It also supports AI-generated transaction drafts from natural-language descriptions, receipt images, and voice input. Users must review and approve these drafts before they are saved.

V2 does not include bank or card connections, automatic transaction imports, shared household finances, business accounting, investment execution, tax reporting, or professional financial advice. Debt and installment commitments may be represented for visibility, but detailed payoff planning is outside the initial V2 scope.

AI features are optional and must remain explainable and user-controlled. AI may interpret input, explain recorded data, suggest possibilities, and prepare proposals for supported actions, but it must not apply changes or decisions without explicit user confirmation. The data model, transaction fields, technical architecture, browser API choices, and entity relationships belong in the architecture document rather than this PRD.

## Definition of success

V2 is successful when an individual user can maintain a reliable transaction history for income and expenses, understand their selected month's cashflow and balances, and review spending patterns through analytics. They should also be able to manage recurring commitments and Savings goals that support their priorities.
