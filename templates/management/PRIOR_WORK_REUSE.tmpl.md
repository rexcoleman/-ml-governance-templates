# PRIOR WORK REUSE STRATEGY

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

| # | Source Path | What to Extract | Destination | Notes |
|---|-----------|-----------------|-------------|-------|
| 1 | *(path)* | *(what)* | *(dest)* | *(notes)* |
| *(add rows)* | | | | |

### Files NOT Copied (and Why)

| Source File | Why Excluded |
|-------------|-------------|
| *(file)* | *(reason)* |

### Data File Verification

| File | SHA-256 | Match Prior? |
|------|---------|-------------|
| *(file)* | *(hash)* | *(yes/no)* |

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

## 9) Required Contract Updates

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
