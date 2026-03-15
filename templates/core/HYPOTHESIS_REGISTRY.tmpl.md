# HYPOTHESIS REGISTRY

<!-- version: 1.0 -->
<!-- created: 2026-03-15 -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `{{TIER1_DOC}}` | Primary spec — highest authority |
> | Tier 2 | `{{TIER2_DOC}}` | Clarifications — cannot override Tier 1 |
> | Tier 3 | `{{TIER3_DOC}}` | Advisory only — non-binding if inconsistent with Tier 1/2 |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.
> Update this contract via `CONTRACT_CHANGE` or align implementation to the higher tier.

### Companion Contracts

**Upstream (this contract depends on):**
- See PROJECT_BRIEF for research questions that motivate hypotheses

**Downstream (depends on this contract):**
- See FINDINGS.md for hypothesis resolution narratives and evidence references

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{MIN_HYPOTHESES}}` | Minimum number of pre-registered hypotheses | `2` |
| `{{HYPOTHESIS_TABLE}}` | The populated hypothesis registry table | See §3 template |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Pre-Registration Protocol

Hypotheses MUST be written **before** Phase 1 experiments begin.

**Gate:** >= {{MIN_HYPOTHESES}} hypotheses (default: 2) registered and committed to version control before any experiment script is executed.

**Enforcement:**
- The hypothesis registry file MUST have a git commit timestamp earlier than any experiment output file.
- Adding hypotheses after seeing results is an academic integrity violation.
- Amendments to existing hypotheses (e.g., refining a threshold) MUST be tracked via `CONTRACT_CHANGE` commits with justification.

---

## 2) Hypothesis Format

Each hypothesis MUST include all fields in the following schema:

| Field | Description | Example |
|-------|-------------|---------|
| `hypothesis_id` | Sequential identifier | H-1, H-2, ... |
| `statement` | Clear, falsifiable statement | "Random Forest will outperform Decision Tree on balanced accuracy by >= 5pp on both datasets" |
| `falsification_criterion` | What evidence would reject this hypothesis | "RF balanced accuracy is < DT balanced accuracy + 5pp on either dataset" |
| `metric` | Quantitative threshold for support/rejection | `balanced_accuracy >= DT_balanced_accuracy + 0.05` |
| `resolution` | Final status | `SUPPORTED` / `REFUTED` / `INCONCLUSIVE` / `PENDING` |
| `evidence` | Reference to specific output file + metric value | `outputs/part1/adult/rf/summary.json → bal_acc=0.87 vs DT 0.79` |

**Statement quality rules:**
- Statements MUST be falsifiable. "Model X will perform well" is not acceptable.
- Statements MUST reference a specific metric and threshold (absolute or relative).
- Statements MUST specify the comparison (vs baseline, vs another model, vs chance).

---

## 3) Registry Table

{{HYPOTHESIS_TABLE}}

**Template (copy and populate):**

| hypothesis_id | statement | falsification_criterion | metric | resolution | evidence |
|---------------|-----------|------------------------|--------|------------|----------|
| H-1 | *(statement)* | *(criterion)* | *(threshold)* | PENDING | — |
| H-2 | *(statement)* | *(criterion)* | *(threshold)* | PENDING | — |

---

## 4) Resolution Protocol

After experiments complete, revisit **every** hypothesis and assign a resolution:

| Resolution | Criteria |
|------------|----------|
| **SUPPORTED** | Metric meets or exceeds the stated threshold across all specified conditions |
| **REFUTED** | Metric falls below the stated threshold |
| **INCONCLUSIVE** | Ambiguous results (e.g., supported on one dataset but not another), insufficient data, or metric within noise margin (+/-1 std of threshold) |

**Resolution rules:**
- Every hypothesis MUST be resolved before Phase N+2 begins.
- The `evidence` field MUST reference a specific output file path and the exact metric value.
- INCONCLUSIVE resolutions MUST include a brief explanation of why the result is ambiguous.
- Resolutions are final once committed. A later experiment cannot retroactively change a resolution (register a new hypothesis instead).

---

## 5) Acceptance Criteria

- [ ] >= {{MIN_HYPOTHESES}} hypotheses registered before Phase 1
- [ ] All hypotheses follow the required format (all 6 fields populated)
- [ ] All hypotheses resolved (no PENDING status at project end)
- [ ] Every resolution includes an evidence reference to a specific output file
- [ ] No hypothesis was added after experiment results were observed (verified by git timestamps)
- [ ] Resolution narrative for each hypothesis included in FINDINGS.md
