# EXPERIMENT CONTRACT

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §3 for split definitions and §4 for leakage prevention
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §8 for determinism and seeding defaults
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for required metrics and §5 for convergence threshold

**Downstream (depends on this contract):**
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §3 for experiment-sourced figures
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §3 for per-run provenance files
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §4 for experiment script specifications

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{EXPERIMENT_PARTS}}` | List of experimental parts/phases | Part 1: RO, Part 2: Adam Ablations, Part 3: Regularization |
| `{{BUDGET_CONFIG_FILE}}` | Path to budget config | config/budgets.yaml |
| `{{BACKBONE_DESCRIPTION}}` | Model architecture description | PyTorch compact MLP from prior project |
| `{{SEED_LIST}}` | Stability seeds | [42, 123, 456, 789, 1024] |
| `{{DEFAULT_SEED}}` | Primary seed | 42 |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Scope & Experiment Matrix

This contract defines the experimental protocol for **{{PROJECT_NAME}}**.

### 1.1 Experiment Parts

| Part | Description | Datasets | Methods | Budget Type |
|------|-------------|----------|---------|-------------|
| *(e.g.)* Part 1 | *(e.g.)* Randomized Optimization | *(e.g.)* Adult + Wine | *(e.g.)* RHC, SA, GA | func_evals |
| *(e.g.)* Part 2 | *(e.g.)* Optimizer Ablations | *(e.g.)* Adult only | *(e.g.)* 7 optimizers | grad_evals |
| *(e.g.)* Part 3 | *(e.g.)* Regularization Study | *(e.g.)* Adult only | *(e.g.)* 4 techniques + combo | grad_evals |
| *(add parts)* | | | | |

---

## 2) Compute Budgets

### 2.1 Budget Source

All budgets are defined in `{{BUDGET_CONFIG_FILE}}`. Scripts read values at runtime. No hardcoded budgets in code.

### 2.2 Budget Schema

```yaml
# {{BUDGET_CONFIG_FILE}}
part1:
  func_evals: {{PART1_BUDGET}}
part2:
  grad_evals: {{PART2_BUDGET}}
  eval_interval_steps: {{EVAL_INTERVAL}}
  threshold_l: {{THRESHOLD_L}}
part3:
  grad_evals: {{PART3_BUDGET}}  # MUST equal part2.grad_evals
seeds:
  default: {{DEFAULT_SEED}}
  stability_list: {{SEED_LIST}}
