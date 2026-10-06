# V2 Product Context

## Product direction

Expense Tracker is a personal money companion that helps users turn everyday financial activity into a clearer sense of control and progress. It brings income, expenses, monthly availability, savings, and financial priorities into one place so users can understand where their money is going, know what they can safely spend, and gradually direct more money toward the life they want.

V2 is built on the existing expense-tracking MVP. The MVP behaviour remains available and stable while the product grows through implementation layers. Each layer must provide a useful user outcome and remain usable when AI is unavailable.

## Target user and boundaries

The product is for individuals managing personal finances. It should be approachable for people who feel overwhelmed by traditional budgeting and should encourage awareness without shame or perfectionism.

V2 does not include bank or card connections, automatic transaction imports, shared household finances, business accounting, investment execution, tax reporting, or professional financial advice. Debt and installment commitments may be represented for visibility, but detailed payoff planning is outside the initial V2 scope.

## Product-wide rules

- Deterministic application logic is the source of truth for balances, periods, totals, comparisons, projections, and financial effects.
- The AI Companion explains application results, supports reflection, estimates scenarios, and prepares proposals for supported actions. It is not the source of truth.
- A proposal is not a data change. Every proposal must show the operation, affected fields, uncertainty, and expected effect when calculable.
- The user can edit, cancel, or explicitly confirm a proposal. Only the normal validated application command can apply it.
- Confirmation must recheck ownership, permissions, required fields, supported values, dates, amounts, current balances, conflicts, and stale data.
- The Companion must not infer consent, silently classify a record, bundle unrelated changes, or claim success before the application confirms success.
- Manual flows remain complete alternatives to AI flows.
- AI responses must identify the relevant period and data subset, distinguish facts from calculations and suggestions, and acknowledge incomplete or estimated data.
- The Companion may use curated external knowledge about general financial education and healthy financial habits for explanation, reflection, and non-professional guidance.
- External knowledge must not be presented as the user's personal financial facts. Personalized facts, calculations, and actions remain grounded in the application data and capabilities.
- The product uses supportive, non-judgmental language. B/U/C and Need/Love/Like/Want are descriptive reflection tools, not moral scores.

## Core terminology

- **Transaction history:** income, one-time expenses, and recorded recurring-commitment payments.
- **One-time expense:** an individual expense entered through the quick expense flow.
- **Recurring commitment:** a repeated financial obligation that can generate linked expense records.
- **Monthly result:** income minus expenses and applicable commitments for a selected month.
- **Money left to spend:** current-month cashflow after income, expenses, commitments, and applicable Goal allocation.
- **Available balance:** unallocated money carried forward for ordinary spending.
- **Savings reserve:** money intentionally set aside, including unassigned reserve, monthly allocations, goal allocations, and explicit transfers.
- **Savings goal:** a named purpose with a target, deadline, and/or contribution plan.
- **B/U/C:** Bill, Usage, or Choice classification for an expense.
- **Reflective context:** one optional Need, Love, Like, or Want tag for an expense.
- **Companion action proposal:** structured, reviewable input prepared by AI and applied only after explicit user confirmation.

## Context models

B/U/C describes the user's control over spending. Bills are fixed obligations, Usage changes with consumption, and Choice can be increased, reduced, replaced, or stopped.

Need/Love/Like/Want adds personal meaning. Need supports wellbeing or functioning, Love creates lasting value or joy, Like creates temporary enjoyment, and Want is mainly immediate gratification. The model is personal and never a universal ranking of responsible spending.

Both context fields are optional Layer 1 data. They are separate from general categories and are never inferred automatically from a category, receipt, voice input, or transaction description.

## AI Companion progression

The Companion begins in Layer 1 with transaction-history questions and transaction proposals. It expands in later layers to explain cashflow, explore analytics, support financial planning, and provide cross-feature reflection. It may prepare supported actions in every layer, but only explicit user confirmation can mutate application data.

The future direction may include a more advisor-like guidance experience. Layer 5 may use curated external knowledge to discuss general financial habits, but it does not include live external account or market data, external financial-product recommendations, or professional financial advice. Any future guidance must distinguish general knowledge from application facts and preserve the confirmation and professional-advice boundaries above.

## Success

V2 is successful when a user can maintain reliable income and expense history, understand monthly cashflow and balances, review patterns, manage financial plans, and use a grounded Companion without losing control of their data or decisions.
