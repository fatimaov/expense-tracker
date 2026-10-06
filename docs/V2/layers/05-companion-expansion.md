# Layer 5 — Companion Expansion

## Purpose and user value

Bring the Companion capabilities from Layers 1–4 into one dependable experience for grounded questions, reflection, planning support, and confirmed application actions.

## Scope

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

## AI action proposals and confirmation

## Effects on other layers

## Testing

## Out of scope

### Future advisor direction

An advisor-like experience may eventually provide more proactive, grounded guidance. That is a future product decision, not an automatic permission for autonomous actions or professional financial advice. Any future expansion must preserve user control, deterministic calculations, transparent assumptions, privacy, and explicit confirmation for mutations.

## Acceptance criteria

- Supported answers are grounded in deterministic evidence.
- The Companion identifies uncertainty and incomplete data.
- Supported action proposals are reviewable and require explicit confirmation.
- Unsupported actions are refused or clarified safely.
- Provider failure does not block manual application flows.
- Evaluation cases cover empty data, ambiguity, estimates, negative balances, multiple periods, stale proposals, and rejected proposals.
