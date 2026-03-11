# EXECUTION MANIFEST

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
- See [EXPERIMENT_CONTRACT](../core/EXPERIMENT_CONTRACT.tmpl.md) §2 for budget definitions and §6-N for per-part protocols
- See [METRICS_CONTRACT](../core/METRICS_CONTRACT.tmpl.md) §2 for metric definitions and §9 for logging schema
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for hash verification
- See [FIGURES_TABLES_CONTRACT](../core/FIGURES_TABLES_CONTRACT.tmpl.md) §3-4 for artifact inventory

**Downstream (depends on this contract):**
- See [REPORT_ASSEMBLY_PLAN](REPORT_ASSEMBLY_PLAN.tmpl.md) §4 for figure/table placement sourced from this manifest
- See [REPRODUCIBILITY_SPEC](REPRODUCIBILITY_SPEC.tmpl.md) for reproduction commands referencing this manifest

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Optimizer Comparison Study |
| `{{GIT_SHA}}` | Git commit SHA of final artifacts | abc123def456 |
| `{{PRODUCER_SCRIPT}}` | Artifact generation script | scripts/make_report_artifacts.py |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose

This manifest is the single source of truth for all numbers, figures, and tables in the **{{PROJECT_NAME}}** report. Every quantitative claim in the report MUST trace to an entry in this manifest.

**Rule:** Report numbers MUST come from these artifacts. If a number appears in the report but not in this manifest, it is unverified and MUST be either added to the manifest or removed from the report.

**Verification:** For each quantitative claim in the report, search this manifest for the corresponding artifact and field. Any claim without a manifest entry is flagged for review.

---

## 2) Manifest Metadata

| Property | Value |
|----------|-------|
| **Project** | {{PROJECT_NAME}} |
| **Git SHA** | {{GIT_SHA}} |
| **Generated** | *(UTC timestamp of last artifact generation)* |
| **Producer** | `{{PRODUCER_SCRIPT}}` |
| **Verification** | `python scripts/verify_manifests.py` exits 0 |

---

## 3) Methods Summary

### 3.1 Experiment Matrix

Auto-generated from experiment outputs. This table summarizes what was actually run (not what was planned).

| Part | Dataset | Methods | Seeds | Budget Type | Budget Value | Runs Completed |
|------|---------|---------|-------|-------------|-------------|---------------|
| *(e.g.)* Part 1 | Adult | RHC, SA, GA | 5 | func_evals | 10000 | 15/15 |
| *(e.g.)* Part 2 | Adult | SGD, SGD+M, Nesterov, Adam, Adam-noBias, Adam-β1=0, AdamW | 5 | grad_evals | 10000 | 35/35 |
| *(add rows)* | | | | | | |

**Verification:** Compare "Runs Completed" column against expected count (`methods × seeds`). Any shortfall MUST be explained.

### 3.2 Environment Summary

| Property | Value | Source |
|----------|-------|--------|
| **Python** | *(version)* | `outputs/provenance/versions.txt` |
| **Key libraries** | *(versions)* | `outputs/provenance/versions.txt` |
| **Platform** | *(OS + hardware)* | `outputs/provenance/versions.txt` |
| **Git SHA** | *(commit)* | `outputs/provenance/git_commit_sha.txt` |

### 3.3 Configuration Snapshot

Key configuration values that govern all experiments:

| Config Key | Value | Source File |
|-----------|-------|------------|
| *(e.g.)* `part2.grad_evals` | 10000 | `{{BUDGET_CONFIG_FILE}}` |
| *(e.g.)* `part2.threshold_l` | 0.45 | `{{BUDGET_CONFIG_FILE}}` |
| *(e.g.)* `seeds.stability_list` | [42, 123, 456, 789, 1024] | `{{BUDGET_CONFIG_FILE}}` |
| *(add rows)* | | |

---

## 4) Results Index

### 4.1 Per-Run Results

| Run ID | Part | Dataset | Method | Seed | Best Val Loss | Budget Used | Over Budget | Manifest Path |
|--------|------|---------|--------|------|--------------|-------------|:-----------:|--------------|
| *(auto-generated row per run)* | | | | | | | | |

**Source:** Aggregated from `summary.json` in each run directory.

### 4.2 Final Evaluation Results

| Dataset | Method | Test Metric | Test Accuracy | Source |
|---------|--------|------------|:-------------:|--------|
| *(e.g.)* Adult | Adam | F1 = 0.72 | 0.85 | `final_eval_results.json` |
| *(e.g.)* Wine | Adam | Macro-F1 = 0.68 | 0.71 | `final_eval_results.json` |
| *(add rows)* | | | | |

