# Expense Tracker V2 — Five-Week Roadmap

This roadmap turns the V2 PRD into five small, user-visible delivery slices. The goal is to start building the AI Companion immediately while keeping financial calculations deterministic and the product useful without AI.

The roadmap is intentionally outcome-led. Each week should end with something a user can try, not only a completed backend layer. Dates are omitted so the plan can start in the next available development week.

## Working principles

- Build one thin vertical slice at a time: data model, API, UI, deterministic calculations, and one Companion use case.
- Treat the deterministic calculation service as the source of truth. The Companion receives a structured context or evidence object; it does not query tables or calculate balances on its own.
- Keep every AI flow optional, grounded, reviewable, and safe to disable. AI may prepare an action proposal, but only explicit user confirmation can apply it.
- Start with a narrow question set and explicit evaluation examples instead of building an open-ended chatbot first.
- Do not add a feature to the roadmap unless it creates a user-visible outcome within the same week.

## Week 1 — Complete transaction history with the Companion foundation

**User value:** The user can manage their full transaction history, use the easiest available entry method, and ask the Companion about transactions or request a reviewable transaction change.

**Build:**

- Define the V2 transaction contract for income and one-time expenses while preserving existing MVP behaviour.
- Complete transaction-history CRUD for income and one-time expenses, including search and record selection.
- Add initial category management: list, add, deactivate, validate, and preserve historical categories.
- Add optional B/U/C classification and Need/Love/Like/Want reflective context fields to Layer 1 forms, record editing, and transaction storage.
- Add manual, natural-language, receipt, and voice entry boundaries. The manual form must remain complete even if AI entry is unavailable.
- Add a Companion entry point that answers questions about transaction history and selected periods.
- Let the Companion prepare transaction creation, edit, and deletion proposals with explicit review, cancel, edit, and confirm states.
- Create a deterministic summary service that returns the selected period, totals, categories, record counts, and missing-data notes.
- Define the proposal shape and confirmation boundary, even if the first week only supports transaction drafts.
- Pass the summary service output to the AI as structured evidence. Include the period in every answer.

**Done when:** A user can manage income and expenses manually, add or edit optional context, ask the Companion about their transaction history, and request a transaction or context change without anything changing until they confirm the reviewed proposal. Add at least five fixed evaluation cases, including an empty month, a month with income and expenses, an ambiguous request, and a rejected proposal.

## Week 2 — Monthly cashflow, reserve, and Companion actions

**User value:** The user can understand what is left to spend and how saving changes their current position, then ask the Companion to prepare a balance or reserve action for confirmation.

**Build:**

- Implement Monthly result, Money left to spend, Available balance, Savings reserve, and the Layer 2 month-close rules.
- Add starting balances and the smallest safe balance correction flow needed for testing.
- Show the formulas or a short “how this was calculated” explanation in the UI.
- Expand the Companion with questions such as “How much do I have left to spend?”, “Why did my reserve change?”, and “What if I spend €100 less this month?”
- Let the Companion prepare proposals for changing starting balances, switching savings allocation, and transferring money between Available balance and Unassigned reserve.
- Show the affected balances, recalculation effects, validation state, and Confirm, Edit, and Cancel actions for every Layer 2 proposal.
- Make the evidence object distinguish current-state values from selected-period totals.

**Done when:** The dashboard and Companion agree for positive, negative, zero, and changed-income cases. The user can see when a value is provisional and when it reflects a month-close calculation. A confirmed Layer 2 proposal changes the correct balance or setting, while a cancelled, stale, or invalid proposal changes nothing.

## Week 3 — Analytics, search, filters, and Companion exploration

**User value:** The user can explore the transaction history through analytics, search, filters, and comparisons, then ask the Companion about exactly the records and period they are viewing.

**Build:**

