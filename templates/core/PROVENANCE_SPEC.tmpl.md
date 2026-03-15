# PROVENANCE SPEC

<!-- version: 1.0 -->
<!-- created: 2026-03-15 -->

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
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §8 for determinism and seeding requirements

**Downstream (depends on this contract):**
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §3 for per-run provenance file requirements

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{FLOAT_TOLERANCE}}` | Acceptable floating-point delta for reproducibility | `1e-6` |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Required Artifacts

Every experiment run MUST produce the following four provenance artifacts in the run's output directory:

### 1.1 config_resolved.yaml

All experiment parameters, fully resolved. No hidden defaults — every parameter that affects the run MUST appear explicitly.

```yaml
# Example
model:
  algorithm: random_forest
  n_estimators: 100
  max_depth: 10
  random_state: 42
data:
  dataset: adult
  split_seed: 42
  train_fraction: 1.0
  preprocessing: standard_scaler
budget:
  type: n/a
  allocated: n/a
  used: n/a
```

**Rules:**
- CLI overrides MUST be merged into the resolved config (not stored separately).
- Default values MUST be written explicitly (not omitted because "that's the default").
- The resolved config MUST be a single flat-or-nested YAML file, not a chain of includes.

### 1.2 versions.txt

Complete environment snapshot.

```
python: 3.11.5
numpy: 1.26.4
pandas: 2.1.5
scikit-learn: 1.4.0
torch: 2.2.1+cu121
xgboost: 2.0.3
...
```

**Generation:** `pip freeze > versions.txt` or `conda list --export > versions.txt`.

### 1.3 output_manifest.json

Every output file produced by the run, with integrity hashes.

```json
{
  "generated_at": "2026-03-15T10:30:00Z",
  "files": [
    {
      "path": "outputs/part1/adult/rf/seed_42/metrics.csv",
      "sha256": "a1b2c3d4...",
      "size_bytes": 12345,
      "timestamp": "2026-03-15T10:29:55Z"
    }
  ]
}
```

**Rules:**
- MUST include every file in the run output directory.
- SHA-256 hash MUST be computed on the raw file bytes.
- Timestamp is the file's last-modified time at generation.

### 1.4 git_info.txt

Repository state at experiment time.

```
commit: a1b2c3d4e5f6...
branch: main
dirty: false
remote: https://github.com/user/repo.git
```

**Rules:**
- `dirty: true` if there are uncommitted changes. Dirty runs are permitted but MUST be flagged.
- If not in a git repository, record `commit: n/a` and `dirty: n/a`.

---

## 2) Generation Protocol

Run `gen_provenance.py` at two points:

1. **Experiment start:** Generate `config_resolved.yaml`, `versions.txt`, and `git_info.txt` before any training begins. Save as `provenance_start/`.
2. **Experiment end:** Generate all four artifacts (including `output_manifest.json`) after all outputs are written. Save as `provenance_end/`.

**Drift detection:** After the run, compare `provenance_start/versions.txt` with `provenance_end/versions.txt`. Any difference indicates environment drift during the experiment and MUST be flagged in the run summary.

```
outputs/{part}/{dataset}/{method}/seed_{seed}/
├── provenance_start/
│   ├── config_resolved.yaml
│   ├── versions.txt
│   └── git_info.txt
├── provenance_end/
│   ├── config_resolved.yaml
│   ├── versions.txt
│   ├── git_info.txt
│   └── output_manifest.json
├── metrics.csv
├── summary.json
└── ...
```

---

## 3) reproduce.sh

A script that recreates the environment and reruns all experiments from scratch.

**Requirements:**
- MUST create a fresh virtual environment (not reuse an existing one).
- MUST install exact versions from `versions.txt`.
- MUST run all experiment scripts in the correct order.
- MUST compare output hashes against `output_manifest.json`.

**Template:**
```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Create fresh environment
python -m venv .reproduce_env
source .reproduce_env/bin/activate
pip install -r requirements.txt  # pinned versions

# 2. Run experiments
python scripts/run_all.py --config config_resolved.yaml

# 3. Verify outputs
python scripts/verify_provenance.py \
  --manifest provenance_end/output_manifest.json \
  --tolerance {{FLOAT_TOLERANCE}}
```

**Hash comparison rules:**
- Binary files (models, images): exact SHA-256 match required.
- Floating-point outputs (CSV, JSON with numeric values): allow delta of {{FLOAT_TOLERANCE}} (default: `1e-6`) per value. Hash comparison is on the rounded representation.
- Text files (logs): exact match not required (timestamps will differ). Exclude from hash verification.

---

## 4) Acceptance Criteria

- [ ] All 4 provenance artifacts exist for every run (`config_resolved.yaml`, `versions.txt`, `output_manifest.json`, `git_info.txt`)
- [ ] `provenance_start/` and `provenance_end/` both present
- [ ] No environment drift detected (start/end `versions.txt` match)
- [ ] `config_resolved.yaml` contains no hidden defaults (all parameters explicit)
- [ ] `output_manifest.json` covers every file in the run output directory
- [ ] `reproduce.sh` runs without error on a clean environment
- [ ] Output hashes match within tolerance ({{FLOAT_TOLERANCE}} for floating-point, exact for binary)
- [ ] Dirty git state flagged in `summary.json` if `git_info.txt` shows `dirty: true`
