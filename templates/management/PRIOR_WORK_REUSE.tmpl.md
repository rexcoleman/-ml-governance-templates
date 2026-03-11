# PRIOR WORK REUSE STRATEGY

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
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §3 for split inheritance and §6 for EDA compatibility
- See [ENVIRONMENT_CONTRACT](../core/ENVIRONMENT_CONTRACT.tmpl.md) §4 for dependency compatibility

**Downstream (depends on this contract):**
- See [DECISION_LOG](DECISION_LOG.tmpl.md) for reuse-related ADR entries
- See [CHANGELOG](CHANGELOG.tmpl.md) for CONTRACT_CHANGE entries from reuse decisions

{{PROJECT_NAME}} — Reuse Analysis & Implementation Plan

---

## 1) Executive Summary

The **{{PROJECT_NAME}}** project requires reusing components from a prior project (**{{PRIOR_PROJECT_NAME}}**). This document evaluates repo-management patterns, selects the best option, and provides a concrete implementation plan.

*(Fill in your recommendation and key decisions.)*

---

## 2) What Needs to Be Reused

| Component | Prior Project Source | OL Destination | Why Needed |
|-----------|-------------------|----------------|------------|
| *(e.g.)* Model architecture | `src/model.py` | `src/backbone.py` | Required by project specification |
| *(e.g.)* Data splits | `splits/*.npz` | `data/splits/*.json` | Same splits required |
| *(e.g.)* Preprocessing | `src/preprocessing.py` | `src/preprocessing.py` | Consistency with prior work |
| *(add rows)* | | | |

**Prior project commit SHA:** `{{PRIOR_COMMIT_SHA}}`
**Prior project status:** *(e.g., Frozen/submitted, Active)*

---

## 3) Options Comparison

### Option A: Vendor Snapshot

Copy a minimal, auditable subset of files into the new repo with a machine-verifiable provenance record.

| Dimension | Assessment |
|-----------|-----------|
| **Self-containment** | Excellent — repo is fully self-contained |
| **Operational complexity** | Low — one-time copy + hash |
| **Audit trail** | `provenance.json` with commit SHA + per-file hashes |
| **Ongoing maintenance** | None (prior project is frozen) |

### Option B: Shared Package

Factor common code into an installable Python package.

| Dimension | Assessment |
|-----------|-----------|
| **Self-containment** | Poor — requires separate package install |
| **Operational complexity** | High — package structure, versioning, install path |
| **Audit trail** | Package version pin |
| **Ongoing maintenance** | Version management |

### Option C: Git Subtree / Submodule

Pull prior repo into current repo via git mechanism.

| Dimension | Assessment |
|-----------|-----------|
| **Self-containment** | Good (subtree) / Poor (submodule) |
| **Operational complexity** | Medium — git subtree/submodule commands |
| **Audit trail** | Git history |
| **Ongoing maintenance** | Subtree/submodule bookkeeping |

### Comparison Matrix

| Criterion | A: Vendor | B: Package | C: Subtree |
|-----------|:---------:|:----------:|:----------:|
| Self-contained repo | Yes | No | Partial |
| Reviewer portability | Pass | Risk | Pass |
| Operational complexity | Low | High | Medium |
| Ongoing maintenance | None | Versioning | Bookkeeping |
| Appropriate for | Frozen upstream, few files | Active upstream, many files | Active upstream, moderate files |

### Decision Guide

```
Is the prior project frozen (submitted/released)?
├── YES → Is the file count small (< 10 files)?
│         ├── YES → Option A: Vendor Snapshot ✓
│         └── NO  → Option A (selective) or Option C: Git Subtree
└── NO  → Will you need ongoing upstream updates?
          ├── YES → Option C: Git Subtree (or Option B if many shared modules)
          └── NO  → Option A: Vendor Snapshot ✓
```

---

## 4) Chosen Approach

*(Document your choice and rationale.)*

**Recommendation:** *(e.g., Option A — Vendor Snapshot)*

**Rationale:**
1. *(Reason 1)*
2. *(Reason 2)*
3. *(Reason 3)*

---

## 5) File Inventory

### Files to Extract

Every extracted file MUST have a SHA-256 hash recorded for verification.

| # | Source Path | What to Extract | Destination | SHA-256 | Approx Size |
|---|-----------|-----------------|-------------|---------|-------------|
| 1 | *(path)* | *(what — class names, function names, or "full file")* | *(dest)* | *(hash)* | *(lines or KB)* |
| *(add rows)* | | | | | |

### Files NOT Copied (and Why)

| Source File | Why Excluded | Risk if Accidentally Included |
|-------------|-------------|-------------------------------|
| *(file)* | *(reason)* | *(e.g., "Contains SGD-only enforcement; breaks optimizer ablations")* |

### Data File Verification

