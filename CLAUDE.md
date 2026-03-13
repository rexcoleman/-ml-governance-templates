# govML — Claude Code Context

## Project Purpose
Reusable governance framework for ML experiment projects. **v2.1** — 27 templates across 4 directories, 6 quickstart profiles, AI-assisted prompt playbook, 3 code generators + master runner.

## Key Files
- `TEMPLATE_INDEX.md` — full inventory, 6 quickstart profiles, Mermaid dependency graph
- `ROADMAP.md` — version history, planned generators, orchestration maturity model
- `PROMPT_PLAYBOOK.md` — AI-assisted customization workflow (stages 1-9 + 1b, 4f-4k)
- `README.md` — project overview with template tiers and profiles
- `EXECUTION_PLAN.md` — v2.0 upgrade plan (31 upgrades, all complete)
- `project.yaml.example` — structured config schema for generators
- `templates/core/` — 13 core contract templates
- `templates/management/` — 7 project management templates (including CLAUDE_MD)
- `templates/report/` — 4 delivery templates + IEEE LaTeX reference
- `templates/publishing/` — 3 publishing templates
- `examples/` — worked examples per quickstart profile
- `scripts/init_project.sh` — project initializer with `--profile` and `--generate` flags
- `scripts/generators/` — code generators that read project.yaml:
  - `generate_all.py` — master runner (invokes G1, G5, G6)
  - `orchestrate.py` — Claude Agent SDK orchestrator (agent mode, standalone mode, dry-run)
  - `gen_sweep.py` — G1: experiment sweep script
  - `gen_manifest_verifier.py` — G5: artifact integrity verifier
  - `gen_phase_gates.py` — G6: phase gate check scripts

## Conventions
- All templates use `{{PLACEHOLDER}}` syntax for project-specific values
- Each template starts with version metadata, authority hierarchy, companion contracts, and customization guide
- Templates include `**Verification:**` annotations on MUST requirements
- Optional templates (ADVERSARIAL_EVALUATION, ENVIRONMENT_SPEC) have activation markers
- MUST vs SHOULD: MUST = backed by Tier 1/2 requirement, SHOULD = best practice
- CONTRACT_CHANGE protocol: decision log ADR → change → changelog → commit with prefix → regen artifacts
- Generators read `project.yaml`, never parse markdown templates

## Version History
- `v1.5-foundation` — Phase 1: Foundation (U1-U9, U28)
- `v1.8-deepened` — Phase 2: Deepen existing templates (U12-U21, U3)
- `v2.0` — Phase 3: New templates + final polish (U10, U11, U22-U27, U29-U31, README, init script)
- `v2.1` — Layer 2: Executable scaffolding (project.yaml, generators G1/G5/G6, CLAUDE_MD template, --generate flag)

## All 31 Upgrades — COMPLETE
- Phase 1 (U1-U9, U28): Version headers, authority hierarchy, companion contracts, customization guides, enforcement pass, new core templates, config scoring appendix
- Phase 2 (U12-U21, U3): Deep upgrades to all existing templates + verification annotations
- Phase 3 (U10-U11, U22-U27, U29-U31): Adversarial evaluation, RL environment spec, quickstart profiles, worked examples, prompt playbook stages, execution manifest, research tool guide, dependency graph, publishing templates, README rewrite, init script update
