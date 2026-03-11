# METRICS & EVALUATION CONTRACT

<!-- version: 1.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_OL_Report -->

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §2 for canonical dataset paths and §5 for preprocessing

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §5 for evaluation rules and metric logging
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §4 for summary table column definitions
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) §5 for baseline comparison requirements
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §4 for sanity check scripts

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{DATASET_N_NAME}}` | Dataset name | Dataset A |
| `{{DATASET_N_TASK}}` | Task type | binary classification |
| `{{DATASET_N_PRIMARY_METRICS}}` | Required primary metrics | Accuracy + F1 (binary) |
| `{{DATASET_N_METRIC_FUNCTION}}` | Exact sklearn/torch call | `f1_score(average='binary', pos_label=1)` |
| `{{OPTIMIZATION_OBJECTIVE}}` | What experiments minimize/maximize | validation loss |
| `{{THRESHOLD_DEFINITION}}` | How convergence threshold is defined | Derived from baseline run |
| `{{SANITY_CHECKS}}` | Required sanity baselines | Dummy classifier, shuffled labels |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines how metrics are computed, thresholds are set, and evaluation results are validated for the **{{PROJECT_NAME}}** project.

---

## 2) Dataset / Task Mapping & Mandatory Metrics

| Dataset | Task | Primary Metrics | Computation |
|---------|------|-----------------|-------------|
| {{DATASET_1_NAME}} | {{DATASET_1_TASK}} | {{DATASET_1_PRIMARY_METRICS}} | {{DATASET_1_METRIC_FUNCTION}} |
| {{DATASET_2_NAME}} | {{DATASET_2_TASK}} | {{DATASET_2_PRIMARY_METRICS}} | {{DATASET_2_METRIC_FUNCTION}} |

**Rules:**
- Primary metrics are non-negotiable. They MUST appear in every summary and the final evaluation.
- Additional metrics may be reported if justified and consistent, but MUST NOT replace primary metrics.
- All metric computations MUST be centralized in a single module to prevent inconsistent calls.

---

## 3) Primary Optimization Objective

All experiments optimize: **{{OPTIMIZATION_OBJECTIVE}}**

*(e.g., "validation loss" — all parts use validation loss as the objective for comparisons, hyperparameter selection, and convergence analysis.)*

---

## 4) Prediction Conventions

### Classification Threshold

- **Default threshold:** 0.5 for binary classification
- If a non-default threshold is used, it MUST be justified, logged in `config_resolved.yaml`, and disclosed in the report

### Positive Class Convention

*(For binary classification: define which class is positive and the label mapping.)*

| Label | Value | Description |
|-------|-------|-------------|
| *(e.g.)* Negative | 0 | *(e.g.)* Income <=50K |
| *(e.g.)* Positive | 1 | *(e.g.)* Income >50K |

---

## 5) Convergence Threshold

*(If your project uses a convergence threshold for time-to-threshold comparisons:)*

### Definition

- **Symbol:** ℓ (or equivalent)
- **Derivation:** {{THRESHOLD_DEFINITION}}
- **Lock rule:** The threshold MUST be defined once and used consistently across all comparable experiments. Changing it after experiments begin requires a `CONTRACT_CHANGE`.

### Procedure

1. Run the baseline method with the default seed
2. Record the final validation loss
3. Set ℓ to *(describe: e.g., the final val loss of the baseline, or a percentile)*
4. Lock ℓ in the budget config file
5. All compared methods report `steps_to_l`, `reached_l`, and `wall_clock_to_l`

---

## 6) Generalization Gap

The generalization gap is defined as:

```
gen_gap = train_loss - val_loss  (at budget endpoint)
```

*(Or use your preferred definition.)*

- MUST be computed for every experiment run
- MUST be logged in `summary.json`
- MUST be discussed in the report for each experimental part

---

## 7) Sanity Checks

Before running main experiments, run sanity checks to establish pipeline credibility.

| Check | Expected Behavior | Script |
|-------|-------------------|--------|
| Dummy baseline | Accuracy ≈ majority class proportion; F1 ≈ 0 for minority class | `scripts/run_sanity_checks.py` |
| Shuffled labels | Performance ≈ random chance; model cannot learn from noise | `scripts/run_sanity_checks.py` |

*(Add project-specific sanity checks as needed.)*

If sanity checks produce unexpected results, MUST investigate before proceeding.

---

## 8) Summary Table Interface

The summary table (T1) MUST include these columns at minimum:

| Column | Description |
|--------|-------------|
| Method | Algorithm/optimizer/technique name |
| Best Val Loss | Lowest validation loss achieved |
| Test Metric | Primary test metric (from final eval only) |
| Time to ℓ | Steps/evals to reach threshold ℓ (if applicable) |
| Budget Used | Gradient evals, function evals, or equivalent |
| Notes | Over-budget flag, architecture changes, etc. |

- SL/prior baseline row MUST be included if applicable
- Over-budget runs MUST be marked and excluded from head-to-head claims
- Dispersion (median + IQR) MUST be shown for seed-aggregated results

---

## 9) Logging Schema

Every experiment run MUST log metrics in a consistent schema.

### Per-step logging (`metrics.csv`)

| Field | Type | Description |
|-------|------|-------------|
| step | int | Step/eval/epoch number |
| train_loss | float | Training loss at this step |
| val_loss | float | Validation loss at this step |
| val_metric_1 | float | Primary validation metric |
| wall_clock_s | float | Cumulative wall-clock seconds |
| *(add fields)* | | |

### Per-run summary (`summary.json`)

| Field | Type | Description |
|-------|------|-------------|
| dataset | str | Dataset name |
| method | str | Method/algorithm name |
| seed | int | Random seed used |
| best_val_loss | float | Best validation loss |
| budget_used | dict | `{grad_evals: N, func_evals: M}` |
| over_budget | bool | Whether budget was exceeded |
| gen_gap | float | Generalization gap at budget endpoint |
| steps_to_l | int/null | Steps to reach threshold ℓ |
| reached_l | bool | Whether ℓ was reached |
| *(add fields)* | | |

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Metric definitions or computation functions
- Positive class convention or label mapping
- Classification threshold
- F1 averaging mode (binary vs macro vs weighted)
- Convergence threshold ℓ (after initial lock)
- Generalization gap definition
- Sanity check requirements
- Evaluation determinism rules
- Test-split access policy
- Logging schema fields