| File | SHA-256 | Prior Match? | Notes |
|------|---------|:------------|-------|
| *(file)* | *(hash)* | *(yes/no)* | *(e.g., "Identical in both projects")* |

**Verification command:**
```bash
python -c "import hashlib; print(hashlib.sha256(open('{{FILE}}','rb').read()).hexdigest())"
```

---

## 6) Critical Issues & Resolutions

*(Document any ambiguities, inconsistencies, or decisions needed when reusing prior work.)*

### Issue {{N}}: {{TITLE}}

**Problem:** *(What's wrong or ambiguous)*
**Source:** *(Which requirement or file)*
**Resolution:** *(How you resolved it)*
**ADR:** *(Reference to DECISION_LOG entry if applicable)*

---

## 7) Ambiguity Register

| # | Item | Authority Says | Prior Project Shows | Resolution |
|---|------|----------------|-------------------|-----------|
| *(num)* | *(item)* | *(quote)* | *(evidence)* | *(resolution + ADR reference)* |

---

## 8) Implementation Sequence

```
1. Record provenance              → config/provenance.json
2. Extract source files           → src/
3. Archive prior artifacts        → vendor/
4. Write conversion scripts       → scripts/
5. Run conversion                 → data/
6. Write verification script      → scripts/
7. Run verification               → exits 0
8. Record decisions               → DECISION_LOG (ADR entries)
9. Record changelog               → CHANGELOG
10. Update contracts              → docs/*.md
11. Commit as CONTRACT_CHANGE     → single atomic commit
```

---

## 9) Verification Script Pattern

A verification script (`scripts/verify_{{PRIOR_PROJECT}}_snapshot.py`) MUST be implemented to validate the integrity of the vendor snapshot.

### Required Checks

```python
# scripts/verify_{{PRIOR_PROJECT}}_snapshot.py
#
# 1. Load provenance record (config/{{PRIOR_PROJECT}}_provenance.json)
# 2. Verify SHA-256 of each archived file against recorded hashes
# 3. Verify SHA-256 of raw data files (if shared between projects)
# 4. Verify split JSON structural integrity:
#    - No overlap between train/val/test indices
#    - len(train) + len(val) + len(test) == n_total
#    - All indices in range(0, n_total)
#    - split_hash matches recomputed value
# 5. Smoke-test extracted code:
#    - Import key classes/functions → confirms no missing dependencies
#    - Run a minimal forward pass with dummy data → confirms architecture works
# 6. Print pass/fail summary; exit 0 on all pass, exit 1 on any failure
```

**Exit code contract:** The script MUST exit non-zero if ANY check fails. It is a Phase 0 gate requirement.

---

## 10) Frozen Upstream Documentation

When the prior project is frozen (submitted/released), document this explicitly:

| Field | Value |
|-------|-------|
| **Prior project status** | *(e.g., "Frozen — submitted 2026-02-15")* |
| **Will upstream change?** | *(e.g., "No — submitted and graded")* |
| **Sync strategy** | *(e.g., "None — one-time vendor snapshot")* |
| **Bug fix policy** | *(e.g., "If a bug is found in extracted code, fix in current project only; do not modify prior repo")* |

This section prevents unnecessary sync machinery for frozen upstreams.

---

## 11) Format Conversion Guidance

When prior project artifacts use a different format than the current project requires, document the conversion:

| Prior Format | Current Format | Conversion Script | Notes |
|-------------|---------------|-------------------|-------|
| *(e.g.)* NPZ (train/test only) | JSON (train/val/test) | `scripts/convert_{{PRIOR_PROJECT}}_splits.py` | Val derived via StratifiedShuffleSplit |
| *(e.g.)* YAML config | Python dataclass | `scripts/convert_config.py` | One-time conversion |
| *(add rows)* | | | |

**Conversion script requirements:**
- MUST verify input file hashes before conversion
- MUST verify output integrity (no overlap, full coverage, etc.)
- MUST exit non-zero on any failure
- MUST be idempotent (running twice produces identical output)

---

## 12) Required Contract Updates

| Document | Section | Update Description |
|----------|---------|-------------------|
| *(contract)* | *(section)* | *(what to update)* |
| *(add rows)* | | |

---

## 10) Provenance Record Schema

```json
{
  "prior_project": "{{PRIOR_PROJECT_NAME}}",
  "prior_commit_sha": "{{PRIOR_COMMIT_SHA}}",
  "snapshot_date": "YYYY-MM-DD",
  "source_files": {
    "path/to/source": {
      "sha256": "<hash>",
      "extracted": ["ClassA", "function_b"],
      "lines": "N-M",
      "note": "What was NOT copied and why"
    }
  },
  "archived_files": {
    "path/to/archive": {
      "sha256": "<hash>"
    }
  },
  "data_verified": {
    "data_file.csv": {
      "sha256": "<hash>",
      "match": true,
      "note": "Identical in both projects"
    }
  }
}
```
