# RISK REGISTER

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
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §4 for leakage prevention rules (Category A risks)
- See [EXPERIMENT_CONTRACT](../core/EXPERIMENT_CONTRACT.tmpl.md) §2 for budget-matching rules (Category C risks)
- See [METRICS_CONTRACT](../core/METRICS_CONTRACT.tmpl.md) §5 for threshold governance (Category B risks)
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for integrity rules (Category E risks)
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §2 for exit codes used by automation hooks

**Downstream (depends on this contract):**
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.tmpl.md) §5 for stop-ship checks sourced from this register
- See [CHANGELOG](CHANGELOG.tmpl.md) for risk mitigation cross-references per change entry

## {{PROJECT_NAME}} — Risk Register

**Status:** Living document; review at every phase gate.

---

### Purpose

This register catalogues risks that can invalidate runs, fail acceptance criteria, or block delivery. Every entry is anchored to a specific requirement. The register is action-oriented: each risk has a concrete detection test, a mitigation step, and a phase-gate owner.

### How to Use

- **When to review:** At every phase gate and before delivery. Re-scan all High-severity rows before final release.
- **How to update:** Add new risks via `CONTRACT_CHANGE` commit. Mark mitigated risks as `CLOSED` with the commit SHA. Do not delete rows.
- **Owner codes:** `Data` = data pipeline | `Training` = experiment scripts | `Eval` = evaluation/metrics | `Report` = report writing

---

### Top Critical Invalidators

*(List the issues that, if present at delivery, result in critical invalidation or non-compliance. These are your non-negotiables.)*

1. **{{INVALIDATOR_1}}** — *(e.g., Wrong datasets)* → *(consequence)*
2. **{{INVALIDATOR_2}}** — *(e.g., Preprocessing leakage)* → *(consequence)*
3. **{{INVALIDATOR_3}}** — *(e.g., Test used for tuning)* → *(consequence)*
4. **{{INVALIDATOR_4}}** — *(e.g., Unequal budgets in comparisons)* → *(consequence)*
5. *(add more)*

---

### Risk Table

| ID | Risk | Source | Sev | Lklhd | Detection Test | Mitigation | Owner | Gate |
|----|------|--------|-----|-------|----------------|------------|-------|------|
| **A — Data & Leakage** | | | | | | | | |
| R-A1 | Dataset mismatch | *(cite)* | High | Low | `check_data_ready.py` exits 0 | Lock paths; verify hashes | Data | Phase 0 |
| R-A2 | Preprocessing leakage (fit on full data) | *(cite)* | High | Med | `check_leakage.py` LT-1, LT-3 | Pipeline.fit(X_train) only | Data | Phase 0 |
| R-A3 | Test split accessed prematurely | *(cite)* | High | Med | `check_leakage.py` LT-2 | `allow_test=False` default | Data | Phase 0 |
| R-A4 | Split drift from prior project | *(cite)* | High | Low | Hash comparison | Lock splits; CONTRACT_CHANGE for edits | Data | Phase 1 |
| **B — Evaluation Discipline** | | | | | | | | |
| R-B1 | Test used more than once | *(cite)* | High | Low | Grep for test metric keys in per-run outputs | Single test-access path | Eval | Phase 2 |
| R-B2 | Wrong metric definition | *(cite)* | High | Low | Assert correct sklearn call signature | Centralize metric computation | Eval | Phase 1 |
| R-B3 | Threshold changed after experiments | *(cite)* | High | Med | Git log for budget config edits | Lock via CONTRACT_CHANGE before experiments | Eval | Phase 1 |
| R-B4 | Missing seed dispersion | *(cite)* | High | Med | Assert seed list populated; multi-seed outputs exist | Run all seeds; report median + IQR | Training | Phase 1 |
| **C — Compute Fairness** | | | | | | | | |
| R-C1 | Mismatched budgets across methods | *(cite)* | High | Med | Assert equal budget_used across methods per seed | Scripts enforce budget cap | Training | Phase 1 |
| R-C2 | Cross-part budget mismatch | *(cite)* | High | Med | Assert part3.budget == part2.budget | Shared config key | Training | Phase 0 |
| **D — Method-Specific Pitfalls** | | | | | | | | |
| *(Add risks specific to your methods — e.g., RO determinism, optimizer LR scale, regularization confounds)* | | | | | | | | |
| **E — Artifact & Repro Risks** | | | | | | | | |
| R-E1 | Missing provenance files | *(cite)* | Med | Med | `verify_manifests.py` | First run writes provenance | Report | Phase 2 |
| R-E2 | Missing figures/tables | *(cite)* | High | Low | ls outputs/figures/ tables/ | Producer script errors on missing input | Eval | Phase 2 |
| R-E3 | Test metrics outside final_eval | *(cite)* | High | Low | Grep per-run outputs | Centralize in final_eval.py | Eval | Phase 2 |
| **F — Report Compliance** | | | | | | | | |
| R-F1 | Exceeds page limit | *(cite)* | High | Med | Page count check | Tighten prose, reduce figure sizes | Report | Phase 3 |
| R-F2 | Excess bullets (not prose) | *(cite)* | High | Med | Visual scan | Write analysis as paragraphs | Report | Phase 3 |
| R-F3 | Missing hypotheses or resolution | *(cite)* | High | Med | Search report text | Write before experiments; resolve with evidence | Report | Phase 1 |
| R-F4 | Missing baseline comparison | *(cite)* | Med | Med | Search for baseline reference | Include baseline row in summary table | Report | Phase 3 |
| R-F5 | Missing AI Use Statement | *(cite)* | Med | Low | Ctrl-F report | Add before References | Report | Phase 3 |
| R-F6 | Code on wrong repository | *(cite)* | Low | Low | Verify repo URL | Push to designated repo | Report | Final |

---

### Automation Hooks

| Hook | Risks Covered | Implementation | Trigger |
|------|---------------|----------------|---------|
| Leakage tripwire | R-A2, R-A3 | `check_leakage.py` exits 0 | Pre-experiment |
| Test-access guard | R-A3, R-B1, R-E3 | Grep for test metric keys | Post-experiment |
| Budget equality | R-C1, R-C2 | Parse summary.json per part | Post-experiment |
| Init-weight match | *(method-specific)* | Forward-pass equality check | Start of comparison experiments |
| Budget config schema | R-B3, R-C2 | Validate required keys | Phase 0 gate |
| Manifest integrity | R-E1 | `verify_manifests.py` | Pre-delivery |
