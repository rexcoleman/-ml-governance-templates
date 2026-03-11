# ML Project Governance Templates

A reusable framework of 25 governance templates for machine learning projects — from experiment design through publication.

---

## What This Is

A suite of markdown templates organized into four tiers that provide structure, discipline, and traceability for ML projects. The framework enforces:

- **Reproducibility** — locked environments, deterministic seeding, artifact hashing
- **Data integrity** — leakage prevention, fit-on-train discipline, test-split isolation
- **Fair comparisons** — budget matching, shared initialization, multi-seed stability
- **Change control** — CONTRACT_CHANGE protocol, decision records, changelog
- **Delivery readiness** — pre-flight checklists, report assembly, execution manifests
- **Publication quality** — anti-claims, message governance, academic integrity firewalls
- **Specialized evaluation** — adversarial robustness, RL environment specs, hypothesis pre-registration

---

## Quick Start

```bash
# Choose a quickstart profile matching your project type
bash scripts/init_project.sh /path/to/your/project --profile supervised

# Available profiles: minimal, supervised, optimization, unsupervised, rl-agent, full
```

Then fill in `{{PLACEHOLDERS}}` in each template — start with ENVIRONMENT_CONTRACT and DATA_CONTRACT.

**Prompt-driven alternative:** Use the [Prompt Playbook](PROMPT_PLAYBOOK.md) to walk through template customization with an AI assistant. Stages 1-5 go from raw problem statement to filled templates; Stage 6 is the hallucination firewall.

See [TEMPLATE_INDEX.md](TEMPLATE_INDEX.md) for quickstart profiles, dependency graph, and the full template inventory.

---

## Template Tiers

### Core Contracts (`templates/core/` — 13 templates)

The experiment infrastructure. Every ML project with reproducibility requirements uses a subset of these.

| Template | Purpose |
|----------|---------|
| `ENVIRONMENT_CONTRACT` | Python version, dependencies, determinism, platform |
| `DATA_CONTRACT` | Data paths, splits, leakage prevention, preprocessing |
| `EXPERIMENT_CONTRACT` | Experiment matrix, budgets, seeding, output schemas |
| `METRICS_CONTRACT` | Metric definitions, thresholds, sanity checks |
| `FIGURES_TABLES_CONTRACT` | Figure/table specs, captions, traceability |
| `ARTIFACT_MANIFEST_SPEC` | Run IDs, SHA-256 hashing, integrity verification |
| `SCRIPT_ENTRYPOINTS_SPEC` | CLI conventions, phase gates, exit codes |
| `HYPOTHESIS_CONTRACT` | Pre-registered hypotheses with temporal gating |
| `AI_DIVISION_OF_LABOR` | Human-AI collaboration boundaries, anti-ghostwriting firewall |
| `CONFIGURATION_SPEC` | Layered config governance, locked keys, resolved snapshots |
| `TEST_ARCHITECTURE` | Structured testing: leakage, determinism, sanity categories |
| `ADVERSARIAL_EVALUATION` | *(Optional)* Threat models, robustness metrics, attack protocols |
| `ENVIRONMENT_SPEC` | *(Optional)* RL/simulation MDP specification |

### Management Templates (`templates/management/` — 6 templates)

Project tracking for multi-phase work with dependencies and change control.

| Template | Purpose |
|----------|---------|
| `IMPLEMENTATION_PLAYBOOK` | Phase plan with DoD gates, iteration loop, stop-ship checks |
| `TASK_BOARD` | Phase-gated task tracking with critical path |
| `RISK_REGISTER` | Risk table with detection tests and automation hooks |
| `DECISION_LOG` | ADR-format architecture decision records |
| `CHANGELOG` | CONTRACT_CHANGE tracking with artifact regeneration |
| `PRIOR_WORK_REUSE` | Vendor snapshot strategy for reusing prior project artifacts |

### Report & Delivery (`templates/report/` — 4 templates + 1 reference)

Assemble and verify final deliverables with full traceability.

| Template | Purpose |
|----------|---------|
| `REPORT_ASSEMBLY_PLAN` | Section outline, page budget, hypothesis templates |
| `REPRODUCIBILITY_SPEC` | Single-document reproduction guide |
| `PRE_SUBMISSION_CHECKLIST` | Attribution, compliance, artifact verification audit |
| `EXECUTION_MANIFEST` | Auto-generated methods summary + results index |
| `IEEE_Report_Template.tex` | Standard IEEE LaTeX template (reference) |

### Publishing (`templates/publishing/` — 3 templates)

Communication strategy, integrity verification, and strategic hypothesis framing for formal delivery.

| Template | Purpose |
|----------|---------|
| `PUBLICATION_BRIEF` | Target reader, anti-claims, message governance, portfolio alignment |
| `ACADEMIC_INTEGRITY_FIREWALL` | Three walls (data/code/content), transferable vs prohibited lists |
| `LEAN_HYPOTHESIS` | Customer-problem fit, kill criteria, minimum viable experiment |

---

## Quickstart Profiles

Choose a profile based on project type. See [TEMPLATE_INDEX.md](TEMPLATE_INDEX.md) for full details including which optional appendices to activate.

| Profile | Templates | Use For |
|---------|:---------:|---------|
| **Minimal** | 3 | Quick experiments, prototypes |
| **Supervised ML** | 9 | Classification/regression with formal report |
| **Optimization Benchmark** | 11 | Optimizer comparisons, ablation studies |
| **Unsupervised Analysis** | 21 | Clustering, dimensionality reduction |
| **RL / Agent Study** | 22 | Reinforcement learning, full delivery |
| **Full + Publishing** | 25 | Complex projects with publication goals |

