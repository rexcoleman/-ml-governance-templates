# Example: Sample ML Project

This directory shows how the governance templates map to a real project — a multi-part ML experiment comparing optimization algorithms, optimizer ablations, and regularization techniques on two datasets using a fixed PyTorch backbone.

---

## Project Overview

- **Goal:** Compare randomized optimization, gradient-based optimizers, and regularization techniques on two classification datasets
- **Datasets:** Two classification datasets (one binary, one multiclass)
- **Structure:** 4 experimental parts + final evaluation + technical report

---

## Template → Project Document Mapping

| Template | Project Document | Key Customizations |
|----------|------------------|--------------------|
| `DATA_CONTRACT.tmpl.md` | `DATA_CONTRACT.md` | Two datasets; split reuse from prior project; OHE + StandardScaler preprocessing |
| `ENVIRONMENT_CONTRACT.tmpl.md` | `ENVIRONMENT_CONTRACT.md` | Python 3.10.13; mamba/conda; PyTorch 2.2.2 CPU |
| `EXPERIMENT_CONTRACT.tmpl.md` | `EXPERIMENT_CONTRACT.md` | 4 parts: RO (5k func_evals), optimizer ablations (10k grad_evals), regularization (10k), integrated |
| `METRICS_CONTRACT.tmpl.md` | `METRICS_CONTRACT.md` | Dataset A: Accuracy + binary F1; Dataset B: Accuracy + Macro-F1; threshold_l = 0.33 |
| `FIGURES_TABLES_CONTRACT.tmpl.md` | `FIGURES_TABLES_CONTRACT.md` | 10 figures (F1-F10), 2 tables (T1 summary, T2 sanity checks) |
| `ARTIFACT_MANIFEST_SPEC.tmpl.md` | `ARTIFACT_MANIFEST_SPEC.md` | Run ID: `{part}_{dataset}_{method}_seed{seed}`; SHA-256 |
| `SCRIPT_ENTRYPOINTS_SPEC.tmpl.md` | `SCRIPT_ENTRYPOINTS_SPEC.md` | 18 scripts across 3 phases; shared flags: --seed, --output_dir, --budgets_path |
| `IMPLEMENTATION_PLAYBOOK.tmpl.md` | `IMPLEMENTATION_PLAYBOOK.md` | 10 phases (0-9); Tier 1/2/3 authority hierarchy |
| `TASK_BOARD.tmpl.md` | `TASK_BOARD.md` | 30+ tasks across 10 phases; 6-week cadence |
| `RISK_REGISTER.tmpl.md` | `RISK_REGISTER.md` | 30+ risks (R-A1 through R-H13); 10 critical invalidators |
| `DECISION_LOG.tmpl.md` | `DECISION_LOG.md` | 7 ADRs: CPU-only, test isolation, fit-on-train, fixed backbone, locked metrics, vendor snapshot, val split derivation |
| `CHANGELOG.tmpl.md` | `CHANGELOG.md` | 3 CONTRACT_CHANGE entries tracking backbone fix, prior-work snapshot, budget population |
| `PRIOR_WORK_REUSE.tmpl.md` | `PRIOR_WORK_REUSE.md` | Vendor snapshot of prior backbone + preprocessing + splits; 3 options evaluated |
| `REPORT_ASSEMBLY_PLAN.tmpl.md` | `REPORT_ASSEMBLY_PLAN.md` | 8-page IEEE format; 10 sections; CCC paragraph structure; hypothesis templates |
| `PRE_SUBMISSION_CHECKLIST.tmpl.md` | *(derived from audit experience)* | Orphan branch cleanup; prohibited file removal; SHA verification |

---

## Key Placeholder Values Used

| Placeholder | Value |
|-------------|-------|
| `{{PROJECT_NAME}}` | Optimization Benchmark |
| `{{PYTHON_VERSION}}` | 3.10.13 |
| `{{ENV_NAME}}` | ml-benchmark |
| `{{DEFAULT_SEED}}` | 42 |
| `{{SEED_LIST}}` | [42, 123, 456, 789, 1024] |
| `{{DATASET_1_NAME}}` | Dataset A |
| `{{DATASET_1_FILE}}` | dataset_a.csv |
| `{{DATASET_2_NAME}}` | Dataset B |
| `{{DATASET_2_FILE}}` | dataset_b.csv |
| `{{PAGE_LIMIT}}` | 8 |
| `{{MIN_REFS}}` | 2 |
| `{{TIER_1_DOC}}` | Primary assignment specification |
| `{{TIER_2_DOC}}` | Assignment FAQ / clarifications |

---

## Lessons Learned

1. **Start governance early.** Setting up contracts before writing code prevents rework. This project established all 7 core contracts before Phase 1 experiments.

2. **The authority hierarchy prevents arguments.** When in doubt, trace to Tier 1. This resolved every ambiguity (e.g., backbone architecture discrepancy, validation split derivation).

3. **Leakage tripwires catch bugs early.** The automated `check_leakage.py` script caught a fit-on-full-data bug during development that would have invalidated all results.

4. **CONTRACT_CHANGE discipline is worth it.** Logging every material change made the audit trail trivial. When the backbone config needed correction, the CHANGELOG + ADR made the rationale clear.

5. **Pre-submission cleanup is non-trivial.** The project needed an orphan branch rewrite to remove internal documents from git history. The PRE_SUBMISSION_CHECKLIST template captures this experience.

6. **Risk register drives automation.** High-severity risks (leakage, test access, budget mismatch) each got an automated check. This caught issues that manual review would have missed.
