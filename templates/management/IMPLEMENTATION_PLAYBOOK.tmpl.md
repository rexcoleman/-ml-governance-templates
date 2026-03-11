# IMPLEMENTATION PLAYBOOK

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
- See [ENVIRONMENT_CONTRACT](../core/ENVIRONMENT_CONTRACT.tmpl.md) §5 for setup commands (Phase 0)
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §8 for data acceptance tests (Phase 1)
- See [METRICS_CONTRACT](../core/METRICS_CONTRACT.tmpl.md) §7 for sanity check requirements (Phase 3)
- See [EXPERIMENT_CONTRACT](../core/EXPERIMENT_CONTRACT.tmpl.md) §exit gates for per-part exit criteria
- See [FIGURES_TABLES_CONTRACT](../core/FIGURES_TABLES_CONTRACT.tmpl.md) §7 for artifact acceptance criteria
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §8 for manifest verification gate
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §6 for reproduction sequence

**Downstream (depends on this contract):**
- See [TASK_BOARD](TASK_BOARD.tmpl.md) for operational task tracking derived from phase plan
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for phase-gate risk scanning

{{PROJECT_NAME}} — Execution Playbook

---

## 0) Purpose

This playbook is the single operational document for implementing the **{{PROJECT_NAME}}** project end-to-end. It translates all tiered requirements and project contracts into a concrete iteration loop with phase gates, commands, and stop-ship checks.

**Scope:** Code implementation, experiment execution, artifact generation, and report assembly. This playbook does NOT replace any contract; it orchestrates them.

---

## 1) Conflict Resolution Rules

1. **T1 vs anything:** T1 wins. No exceptions.
2. **T2 vs T3 or contracts:** T2 wins.
3. **T3 vs contracts:** T3 is advisory. If T3 contradicts a contract, check whether the contract is grounded in T1/T2. If yes, the contract stands.
4. **Contract vs contract:** Resolve by tracing both to T1/T2. The one with stronger grounding wins. If ambiguous, record in DECISION_LOG and pick the conservative interpretation.
5. **Silence:** If T1/T2 are silent, contracts may specify choices using SHOULD (not MUST).

### MUST vs SHOULD Convention

- **MUST** = backed by explicit T1/T2 requirement or a contract clause directly implementing one
- **SHOULD** = project-level hardening or best practice not explicitly mandated by T1/T2

---

## 2) Phase Plan with DoD Gates

Each phase has a hard gate. No work in phase N+1 may begin until phase N's gate passes.

### Phase 0 — Environment & Governance Lock

**Goal:** Infrastructure ready, budgets locked, splits frozen.

| Step | Command / Action | DoD |
|------|-----------------|-----|
| Create environment | `{{ENV_MANAGER}} env create -f {{ENV_FILE}}` | Exits 0; env active |
| Verify environment | `bash scripts/verify_env.sh` | Exits 0; versions printed |
| Populate budgets | Fill all keys in `{{BUDGET_CONFIG}}` | All keys non-null; cross-part budget constraints satisfied |
| Lock data splits | Verify/generate split files | Split files in `data/splits/`; hashes recorded |
| Commit governance | `git commit -m "CONTRACT_CHANGE: ..."` | All contracts + configs committed |

**Gate:** All steps pass. Record in CHANGELOG.

---

### Phase 1 — Data Readiness & Validation

**Goal:** Data verified, leakage prevented, EDA complete.

| Step | Command | DoD |
|------|---------|-----|
| Verify raw data | `python scripts/check_data_ready.py` | Exits 0; files present |
| Run leakage tripwires | `python scripts/check_leakage.py` | Exits 0; all tripwires pass |
| Run EDA | `python scripts/run_eda.py --dataset {{DATASET}} --seed {{DEFAULT_SEED}}` | Exits 0; EDA summaries written |
| Save initial weights | *(Implemented in training scripts)* | `state_dict` saved per seed |

**Gate:** All checks pass; EDA summaries exist.

