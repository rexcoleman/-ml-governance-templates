# Template Index

Complete list of all governance templates with descriptions, dependencies, and when to use each.

---

## Core Contracts (`templates/core/`)

| # | Template | File | Depends On | When to Use |
|---|----------|------|------------|-------------|
| 1 | **Data Contract** | `DATA_CONTRACT.tmpl.md` | — | You have datasets with train/val/test splits and need leakage prevention |
| 2 | **Environment Contract** | `ENVIRONMENT_CONTRACT.tmpl.md` | — | You need reproducible experiments on a specified platform |
| 3 | **Experiment Contract** | `EXPERIMENT_CONTRACT.tmpl.md` | Data, Environment, Metrics | You're running structured experiments with budgets and comparisons |
| 4 | **Metrics Contract** | `METRICS_CONTRACT.tmpl.md` | Data | You need locked metric definitions, thresholds, and sanity checks |
| 5 | **Figures & Tables Contract** | `FIGURES_TABLES_CONTRACT.tmpl.md` | Experiment, Metrics | You're generating report-ready figures and tables |
| 6 | **Artifact Manifest Spec** | `ARTIFACT_MANIFEST_SPEC.tmpl.md` | Experiment | You want SHA-256 integrity verification of all outputs |
| 7 | **Script Entrypoints Spec** | `SCRIPT_ENTRYPOINTS_SPEC.tmpl.md` | All core contracts | You have multiple scripts with CLI flags and need a stable interface |

**Recommended setup order:** Environment → Data → Metrics → Experiment → Scripts → Figures/Tables → Artifacts

---

## Management Templates (`templates/management/`)

| # | Template | File | Depends On | When to Use |
|---|----------|------|------------|-------------|
| 8 | **Implementation Playbook** | `IMPLEMENTATION_PLAYBOOK.tmpl.md` | All core contracts | Multi-phase project; need phase gates and iteration discipline |
| 9 | **Task Board** | `TASK_BOARD.tmpl.md` | Playbook | Need task tracking with dependencies and critical path |
| 10 | **Risk Register** | `RISK_REGISTER.tmpl.md` | All core contracts | Project has acceptance criteria or compliance requirements |
| 11 | **Decision Log** | `DECISION_LOG.tmpl.md` | — | Making architectural decisions that need to be recorded |
| 12 | **Changelog** | `CHANGELOG.tmpl.md` | Decision Log | Tracking CONTRACT_CHANGE commits |
| 13 | **Prior Work Reuse** | `PRIOR_WORK_REUSE.tmpl.md` | Data, Environment | Reusing code/data/models from a prior project |

---

## Report Templates (`templates/report/`)

| # | Template | File | Depends On | When to Use |
|---|----------|------|------------|-------------|
| 14 | **Report Assembly Plan** | `REPORT_ASSEMBLY_PLAN.tmpl.md` | Figures/Tables, Metrics | Writing a structured technical report with figures and hypotheses |
| 15 | **Pre-Delivery Checklist** | `PRE_SUBMISSION_CHECKLIST.tmpl.md` | All | Final delivery audit (attribution & compliance, reproducibility, artifacts) |
| ref | **IEEE Report Template** | `IEEE_Report_Template.tex` | — | Need a LaTeX starting point for IEEE-format papers |

---

## Prompt Playbook

| # | Document | File | Purpose |
|---|----------|------|---------|
| — | **Prompt Playbook** | `PROMPT_PLAYBOOK.md` | AI-assisted 8-stage workflow: initial setup (Stages 1-5), governance audits & patches (Stages 6-7), and test code generation (Stage 8) |

---

## Starter Configurations

### Minimal (Quick Experiment)
Use when you have a simple, single-part experiment:
- `ENVIRONMENT_CONTRACT`
- `DATA_CONTRACT`
- `METRICS_CONTRACT`

### Standard (Multi-Phase Project)
Use for a multi-phase project with delivery requirements:
- All 7 core contracts
- `IMPLEMENTATION_PLAYBOOK`
- `RISK_REGISTER`
- `REPORT_ASSEMBLY_PLAN`
- `PRE_SUBMISSION_CHECKLIST`

### Full (Complex Multi-Phase Project)
Use for projects with prior work reuse, multiple experimental parts, and strict compliance:
- All 15 templates
