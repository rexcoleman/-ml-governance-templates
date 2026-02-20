# DECISION LOG

## Purpose

This log records architectural and methodological decisions for the **{{PROJECT_NAME}}** project using a lightweight ADR (Architecture Decision Record) format. Each decision captures the context, alternatives, rationale, and consequences so that future changes are informed rather than accidental.

**Relationship to CHANGELOG:** When a decision triggers a `CONTRACT_CHANGE` commit, the change MUST also be logged in CHANGELOG with a cross-reference to the ADR ID.

**Authority hierarchy:**

| Priority | Document | Role |
|----------|----------|------|
| Tier 1 | `{{TIER_1_DOC}}` | Highest authority |
| Tier 2 | `{{TIER_2_DOC}}` | Clarifications |
| Tier 3 | `{{TIER_3_DOC}}` | Advisory only |

---

## Decision Record Template

Copy this block for each new decision:

```markdown
## ADR-XXXX: [Short title]

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded

### Context
[Problem statement and constraints. Cite authority documents when relevant.]

### Decision
[The chosen approach.]

### Alternatives Considered
1. [Alternative A] — [why rejected]
2. [Alternative B] — [why rejected]

### Rationale
[Why this approach is best given the project constraints.]

### Consequences
[Tradeoffs and risks. Reference RISK_REGISTER entries if applicable.]

### Implementation Notes
[Which contracts/specs and scripts are affected.]

### Evidence Plan
[What artifacts, figures, or tests will validate this decision.]
```

---

## Decisions

*(Record decisions below. Number sequentially: ADR-0001, ADR-0002, etc.)*

---

## ADR-0001: [First decision title]

- **Date:** YYYY-MM-DD
- **Status:** Proposed

### Context
*(Describe the problem and constraints.)*

### Decision
*(State the chosen approach.)*

### Alternatives Considered
1. *(Alternative and why rejected)*

### Rationale
*(Why this is the best choice.)*

### Consequences
*(Tradeoffs, risks, downstream effects.)*

### Implementation Notes
*(Affected contracts, scripts, configs.)*

### Evidence Plan
*(How to verify the decision was implemented correctly.)*
