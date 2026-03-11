# LEAN HYPOTHESIS

<!-- version: 1.0 -->
<!-- created: 2026-03-11 -->

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
- See [HYPOTHESIS_CONTRACT](../core/HYPOTHESIS_CONTRACT.tmpl.md) for technical hypothesis format (prediction + mechanism + evidence)
- See [PUBLICATION_BRIEF](PUBLICATION_BRIEF.tmpl.md) §5 for portfolio alignment context

**Downstream (depends on this contract):**
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) for how lean hypotheses map to report narrative
- See [DECISION_LOG](../management/DECISION_LOG.tmpl.md) for ADR entries when kill criteria are triggered

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Optimizer Comparison Study |
| `{{CUSTOMER_SEGMENT}}` | Who benefits from the project outcome | ML practitioners choosing optimizers |
| `{{PROBLEM_STATEMENT}}` | Core problem being addressed | No clear guidance on when Adam outperforms SGD |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose

This template applies lean startup hypothesis thinking to ML projects. It forces explicit articulation of the problem being solved, the assumptions being tested, and the criteria for declaring an experiment line successful or worth killing. It complements the technical HYPOTHESIS_CONTRACT with strategic framing.

**When to use:** Projects that need to justify resource allocation, prioritize experiment lines, or align with stakeholder/portfolio goals.

---

## 2) Customer-Problem Hypothesis

### 2.1 Problem Statement

| Property | Value |
|----------|-------|
| **Customer segment** | {{CUSTOMER_SEGMENT}} |
| **Problem** | {{PROBLEM_STATEMENT}} |
| **Current alternatives** | *(How do they solve this today? e.g., "Default Adam with lr=0.001, no systematic comparison")* |
| **Pain severity** | *(Low / Medium / High — how much does this problem matter to the customer?)* |

### 2.2 Customer-Problem Fit Hypothesis

> *"We believe that **{{CUSTOMER_SEGMENT}}** experience **{{PROBLEM_STATEMENT}}** because **{{ROOT_CAUSE}}**, and that a systematic **{{APPROACH}}** would provide **{{VALUE_PROPOSITION}}**."*

### 2.3 Validation Criteria

How will you know the problem is real and worth solving?

| Signal | Metric | Threshold |
|--------|--------|-----------|
| *(e.g.)* Literature gap | Number of existing systematic comparisons | < 3 published comparisons under matched budgets |
| *(e.g.)* Stakeholder interest | Alignment with project specification | Required by Tier 1 |
| *(add rows)* | | |

---

## 3) Solution Hypothesis

### 3.1 Hypothesis Statement

> *"We believe that **{{SOLUTION_APPROACH}}** will **{{EXPECTED_OUTCOME}}** for **{{CUSTOMER_SEGMENT}}**, as measured by **{{SUCCESS_METRIC}}**."*

### 3.2 Solution-Problem Fit Table

| Experiment Part | Problem Addressed | Hypothesized Mechanism | Success Metric |
|----------------|-------------------|----------------------|---------------|
| *(e.g.)* Part 1: RO | Can RO optimize NN weights competitively? | Population-based search explores weight space differently than gradients | val_loss within 2× of gradient baseline |
| *(e.g.)* Part 2: Ablations | Which optimizer components matter most? | Adaptive learning rates compensate for gradient magnitude variation | Convergence speed ranking + statistical significance |
| *(add rows)* | | | |

### 3.3 Assumptions Register

Every hypothesis rests on assumptions. Make them explicit:

| # | Assumption | Type | How to Test | Status |
|---|-----------|------|-------------|--------|
| A1 | *(e.g.)* Compact MLP is sufficient for both datasets | Technical | Baseline achieves reasonable accuracy | *(untested / confirmed / refuted)* |
| A2 | *(e.g.)* 10K grad_evals is enough to differentiate methods | Resource | At least 3 of 7 optimizers reach threshold ℓ | *(untested / confirmed / refuted)* |
| A3 | *(e.g.)* Results generalize across seeds | Statistical | IQR < 10% of median for key metrics | *(untested / confirmed / refuted)* |
| *(add rows)* | | | | |

---

## 4) Validation Plan

### 4.1 Experiment-to-Hypothesis Mapping

Every experiment MUST map to at least one hypothesis. Experiments without hypothesis backing are exploratory and MUST be labeled as such.

