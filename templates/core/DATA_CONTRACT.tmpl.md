# DATA CONTRACT

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
- None — this is a foundational contract.

**Downstream (depends on this contract):**
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for dataset/task metric mapping
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §3 for split usage and leakage prevention in experiments
- See [PRIOR_WORK_REUSE](../management/PRIOR_WORK_REUSE.tmpl.md) §2 for reused data components and split inheritance
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §3 for data verification scripts (`check_data_ready.py`, `check_leakage.py`)
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for Phase 1 data readiness gate

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{DATASET_N_NAME}}` | Human-readable dataset name | IMDB Reviews |
| `{{DATASET_N_FILE}}` | Raw data filename | dataset_a.csv |
| `{{DATASET_N_TASK}}` | ML task type | binary classification |
| `{{DATASET_N_CLASSES}}` | Number of classes or target description | 2 (>50K vs <=50K) |
| `{{DATASET_N_FEATURES}}` | Feature count after preprocessing | 104 after one-hot encoding |
| `{{SPLIT_METHOD}}` | How splits are created/sourced | StratifiedShuffleSplit, prior project, etc. |
| `{{SPLIT_SEED}}` | Seed for split generation | 42 |
| `{{SPLIT_RATIOS}}` | Train/val/test proportions | 64/16/20 |
| `{{PREPROCESSING_STEPS}}` | Per-dataset preprocessing pipeline | StandardScaler, OneHotEncoder, SimpleImputer |
| `{{DATA_SOURCE}}` | Where raw data comes from | Kaggle, UCI ML Repository, Hugging Face |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines the data governance rules for the **{{PROJECT_NAME}}** project. It covers:

- Canonical data paths and file formats
- Train/val/test split discipline and storage
- Leakage prevention rules and automated tripwires
- Per-dataset preprocessing protocols
- Data provenance and audit artifacts
- Change control triggers

---

## 2) Canonical Data Paths

| Dataset | Raw Path | Description |
|---------|----------|-------------|
| {{DATASET_1_NAME}} | `data/raw/{{DATASET_1_FILE}}` | {{DATASET_1_TASK}}, {{DATASET_1_CLASSES}} |
| {{DATASET_2_NAME}} | `data/raw/{{DATASET_2_FILE}}` | {{DATASET_2_TASK}}, {{DATASET_2_CLASSES}} |

*(Add rows for additional datasets as needed.)*

Raw data files MUST NOT be committed to git. Add `data/raw/**` to `.gitignore`. Data placement instructions go in the REPRO document.

---

## 3) Split Discipline

### 3.1 Split Source

*(Describe how splits are created: from a prior project, generated fresh, provided by the project specification, etc.)*

**Method:** {{SPLIT_METHOD}}
**Seed:** {{SPLIT_SEED}}
**Ratios:** {{SPLIT_RATIOS}} (train / val / test)

### 3.2 Split Storage Format

Splits are stored as JSON files at `data/splits/{{DATASET_NAME}}/split_seed{{SEED}}.json` with the following schema:

```json
{
  "dataset": "{{DATASET_NAME}}",
  "seed": {{SPLIT_SEED}},
  "source": "{{SPLIT_SOURCE_DESCRIPTION}}",
  "n_total": 0,
  "n_train": 0,
  "n_val": 0,
  "n_test": 0,
  "train_indices": [],
  "val_indices": [],
  "test_indices": [],
  "split_hash": "<sha256 of sorted(train) + sorted(val) + sorted(test)>"
}
```

### 3.3 Split Invariants

The following MUST hold for every split file:

1. **No overlap:** `train ∩ val = ∅`, `train ∩ test = ∅`, `val ∩ test = ∅`
2. **Full coverage:** `len(train) + len(val) + len(test) == n_total`
3. **Valid range:** All indices in `range(0, n_total)`
4. **Deterministic:** Given the same seed and source data, the split MUST be identical
5. **Hash match:** `split_hash` matches recomputed value from index arrays

### 3.4 Test-Split Access Policy

The held-out test split is accessible exclusively through the final evaluation script. The data-loading utility MUST default to `allow_test=False` and raise a `ValueError` if test indices are requested by any other script.

---

## 4) Leakage Prevention

### 4.1 Fit-on-Train Rule

All preprocessing transformations (scalers, encoders, imputers) MUST be fit exclusively on `X_train`. Validation and test sets receive only `.transform()` calls. This is non-negotiable.

```python
# CORRECT
pipeline.fit(X_train)
X_val = pipeline.transform(X_val)
X_test = pipeline.transform(X_test)

# WRONG — leaks val/test statistics into the fitted model
pipeline.fit(X_all)
```

### 4.2 Leakage Tripwires

Automated checks to detect leakage. Each tripwire has a unique ID for cross-referencing.

| ID | Check | What It Detects | How to Run |
|----|-------|-----------------|------------|
| LT-1 | Fit isolation | `.fit()` called on non-train data | `python scripts/check_leakage.py` |
| LT-2 | Test index isolation | Test indices loaded outside final eval script | `python scripts/check_leakage.py` |
| LT-3 | Transform-only on val/test | `.fit_transform()` called on val/test data | `python scripts/check_leakage.py` |

*(Add project-specific tripwires as needed.)*

### 4.3 When to Run Leakage Checks

- After any change to preprocessing code
- Before starting any experiment phase
- At every phase gate
- Before final delivery

---

## 5) Dataset-Specific Preprocessing

### {{DATASET_1_NAME}}

| Step | Transformer | Parameters | Notes |
|------|-------------|------------|-------|
| *(e.g.)* | StandardScaler | default | Fit on train only |
| *(e.g.)* | OneHotEncoder | handle_unknown="ignore" | Fit on train only |
| *(e.g.)* | SimpleImputer | strategy="median" | Fit on train only |

**Feature count after preprocessing:** {{DATASET_1_FEATURES}}

### {{DATASET_2_NAME}}

| Step | Transformer | Parameters | Notes |
|------|-------------|------------|-------|
| *(e.g.)* | StandardScaler | default | Fit on train only |

**Feature count after preprocessing:** {{DATASET_2_FEATURES}}

*(Repeat for additional datasets.)*

---

## 6) EDA Compatibility

If this project builds on a prior project (e.g., Phase 1 → Phase 2), the EDA MUST be consistent with the prior project unless changes are disclosed and justified.

- **Consistent:** Same features, same preprocessing, same target variable
- **Disclosed change:** Document what changed, why, and how it affects comparability
- **Audit artifact:** `outputs/eda/{{DATASET_NAME}}_eda_summary.json`

---

## 7) Data Provenance & Audit Artifacts

### 7.1 Required Artifacts

| Artifact | Path | Contents |
|----------|------|----------|
| Raw data hashes | `outputs/eda/raw_hashes.json` | SHA-256 of each raw data file |
| EDA summary | `outputs/eda/{{DATASET_NAME}}_eda_summary.json` | Row count, feature count, class distribution, missing values |
| Split labels | `outputs/eda/{{DATASET_NAME}}_split_labels.json` | Class distribution per split |

### 7.2 File Layout

```
data/
+-- raw/                    # Raw data files (gitignored)
|   +-- {{DATASET_1_FILE}}
|   +-- {{DATASET_2_FILE}}
+-- splits/                 # Split index files (committed)
|   +-- {{DATASET_1_NAME}}/
|   |   +-- split_seed{{SEED}}.json
|   +-- {{DATASET_2_NAME}}/
|       +-- split_seed{{SEED}}.json
+-- processed/              # Processed data (gitignored)
```

---

## 8) Acceptance Tests (Phase Gate)

Before proceeding to experiments, the following MUST pass:

- [ ] Raw data files present at canonical paths
- [ ] SHA-256 hashes match recorded values
- [ ] Split JSON files pass all invariants (§3.3)
- [ ] Leakage tripwires pass (§4.2)
- [ ] EDA summaries generated and consistent with prior work (if applicable)
- [ ] Preprocessing pipeline produces expected feature counts

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit and MUST be logged in `CHANGELOG.md`:

- Dataset filenames or paths
- Split definitions (indices, ratios, seed)
- Preprocessing pipeline (scaling, encoding, imputation, step order)
- Target variable or label mapping
- Feature handling (selection, engineering, dropped features)
- Missing-value strategy
- Class-weight or resampling strategy
- Test-access enforcement rules
- Leakage tripwire definitions