---

### Phase 2 — Hypotheses

**Goal:** Testable hypotheses written before experiments.

| Step | Action | DoD |
|------|--------|-----|
| Formulate hypotheses | Write grounded in EDA + theory | Each includes: predicted behavior, reasoning, mechanism, baseline prediction |

**Gate:** Hypotheses committed. Experiments MUST NOT run before this.

---

### Phase 3 — Sanity Checks

**Goal:** Pipeline credibility established.

| Step | Command | DoD |
|------|---------|-----|
| Run sanity checks | `python scripts/run_sanity_checks.py` | Exits 0; results in `outputs/sanity_checks/` |
| Verify results | Inspect outputs | Dummy ≈ majority proportion; shuffled ≈ chance |

**Gate:** Sanity checks pass.

---

### Phase 4-N — Experiments

*(Create one phase per experimental part. Template:)*

### Phase {{N}} — {{PART_NAME}}

**Goal:** *(One-sentence goal)*

| Step | Command | DoD |
|------|---------|-----|
| Run experiments | `python scripts/run_{{PART}}.py ...` | All methods complete; budget matched; required fields logged |
| Multi-seed stability | Repeat for each seed in stability list | All seeds complete; dispersion computable |
| Verify outputs | Inspect summary.json files | Required fields present; budget usage consistent |

**Gate:** Exit gate checklist (see EXPERIMENT_CONTRACT) all pass.

---

### Phase {{N+1}} — Final Evaluation & Artifact Assembly

**Goal:** Test split accessed once; all figures/tables generated.

| Step | Command | DoD |
|------|---------|-----|
| Final eval | `python scripts/final_eval.py --seed {{DEFAULT_SEED}}` | Test split accessed once; results written |
| Generate artifacts | `python scripts/make_report_artifacts.py --seed {{DEFAULT_SEED}}` | All figures/tables produced |
| Verify manifests | `python scripts/verify_manifests.py` | SHA-256 verified; zero mismatches |
| Verify no test leakage | Grep per-run outputs for test metric keys | Zero matches |

**Gate:** All verifications pass. Artifacts are report-ready.

---

### Phase {{N+2}} — Report Writing & Delivery

**Goal:** Report + REPRO delivered by delivery date.

| Step | Action | DoD |
|------|--------|-----|
| Draft report | Write in LaTeX editor; ≤ page limit | Paragraph prose; figures with takeaways; hypotheses resolved |
| AI Use Statement | Add per requirements | Present before References |
| REPRO document | Write with all reproduction details | Report link, Git SHA, commands, seeds, EDA confirmation |
| Push code | Push to designated repository | SHA matches REPRO |
| Pre-flight checklist | Run full checklist | All items pass |
| Deliver | Upload to delivery platform | By delivery date |

---

## 3) Iteration Loop

### 3.1 Pick a Task

1. Read TASK_BOARD to find the next unblocked task in the current phase
2. Verify all dependencies are Done
3. Prefer tasks in ID order within a phase

### 3.2 Implement

1. Read the canonical spec docs for the task
2. Read existing code before modifying (never write blind)
3. Implement the minimum change to satisfy the DoD
4. Do NOT invent numeric budgets — read from config
5. Do NOT access test split except in final_eval
6. Do NOT add features beyond the task scope

### 3.3 Test

1. Run the command in the task's DoD
2. Verify exit code is 0
3. Verify output files exist with expected schema
4. Run relevant checks (leakage, budget match, etc.)

### 3.4 Record Provenance

1. Verify provenance files were written
2. If CONTRACT_CHANGE needed, follow §5 below
3. Commit with descriptive message

### 3.5 Update Logs

1. Update TASK_BOARD: mark task Done
2. If a decision was made: add ADR to DECISION_LOG
3. If a contract changed: add entry to CHANGELOG
4. Move to next task

### 3.6 Phase Gate Check

1. When all tasks in a phase are Done, run gate checks
2. If all pass, proceed
3. If any fail, fix and re-run