```

### 2.3 Budget-Matching Rule

Within each part, all compared methods MUST use identical compute budgets. This is non-negotiable for fair comparisons.

- Scripts enforce budget caps and hard-stop at the limit
- Over-budget runs MUST set `over_budget: true` in `summary.json`
- Over-budget runs MUST be excluded from head-to-head claims

### 2.4 Cross-Part Budget Consistency

Where experiments in different parts are compared (e.g., regularization vs baseline), budgets MUST match. Specifically:
- `part3.grad_evals == part2.grad_evals` (if Part 3 builds on Part 2)
- This is validated at Phase 0 and enforced in scripts

---

## 3) Dataset Splits & Leakage Prevention

### 3.1 Split Source

*(Reference DATA_CONTRACT for full details.)*

Split files: `data/splits/{{DATASET_NAME}}/split_seed{{SEED}}.json`

### 3.2 Test-Split Access Policy

Test split is accessible ONLY through the final evaluation script. All other scripts MUST use train and validation splits only.

### 3.3 Leakage Prevention

- Fit preprocessing on train only (see DATA_CONTRACT §4)
- No test metrics in per-run outputs
- No hyperparameter selection based on test performance

---

## 4) Seeding & Initialization Protocol

### 4.1 Seed Policy

- **Default seed:** {{DEFAULT_SEED}}
- **Stability list:** {{SEED_LIST}}
- Seeds are set before every experiment via the deterministic seeding function (see ENVIRONMENT_CONTRACT §8)

### 4.2 Weight Initialization

For experiments that compare different methods on the same architecture:

1. Initialize the model once per seed
2. Save the initial `state_dict` to `outputs/init_weights/{{DATASET}}_seed_{{SEED}}.pt`
3. Load the same `state_dict` before each method's training run
4. Verify: forward pass on the same input produces identical output within tolerance (1e-6)

This ensures all methods start from the same point, isolating the effect of the method itself.

### 4.3 Multi-Seed Stability

All experiments MUST be run across the full seed list to support:
- Median + IQR reporting (not just single-seed point estimates)
- Stability analysis across methods
- Credible dispersion in comparative claims

---

## 5) Metrics & Evaluation Rules

*(Reference METRICS_CONTRACT for full definitions.)*

### 5.1 Evaluation Determinism

During evaluation (validation loss computation, metric calculation):
- `model.eval()` MUST be called
- Dropout MUST be disabled
- Batch normalization MUST be frozen (running stats, not batch stats)
- Data augmentation MUST be disabled
- `torch.no_grad()` MUST wrap the evaluation block

### 5.2 Required Metrics Per Run

Every run MUST log:
- `train_loss` and `val_loss` at every evaluation interval
- Primary validation metric(s) per dataset
- `wall_clock_s` cumulative timing
- Budget usage (`grad_evals` or `func_evals`)

---

## 6-N) Per-Part Protocols

*(Create one section per experimental part. Each section should define:)*

### Part {{N}}: {{PART_NAME}}

**Goal:** *(One-sentence description)*

**Methods:** *(List all methods/algorithms to be compared)*

**Budget:** `{{BUDGET_CONFIG_KEY}}` from `{{BUDGET_CONFIG_FILE}}`

**Protocol:**
1. *(Step-by-step procedure)*
2. *(What to initialize, what to vary, what to hold constant)*
3. *(What to log beyond standard metrics)*

**Operator Disclosures:** *(For each method, list what hyperparameters/settings must be reported)*

| Method | Required Disclosures |
|--------|---------------------|
| *(e.g.)* RHC | Restart policy, step-size schedule |
| *(e.g.)* SA | Initial temperature, decay factor, cooling schedule |
| *(e.g.)* GA | Population size, selection, crossover, mutation rate, elitism |

**Constraints:**
- *(e.g.)* All methods must start from the same init weights
- *(e.g.)* Architecture must not be modified (except for Part 3 regularization modules)
- *(e.g.)* Locked hyperparameters from prior parts must not be retuned

---

## {{N+1}}) Output Directory Structure

```
outputs/
+-- init_weights/                          # Saved initial state_dicts
+-- part1/{{DATASET}}/{{METHOD}}/seed_*/   # Part 1 outputs
+-- part2/{{DATASET}}/{{METHOD}}/seed_*/   # Part 2 outputs
+-- part3/{{DATASET}}/{{METHOD}}/seed_*/   # Part 3 outputs
+-- sanity_checks/                         # Sanity check results
+-- final_eval/seed_*/                     # Final test evaluation
+-- figures/                               # Generated figures
+-- tables/                                # Generated tables
```

### Per-Run Output Files

Every run directory MUST contain:

| File | Format | Contents |
|------|--------|----------|
| `metrics.csv` | CSV | Per-step metrics (see METRICS_CONTRACT §9) |
| `summary.json` | JSON | Run summary with best metrics, budget usage, flags |
| `config_resolved.yaml` | YAML | Full resolved configuration (CLI + config file + defaults) |
| `run_manifest.json` | JSON | SHA-256 hashes of all output files |

---

## {{N+2}}) Exit Gates

Each experimental part has an exit gate that MUST pass before proceeding.

### Exit Gate Template

- [ ] All methods complete for all seeds
- [ ] Budget usage is consistent across methods (within tolerance)
- [ ] No over-budget runs (or properly flagged and excluded)
- [ ] Required metrics logged in every `summary.json`
- [ ] `metrics.csv` has expected columns and row counts
- [ ] Operator disclosures present in `config_resolved.yaml`
- [ ] *(Part-specific checks)*

---

## {{N+3}}) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Compute budgets (any value in `{{BUDGET_CONFIG_FILE}}`)
- Method list for any part
- Initialization protocol
- Output schemas (metrics.csv, summary.json, config_resolved.yaml)
- Evaluation determinism rules
- Budget-matching constraints
- Part composition rules
