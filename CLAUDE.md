# ML Governance Templates — Claude Code Context

## Project Purpose
Reusable governance framework for ML experiment projects. Currently v1.8 (21 templates, all deepened). Upgrading to v2.0 (25 templates) per `EXECUTION_PLAN.md`.

## Key Files
- `EXECUTION_PLAN.md` — master plan with 31 upgrades (U1-U31), 3 phases, quality gates
- `TEMPLATE_INDEX.md` — current template inventory and dependency graph
- `PROMPT_PLAYBOOK.md` — AI-assisted customization workflow
- `README.md` — project overview
- `templates/core/` — 11 core contract templates (7 original + 4 new in v1.5)
- `templates/management/` — 6 project management templates
- `templates/report/` — 3 delivery templates + IEEE LaTeX reference (1 new in v1.5)

## Source Repos (for reference during upgrades)
These repos contain the battle-tested governance docs that v2.0 upgrades are extracted from:
- `~/CS_7641_Machine_Learning_OL_Report/` — primary source for most innovations (H1-H14 in the gap analysis)
- `~/CS_7641_Machine_Learning_SL_Report/` — source for G1-G6 innovations (authority hierarchy, division of labor, hypothesis gating)

## Conventions
- All templates use `{{PLACEHOLDER}}` syntax for project-specific values
- Each template starts with a Customization Guide table
- Commit messages reference upgrade IDs: `U4: Add version headers to all 15 templates`
- Tags at phase boundaries: `v1.5-foundation`, `v1.8-deepened`, `v2.0`
- MUST vs SHOULD: MUST = backed by Tier 1/2 requirement, SHOULD = best practice

## Current Status
- EXECUTION_PLAN.md is locked in and committed
- Phase 1 (Foundation) — COMPLETE, tagged `v1.5-foundation`
  - Steps 1.1-1.10 (U1-U9, U28): All DONE
- Phase 2 (Deepen Existing Templates) — COMPLETE, tagged `v1.8-deepened`
  - Step 2.1 (U12: DATA_CONTRACT leakage tripwires + split hash) — DONE
  - Step 2.2 (U13: EXPERIMENT_CONTRACT budgets + init + composition) — DONE
  - Step 2.3 (U14: METRICS_CONTRACT threshold + sanity + per-class) — DONE
  - Step 2.4 (U15: FIGURES_TABLES_CONTRACT captions + viz catalog) — DONE
  - Step 2.5 (U16: ARTIFACT_MANIFEST_SPEC provenance + determinism) — DONE
  - Step 2.6 (U17: PRIOR_WORK_REUSE decision tree + verification) — DONE
  - Step 2.7 (U18: RISK_REGISTER taxonomy + automation hooks) — DONE
  - Step 2.8 (U19: DECISION_LOG alternatives + contracts affected) — DONE
  - Step 2.9 (U20: CHANGELOG backward-compat + regen tracking) — DONE
  - Step 2.10 (U21: IMPLEMENTATION_PLAYBOOK Phase 0 + DoD + hooks) — DONE
  - Step 2.11 (U3: Verification annotations across 8 templates) — DONE
- Phase 3 (New Templates + Final Polish) — NOT STARTED
