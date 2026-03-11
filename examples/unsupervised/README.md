# Worked Example: Unsupervised Analysis — Customer Segmentation

This example shows representative placeholder fills for the **Unsupervised Analysis** quickstart profile (10 templates).

---

## Project Overview

| Property | Value |
|----------|-------|
| **Project name** | Customer Segmentation via Clustering |
| **Datasets** | Online Retail II (541K transactions, 8 features) |
| **Task** | Discover customer segments using RFM features + clustering |
| **Methods** | K-Means, DBSCAN, Gaussian Mixture Model, Agglomerative |
| **Seeds** | 5 (42, 123, 456, 789, 1024) |

---

## Key Placeholder Fills

### ENVIRONMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | Customer Segmentation via Clustering |
| `{{PYTHON_VERSION}}` | 3.11.7 |
| `{{PLATFORM}}` | Ubuntu 22.04, x86_64, 32 GB RAM (CPU-only) |

### DATA_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{DATASET_NAME}}` | Online Retail II |
| `{{DATASET_SOURCE}}` | UCI ML Repository |
| `{{SPLIT_STRATEGY}}` | 80/20 fit/holdout (no labels — unsupervised) |
| `{{PREPROCESSING}}` | Remove nulls, RFM feature engineering, StandardScaler fit on train |
| `{{LEAKAGE_RULE}}` | Scaler fit on fit split only; transform holdout |

### METRICS_CONTRACT (Appendix B activated — unsupervised evaluation menu)

| Placeholder | Fill |
|-------------|------|
| `{{PRIMARY_METRIC}}` | Silhouette Score |
| `{{SECONDARY_METRICS}}` | Calinski-Harabasz Index, Davies-Bouldin Index, Cluster Stability (Jaccard across seeds) |
| `{{SANITY_BASELINE}}` | Random assignment (Silhouette ~ 0.0) |
| `{{EXTERNAL_VALIDATION}}` | If business labels available: Adjusted Rand Index, Normalized Mutual Information |

### EXPERIMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{EXPERIMENT_PARTS}}` | Part 1: K selection (K=2..10), Part 2: Method comparison at best K |
| `{{BUDGET_TYPE}}` | wall_clock |
| `{{BUDGET_VALUE}}` | 60 seconds per method per seed |
| `{{OUTPUT_DIR}}` | `outputs/{part}/{method}/seed_{seed}/` |

### FIGURES_TABLES_CONTRACT (§8.5 activated — unsupervised figures)

| Placeholder | Fill |
|-------------|------|
| `{{FIGURE_LIST}}` | F1: Elbow plot (inertia vs K), F2: Silhouette plot per K, F3: 2D cluster visualization (PCA), F4: Cluster profile radar charts |
| `{{TABLE_LIST}}` | T1: Method comparison (Silhouette median ± IQR), T2: Cluster size distribution |
| `{{UNSUPERVISED_VIZ}}` | Elbow with knee annotation, silhouette coefficient bar plots, t-SNE/PCA scatter with cluster colors |

### HYPOTHESIS_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{H1_PREDICTION}}` | Optimal K is between 3 and 5 based on elbow and silhouette |
| `{{H1_MECHANISM}}` | RFM features naturally partition customers into low/medium/high-value tiers |
| `{{H2_PREDICTION}}` | GMM outperforms K-Means on Silhouette Score |
| `{{H2_MECHANISM}}` | Soft assignments capture overlapping segment boundaries better than hard K-Means |

### ARTIFACT_MANIFEST_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{RUN_ID_FORMAT}}` | `{part}_{method}_k{k}_seed{seed}` |
| `{{ARTIFACT_LIST}}` | `summary.json`, `cluster_labels.npy`, `config_resolved.yaml` |

### REPORT_ASSEMBLY_PLAN

| Placeholder | Fill |
|-------------|------|
| `{{REPORT_FORMAT}}` | Technical report, 10 pages max |
| `{{SECTIONS}}` | Introduction, Data & Preprocessing, Methods, K Selection, Method Comparison, Cluster Interpretation, Conclusion |
| `{{FIGURE_PLACEMENT}}` | F1→K Selection §4, F2→K Selection §4, F3→Method Comparison §5, F4→Interpretation §6 |

### REPRODUCIBILITY_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{REPRO_COMMAND}}` | `bash scripts/run_all.sh` |
| `{{EXPECTED_RUNTIME}}` | ~10 minutes on reference platform |

### PRE_SUBMISSION_CHECKLIST

No additional placeholders — use as-is.

---

## Profile Command

```bash
bash scripts/init_project.sh /path/to/customer-segmentation --profile unsupervised
```
