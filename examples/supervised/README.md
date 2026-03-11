# Worked Example: Supervised ML — Heart Disease Classification

This example shows representative placeholder fills for the **Supervised ML** quickstart profile (9 templates).

---

## Project Overview

| Property | Value |
|----------|-------|
| **Project name** | Heart Disease Binary Classification |
| **Datasets** | UCI Heart Disease (303 samples, 13 features) |
| **Task** | Binary classification (presence/absence of heart disease) |
| **Methods** | Logistic Regression, Random Forest, Gradient Boosted Trees, MLP |
| **Seeds** | 5 (42, 123, 456, 789, 1024) |

---

## Key Placeholder Fills

### ENVIRONMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | Heart Disease Binary Classification |
| `{{PYTHON_VERSION}}` | 3.11.7 |
| `{{PLATFORM}}` | Ubuntu 22.04, x86_64, 16 GB RAM |
| `{{ENV_MANAGER}}` | conda |
| `{{ENV_FILE}}` | environment.yml |
| `{{DETERMINISM_SETTINGS}}` | `PYTHONHASHSEED=0`, `CUBLAS_WORKSPACE_CONFIG=:4096:8` |

### DATA_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{DATASET_NAME}}` | UCI Heart Disease |
| `{{DATASET_SOURCE}}` | https://archive.ics.uci.edu/dataset/45/heart+disease |
| `{{SPLIT_STRATEGY}}` | Stratified 70/15/15 by target |
| `{{SPLIT_SEED}}` | 42 |
| `{{RAW_DATA_HASH}}` | `sha256:a1b2c3...` (computed after download) |
| `{{LEAKAGE_RULE}}` | fit_transform on train only; transform on val/test |

### METRICS_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{PRIMARY_METRIC}}` | F1 (binary) |
| `{{SECONDARY_METRICS}}` | Accuracy, AUROC, Precision, Recall |
| `{{THRESHOLD_METRIC}}` | F1 >= 0.75 (sanity floor) |
| `{{SANITY_BASELINE}}` | Majority-class classifier (Acc ~ 0.54) |
| `{{BUDGET_TYPE}}` | wall_clock (seconds) |

### EXPERIMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{EXPERIMENT_PARTS}}` | Part 1: Model Comparison |
| `{{BUDGET_VALUE}}` | 300 seconds per method per seed |
| `{{COMPARISON_RULE}}` | Budget-matched; all methods get equal wall_clock |
| `{{SEEDS}}` | [42, 123, 456, 789, 1024] |
| `{{OUTPUT_DIR}}` | `outputs/part1/{method}/seed_{seed}/` |

### HYPOTHESIS_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{H1_PREDICTION}}` | Gradient Boosted Trees achieves highest F1 on UCI Heart Disease |
| `{{H1_MECHANISM}}` | Ensemble of shallow trees captures non-linear feature interactions better than single models |
| `{{H1_EVIDENCE}}` | Median F1 across 5 seeds; GBT > RF > MLP > LR |
| `{{H1_TEMPORAL_GATE}}` | Registered before any experiment runs |

### FIGURES_TABLES_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{FIGURE_LIST}}` | F1: ROC curves (4 methods), F2: F1 box plots across seeds, F3: Feature importance (top 10) |
| `{{TABLE_LIST}}` | T1: Summary table (method × metric × median ± IQR), T2: Per-seed results |
| `{{PRODUCER_SCRIPT}}` | `scripts/make_report_artifacts.py` |

### REPORT_ASSEMBLY_PLAN

| Placeholder | Fill |
|-------------|------|
| `{{REPORT_FORMAT}}` | IEEE 2-column, 8 pages max |
| `{{SECTIONS}}` | Introduction, Related Work, Methods, Results, Discussion, Conclusion |
| `{{FIGURE_PLACEMENT}}` | F1→Results §4.1, F2→Results §4.2, F3→Discussion §5.1 |

### REPRODUCIBILITY_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{REPRO_COMMAND}}` | `bash scripts/run_all.sh --seeds 42,123,456,789,1024` |
| `{{EXPECTED_RUNTIME}}` | ~25 minutes on reference platform |
| `{{TOLERANCE}}` | Exact match on CPU; ±0.001 on GPU |

### PRE_SUBMISSION_CHECKLIST

No additional placeholders — use as-is with project-specific checks.

---

## Profile Command

```bash
bash scripts/init_project.sh /path/to/heart-disease-project --profile supervised
```
