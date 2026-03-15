# CLAIM STRENGTH SPEC

<!-- version: 1.0 -->
<!-- created: 2026-03-15 -->
<!-- last_validated_against: frontier_project_pipeline FINDINGS.md files -->

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
- See [STATISTICAL_ANALYSIS_SPEC](STATISTICAL_ANALYSIS_SPEC.tmpl.md) for CI computation methods and multi-seed requirements
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §4.3 for multi-seed stability and §5 for metrics definitions

**Downstream (depends on this contract):**
- See [PUBLICATION_PIPELINE](../publishing/PUBLICATION_PIPELINE.tmpl.md) for claim tags required before publication approval
- FINDINGS.md files in all projects — must conform to §5 structure and §6 acceptance criteria

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Adversarial IDS |
| `{{DATA_TYPE}}` | Primary data type (real, synthetic, mixed) | synthetic |
| `{{MIN_SEEDS}}` | Minimum seeds for DEMONSTRATED | 3 |
| `{{FINDINGS_PATH}}` | Path to FINDINGS.md | FINDINGS.md |
| `{{OUTPUTS_DIR}}` | Path to raw outputs | outputs/ |
| `{{AUDIT_SCRIPT}}` | Findings audit script | gen_findings_audit.py |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory references |

---

## 1) Claim Strength Taxonomy

Every quantitative or qualitative claim in `{{FINDINGS_PATH}}` MUST carry exactly one strength tag from this table.

| Tag | Meaning | Required Evidence | Example |
|-----|---------|-------------------|---------|
| [DEMONSTRATED] | Directly measured, reproducible | ≥{{MIN_SEEDS}} seeds, CI reported, raw data matches claim | "XGBoost AUC = 0.739 ± 0.012 (95% CI: [0.721, 0.757]) [DEMONSTRATED]" |
| [SUGGESTED] | Consistent pattern, limited evidence | 1-2 seeds, or qualitative pattern across domains | "Vendor history appears important (SHAP rank #4) [SUGGESTED]" |
| [PROJECTED] | Extrapolated from partial evidence | Trend line, analogical reasoning, or partial measurement | "MCP setup projected to reach <5 min [PROJECTED]" |
| [HYPOTHESIZED] | Untested prediction | Stated as future work, logical but unmeasured | "Gradient-based attacks would likely show different results [HYPOTHESIZED]" |

### Tag Decision Flowchart

```
Is there raw data in {{OUTPUTS_DIR}} matching this claim?
├── NO  → [HYPOTHESIZED]
└── YES
    ├── Is the measurement complete (not extrapolated)?
    │   ├── NO  → [PROJECTED]
    │   └── YES
    │       ├── ≥{{MIN_SEEDS}} seeds with CI?
    │       │   ├── YES → [DEMONSTRATED]
    │       │   └── NO  → [SUGGESTED]
    │       └── Qualitative pattern only?
    │           └── [SUGGESTED]
```

---

## 2) Qualifiers

Qualifiers are appended to the base tag inside the brackets, separated by commas. A claim may carry multiple qualifiers.

| Qualifier | When to Apply | Append to Tag |
|-----------|--------------|---------------|
| SYNTHETIC | Any finding on synthetic or simulated data | [SUGGESTED, SYNTHETIC] |
| SINGLE-SEED | Finding from one random seed only | [SUGGESTED, SINGLE-SEED] |
| NOISE-ONLY | Adversarial finding using only noise perturbation | [DEMONSTRATED, NOISE-ONLY] |
| SCOPED | Finding specific to one configuration, backend, or dataset | [DEMONSTRATED, SCOPED] |

### Qualifier Rules

1. **Stacking:** Qualifiers stack. A single-seed finding on synthetic data is tagged `[SUGGESTED, SINGLE-SEED, SYNTHETIC]`.
2. **Qualifier ceiling:** `SINGLE-SEED` caps the base tag at `[SUGGESTED]` — a single-seed result cannot be `[DEMONSTRATED]` regardless of other evidence.
3. **SYNTHETIC disclosure:** If `{{DATA_TYPE}}` = synthetic, the FINDINGS.md header MUST state: "All findings in this document are based on synthetic data unless otherwise noted."

---

## 3) Prohibited Language Without Evidence

The following words and phrases MUST NOT appear in `{{FINDINGS_PATH}}` without meeting the minimum evidence threshold.

| Word/Phrase | Minimum Required Tag | Rationale |
|-------------|---------------------|-----------|
| "novel" | [DEMONSTRATED] + competitive landscape showing no prior art | Overclaiming novelty is the #1 credibility risk |
| "first" | [DEMONSTRATED] + systematic search showing no prior | Same — must verify nobody did it before |
| "validated" | [DEMONSTRATED] with multi-seed + CI | "Validated" implies statistical confirmation |
| "proved" / "proven" | NEVER for ML findings | ML findings are demonstrated or suggested, never proved |
| "breakthrough" | NEVER in FINDINGS.md | Reserve for external peer validation |
| "significant" (without qualifier) | [DEMONSTRATED] + statistical test with p-value or CI | Readers assume "statistically significant" — must back it up |
| "outperforms" | [DEMONSTRATED] + same-budget comparison | Comparative claims require controlled experiments |

