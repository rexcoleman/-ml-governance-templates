# ARTIFACT MANIFEST SPECIFICATION

<!-- version: 1.0 -->
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

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{RUN_ID_FORMAT}}` | Run ID naming scheme | `{part}_{dataset}_{method}_seed{seed}` |
| `{{HASH_ALGORITHM}}` | Hashing algorithm | SHA-256 |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This specification defines how experiment outputs are identified, hashed, and recorded for the **{{PROJECT_NAME}}** project. It ensures that every artifact can be verified for integrity and traced to its producing run.

---

## 2) Run Identity & Naming

### 2.1 Run ID Format

Every experiment run has a unique ID following this scheme:

```
{{RUN_ID_FORMAT}}
```

**Examples:**
- *(e.g.)* `part1_adult_rhc_seed42`
- *(e.g.)* `part2_adult_adam_seed123`

### 2.2 Output Directory

Each run's outputs go to:

```
outputs/{{PART}}/{{DATASET}}/{{METHOD}}/seed_{{SEED}}/
```

---

## 3) Required Provenance Files Per Run

Every run directory MUST contain:

| File | Format | Contents |
|------|--------|----------|
| `metrics.csv` | CSV | Per-step metrics |
| `summary.json` | JSON | Run summary |
| `config_resolved.yaml` | YAML | Full resolved configuration |
| `run_manifest.json` | JSON | {{HASH_ALGORITHM}} hashes of all files in this run |

### 3.1 Run Manifest Schema (`run_manifest.json`)

```json
{
  "run_id": "{{RUN_ID}}",
  "timestamp_utc": "2026-01-01T00:00:00Z",
  "files": {
    "metrics.csv": {
      "sha256": "abc123...",
      "size_bytes": 12345
    },
    "summary.json": {
      "sha256": "def456...",
      "size_bytes": 678
    },
    "config_resolved.yaml": {
      "sha256": "ghi789...",
      "size_bytes": 432
    }
  }
}
```

---

## 4) Global Artifact Manifest

A single global manifest records all runs and report-ready artifacts.

**Path:** `outputs/artifact_manifest.json`

**Producer:** `{{PRODUCER_SCRIPT}}` (generated as the final step of artifact assembly)

### 4.1 Schema

```json
{
  "project": "{{PROJECT_NAME}}",
  "generated_utc": "2026-01-01T00:00:00Z",
  "git_sha": "abc123...",
  "runs": {
    "{{RUN_ID_1}}": {
      "manifest_path": "outputs/part1/.../run_manifest.json",
      "manifest_sha256": "..."
    }
  },
  "figures": {
    "f1_loss_vs_wallclock.pdf": {
      "sha256": "...",
      "size_bytes": 12345
    }
  },
  "tables": {
    "t1_summary_table.csv": {
      "sha256": "...",
      "size_bytes": 678
    }
  }
}
```

---

## 5) Hashing & Integrity Rules

### 5.1 Algorithm

All hashes use **{{HASH_ALGORITHM}}** (e.g., SHA-256).

### 5.2 What Gets Hashed

- Every file in every run directory
- Every generated figure and table
- The global manifest itself (recorded in verification output)

### 5.3 Determinism Requirement

Running the same experiment with the same seed, data, and environment MUST produce byte-identical outputs. If outputs differ, the determinism contract (ENVIRONMENT_CONTRACT §8) has been violated.

### 5.4 Verification

```bash
python scripts/verify_manifests.py
```

This script MUST:
1. Load `artifact_manifest.json`
2. Recompute {{HASH_ALGORITHM}} for every listed file
3. Compare against recorded hashes
4. Exit 0 if all match, exit 1 on any mismatch or missing file
5. Print a summary: `N files verified, 0 mismatches, 0 missing`

---

## 6) Results Artifact Schemas

*(Define schemas for any aggregated result files beyond per-run outputs.)*

### Heatmap CSVs (if applicable)

```csv
alpha,beta1,val_loss,reached_l,steps_to_l
0.001,0.9,0.342,true,5000
...
```

### Stability Summary (if applicable)

```json
{
  "method": "adam",
  "seeds": [42, 123, 456, 789, 1024],
  "best_val_loss": {"median": 0.33, "iqr": [0.32, 0.34]},
  "test_f1": {"median": 0.75, "iqr": [0.73, 0.77]}
}
```

*(Add schemas for your project-specific aggregated results.)*

---

## 7) Interaction with Figures & Tables

The artifact generation script (`{{PRODUCER_SCRIPT}}`) MUST:

1. Discover all run manifests under `outputs/`
2. Load `final_eval_results.json` for test metrics
3. Generate all figures and tables
4. Record everything in the global manifest
5. NOT re-run any training or evaluation

---

## 8) Phase Gates / Acceptance Checklist

- [ ] Every run directory has a `run_manifest.json`
- [ ] Global `artifact_manifest.json` exists and is complete
- [ ] `verify_manifests.py` exits 0 (all hashes match)
- [ ] No orphan files (files in output dirs not recorded in manifests)
- [ ] Determinism check: re-running producer script produces identical hashes

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Run ID naming scheme
- Provenance file requirements or formats
- Manifest schemas (run or global)
- Results artifact schemas
- Hashing algorithm or rules
- Discovery or data-flow rules in the producer script
