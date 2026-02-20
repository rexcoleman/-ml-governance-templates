# ML Project Governance Templates

A reusable framework of governance documents for machine learning projects.

---

## What This Is

A suite of 15 markdown templates that provide structure, discipline, and traceability for ML experiment projects. The framework enforces:

- **Reproducibility** — locked environments, deterministic seeding, artifact hashing
- **Data integrity** — leakage prevention, fit-on-train discipline, test-split isolation
- **Fair comparisons** — budget matching, shared initialization, multi-seed stability
- **Change control** — CONTRACT_CHANGE protocol, decision records, changelog
- **Submission readiness** — pre-flight checklists, academic honesty audits, report assembly

---

## Quick Start

```bash
# 1. Copy templates to your project
bash ml-governance-templates/scripts/init_project.sh /path/to/your/project

# 2. Fill in {{PLACEHOLDERS}} in each template
#    Start with ENVIRONMENT_CONTRACT and DATA_CONTRACT

# 3. Commit as your initial governance setup
git add docs/ && git commit -m "Initialize project governance"
```

---

## Template Tiers

### Tier 1: Core Contracts (Always Use)

These 7 templates define the experiment infrastructure. Use them for any ML project with reproducibility requirements.

| Template | Purpose | Start Here If... |
|----------|---------|-------------------|
| `ENVIRONMENT_CONTRACT` | Python version, dependencies, determinism, repro commands | You need reproducible experiments |
| `DATA_CONTRACT` | Data paths, splits, leakage prevention, preprocessing | You have train/val/test splits |
| `EXPERIMENT_CONTRACT` | Experiment matrix, budgets, seeding, output schemas | You're comparing methods |
| `METRICS_CONTRACT` | Metric definitions, thresholds, sanity checks | You need consistent evaluation |
| `FIGURES_TABLES_CONTRACT` | Figure/table specs, captions, traceability | You're generating report artifacts |
| `ARTIFACT_MANIFEST_SPEC` | Run IDs, SHA-256 hashing, integrity verification | You want verifiable outputs |
| `SCRIPT_ENTRYPOINTS_SPEC` | CLI conventions, phase gates, exit codes | You have multiple scripts |

### Tier 2: Project Management (For Multi-Week Projects)

These 6 templates add project tracking. Use them when the project spans multiple weeks or has complex dependencies.

| Template | Purpose |
|----------|---------|
| `IMPLEMENTATION_PLAYBOOK` | Phase plan with DoD gates, iteration loop, change control |
| `TASK_BOARD` | Phase-gated task tracking with critical path |
| `RISK_REGISTER` | Risk table with detection tests and automation hooks |
| `DECISION_LOG` | ADR-format architecture decision records |
| `CHANGELOG` | CONTRACT_CHANGE tracking |
| `PRIOR_WORK_REUSE` | Strategy for reusing artifacts from prior projects |

### Tier 3: Report Assembly (For Graded Deliverables)

These 2 templates plus 1 reference file help assemble and verify the final report.

| Template | Purpose |
|----------|---------|
| `REPORT_ASSEMBLY_PLAN` | Section outline, page budget, hypothesis templates, pre-flight checklist |
| `PRE_SUBMISSION_CHECKLIST` | Academic honesty audit, artifact verification, git cleanup |
| `IEEE_Report_Template.tex` | Standard IEEE LaTeX template (reference, not templatized) |

---

## Core Concepts

### Authority Hierarchy

Every template supports a tiered authority structure:
- **Tier 1:** The primary requirements document (assignment, spec, client requirements)
- **Tier 2:** Clarifications and FAQ (cannot override Tier 1)
- **Tier 3:** Derived/advisory specifications
- **Contracts:** Your governance docs (subordinate to all tiers)

When conflicts arise: Tier 1 wins. Always. Trace every contract clause back to its authority source.

### MUST vs SHOULD

- **MUST** = backed by an explicit Tier 1/2 requirement
- **SHOULD** = project-level best practice, not externally mandated

### CONTRACT_CHANGE Protocol

When modifying any contracted item:
1. Record the decision in `DECISION_LOG` (ADR format)
2. Make the change
3. Log it in `CHANGELOG`
4. Commit with `CONTRACT_CHANGE:` prefix
5. Regenerate impacted downstream artifacts

### Phase Gates

Work proceeds in phases. Each phase has a hard gate — a set of checks that MUST pass before the next phase begins. This prevents building on a broken foundation.

### Leakage Prevention

The framework treats data leakage as a critical invalidator:
- Fit preprocessing on train only
- Test split accessible only through final eval script
- Automated tripwires catch violations early

---

## Customization

Every template uses `{{PLACEHOLDER}}` syntax for project-specific values. Each template starts with a **Customization Guide** table listing all placeholders, their descriptions, and examples.

**Customization workflow:**
1. Copy templates to `docs/`
2. Read each Customization Guide
3. Replace all `{{PLACEHOLDERS}}` with your project values
4. Delete the Customization Guide section when done
5. Cross-link companion contracts

---

## Directory Structure

```
ml-governance-templates/
+-- README.md                              # This file
+-- TEMPLATE_INDEX.md                      # All templates with descriptions
+-- templates/
|   +-- core/                              # Always use (7 templates)
|   |   +-- DATA_CONTRACT.tmpl.md
|   |   +-- ENVIRONMENT_CONTRACT.tmpl.md
|   |   +-- EXPERIMENT_CONTRACT.tmpl.md
|   |   +-- METRICS_CONTRACT.tmpl.md
|   |   +-- FIGURES_TABLES_CONTRACT.tmpl.md
|   |   +-- ARTIFACT_MANIFEST_SPEC.tmpl.md
|   |   +-- SCRIPT_ENTRYPOINTS_SPEC.tmpl.md
|   +-- management/                        # For multi-week projects (6 templates)
|   |   +-- IMPLEMENTATION_PLAYBOOK.tmpl.md
|   |   +-- TASK_BOARD.tmpl.md
|   |   +-- RISK_REGISTER.tmpl.md
|   |   +-- DECISION_LOG.tmpl.md
|   |   +-- CHANGELOG.tmpl.md
|   |   +-- PRIOR_WORK_REUSE.tmpl.md
|   +-- report/                            # For graded deliverables (2 + 1 ref)
|       +-- REPORT_ASSEMBLY_PLAN.tmpl.md
|       +-- PRE_SUBMISSION_CHECKLIST.tmpl.md
|       +-- IEEE_Report_Template.tex
+-- examples/
|   +-- sample-project/                    # Worked example
|       +-- README.md
+-- scripts/
    +-- init_project.sh                    # Copy templates to a new project
```

---

## Origin

These templates were extracted from the governance framework used in a graduate-level machine learning course project. The original project used 18 governance documents to manage a multi-part experiment comparing optimization algorithms, optimizer ablations, and regularization techniques across two datasets.

Project-specific content (datasets, algorithms, metrics, budgets) has been replaced with `{{PLACEHOLDER}}` syntax. The reusable patterns — phase gates, leakage prevention, budget matching, CONTRACT_CHANGE protocol, risk tracking, and decision records — are preserved verbatim.