**Rule:** Test metrics in the report MUST match these values exactly. No rounding, no recalculation.

**Verification:** Diff report table values against this index. Zero discrepancies required.

### 4.3 Seed-Aggregated Results

| Part | Dataset | Method | Metric | Median | IQR [Q1, Q3] | n_seeds |
|------|---------|--------|--------|--------|:-------------:|:-------:|
| *(auto-generated)* | | | | | | |

**Rule:** All comparative claims in the report MUST use seed-aggregated values from this table, not single-seed results.

---

## 5) Figure Registry

| Figure ID | Title | Source Data | Producer Script | SHA-256 | Report Section |
|-----------|-------|-----------|----------------|---------|---------------|
| F1 | *(title)* | *(run IDs or data files)* | `{{PRODUCER_SCRIPT}}` | *(hash)* | *(section)* |
| F2 | *(title)* | *(source)* | `{{PRODUCER_SCRIPT}}` | *(hash)* | *(section)* |
| *(add rows)* | | | | | |

**Rule:** Every figure in the report MUST appear in this registry. Figures not in the registry are unauthorized.

**Verification:** `python scripts/verify_manifests.py` checks all figure hashes. `ls outputs/figures/` matches registry entries.

---

## 6) Table Registry

| Table ID | Title | Source Data | Producer Script | SHA-256 | Report Section |
|----------|-------|-----------|----------------|---------|---------------|
| T1 | Summary Table | `summary.json` + `final_eval_results.json` | `{{PRODUCER_SCRIPT}}` | *(hash)* | *(section)* |
| T2 | *(title)* | *(source)* | `{{PRODUCER_SCRIPT}}` | *(hash)* | *(section)* |
| *(add rows)* | | | | | |

---

## 7) Claim-to-Evidence Traceability

Every quantitative claim in the report maps to a specific artifact.

| Report Section | Claim | Evidence Source | Manifest Entry |
|---------------|-------|----------------|---------------|
| *(e.g.)* Results §5.2 | "Adam converges 3× faster than SGD" | T1: Time to ℓ column | §4.3 seed-aggregated results |
| *(e.g.)* Results §5.3 | "Dropout reduces val_loss by 5%" | F5: Regularization comparison | §4.1 per-run results, Part 3 |
| *(e.g.)* Conclusion | "Best combo achieves F1=0.74" | T1: Test Metric column | §4.2 final eval results |
| *(add rows)* | | | |

**Rule:** This table MUST be completed before the report is finalized. Every comparative or quantitative claim in the report MUST have a row here.

---

## 8) Baseline Reference

| Baseline | Source | Metrics | Purpose |
|----------|--------|---------|---------|
| *(e.g.)* SL Report NN (SGD) | `config/sl_baseline.yaml` | Adult: Acc=0.85, F1=0.70; Wine: Acc=0.68, Macro-F1=0.60 | Cross-project comparison |
| *(e.g.)* Sanity: Dummy | `outputs/sanity_checks/` | Acc ≈ majority proportion, F1 ≈ 0 | Pipeline credibility |
| *(e.g.)* Sanity: Shuffled | `outputs/sanity_checks/` | Performance ≈ chance | Leakage detection |
| *(add rows)* | | | |

---

## 9) Manifest Generation

### 9.1 Auto-Generation Protocol

This manifest SHOULD be auto-generated by `{{PRODUCER_SCRIPT}}` or a dedicated manifest builder script. The generation process:

1. Discover all run directories under `outputs/`
2. Parse `summary.json` from each run
3. Parse `final_eval_results.json`
4. Compute seed aggregations (median + IQR)
5. List all figures and tables with hashes
6. Write this manifest

### 9.2 Manual Sections

The following sections require human input and cannot be auto-generated:
- §7 Claim-to-Evidence Traceability (requires reading the report)
- §8 Baseline Reference (requires external data)

---

## 10) Acceptance Criteria

- [ ] All runs listed in §4.1 completed successfully
- [ ] Final evaluation results present in §4.2
- [ ] Seed aggregations computed in §4.3
- [ ] All figures registered in §5 with valid hashes
- [ ] All tables registered in §6 with valid hashes
- [ ] `verify_manifests.py` exits 0
- [ ] Claim-to-evidence table (§7) covers all quantitative claims
- [ ] Report numbers match manifest values exactly

---

## 11) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Experiment matrix (parts, methods, datasets, seeds)
- Figure or table registry entries
- Baseline reference values
- Manifest generation protocol
- Claim-to-evidence traceability requirements
