# Template Index

Complete list of all governance templates with descriptions, dependencies, and when to use each.

> **v1.5-foundation:** All 21 templates have standardized version metadata (`<!-- version: 1.0 -->`),
> authority hierarchy headers, and companion contract cross-references (Tier A meta-governance: U1-U4).

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
| 8 | **Hypothesis Contract** | `HYPOTHESIS_CONTRACT.tmpl.md` | Data, Metrics | You need pre-registered hypotheses with temporal gating before experiments |
| 9 | **AI Division of Labor** | `AI_DIVISION_OF_LABOR.tmpl.md` | Experiment, Data | You're using AI tools and need human-AI collaboration boundaries |
| 10 | **Configuration Spec** | `CONFIGURATION_SPEC.tmpl.md` | Experiment, Metrics, Data | You have layered config files and need config-as-code governance |
| 11 | **Test Architecture** | `TEST_ARCHITECTURE.tmpl.md` | Data, Experiment, Metrics, Configuration | You need structured testing with leakage, determinism, and sanity categories |

**Recommended setup order:** Environment → Data → Metrics → Hypothesis → Experiment → Configuration → Scripts → Figures/Tables → Artifacts → Test Architecture → AI Division of Labor

---

## Management Templates (`templates/management/`)

| # | Template | File | Depends On | When to Use |
|---|----------|------|------------|-------------|
| 12 | **Implementation Playbook** | `IMPLEMENTATION_PLAYBOOK.tmpl.md` | All core contracts | Multi-phase project; need phase gates and iteration discipline |
| 13 | **Task Board** | `TASK_BOARD.tmpl.md` | Playbook | Need task tracking with dependencies and critical path |
| 14 | **Risk Register** | `RISK_REGISTER.tmpl.md` | All core contracts | Project has acceptance criteria or compliance requirements |
| 15 | **Decision Log** | `DECISION_LOG.tmpl.md` | — | Making architectural decisions that need to be recorded |
| 16 | **Changelog** | `CHANGELOG.tmpl.md` | Decision Log | Tracking CONTRACT_CHANGE commits |
| 17 | **Prior Work Reuse** | `PRIOR_WORK_REUSE.tmpl.md` | Data, Environment | Reusing code/data/models from a prior project |

---

## Report Templates (`templates/report/`)

| # | Template | File | Depends On | When to Use |
|---|----------|------|------------|-------------|
| 18 | **Report Assembly Plan** | `REPORT_ASSEMBLY_PLAN.tmpl.md` | Figures/Tables, Metrics | Writing a structured technical report with figures and hypotheses |
| 19 | **Reproducibility Spec** | `REPRODUCIBILITY_SPEC.tmpl.md` | Environment, Data, Scripts, Artifacts | You need a single document enabling end-to-end reproduction from a fresh clone |
| 20 | **Pre-Delivery Checklist** | `PRE_SUBMISSION_CHECKLIST.tmpl.md` | All | Final delivery audit (attribution & compliance, reproducibility, artifacts) |
| ref | **IEEE Report Template** | `IEEE_Report_Template.tex` | — | Need a LaTeX starting point for IEEE-format papers |

---

## Prompt Playbook

| # | Document | File | Purpose |
|---|----------|------|---------|
| — | **Prompt Playbook** | `PROMPT_PLAYBOOK.md` | AI-assisted 9-stage workflow: initial setup (1-5), RFP traceability audit (6), governance audits & patches (7-8), and test code generation (9) |

---

## Starter Configurations

### Minimal (Quick Experiment)
Use when you have a simple, single-part experiment:
- `ENVIRONMENT_CONTRACT`
- `DATA_CONTRACT`
- `METRICS_CONTRACT`

### Standard (Multi-Phase Project)
Use for a multi-phase project with delivery requirements:
- All 7 original core contracts (#1-7)
- `HYPOTHESIS_CONTRACT`
- `CONFIGURATION_SPEC`
- `IMPLEMENTATION_PLAYBOOK`
- `RISK_REGISTER`
- `REPORT_ASSEMBLY_PLAN`
- `REPRODUCIBILITY_SPEC`
- `PRE_SUBMISSION_CHECKLIST`

### Standard + AI Governance
Use when the Standard configuration involves AI coding assistants or chat-based tools:
- Everything in Standard, plus:
- `AI_DIVISION_OF_LABOR`

### Full (Complex Multi-Phase Project)
Use for projects with prior work reuse, multiple experimental parts, and strict compliance:
- All 21 templates
