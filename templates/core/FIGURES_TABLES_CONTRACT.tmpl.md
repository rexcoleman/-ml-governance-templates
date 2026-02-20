# FIGURES & TABLES CONTRACT

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{FIGURE_COUNT}}` | Number of required figures | 8-10 |
| `{{TABLE_COUNT}}` | Number of required tables | 2 |
| `{{PRODUCER_SCRIPT}}` | Script that generates artifacts | scripts/make_report_artifacts.py |
| `{{FIGURE_FORMAT}}` | Output format | PDF |

---

## 1) Purpose & Scope

This contract defines every figure and table required for the **{{PROJECT_NAME}}** report. Each artifact has a unique ID, a data source, a producer script, and caption requirements.

---

## 2) Artifact Directories & Naming

| Type | Directory | Naming Convention |
|------|-----------|-------------------|
| Figures | `outputs/figures/` | `f{{N}}_{{short_name}}.{{FORMAT}}` |
| Tables | `outputs/tables/` | `t{{N}}_{{short_name}}.csv` |

**Producer script:** `{{PRODUCER_SCRIPT}}`

The producer script MUST:
- Be deterministic (same inputs → same outputs, byte-for-byte)
- Read from experiment outputs and `final_eval_results.json` only
- NOT re-run any training
- Generate all figures and tables in a single invocation
- Write the artifact manifest as its final step

---

## 3) Required Figures

| ID | Title | Report Section | Data Source | Key Interpretation |
|----|-------|---------------|-------------|-------------------|
| F1 | *(e.g.)* Loss vs Wall-Clock | *(e.g.)* Sec 5-7 | `metrics.csv` | *(e.g.)* Which methods converge fastest |
| F2 | *(title)* | *(section)* | *(source)* | *(what to interpret)* |
| *(add rows)* | | | | |

*(Fill in one row per required figure. Include optional figures with a note.)*

---

## 4) Required Tables

| ID | Title | Report Section | Columns | Data Source |
|----|-------|---------------|---------|-------------|
| T1 | Summary Table | *(e.g.)* Before Conclusion | Method, Best Val Loss, Test Metric, Time to ℓ, Budget, Notes | `summary.json` + `final_eval_results.json` |
| T2 | Sanity Checks | *(e.g.)* Part 2 | Check, Accuracy, F1, Expected | `sanity_checks/*.json` |
| *(add rows)* | | | | |

### Summary Table Requirements

- [ ] Includes all methods from all experimental parts
- [ ] Includes baseline/prior-work row(s) for comparison
- [ ] Over-budget runs marked and excluded from head-to-head claims
- [ ] Dispersion shown (median + IQR) for seed-aggregated results
- [ ] Test metrics sourced exclusively from `final_eval_results.json`

---

## 5) Caption Requirements

Every figure and table caption MUST include:

1. **Descriptive title** — What is being shown
2. **Key parameters** — Budget, seed count, aggregation method, threshold (where applicable)
3. **Takeaway** — One interpretive sentence explaining what the result means, tied to the experiment's mechanism (not just describing the visual)

**Bad caption:** "Validation loss curves for 7 optimizers."
**Good caption:** "Validation loss vs gradient evaluations for 7 optimizers on Adult (10k grad evals, 5 seeds, median shown). Adam converges 3x faster than SGD, consistent with adaptive scaling compensating for gradient magnitude variation."

### Per-Figure Caption Checklist

*(Customize per figure. Example:)*

- **F1 (Loss vs Wall-Clock):** Budget, seed count, methods shown, which is fastest
- **F2 (RO Progress):** Algorithm settings (operator disclosures), func_eval budget, trainable param count
- **Summary Table (T1):** Column definitions, what "Test Metric" means per dataset, SL baseline source

---

## 6) Integration Constraints

- Figures MUST be referenced in the report text with an interpretation (not just "see Figure X")
- Each figure/table reference MUST include a takeaway sentence
- Figures MUST be placed near their first reference in the text
- Figure PDFs MUST be vector format for print quality

---

## 7) Acceptance Criteria / Exit Gate

- [ ] All required figures present in `outputs/figures/`
- [ ] All required tables present in `outputs/tables/`
- [ ] Producer script runs without errors
- [ ] Artifact manifest records SHA-256 for every figure/table
- [ ] Captions drafted with takeaways (review before delivery)
- [ ] Summary table has all required columns and rows
- [ ] Test metrics in tables match `final_eval_results.json` exactly

---

## 8) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Figure or table definitions (axes, series, required content, data sources)
- Summary table column list
- Filename conventions or directory layout
- Caption requirements
- Acceptance criteria
- Producer script identity
