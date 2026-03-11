# ML Governance Templates — Claude Code Context

## Project Purpose
Reusable governance framework for ML experiment projects. Currently v1.0 (15 templates). Upgrading to v2.0 (25 templates) per `EXECUTION_PLAN.md`.

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
- Phase 1 in progress:
  - Step 1.1 (U4: template versioning) — DONE
  - Step 1.2 (U1: authority hierarchy header) — DONE
  - Step 1.3 (U2: cross-contract references) — DONE
  - Step 1.4 (U5: HYPOTHESIS_CONTRACT) — DONE
  - Step 1.5 (U6: AI_DIVISION_OF_LABOR) — DONE
  - Step 1.6 (U7: REPRODUCIBILITY_SPEC) — DONE
  - Step 1.7 (U8+U28: CONFIGURATION_SPEC) — DONE
  - Step 1.8 (U9: TEST_ARCHITECTURE) — DONE
  - Step 1.9 (Update TEMPLATE_INDEX.md) — DONE
  - Step 1.10 (Tag v1.5-foundation) — DONE
