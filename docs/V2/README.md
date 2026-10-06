# Expense Tracker V2 Documentation

This folder is the working reference for implementing V2. It is intentionally small and organized around the way the product is built.

## Reading order for implementation

1. Read [context](./context.md) for product rules, terminology, boundaries, and AI behaviour.
2. Read [architecture](./architecture.md) for shared technical decisions and conventions.
3. Read [roadmap](./roadmap.md) for implementation order and current delivery goals.
4. Read the target layer file in `layers/`.
5. Read any dependency layers named in the target layer's `Depends on` section.
6. Inspect the existing code before changing it, and keep the layer's acceptance criteria visible while implementing.

## Documents

### Shared context

- [context.md](./context.md) — product direction, scope, terminology, AI rules, and decisions that apply to every layer.
- [architecture.md](./architecture.md) — shared stack, project boundaries, security, AI integration, and data/API conventions.

### Implementation layers

- [Layer 1 — Transaction foundation](./layers/01-transaction-foundation.md)
- [Layer 2 — Cashflow and reserve](./layers/02-cashflow-and-reserve.md)
- [Layer 3 — Analytics and awareness](./layers/03-analytics-and-awareness.md)
- [Layer 4 — Financial planning](./layers/04-financial-planning.md)
- [Layer 5 — Companion expansion](./layers/05-companion-expansion.md)

The layer files are implementation briefs. Each one describes the user value, included core features, dependencies, data and calculations, manual flows, Companion capabilities, confirmation rules, and acceptance criteria for that layer.

Savings Goals and Recurring Commitments are features within Layer 4, not separate implementation layers.
