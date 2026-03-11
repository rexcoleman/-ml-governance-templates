# TASK BOARD

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
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for phase plan and gate definitions
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for risk IDs referenced in task rows

**Downstream (depends on this contract):**
- None — this is an operational tracking document.

## {{PROJECT_NAME}} — Operational Task Board

**Status:** Living document; update task status at every phase gate.

---

### Conventions

- All tasks trace to authority documents. Where a task enforces a requirement, the DoD uses **MUST**. Where it enforces project hardening, the DoD uses **SHOULD**.
- **Owner codes:** `Data` = data pipeline | `Training` = experiment scripts | `Eval` = evaluation/metrics | `Report` = report writing
- **Budget references:** All budget values from `{{BUDGET_CONFIG}}`. No fabricated numbers.
- **Risk IDs:** From RISK_REGISTER (R-XX).

---

## Phase 0 — Environment & Governance Lock

_Goal: Infrastructure ready, budgets locked, splits frozen. No experiments until this gate passes._

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T0.1 | Create environment | *(cite)* | `{{ENV_FILE}}` | Active env | Data | — | `{{ENV_MANAGER}} env create` exits 0 | — |
| T0.2 | Verify environment | *(cite)* | Active env | stdout versions | Data | T0.1 | `verify_env.sh` exits 0 | — |
| T0.3 | Populate budget config | *(cite)* | Requirements | `{{BUDGET_CONFIG}}` all keys non-null | Training | T0.1 | Cross-part constraints verified; committed | *(risk IDs)* |
| T0.4 | Lock data splits | *(cite)* | Split source | `data/splits/` JSON files | Data | — | Hashes recorded; invariants pass | *(risk IDs)* |
| T0.5 | Commit governance | *(cite)* | All contracts | Git commit | Report | T0.3, T0.4 | All docs committed | — |

**Phase 0 gate:** T0.1-T0.5 Done.

---

## Phase 1 — Data Readiness & Validation

_Goal: Data verified, leakage prevented, EDA complete._

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T1.1 | Verify raw data | *(cite)* | `data/raw/` | Checklist pass | Data | T0.5 | `check_data_ready.py` exits 0 | *(risk IDs)* |
| T1.2 | Run leakage tripwires | *(cite)* | Splits, code | LT pass | Data | T1.1 | `check_leakage.py` exits 0 | *(risk IDs)* |
| T1.3 | Run EDA | *(cite)* | Raw data | EDA summaries | Data | T1.2 | Consistent with prior work | *(risk IDs)* |
| T1.4 | Save initial weights | *(cite)* | Model arch | `init_weights/*.pt` | Training | T1.2 | Forward pass reproducible | *(risk IDs)* |

**Phase 1 gate:** T1.1-T1.4 Done.

---

## Phase 2 — Hypotheses

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T2.1 | Formulate hypotheses | *(cite)* | EDA, baseline | Hypothesis text | Report | T1.3 | Prediction + reasoning + mechanism + baseline prediction; written before experiments | *(risk IDs)* |

---

## Phase 3 — Sanity Checks

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T3.1 | Run baselines | *(cite)* | Data, splits | `sanity_checks/` JSONs | Eval | T1.2 | Dummy + shuffled complete | *(risk IDs)* |
| T3.2 | Verify results | *(cite)* | JSONs | Pass/fail | Eval | T3.1 | Expected behavior confirmed | *(risk IDs)* |

---

## Phase 4-N — Experiments

*(Create one phase section per experimental part. Template:)*

## Phase {{N}} — {{PART_NAME}}

_Goal: {{GOAL_DESCRIPTION}}_

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T{{N}}.1 | Run experiments (seed={{DEFAULT_SEED}}) | *(cite)* | Init weights, splits, budget | `outputs/{{PART}}/` | Training | *(deps)* | All methods complete; budget matched; required fields logged | *(risk IDs)* |
| T{{N}}.2 | Multi-seed stability | *(cite)* | Seed list | Multi-seed outputs | Training | T{{N}}.1 | All seeds complete; dispersion computable | *(risk IDs)* |
| T{{N}}.3 | Exit gate | *(cite)* | All outputs | Gate pass | Eval | T{{N}}.2 | Exit gate checklist all pass | — |

---

## Phase {{N+1}} — Final Eval & Artifacts

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T{{N+1}}.1 | Run final_eval | *(cite)* | All outputs | `final_eval_results.json` | Eval | *(all experiment gates)* | Test accessed once | *(risk IDs)* |
| T{{N+1}}.2 | Generate artifacts | *(cite)* | All outputs | Figures + tables | Eval | T{{N+1}}.1 | All required artifacts produced | *(risk IDs)* |
| T{{N+1}}.3 | Verify manifests | *(opt)* | Manifest | Integrity report | Eval | T{{N+1}}.2 | SHA-256 verified | *(risk IDs)* |

---

## Phase {{N+2}} — Report & Delivery

| ID | Task | Req | Inputs | Outputs | Own | Deps | DoD | Risk |
|----|------|-----|--------|---------|-----|------|-----|------|
| T{{N+2}}.1 | Draft report | *(cite)* | Artifacts, hypotheses | Report PDF | Report | T{{N+1}}.2 | Within page limit; paragraph prose; hypotheses resolved | *(risk IDs)* |
| T{{N+2}}.2 | Write REPRO | *(cite)* | Commands, SHA | REPRO PDF | Report | T{{N+2}}.1 | All required items present | — |
| T{{N+2}}.3 | Push code | *(cite)* | Codebase | Git SHA | Report | T{{N+1}}.3 | SHA matches REPRO | *(risk IDs)* |
| T{{N+2}}.4 | Pre-flight | *(cite)* | Everything | Checklist pass | Report | T{{N+2}}.1-3 | All items pass | — |
| T{{N+2}}.5 | Deliver | *(cite)* | PDFs | Delivery confirmation | Report | T{{N+2}}.4 | By delivery date | — |

---

## Critical Path

```
T0.1 → T0.2 → T0.3 → T0.5 → T1.1 → T1.2 → T1.3 → T2.1
                                              ↓
                                            T1.4 → T{{4}}.1 → ... → T{{N+1}}.1 → T{{N+2}}.1 → T{{N+2}}.5
```

*(Fill in the actual critical path for your project. Identify parallelizable work.)*

---

## Stop-Ship Checks

| # | Check | Automated By | Risks Covered |
|---|-------|--------------|---------------|
| 1 | Correct datasets | `check_data_ready.py` | R-XX |
| 2 | No leakage | `check_leakage.py` | R-XX |
| 3 | Test accessed once | Grep outputs | R-XX |
| 4 | Budgets matched | Parse summary.json | R-XX |
| 5 | Required metrics | Verify final_eval | R-XX |
| 6 | Required figures/tables | ls outputs/ | R-XX |
| 7 | Page limit | Manual | R-XX |
| 8 | Prose (no excess bullets) | Manual | R-XX |
| 9 | Hypotheses stated + resolved | Manual | R-XX |
| 10 | Baseline comparison | Search report | R-XX |

*(Fill in actual risk IDs from your RISK_REGISTER.)*
