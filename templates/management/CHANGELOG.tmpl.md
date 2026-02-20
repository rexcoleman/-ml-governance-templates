# CHANGELOG

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
- **Files changed:**
  - `path/to/file1`
  - `path/to/file2`
- **Motivation:** [Cite the requirement, constraint, or risk that drove this change]
- **Backward compatibility:** compatible | breaking
- **Artifacts impacted:** [What must be regenerated]
- **Verification steps:** [Commands to verify correctness]
- **Commit SHA:** [Fill after commit]
- **Risk mitigation:** [RISK_REGISTER entry if applicable]
```

---

## Changelog Entries

*(Record entries below, newest first.)*

---

## Common CONTRACT_CHANGE Triggers

The following categories require a `CONTRACT_CHANGE` commit and MUST be logged here.

### Environment changes
- Python version (including patch)
- Dependencies (add, remove, version change)
- Determinism or leakage guardrails
- Seed policy, `n_jobs` settings

### Data changes
- Dataset filenames or paths
- Split definitions (indices, ratios, seed)
- Preprocessing pipeline (scaling, encoding, imputation, step order)
- Target variable or label mapping
- Feature handling, missing-value strategy
- Test-access enforcement rules

### Experiment changes
- Compute budgets (any value in budget config)
- Method lists for any part
- Initialization protocol
- Output schemas

### Metric changes
- Metric definitions or computation functions
- Classification threshold
- Convergence threshold (after lock)
- Sanity check definitions

### Script changes
- Script filenames or paths
- CLI flag names, types, or defaults
- Required outputs
- Exit code semantics
- Reproduction sequence ordering

### Figure/table changes
- Figure or table definitions
- Summary table columns
- Caption requirements
- Producer script identity

### Artifact changes
- Run ID naming scheme
- Manifest schemas
- Hashing rules