---

## Core Concepts

### Authority Hierarchy

Every template supports a tiered authority structure:
- **Tier 1:** Primary requirements document (highest authority)
- **Tier 2:** Clarifications and FAQ (cannot override Tier 1)
- **Tier 3:** Advisory specifications (non-binding if inconsistent)
- **Contracts:** Your governance docs (subordinate to all tiers)

When conflicts arise: Tier 1 wins. Always.

### CONTRACT_CHANGE Protocol

When modifying any contracted item:
1. Record the decision in `DECISION_LOG` (ADR format)
2. Make the change
3. Log it in `CHANGELOG`
4. Commit with `CONTRACT_CHANGE:` prefix
5. Regenerate impacted downstream artifacts

### Leakage Prevention

The framework treats data leakage as a critical invalidator:
- Fit preprocessing on train only
- Test split accessible only through final eval script
- Automated tripwires catch violations early

---

## Prompt Playbook

The [Prompt Playbook](PROMPT_PLAYBOOK.md) provides AI-assisted workflows:

| Stages | Purpose |
|--------|---------|
| 1, 1b | Problem statement → structured brief → authority hierarchy |
| 2-3 | Requirements extraction → template selection |
| 4a-4e | Core template customization (environment, data, experiment, management, report) |
| 4f-4k | Specialized templates (hypothesis, unsupervised, RL, adversarial, publishing, integrity) |
| 5 | Cross-template consistency audit |
| 6 | RFP traceability audit (hallucination firewall) |
| 7-8 | Ongoing governance audit + targeted patches |
| 9 | Test code generation (pytest suites) |

---

## Directory Structure

```
ml-governance-templates/
+-- README.md
+-- TEMPLATE_INDEX.md                      # Full inventory, profiles, dependency graph
+-- PROMPT_PLAYBOOK.md                     # AI-assisted customization prompts
+-- EXECUTION_PLAN.md                      # v2.0 upgrade plan
+-- CLAUDE.md                              # AI assistant project context
+-- templates/
|   +-- core/                              # 13 templates
|   |   +-- DATA_CONTRACT.tmpl.md
|   |   +-- ENVIRONMENT_CONTRACT.tmpl.md
|   |   +-- EXPERIMENT_CONTRACT.tmpl.md
|   |   +-- METRICS_CONTRACT.tmpl.md
|   |   +-- FIGURES_TABLES_CONTRACT.tmpl.md
|   |   +-- ARTIFACT_MANIFEST_SPEC.tmpl.md
|   |   +-- SCRIPT_ENTRYPOINTS_SPEC.tmpl.md
|   |   +-- HYPOTHESIS_CONTRACT.tmpl.md
|   |   +-- AI_DIVISION_OF_LABOR.tmpl.md
|   |   +-- CONFIGURATION_SPEC.tmpl.md
|   |   +-- TEST_ARCHITECTURE.tmpl.md
|   |   +-- ADVERSARIAL_EVALUATION.tmpl.md
|   |   +-- ENVIRONMENT_SPEC.tmpl.md
|   +-- management/                        # 6 templates
|   |   +-- IMPLEMENTATION_PLAYBOOK.tmpl.md
|   |   +-- TASK_BOARD.tmpl.md
|   |   +-- RISK_REGISTER.tmpl.md
|   |   +-- DECISION_LOG.tmpl.md
|   |   +-- CHANGELOG.tmpl.md
|   |   +-- PRIOR_WORK_REUSE.tmpl.md
|   +-- report/                            # 4 templates + 1 reference
|   |   +-- REPORT_ASSEMBLY_PLAN.tmpl.md
|   |   +-- REPRODUCIBILITY_SPEC.tmpl.md
|   |   +-- PRE_SUBMISSION_CHECKLIST.tmpl.md
|   |   +-- EXECUTION_MANIFEST.tmpl.md
|   |   +-- IEEE_Report_Template.tex
|   +-- publishing/                        # 3 templates
|       +-- PUBLICATION_BRIEF.tmpl.md
|       +-- ACADEMIC_INTEGRITY_FIREWALL.tmpl.md
|       +-- LEAN_HYPOTHESIS.tmpl.md
+-- examples/                              # Worked examples per profile
|   +-- supervised/
|   +-- optimization/
|   +-- unsupervised/
|   +-- rl-agent/
|   +-- publishing/
+-- scripts/
    +-- init_project.sh                    # Copy templates with --profile flag
```

---

## Worked Examples

The `examples/` directory contains worked examples showing representative placeholder fills for each quickstart profile:

- [`examples/supervised/`](examples/supervised/) — Heart Disease Classification
- [`examples/optimization/`](examples/optimization/) — Optimizer Comparison on CIFAR-10
- [`examples/unsupervised/`](examples/unsupervised/) — Customer Segmentation via Clustering
- [`examples/rl-agent/`](examples/rl-agent/) — CartPole Policy Optimization
- [`examples/publishing/`](examples/publishing/) — Multi-Phase ML Portfolio Project

---

## Origin

These templates were extracted from a governance framework used in production ML research. The original project used 18 governance documents to manage multi-part experiments comparing optimization algorithms across multiple datasets.

Project-specific content has been replaced with `{{PLACEHOLDER}}` syntax. The reusable patterns — phase gates, leakage prevention, budget matching, CONTRACT_CHANGE protocol, risk tracking, and decision records — are preserved. v2.0 expanded the framework from 15 to 26 templates with publishing, adversarial evaluation, RL environment, and hypothesis governance support.