- Add selected month, quarter, year, custom range, and all-history queries, starting with the smallest useful set.
- Add category breakdowns, period comparisons, search, filters, charts, and deterministic insight messages.
- Use the Layer 1 B/U/C and Need/Love/Like/Want fields in breakdowns and filters without making them mandatory.
- Add Companion prompts for a selected-period summary, a filtered subset, a comparison, missing context, and a descriptive B/U/C or reflective-context pattern.
- Let the Companion find matching records and prepare reviewed proposals to edit or delete records, or add, change, or remove context on selected records.
- Make filtered subsets, exclusions, and untagged records explicit in the evidence and response.

**Done when:** A user can compare two periods, search and filter records, understand what the analytics includes, and ask the Companion about the selected data without it inventing classifications or treating a filtered subset as the whole picture. Any record or context change still requires explicit confirmation.

## Week 4 — Planning with goals and recurring commitments

**User value:** The user can connect current spending with upcoming obligations and a concrete savings purpose.

**Build:**

- Deliver the smallest complete Savings goal slice: create a goal, show progress, calculate a planned contribution, estimate a timeline, and record an explicit contribution or allocation.
- Deliver the smallest complete Recurring commitment slice: create a fixed commitment, show its next expected payment, and include it in the projected monthly view without double-counting recorded payments.
- Expose deterministic goal and commitment evidence to the Companion.
- Add questions about goal progress, affordability, deadlines, estimated timelines, expected commitments, variable estimates, and the difference between expected and recorded amounts.
- Let the Companion reflect on a possible goal using transaction history and prepare a Savings goal plan with target, deadline, contribution amount or percentage, and estimated completion time.
- Let the Companion prepare a fixed Recurring commitment proposal and proposals for supported edits or lifecycle changes.
- Show every proposed field, assumption, expected impact, validation state, and Confirm, Edit, and Cancel actions. Keep the Savings Goals and Recurring Commitments pages fully usable for manual management.

**Done when:** A user can see what is planned, what is recorded, and what remains available. The Companion can answer questions, estimate goal timelines, and prepare goal or commitment proposals, but nothing changes until the user confirms it through the normal validated application flow. The same actions remain possible manually from both management pages.

## Week 5 — Companion expansion, trust, and release readiness

**User value:** The user has one dependable place to ask grounded questions about their finances and knows when an answer needs checking.

**Build:**

- Consolidate the Companion view, starter prompts, period selection, conversation states, loading/error/empty states, and the AI disclaimer.
- Add a structured Companion context builder that exposes only the signed-in user's permitted data.
- Add provider failure fallback, incomplete-data messaging, response length limits, and logging that excludes sensitive raw prompts where possible.
- Add proposal validation, stale-data checks, duplicate-submission protection, cancellation, and clear success/failure states after confirmation.
- Test the Companion against representative cases: empty data, one record, missing optional context, estimated commitments, negative balance, multiple periods, and ambiguous questions.
- Review the five-week slices for accessibility, mobile use, privacy, and accidental mutation paths.

**Done when:** The Companion answers the supported question set with grounded evidence, identifies uncertainty, prepares supported action proposals, requires explicit confirmation before mutation, refuses unsupported actions safely, and leaves the core tracker fully usable when the AI is disabled.

## Scope guardrails

The five-week plan does not include bank or card connections, persistent chat memory, autonomous actions, automatic classifications, investment or tax advice, shared finances, or a complete voice/receipt pipeline. Confirmed proposals for supported actions are included from Layer 1; autonomous or unconfirmed mutations are not. Broader action coverage can be evaluated after the Companion expansion proves that grounded explanations and proposals create value.

If implementation capacity is lower than expected, preserve the order and reduce breadth: complete the current week's end-to-end slice before starting the next layer. The first slice to cut is breadth of prompts, not deterministic correctness, manual entry, or user control.

## First step

Start with Week 1 by writing the transaction evidence and action-proposal contracts, then trace these flows end to end:

> “Summarize my spending this month.”

> “Create a €40 expense for groceries today.”

Before adding a chat UI, make sure the same structured evidence can power the transaction view, API responses, automated tests, and Companion answers. The proposal must flow through the normal form or command validation after confirmation. These contracts are the foundation for every later AI answer and action.