| Experiment | Hypothesis Tested | Expected Evidence | Actual Evidence |
|-----------|-------------------|-------------------|-----------------|
| *(e.g.)* Part 2: 7 optimizers × 5 seeds | "Adam converges fastest" | Adam reaches ℓ first in ≥ 3 of 5 seeds | *(fill after experiments)* |
| *(add rows)* | | | |

### 4.2 Evidence Strength Levels

| Level | Definition | Implication |
|-------|-----------|-------------|
| **Strong** | Consistent across all seeds and datasets; large effect size | Claim is well-supported |
| **Moderate** | Consistent across most seeds; effect size above noise | Claim is supported with caveats |
| **Weak** | Inconsistent across seeds or small effect size | Claim requires hedging; report as "suggestive" |
| **Null** | No meaningful difference from baseline or random | Hypothesis refuted; discuss why |

### 4.3 Minimum Viable Experiment (MVE)

What is the smallest experiment that would test the core hypothesis?

| Property | Value |
|----------|-------|
| **MVE scope** | *(e.g., "Adam vs SGD on Adult only, single seed, 5K grad_evals")* |
| **MVE success criterion** | *(e.g., "Adam val_loss < SGD val_loss at budget midpoint")* |
| **Full experiment** | *(e.g., "7 optimizers × 2 datasets × 5 seeds × 10K grad_evals")* |
| **Scale-up trigger** | *(e.g., "If MVE shows >5% val_loss improvement, run full experiment")* |

---

## 5) Kill Criteria

### 5.1 When to Stop an Experiment Line

Kill criteria define when to abandon an approach and redirect resources. They MUST be defined before experiments begin.

| # | Kill Criterion | Threshold | Action if Triggered |
|---|---------------|-----------|-------------------|
| K1 | *(e.g.)* Method fails to beat random baseline | val_loss no better than untrained model after 50% budget | Abandon method; document failure; try alternative |
| K2 | *(e.g.)* Instability too high for credible claims | IQR > 50% of median across seeds | Investigate root cause; if unfixable, report as negative result |
| K3 | *(e.g.)* Compute budget insufficient for convergence | No method reaches ℓ within budget | Request budget increase via CONTRACT_CHANGE or adjust ℓ |
| K4 | *(e.g.)* Assumption A2 refuted | Fewer than 2 of 7 optimizers reach ℓ | Revisit budget or threshold definition |
| *(add rows)* | | | |

### 5.2 Kill Decision Process

```
1. Kill criterion threshold met?
   ├── NO → Continue experiment
   └── YES → Document in DECISION_LOG (ADR entry)
              ├── Is the kill criterion due to a fixable issue?
              │   ├── YES → Fix via CONTRACT_CHANGE → Resume
              │   └── NO → Report as negative result → Redirect resources
              └── Update TASK_BOARD to reflect redirected scope
```

### 5.3 Negative Result Protocol

Killed experiment lines are NOT deleted. They are documented as negative results:

- Record the kill decision in DECISION_LOG with full context
- Include negative results in the report (they are informative)
- Discuss why the approach failed and what was learned
- Attribute causes (insufficient budget, wrong assumptions, algorithm limitations)

---

## 6) Strategy Alignment

### 6.1 Resource Allocation

| Experiment Part | Estimated Effort | Strategic Value | Priority |
|----------------|-----------------|----------------|----------|
| *(e.g.)* Part 1: RO | 20% of total | Medium (required by spec) | P1 |
| *(e.g.)* Part 2: Ablations | 40% of total | High (core demonstration) | P0 |
| *(e.g.)* Part 3: Regularization | 25% of total | Medium (builds on P2) | P1 |
| *(e.g.)* Part 4: Integration | 15% of total | Low (optional extra credit) | P2 |

### 6.2 Pivot Scenarios

| Scenario | Trigger | Response |
|----------|---------|----------|
| *(e.g.)* Time running short | < 48h to deadline, Part 4 not started | Drop Part 4; focus on report quality |
| *(e.g.)* Key assumption refuted | Assumption A1 fails | Simplify architecture; document limitation |
| *(add rows)* | | |

---

## 7) Hypothesis Resolution Tracker

*(Fill in after experiments complete.)*

| Hypothesis | Evidence Level | Resolution | Key Finding |
|-----------|---------------|-----------|-------------|
| *(hypothesis 1)* | *(strong/moderate/weak/null)* | *(confirmed/refuted/partial)* | *(one-sentence finding)* |
| *(add rows)* | | | |

---

## 8) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Customer-problem hypothesis
- Solution hypothesis or success metrics
- Kill criteria thresholds
- Resource allocation priorities
- Pivot scenario triggers
