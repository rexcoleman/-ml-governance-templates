# CHANGELOG

<!-- version: 2.0 -->
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
- See [DECISION_LOG](DECISION_LOG.tmpl.md) for ADR entries that trigger CONTRACT_CHANGE commits
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for risk mitigation entries cross-referenced by changes

**Downstream (depends on this contract):**
- None — this is a chronological record.

## Purpose

This changelog tracks every material change to the **{{PROJECT_NAME}}** project's contracts, specifications, code, data, and environment. It is the single chronological record that makes `CONTRACT_CHANGE` commits traceable and auditable.

**Relationship to CONTRACT_CHANGE:** The ENVIRONMENT_CONTRACT requires that certain changes be made via a commit labeled `CONTRACT_CHANGE`. This log summarizes every such commit so reviewers can quickly identify what changed, why, and what must be regenerated.

**Relationship to DECISION_LOG:** Architectural decisions that trigger a `CONTRACT_CHANGE` should be recorded in DECISION_LOG first (as an ADR), then the resulting change logged here. Cross-reference the ADR ID in the Motivation field.

---

## Versioning Convention

- Entries use **YYYY-MM-DD** dates (not semantic versions)
- Each date entry may contain multiple Change Items
- Entries are listed in reverse chronological order (newest first)
- Every Change Item uses the template below

---

## Change Item Template

```markdown
### YYYY-MM-DD

#### [Short title of change]

- **Type:** CONTRACT_CHANGE | DOC_CHANGE | CODE_CHANGE | DATA_CHANGE
- **Scope:** environment | data | experiments | metrics | figures | scripts | report
- **ADR:** [ADR-XXXX if applicable, or "N/A"]
- **Files changed:**
  - `path/to/file1`
  - `path/to/file2`
- **Motivation:** [Cite the requirement, constraint, or risk that drove this change]
- **Backward compatibility:** compatible | breaking
  - If breaking: [What existing outputs are invalidated]
- **Artifacts impacted:**
  | Artifact | Status | Regeneration Command |
  |----------|--------|---------------------|
  | [artifact path or category] | needs-regen / not-affected | [command] |
- **Verification steps:** [Commands to verify correctness]
- **Commit SHA:** [Fill after commit]
- **Risk mitigation:** [RISK_REGISTER entry if applicable, e.g., "Mitigates R-A2"]
```

### Backward Compatibility Rules

- **compatible:** No existing outputs are invalidated. Additive changes (new files, new fields with defaults, documentation clarifications).
- **breaking:** Existing outputs may be incorrect or incomplete. ALL downstream artifacts listed in the "Artifacts impacted" table MUST be regenerated before the next phase gate.

**Rule:** After a breaking `CONTRACT_CHANGE`, no phase gate may pass until all `needs-regen` artifacts are regenerated and their manifests re-verified.

---

## Changelog Entries

*(Record entries below, newest first.)*

---

## Common CONTRACT_CHANGE Triggers

The following categories require a `CONTRACT_CHANGE` commit and MUST be logged here. Each trigger cites the governing contract section.

| Category | Trigger | Contract Reference |
|----------|---------|-------------------|
| **Environment** | Python version (including patch) | ENVIRONMENT_CONTRACT §{{ENV_CHANGE_SECTION}} |
| | Dependencies (add, remove, version change) | ENVIRONMENT_CONTRACT §{{ENV_CHANGE_SECTION}} |
| | Determinism or leakage guardrails | ENVIRONMENT_CONTRACT §{{ENV_CHANGE_SECTION}} |
| | Seed policy, `n_jobs` settings | ENVIRONMENT_CONTRACT §{{ENV_CHANGE_SECTION}} |
| **Data** | Dataset filenames or paths | DATA_CONTRACT §{{DATA_CHANGE_SECTION}} |
| | Split definitions (indices, ratios, seed) | DATA_CONTRACT §{{DATA_CHANGE_SECTION}} |
| | Preprocessing pipeline (scaling, encoding, step order) | DATA_CONTRACT §{{DATA_CHANGE_SECTION}} |
| | Target variable or label mapping | DATA_CONTRACT §{{DATA_CHANGE_SECTION}} |
| | Feature handling, missing-value strategy | DATA_CONTRACT §{{DATA_CHANGE_SECTION}} |
| | Test-access enforcement rules | DATA_CONTRACT §{{DATA_CHANGE_SECTION}} |
| **Experiments** | Compute budgets (any value in budget config) | EXPERIMENT_CONTRACT §{{EXPERIMENT_CHANGE_SECTION}} |
| | Method lists for any part | EXPERIMENT_CONTRACT §{{EXPERIMENT_CHANGE_SECTION}} |
| | Initialization protocol | EXPERIMENT_CONTRACT §{{EXPERIMENT_CHANGE_SECTION}} |
| | Output schemas | EXPERIMENT_CONTRACT §{{EXPERIMENT_CHANGE_SECTION}} |
| **Metrics** | Metric definitions or computation functions | METRICS_CONTRACT §{{METRICS_CHANGE_SECTION}} |
| | Classification threshold | METRICS_CONTRACT §{{METRICS_CHANGE_SECTION}} |
| | Convergence threshold (after lock) | METRICS_CONTRACT §{{METRICS_CHANGE_SECTION}} |
| | Sanity check definitions | METRICS_CONTRACT §{{METRICS_CHANGE_SECTION}} |
| **Scripts** | Script filenames or paths | SCRIPT_ENTRYPOINTS_SPEC §{{SCRIPT_CHANGE_SECTION}} |
| | CLI flag names, types, or defaults | SCRIPT_ENTRYPOINTS_SPEC §{{SCRIPT_CHANGE_SECTION}} |
| | Required outputs, exit code semantics | SCRIPT_ENTRYPOINTS_SPEC §{{SCRIPT_CHANGE_SECTION}} |
| | Reproduction sequence ordering | SCRIPT_ENTRYPOINTS_SPEC §{{SCRIPT_CHANGE_SECTION}} |
| **Figures/Tables** | Figure or table definitions | FIGURES_TABLES_CONTRACT §{{FIGURES_CHANGE_SECTION}} |
| | Summary table columns | FIGURES_TABLES_CONTRACT §{{FIGURES_CHANGE_SECTION}} |
| | Caption requirements, producer script identity | FIGURES_TABLES_CONTRACT §{{FIGURES_CHANGE_SECTION}} |
| **Artifacts** | Run ID naming scheme | ARTIFACT_MANIFEST_SPEC §{{ARTIFACT_CHANGE_SECTION}} |
| | Manifest schemas, hashing rules | ARTIFACT_MANIFEST_SPEC §{{ARTIFACT_CHANGE_SECTION}} |
