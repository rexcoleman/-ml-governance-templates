# SANITY BASELINE SPEC

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §1 for experiment matrix and dataset list
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for primary metric definitions

**Downstream (depends on this contract):**
- See FINDINGS.md for sanity baseline discussion and delta-above-dummy reporting

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{MINIMUM_DELTA_PP}}` | Minimum improvement over dummy in percentage points | `5` |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Required Baselines

Every project MUST run three sanity baselines to establish the chance-level performance floor:

### 1.1 DummyClassifier — Stratified

- **Method:** `sklearn.dummy.DummyClassifier(strategy="stratified")`
- **Behavior:** Random predictions matching the training set's class distribution.
- **Purpose:** Establishes the expected performance of a random classifier that respects class priors.

### 1.2 DummyClassifier — Most Frequent

- **Method:** `sklearn.dummy.DummyClassifier(strategy="most_frequent")`
- **Behavior:** Always predicts the majority class.
- **Purpose:** Establishes the trivial baseline. Any useful model MUST beat this.

### 1.3 Shuffled-Label Baseline

- **Method:** Train the **real model** (best algorithm, best hyperparameters) on **shuffled labels**.
- **Behavior:** The model sees real features but random label assignments.
- **Purpose:** Proves the model learns from the feature-label relationship, not from artifacts (data ordering, feature correlations unrelated to target, leakage).
- **Implementation:**
  ```python
  y_shuffled = np.random.permutation(y_train)
  model.fit(X_train, y_shuffled)
  y_pred = model.predict(X_val)
  ```

**For regression tasks:** Replace DummyClassifier with `sklearn.dummy.DummyRegressor` using `strategy="mean"` and `strategy="median"`. The shuffled-label baseline applies unchanged.

---

## 2) Evaluation Protocol

- All baselines MUST use the **same test/validation set** as real models.
- All baselines MUST report the **same metrics** as real models (see METRICS_CONTRACT §2).
- All baselines MUST use the **same seeds** from the stability list.
- Report **mean +/- std** across seeds for each baseline.

**Output files:** `outputs/baselines/sanity_{baseline_name}_seed{seed}.json`

Each JSON file MUST contain:
```json
{
  "baseline": "stratified | most_frequent | shuffled_label",
  "seed": 42,
  "metrics": {
    "primary_metric": 0.0,
    "secondary_metric": 0.0
  }
}
```

---

## 3) Interpretation

| Condition | Implication | Action |
|-----------|-------------|--------|
| Real model <= dummy_stratified + {{MINIMUM_DELTA_PP}}pp | Model is not learning meaningful patterns | Investigate features, preprocessing, hyperparameters |
| Real model <= dummy_most_frequent + {{MINIMUM_DELTA_PP}}pp | Model no better than trivial prediction | Investigate class imbalance, metric choice, model capacity |
| Shuffled-label ~= real model (within 2pp) | Possible data leakage or spurious correlations | Audit preprocessing pipeline, check for target leakage |
| Shuffled-label >> dummy baselines | Model memorizing noise; not necessarily leakage but high variance | Check overfitting, reduce model complexity |

**Default minimum delta:** {{MINIMUM_DELTA_PP}} percentage points (default: 5pp).

---

## 4) Reporting

- Include a **sanity baseline row** in every results comparison table.
- Every model comparison MUST show **delta above dummy** (best dummy baseline):
  ```
  Delta = model_metric - max(dummy_stratified, dummy_most_frequent)
  ```
- The shuffled-label result MUST be discussed in FINDINGS.md as evidence that the model learns from signal.

**Example results table format:**

| Model | Balanced Acc | Delta vs Dummy |
|-------|-------------|----------------|
| Dummy (stratified) | 0.50 +/- 0.02 | — |
| Dummy (most frequent) | 0.48 +/- 0.00 | — |
| Shuffled-label (RF) | 0.51 +/- 0.03 | — |
| Decision Tree | 0.78 +/- 0.02 | +28pp |
| Random Forest | 0.85 +/- 0.01 | +35pp |

---

## 5) Acceptance Criteria

- [ ] All 3 baselines run (stratified, most_frequent, shuffled-label)
- [ ] Results saved to `outputs/baselines/sanity_*.json`
- [ ] All baselines use same seeds, metrics, and evaluation set as real models
- [ ] Real model beats both dummy baselines by >= {{MINIMUM_DELTA_PP}}pp (default: 5pp)
- [ ] Sanity baseline rows included in results tables
- [ ] Delta-above-dummy column present in comparison tables
- [ ] Shuffled-label result discussed in FINDINGS.md
