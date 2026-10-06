# Layer 5 — Companion Expansion

## Purpose and user value

Bring the Companion capabilities from Layers 1–4 into one dependable experience for grounded questions, reflection, planning support, and confirmed application actions.

## Scope

The V2 Companion uses the signed-in user's permitted application data, deterministic calculations, information the user provides in the conversation, and curated external knowledge about general financial education and healthy financial habits. External knowledge can support explanation, reflection, and non-professional guidance, but it must not be presented as the user's personal financial facts or replace the application's calculations.

This layer does not use live external account data, market data, external financial-product recommendations, legal or regulatory interpretation, or professional financial advice. Any knowledge source must be curated, attributable, and governed by source, freshness, privacy, and safety rules. A broader advisor-like experience would require a separate product decision and architecture.

## Included core features

- Shared Companion view and starter prompts.
- Cross-layer evidence/context builder.
- Period-aware answers across transactions, cashflow, analytics, goals, and commitments.
- Proposal review, cancellation, confirmation, validation, stale-data checks, and duplicate-submission protection.
- Provider fallback, uncertainty handling, response limits, privacy controls, and evaluation fixtures.

## Depends on

- All previous implementation layers.
- Shared AI and security rules in [context](../context.md) and [architecture](../architecture.md).

## Existing capabilities used

## Data model

## Backend

## Frontend

## Business rules and calculations

## Manual user flows

The manual product remains fully usable when the AI provider is unavailable.

## Companion capabilities

The Companion distinguishes recorded facts, deterministic calculations, interpretations, estimates, and suggestions. It states the relevant period and exclusions, acknowledges missing or estimated data, and refuses unsupported actions safely.

It may prepare supported proposals across the app, but it never applies them directly.

Answers and proposals must keep application evidence and external knowledge distinct. Application facts and calculations come from permitted app data and deterministic services. External knowledge can provide general context or healthy-habit guidance, but it cannot fill missing personal data, invent a calculation, or become unsupported personalized advice.

## AI action proposals and confirmation

## Effects on other layers

## Testing

## Out of scope

### Future advisor direction

An advisor-like experience may eventually provide more proactive, grounded guidance using application evidence and curated external knowledge. That is not permission for autonomous actions or professional financial advice. Any future expansion must preserve source attribution, freshness, user control, deterministic calculations, transparent assumptions, privacy, and explicit confirmation for mutations.

## Acceptance criteria

- Supported answers are grounded in deterministic evidence.
- The Companion identifies uncertainty and incomplete data.
- Supported action proposals are reviewable and require explicit confirmation.
- Unsupported actions are refused or clarified safely.
- Provider failure does not block manual application flows.
- Evaluation cases cover empty data, ambiguity, estimates, negative balances, multiple periods, stale proposals, and rejected proposals.