### Enforcement

- `{{AUDIT_SCRIPT}}` scans for prohibited language and flags violations
- Each flag MUST be resolved before FINDINGS.md is marked complete
- Permitted workarounds: quote the word in a literature reference, or downgrade the claim

---

## 4) Application Protocol

### Step 1: Draft Without Tags

Write the full FINDINGS.md content without any claim tags. Focus on clarity and completeness.

### Step 2: Tag Each Claim

For each quantitative or qualitative claim:

1. **Data reconciliation:** Does raw data in `{{OUTPUTS_DIR}}` match the stated number?
   - If NO → fix the number to match the data, not the other way around
2. **Seed count:** How many seeds produced this result?
   - ≥{{MIN_SEEDS}} → eligible for [DEMONSTRATED]
   - <{{MIN_SEEDS}} → [SUGGESTED] maximum
3. **Data source:** Is the underlying data real or synthetic?
   - Synthetic → add SYNTHETIC qualifier
4. **Scope:** Does the finding generalize or is it specific to one configuration?
   - Narrow scope → add SCOPED qualifier
5. **Extrapolation:** Is any part of the claim extrapolated beyond measured data?
   - Yes → [PROJECTED] maximum
6. **Assign tag:** Apply the strongest tag the evidence supports (not stronger)

### Step 3: Review Placement

- **Executive Summary:** [DEMONSTRATED] and [SUGGESTED] claims only
- **Limitations section:** All [HYPOTHESIZED] claims must appear here
- **Future Work:** [PROJECTED] and [HYPOTHESIZED] claims belong here

### Step 4: Audit

Run `{{AUDIT_SCRIPT}}` to verify:
- 100% tag coverage
- No prohibited language violations
- Raw data reconciliation

---

## 5) FINDINGS.md Required Structure

Every FINDINGS.md governed by this spec MUST include the following sections in order.

### 5.1 Required Header

```markdown
# Findings: {{PROJECT_NAME}}

**Data type:** {{DATA_TYPE}}
**Seeds:** {{MIN_SEEDS}}+
**Claim tagging:** Per CLAIM_STRENGTH_SPEC v1.0
```

### 5.2 Claim Strength Legend

Copy the §1 taxonomy table into every FINDINGS.md as a legend, placed immediately after the header.

### 5.3 Executive Summary

- Contains only [DEMONSTRATED] and [SUGGESTED] claims
- Each claim is inline-tagged
- No [PROJECTED] or [HYPOTHESIZED] claims permitted in this section

### 5.4 Detailed Findings

- Every quantitative claim is inline-tagged
- Raw numbers match `{{OUTPUTS_DIR}}` data exactly
- Confidence intervals reported for all [DEMONSTRATED] claims

### 5.5 Limitations

- All [HYPOTHESIZED] items listed here
- All qualifiers (SYNTHETIC, SCOPED, etc.) summarized
- Threats to validity enumerated

### 5.6 Claims on Synthetic Data (conditional)

Required if `{{DATA_TYPE}}` = synthetic or mixed:
- Separate subsection listing all claims derived from synthetic data
- Each claim tagged with SYNTHETIC qualifier
- Explicit statement of how synthetic data may differ from production data

---

## 6) Acceptance Criteria

A FINDINGS.md passes this spec when ALL of the following hold:

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | 100% of quantitative claims tagged | `{{AUDIT_SCRIPT}}` tag coverage check |
| 2 | No prohibited language without required evidence | `{{AUDIT_SCRIPT}}` language scan |
| 3 | Raw data reconciliation passed | `{{AUDIT_SCRIPT}}` data-vs-claim check against `{{OUTPUTS_DIR}}` |
| 4 | Executive Summary contains only [DEMONSTRATED] or [SUGGESTED] | Manual review |
| 5 | All [HYPOTHESIZED] claims appear in Limitations | Manual review |
| 6 | Claim Strength Legend present | `{{AUDIT_SCRIPT}}` structure check |
| 7 | SYNTHETIC subsection present if `{{DATA_TYPE}}` != real | `{{AUDIT_SCRIPT}}` structure check |
| 8 | No [DEMONSTRATED] claims with fewer than {{MIN_SEEDS}} seeds | `{{AUDIT_SCRIPT}}` seed count cross-check |

---

## 7) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Taxonomy tags (adding, removing, or redefining a tag)
- Qualifier definitions or stacking rules
- Prohibited language list
- Minimum seed threshold for [DEMONSTRATED]
- FINDINGS.md required structure
- Acceptance criteria
- Audit script interface