---

## 4) Change Control

### 4.1 When CONTRACT_CHANGE Is Required

| Category | Examples | Contract Reference |
|----------|---------|-------------------|
| Environment | Python version, dependencies | ENVIRONMENT_CONTRACT §11 |
| Data | Paths, splits, preprocessing | DATA_CONTRACT §9 |
| Experiments | Budgets, method lists, init protocol, output schemas | EXPERIMENT_CONTRACT change control section |
| Metrics | Definitions, thresholds, sanity checks | METRICS_CONTRACT §10 |
| Scripts | Filenames, CLI flags, outputs | SCRIPT_ENTRYPOINTS_SPEC §8 |
| Figures/Tables | Definitions, columns, captions | FIGURES_TABLES_CONTRACT §8 |
| Artifacts | Run ID, manifests, hashing | ARTIFACT_MANIFEST_SPEC §9 |

### 4.2 How to Record

1. **DECISION_LOG** — Add ADR entry (if architectural decision)
2. **Make the change** — Edit contract/config/code
3. **CHANGELOG** — Add change item entry
4. **Commit** — `git commit -m "CONTRACT_CHANGE: [description]"`
5. **Regenerate** — Re-run impacted downstream artifacts

---

## 5) Stop-Ship Checks

Run ALL before delivery. **CRITICAL** items risk invalidation or critical compliance failure.

### Data Integrity (CRITICAL)

- [ ] Correct datasets used (no substitutes)
- [ ] No preprocessing leakage (fit on train only)
- [ ] Test split accessed exactly once, only via final_eval

### Compute Discipline (CRITICAL)

- [ ] Budgets matched within each part
- [ ] All methods start from same init weights (where required)
- [ ] Cross-part budget constraints satisfied
- [ ] Over-budget runs marked and excluded

### Metrics (CRITICAL)

- [ ] Required metrics present for each dataset
- [ ] Sanity checks run and reported
- [ ] Dispersion shown (median + IQR), not just means

### Artifacts (CRITICAL)

- [ ] All required figures present
- [ ] All required tables present
- [ ] Summary table has required columns + baseline row

### Report Compliance

- [ ] Within page limit
- [ ] Paragraph prose in results/discussion (no excess bullets)
- [ ] Hypotheses stated before experiments, resolved with evidence
- [ ] Baseline comparison per dataset
- [ ] Decision rule / practical recommendation in conclusion
- [ ] AI Use Statement present
- [ ] Sufficient peer-reviewed references
- [ ] Consistent citation style
- [ ] READ-ONLY link present
- [ ] Two deliverables released (Report + REPRO)

---

## 6) Canonical Spec Pointers

| Topic | Document | Key Sections |
|-------|----------|-------------|
| Environment, commands, CPU rule | ENVIRONMENT_CONTRACT | Setup, commands, determinism, change control |
| Data paths, splits, leakage | DATA_CONTRACT | Splits, leakage, preprocessing, acceptance |
| Experiment protocol, budgets | EXPERIMENT_CONTRACT | Budgets, init, per-part protocols, exit gates |
| Metric definitions, thresholds | METRICS_CONTRACT | Metrics, threshold, sanity checks, logging |
| Figures, tables, captions | FIGURES_TABLES_CONTRACT | Figure/table defs, captions, acceptance |
| Script CLIs, flags, outputs | SCRIPT_ENTRYPOINTS_SPEC | Conventions, per-script specs, repro sequence |
| Manifests, hashing | ARTIFACT_MANIFEST_SPEC | Run ID, provenance, manifests, hashing |
| Risk tracking | RISK_REGISTER | Full document |
| Task dependencies | TASK_BOARD | Phase tables, critical path |
| Report structure | REPORT_ASSEMBLY_PLAN | Outline, figures, baselines, hypotheses, checklist |
| Decisions | DECISION_LOG | ADR entries |
| Change history | CHANGELOG | Chronological entries |
