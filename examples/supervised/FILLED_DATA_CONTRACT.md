# DATA CONTRACT

<!-- version: 2.0 -->
<!-- filled-from: supervised profile example (Heart Disease Classification) -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `CS7641_Assignment1_Spec.pdf` | Primary spec — highest authority |
> | Tier 2 | `Piazza_Clarifications.md` | Clarifications — cannot override Tier 1 |
> | Tier 3 | `TA_Office_Hours_Notes.md` | Advisory only — non-binding if inconsistent with Tier 1/2 |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.
> Update this contract via `CONTRACT_CHANGE` or align implementation to the higher tier.

### Companion Contracts

**Upstream (this contract depends on):**
- None — this is a foundational contract.

**Downstream (depends on this contract):**
- See [METRICS_CONTRACT](METRICS_CONTRACT.md) §2 for dataset/task metric mapping
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.md) §3 for split usage and leakage prevention in experiments

---

## 1) Purpose & Scope

This contract defines the data governance rules for the **Heart Disease Binary Classification** project. It covers:

- Canonical data paths and file formats
- Train/val/test split discipline and storage
- Leakage prevention rules and automated tripwires
- Per-dataset preprocessing protocols
- Data provenance and audit artifacts
- Change control triggers

---

## 2) Canonical Data Paths

| Dataset | Raw Path | Description |
|---------|----------|-------------|
| UCI Heart Disease | `data/raw/heart.csv` | Binary classification, 2 classes (presence/absence) |

Raw data files MUST NOT be committed to git. Add `data/raw/**` to `.gitignore`. Data placement instructions go in the REPRO document.

**Verification:** `git ls-files data/raw/` returns empty. `.gitignore` contains `data/raw/**`.

---

## 3) Split Discipline

| Property | Value |
|----------|-------|
| **Method** | StratifiedShuffleSplit (sklearn) |
| **Ratios** | 70 / 15 / 15 (train / val / test) |
| **Seed** | 42 |
| **Stratify** | target column |
| **Storage** | `data/splits/{train,val,test}.csv` |

**SHA-256 hashes** (computed after first split, locked thereafter):
- `data/splits/train.csv` → `sha256:a1b2c3...`
- `data/splits/val.csv` → `sha256:d4e5f6...`
- `data/splits/test.csv` → `sha256:g7h8i9...`

**Verification:** `sha256sum data/splits/*.csv` matches hashes above. Any mismatch halts the pipeline.

---

## 4) Leakage Prevention

### Hard Rules

1. **Fit on train only.** All preprocessing (StandardScaler, SimpleImputer) MUST be fit on the training split and applied (transform only) to val/test.
2. **Test isolation.** The test split is accessed ONLY by `scripts/final_eval.py`. No intermediate analysis may touch test data.
3. **No target encoding with val/test rows.** Any feature engineering that uses label information must exclude val/test rows.

### Automated Tripwires

| Check | Script | When |
|-------|--------|------|
| Split hash verification | `scripts/check_data_ready.py` | Before every experiment run |
| Fit-on-train audit | `scripts/check_leakage.py` | Before every experiment run |
| Test access log | `scripts/final_eval.py --audit` | After final evaluation only |

**Verification:** `python scripts/check_leakage.py` exits 0 before any model training begins.

---

## 5) Per-Dataset Preprocessing

### UCI Heart Disease

| Step | Method | Fit On | Apply To |
|------|--------|--------|----------|
| Missing values | SimpleImputer(strategy='median') | Train | Train, Val, Test |
| Numeric scaling | StandardScaler() | Train | Train, Val, Test |
| Categorical encoding | OneHotEncoder(drop='first') | Train | Train, Val, Test |

**Feature count after preprocessing:** 18 (from 13 raw features after one-hot encoding)

---

## 6) Data Provenance

| Property | Value |
|----------|-------|
| **Source** | UCI ML Repository |
| **URL** | https://archive.ics.uci.edu/dataset/45/heart+disease |
| **Download date** | 2026-01-15 |
| **Raw file hash** | `sha256:j0k1l2...` |
| **License** | CC BY 4.0 |
| **Citation** | Janosi, A., et al. (1988). Heart Disease. UCI Machine Learning Repository. |

---

## 7) Change Control

Any change to this contract requires:
1. Record decision in `DECISION_LOG.md` (ADR format)
2. Make the change
3. Log it in `CHANGELOG.md`
4. Commit with `CONTRACT_CHANGE: DATA_CONTRACT — <description>`
5. Regenerate impacted downstream artifacts (splits, preprocessed files)

**Trigger conditions for contract change:**
- New dataset added
- Split ratios or seed modified
- Preprocessing pipeline changed (new step, parameter change, step removal)
- Leakage rule exception granted (must cite Tier 1/2 authority)
