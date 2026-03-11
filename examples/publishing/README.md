# Worked Example: Publishing — Multi-Phase ML Portfolio Project

This example shows representative placeholder fills for the **publishing** templates (Publication Brief, Academic Integrity Firewall, Lean Hypothesis). These are typically added on top of another profile when the project has formal delivery, portfolio, or compliance requirements.

---

## Project Overview

| Property | Value |
|----------|-------|
| **Project name** | Neural Architecture Search Benchmark |
| **Context** | Third project in a graduate ML course sequence |
| **Prior project** | Supervised Learning Report (SL Report) |
| **Deliverable** | IEEE-format technical report + reproducibility package |
| **Audience** | Course grader + portfolio for job applications |

---

## Key Placeholder Fills

### PUBLICATION_BRIEF

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | Neural Architecture Search Benchmark |
| `{{TARGET_READER}}` | Course grader (primary), ML hiring manager (secondary) |
| `{{PRIMARY_DEMONSTRATION}}` | Rigorous experimental design with controlled NAS comparisons |
| `{{PORTFOLIO_CONTEXT}}` | Third of three ML course projects; demonstrates progression from supervised learning to architecture optimization |
| `{{ONE_SENTENCE_TAKEAWAY}}` | "This person can design and execute controlled architecture search experiments with statistical rigor." |

**Anti-Claims (§4.2):**

| Anti-Claim | Why Prohibited | Acceptable Alternative |
|-----------|---------------|----------------------|
| "Our NAS method is state-of-the-art" | Limited search space, single dataset | "Our NAS configuration achieves competitive accuracy on CIFAR-10 within the evaluated search space" |
| "We prove random search is sufficient" | Only tested on one benchmark | "Random search performs comparably to more sophisticated methods on this benchmark" |
| "Novel architecture discovered" | Search space is well-studied | "The top architecture found by our search exhibits an interesting skip-connection pattern" |

**Key Messages (§6.1):**

| # | Message | Supporting Evidence |
|---|---------|-------------------|
| 1 | Budget-matched NAS comparisons reveal similar final accuracy across methods | T1: Summary table, F1: Accuracy vs compute curves |
| 2 | Search method choice matters more for efficiency than final quality | F2: Time-to-threshold box plots |
| 3 | Multi-seed evaluation is essential — single-seed rankings are unreliable | F3: Ranking stability across seeds |

### ACADEMIC_INTEGRITY_FIREWALL

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | Neural Architecture Search Benchmark |
| `{{INSTITUTION}}` | Example University |
| `{{HONOR_CODE_REF}}` | University Academic Integrity Policy §3.2 |
| `{{PRIOR_PROJECT}}` | sl_report |

**Data Wall (§2, Wall 1):**

| Artifact | Status | Notes |
|----------|--------|-------|
| CIFAR-10 raw data | Transferable | Public dataset; cite source |
| Train/val/test splits from SL Report | Transferable with provenance | SHA-256 verified via `verify_sl_report_snapshot.py` |
| Preprocessing pipeline from SL Report | Transferable with disclosure | Documented in PRIOR_WORK_REUSE §5 |

**Code Wall (§2, Wall 2):**

| Artifact | Status | Notes |
|----------|--------|-------|
| Training loop from SL Report | Transferable with provenance | Vendor snapshot in `vendor/sl_report/` |
| NAS search code | Original to this project | Written for this project |
| AI-generated boilerplate | Permitted with disclosure | Documented in AI_DIVISION_OF_LABOR |

**Content Wall (§2, Wall 3):**

| Artifact | Status | Notes |
|----------|--------|-------|
| Report prose | Must be original | No verbatim text from SL Report |
| Figure designs | Transferable as templates | New data, new captions |
| Analysis and conclusions | Must be human-written | AI may assist with editing only |

**Verification Commands:**

```bash
python scripts/verify_sl_report_snapshot.py  # exits 0
python scripts/check_data_ready.py           # exits 0
grep -c "AI Use Statement" report/main.tex   # >= 1
```

### LEAN_HYPOTHESIS

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | Neural Architecture Search Benchmark |
| `{{CUSTOMER_SEGMENT}}` | ML practitioners choosing NAS strategies |
| `{{PROBLEM_STATEMENT}}` | No clear guidance on when sophisticated NAS outperforms random search under matched compute budgets |

**Kill Criteria (§5.1):**

| # | Kill Criterion | Threshold | Action |
|---|---------------|-----------|--------|
| K1 | No method beats random baseline | Best NAS method < random search accuracy after 100% budget | Report as negative result |
| K2 | Instability too high | IQR > 20% of median accuracy | Investigate variance sources; increase seeds if feasible |
| K3 | Compute budget exhausted | < 50% of planned runs complete by 72h before deadline | Drop lowest-priority experiment part |

**Minimum Viable Experiment (§4.3):**

| Property | Value |
|----------|-------|
| **MVE scope** | Random search vs Bayesian optimization on CIFAR-10, 3 seeds, 1K budget |
| **MVE success criterion** | Both methods find architectures with val_acc > 90% |
| **Full experiment** | 4 NAS methods × 2 search spaces × 5 seeds × 10K budget |
| **Scale-up trigger** | If MVE shows >1% accuracy spread between methods |

**Resource Allocation (§6.1):**

| Experiment Part | Effort | Strategic Value | Priority |
|----------------|--------|----------------|----------|
| Part 1: NAS method comparison | 50% | High (core demonstration) | P0 |
| Part 2: Search space analysis | 30% | Medium (depth of analysis) | P1 |
| Part 3: Transfer to new dataset | 20% | Low (stretch goal) | P2 |

---

## Profile Command

```bash
# Start with a base profile, then add publishing templates
bash scripts/init_project.sh /path/to/nas-benchmark --profile full
```
