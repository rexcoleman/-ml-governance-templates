# STATISTICAL ANALYSIS SPEC

<!-- version: 1.0 -->
<!-- created: 2026-03-15 -->
<!-- last_validated_against: frontier_project_pipeline -->

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §4 for seeding and initialization protocol
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for required metrics and §5 for convergence threshold
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §3 for split definitions

**Downstream (depends on this contract):**
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §3 for CI visualization requirements
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §3 for per-run provenance files
- FINDINGS documents must comply with reporting formats defined here
- PUBLICATION_PIPELINE must verify all claims against acceptance criteria in §9

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{MIN_SEEDS}}` | Minimum number of random seeds per experiment | 3 (recommend 5) |
| `{{SEED_LIST}}` | Pre-registered list of seeds | [42, 123, 456, 789, 1024] |
| `{{CI_METHOD}}` | Confidence interval method | bootstrap_percentile, bootstrap_bca, analytical |
| `{{CI_LEVEL}}` | Confidence level for intervals | 95 |
| `{{MIN_BASELINES}}` | Minimum number of baselines to compare against | 2 |
| `{{HP_STRATEGY}}` | Hyperparameter search strategy | grid, random, bayesian, default_justified |
| `{{CV_STRATEGY}}` | Cross-validation strategy | k-fold, temporal, stratified |
| `{{DATA_TYPE}}` | Data provenance type | real, synthetic, semi-synthetic |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory references |

---

## 1) Seed Protocol

### 1.1 Minimum Seeds

All experiments MUST be run with at least **{{MIN_SEEDS}}** seeds. The recommended minimum is 3; prefer 5 for publishable results.

### 1.2 Seed List

Pre-registered seed list: `{{SEED_LIST}}`

*(e.g., `[42, 123, 456, 789, 1024]`)*

**Rules:**
- Seeds MUST be declared before any experiment is run. Post-hoc seed selection is prohibited.
- The seed list MUST NOT change after the first experimental run unless a `CONTRACT_CHANGE` is filed.
- If a seed produces an error (OOM, NaN divergence), the run MUST be reported as failed — the seed MUST NOT be silently replaced.

### 1.3 Reporting Format

All metrics MUST be reported as **mean +/- std** across seeds:

```
Metric = X.XXX +/- X.XXX (n=<NUM_SEEDS> seeds)
```

Single-seed point estimates MUST NOT appear in any comparative claim. They may appear only in per-seed appendix tables.

### 1.4 Seed Selection Integrity

- Seeds MUST be pre-registered in the experiment config before any run.
- Cherry-picking seeds that produce favorable results is a violation of this contract.
- All seeds — including underperforming ones — MUST be included in aggregate statistics.

**Verification:** Assert `len(completed_seeds) == len({{SEED_LIST}})` for every method before any claim is made.

### Deterministic Model Variance
> Some models (XGBoost, LogisticRegression, GradientBoosting) produce identical results across seeds when given the same data split. Reporting std=0.000 is technically correct but misleading — it reflects deterministic computation, not robust performance.
>
> **For deterministic models, use one of these alternative variance methods:**
> 1. **Bootstrap over test set:** Resample the test set 1000 times, compute metric each time → 95% CI
> 2. **Multiple train/test splits:** Create 5 different temporal or random splits → mean ± std across splits
> 3. **Cross-validation:** k-fold CV with k=5+ → mean ± std across folds
>
> **Reporting convention:** If a model is deterministic and only one split is used, report as:
> `metric = X.XXX (deterministic; 95% bootstrap CI: [lo, hi])`
> Not as: `metric = X.XXX ± 0.000`

---

## 2) Confidence Intervals

### 2.1 Method

CI method: **{{CI_METHOD}}**

| Method | When to Use | Implementation |
|--------|------------|---------------|
| `bootstrap_percentile` | Default. Simple, robust for most metrics. | `np.percentile(bootstrap_samples, [2.5, 97.5])` |
| `bootstrap_bca` | When sample distribution is skewed. | `scipy.stats.bootstrap(..., method='BCa')` |
| `analytical` | When closed-form CI exists (e.g., proportion CI). | Metric-specific formula. |

### 2.2 Confidence Level

Confidence level: **{{CI_LEVEL}}%** (default 95%)

### 2.3 Required Coverage

Confidence intervals MUST be computed and reported for **all primary metrics**:
- AUC-ROC
- F1 (macro/weighted as defined in METRICS_CONTRACT)
- Accuracy
- Precision
- Recall
- Any project-specific primary metric declared in METRICS_CONTRACT

### 2.4 Report Format

All CI-bearing metrics MUST use this format:

```
metric = X.XXX ({{CI_LEVEL}}% CI: [X.XXX, X.XXX])
```

*(e.g., `AUC = 0.847 (95% CI: [0.831, 0.862])`)*

### 2.5 Bootstrap Parameters (if applicable)

| Parameter | Value |
|-----------|-------|
| Number of bootstrap samples | >= 10,000 |
| Resampling unit | Per-seed aggregate metric (not per-sample) |
| Random state | Fixed seed for reproducibility |

**Verification:** CI bounds MUST be present in `summary.json` for every primary metric. Schema-validate their presence.

---

## 3) Baseline Requirements

### 3.1 Minimum Baselines

Every proposed model MUST be compared against at least **{{MIN_BASELINES}}** baselines. The recommended minimum is 2; prefer 3 for publishable results.

### 3.2 Required Baseline Types

| Type | Description | Example |
|------|-------------|---------|
| **Naive baseline** | Random or majority-class predictor | Random classifier, majority-class, ZeroR |
| **Domain-standard tool** | Established non-ML method or industry standard | CVSS threshold, EPSS, rule-based IDS, regex classifier |
| **Simple ML baseline** | Minimal ML model with standard features | Logistic Regression, Decision Tree, k-NN |

At minimum, the naive baseline and one of {domain-standard, simple ML} MUST be included. All three types are recommended.

### 3.3 Evaluation Parity

All baselines MUST be evaluated under **identical conditions**:

- Same test set (identical samples, identical ordering)
- Same metrics (all metrics from METRICS_CONTRACT §2)
- Same seeds (same seed list, same splits)
- Same preprocessing (or documented justification for deviation)

**No baseline may receive a handicap.** If a baseline requires different preprocessing (e.g., a rule-based system does not use train/test splits), this MUST be documented and the comparison caveated.

### 3.4 Baseline Documentation

For each baseline, document:

| Field | Required |
|-------|----------|
| Method name and version | Yes |
| Hyperparameters (if any) | Yes |
| Feature set used | Yes |
| Any deviations from standard evaluation protocol | Yes |
| Justification for inclusion | Yes |

**Verification:** Every FINDINGS document MUST include a baseline comparison table with all baselines and all primary metrics.

---

## 4) Hyperparameter Documentation

### 4.1 Search Strategy

Strategy: **{{HP_STRATEGY}}**

| Strategy | Requirements |
|----------|-------------|
| `grid` | Document full grid. Report total configurations evaluated. |
| `random` | Document distributions sampled from, number of trials, and random seed. |
| `bayesian` | Document acquisition function, number of iterations, surrogate model. |
| `default_justified` | MUST justify why defaults are appropriate. Cite benchmark showing defaults are competitive, or explain domain reasoning. |

### 4.2 Documentation Requirements

For every model (including baselines with tunable hyperparameters), document:

| Field | Required |
|-------|----------|
| Search space (ranges/distributions for each HP) | Yes |
| Best hyperparameters found | Yes |
| Number of configurations evaluated | Yes |
| Selection criterion (which metric, which split) | Yes |
| Sensitivity analysis for top-3 most impactful HPs | Recommended |

### 4.3 Cross-Validation Strategy

Strategy: **{{CV_STRATEGY}}**

| Strategy | When to Use |
|----------|------------|
| `k-fold` | Default for i.i.d. tabular data. k >= 5 recommended. |
| `temporal` | When data has temporal ordering (time-series, versioned vulnerabilities). |
| `stratified` | When class imbalance exists. Combine with k-fold. |

**Rules:**
- Hyperparameters MUST be selected on validation data only. Test data MUST NOT influence HP selection.
- The CV strategy MUST be consistent across all models being compared.

### 4.4 Default Justification Template (for `default_justified`)

If using `default_justified`, include this block in your experiment documentation:

```
Hyperparameter defaults justification:
- Model: <model name>
- Defaults source: <library version, documentation URL>
- Justification: <cite benchmark OR explain domain reasoning>
- Risk assessment: <what could go wrong if defaults are suboptimal>
```

**Verification:** Every model's `config_resolved.yaml` MUST contain full hyperparameter values. If `default_justified`, the justification MUST appear in the experiment documentation or ADR.

---

## 5) Effect Size and Practical Significance

### 5.1 Effect Size Reporting

For every key model comparison (proposed vs baseline, proposed vs domain standard), report effect size:

| Comparison Type | Recommended Effect Size Measure |
|----------------|-------------------------------|
| Continuous metrics (AUC, F1) | Cohen's d or Cliff's delta |
| Binary outcomes | Odds ratio or risk ratio |
| Paired predictions | McNemar's test statistic |
| AUC comparisons | DeLong test (z-statistic and p-value) |

### 5.2 Statistical vs Practical Significance

Every claim of improvement MUST address both:

1. **Statistical significance:** Is the difference unlikely due to chance? (p-value or non-overlapping CIs)
2. **Practical significance:** Is the difference large enough to matter in deployment? (effect size, domain context)

Template for comparative claims:

```
Model A outperforms Model B on <metric>:
  A: X.XXX (95% CI: [X.XXX, X.XXX])
  B: X.XXX (95% CI: [X.XXX, X.XXX])
  Difference: X.XXX (Cohen's d = X.XX)
  Statistical test: <test name>, p = X.XXX
  Practical significance: <domain interpretation>
```

### 5.3 Paired Testing

When comparing models evaluated on the same test set:
- Use **paired** statistical tests (not independent-sample tests)
- For classification: McNemar's test (paired binary outcomes)
- For AUC: DeLong's test (paired ROC comparison)
- For general metrics across seeds: Wilcoxon signed-rank test

**Verification:** Any claim of "significantly better" MUST be accompanied by a named statistical test and p-value or CI.

---

## 6) Learning Curves (Recommended)

> **Activation:** Include this section when training set size exceeds 1,000 samples or when data sufficiency is in question. May be omitted for small-scale exploratory experiments with documented justification.

### 6.1 Protocol

Train the model at the following fractions of the full training set:

| Fraction | Purpose |
|----------|---------|
| 10% | Detect severe data insufficiency |
| 25% | Early scaling behavior |
| 50% | Mid-scale performance |
| 75% | Diminishing returns detection |
| 100% | Full training set |

At each fraction:
- Use the same hyperparameters as the full-data run
- Report all primary metrics with CIs (per §2)
- Run all seeds (per §1)

### 6.2 Diagnostic Interpretation

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| Train high, val low at all sizes | Overfitting | Add regularization, reduce model complexity |
| Train low, val low at all sizes | Underfitting | Increase model complexity, add features |
| Val plateaus early (e.g., 25%) | Data sufficient | Document; more data unlikely to help |
| Val still rising at 100% | Data insufficient | Document limitation; recommend more data |

### 6.3 Output

Learning curve data MUST be saved to `outputs/learning_curves/<model_name>.csv`:

```
fraction,train_metric,val_metric,val_ci_lower,val_ci_upper,n_samples
0.10,...
0.25,...
```

**Verification:** If learning curves are included, assert CSV exists and contains all five fractions.

---

## 7) Ablation Study (Recommended if features > 10)

> **Activation:** Include this section when the feature set exceeds 10 features or when the model includes multiple distinct components (e.g., feature groups, preprocessing steps, architectural modules). May be omitted with documented justification.

### 7.1 Feature Group Ablation

Group features into semantically meaningful clusters. For each group:

1. Remove the group entirely
2. Retrain the model with remaining features (same HPs, same seeds)
3. Report change in all primary metrics with CIs

| Feature Group | Features | AUC (full) | AUC (ablated) | Delta | Interpretation |
|--------------|----------|------------|---------------|-------|----------------|
| *(e.g.)* Temporal | age, recency, frequency | X.XXX | X.XXX | -X.XXX | Critical |
| *(e.g.)* Network | degree, centrality | X.XXX | X.XXX | -X.XXX | Moderate |

### 7.2 Permutation Importance (Alternative)

If full ablation is too expensive, use permutation importance:
- Permute each feature (or feature group) and measure metric degradation
- Use multiple permutation seeds (>= 10)
- Report mean importance +/- std
- Apply statistical test (paired t-test or Wilcoxon) to distinguish signal from noise

### 7.3 Output

Ablation results MUST be saved to `outputs/ablation/<model_name>.csv`:

```
feature_group,metric_full,metric_ablated,delta,ci_lower,ci_upper
```

**Verification:** If ablation is included, assert CSV exists and all feature groups are represented.

---

## 8) Data Type Annotation

### 8.1 Data Type Declaration

Data type: **{{DATA_TYPE}}**

| Type | Definition | Claim Constraints |
|------|-----------|------------------|
| `real` | All data is from real-world sources with no synthetic augmentation | Claims may generalize to production settings |
| `synthetic` | Data is entirely generated (simulation, LLM-generated, etc.) | ALL claims MUST carry **[SYNTHETIC]** qualifier |
| `semi-synthetic` | Mix of real and generated data | Document which parts are real vs generated; claims on synthetic portions carry **[SYNTHETIC]** qualifier |

### 8.2 Synthetic Data Disclosure

If `{{DATA_TYPE}}` is `synthetic` or `semi-synthetic`:

| Field | Required |
|-------|----------|
| Generation method | Yes |
| Generation parameters / prompts | Yes |
| Which features/labels are synthetic | Yes (for semi-synthetic) |
| Validation against real-world distribution (if available) | Recommended |
| Known biases or limitations of the generation process | Yes |

### 8.3 Claim Qualification Rules

- **[SYNTHETIC]** qualifier MUST appear in the sentence-level claim, not just in a footnote.
- Example: "The model achieves 0.92 AUC **[SYNTHETIC]** on the generated vulnerability dataset."
- Claims on synthetic data MUST NOT be presented as equivalent to real-world performance without explicit validation.

**Verification:** Every FINDINGS document MUST declare `data_type` in its header. Grep for unqualified claims on synthetic data.

---

## 9) Acceptance Criteria

Before any FINDINGS document or publication draft is considered complete, ALL of the following MUST be satisfied:

### 9.1 Hard Requirements (MUST pass)

- [ ] All primary metrics reported with confidence intervals (§2)
- [ ] >= {{MIN_SEEDS}} seeds run and reported for every model and baseline (§1)
- [ ] >= {{MIN_BASELINES}} baselines compared under identical evaluation protocol (§3)
- [ ] Hyperparameter search strategy documented with full search space and best params (§4)
- [ ] Data type annotated; synthetic claims carry [SYNTHETIC] qualifier (§8)
- [ ] No claim exceeds evidence strength (no causal claims from correlational evidence, no population claims from synthetic data)
- [ ] All comparative claims include effect size or statistical test (§5)
- [ ] Seed list is pre-registered and unchanged from initial declaration (§1)

### 9.2 Soft Requirements (SHOULD pass; document justification if skipped)

- [ ] Learning curves computed at 5 fractions (§6)
- [ ] Ablation study or permutation importance for models with > 10 features (§7)
- [ ] Bootstrap CIs with >= 10,000 samples (§2.5)
- [ ] Sensitivity analysis for top-3 hyperparameters (§4.2)
- [ ] Paired statistical tests for model comparisons (§5.3)

### 9.3 Evidence Strength Ladder

Claims MUST be calibrated to the evidence available:

| Evidence Level | Permitted Claim Language |
|---------------|------------------------|
| Single seed, no CI | "In this run, ..." (no generalization) |
| Multi-seed, no CI | "Across N seeds, mean metric was ..." |
| Multi-seed + CI | "Model achieves X.XX (95% CI: [X.XX, X.XX])" |
| Multi-seed + CI + statistical test | "Model significantly outperforms baseline (p < 0.05)" |
| Multi-seed + CI + test + effect size | "Model outperforms baseline with large effect (Cohen's d = X.XX, p < 0.05)" |
| Above + real data + external validation | "Results suggest production applicability" |

**Verification:** Run acceptance criteria checklist before any FINDINGS merge. Failed hard requirements block the merge.

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Seed list or minimum seed count
- CI method or confidence level
- Baseline list or minimum baseline count
- Hyperparameter search strategy
- Cross-validation strategy
- Data type declaration
- Acceptance criteria (hard or soft)
- Evidence strength ladder
- Any reporting format defined in this document
