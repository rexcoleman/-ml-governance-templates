# Audit Automation Plan: Zero-Manual-Audit Quality Pipeline

**Version:** 1.1
**Date:** 2026-03-13
**Status:** PHASES 1-4 COMPLETE. Systems-benchmark profile shipped (v2.3).
**Drives:** govML v3.0 — from "templates that define WHAT" to "pipelines that VERIFY automatically"

---

## 1. Problem Statement

### The Manual Audit Tax

Commit history analysis from UL and RL reports reveals that **manual auditing dominates the workflow**:

| Metric | UL Report | RL Report |
|--------|-----------|-----------|
| Total commits | 36 | 39 |
| Audit/fix commits | 10+ (28%) | 37 (95%) |
| Distinct audit cycles | 7 | 14 |
| Findings fixed | 49+ | 30+ |
| Audit lenses used | 5 | 8+ |

The user is manually requesting audits through **different lenses** at **different times**, and each lens catches issues the others miss. This is:

1. **Cognitively expensive** — remembering to ask for each audit lens
2. **Temporally fragile** — audits requested too early miss issues; too late wastes rework
3. **Coverage-gapped** — no systematic guarantee all lenses are applied
4. **Brand-inconsistent** — quality depends on which audits the user remembers to request

### Audit Lenses Identified from Commit History

From UL (7 cycles) and RL (14 cycles), we can extract **10 distinct audit lenses** that were applied manually:

| # | Lens | UL Evidence | RL Evidence | When Applied |
|---|------|------------|-------------|-------------|
| L1 | **Template-vs-Requirements** | AC1: 6 fixes | AC1: 6 fixes | Phase 0 (setup) |
| L2 | **Code-vs-Template** | AC2: 4 FAIL, 4 WARN | AC2: within Phase 1 | Phase 0-1 (scaffolding) |
| L3 | **Phase Gate Compliance** | AC2-AC4 | AC3-AC4 | Per-phase |
| L4 | **Test Coverage & Architecture** | AC4: 36 test IDs | AC4: 72 tests | Phase 2-3 |
| L5 | **Data-vs-Report Consistency** | AC5: 10 numeric errors (PCA eigenvalue off 8.6x) | AC5: 3 critical + 1 medium | Post-experiment |
| L6 | **Rubric/FAQ Compliance** | AC6: 5 spec gaps | AC7-AC9: 8 items across 3 cycles | Post-draft |
| L7 | **Ten Simple Rules (Writing Quality)** | AC6: 7 structural improvements | AC10-AC12: 11 items across 3 cycles | Post-draft |
| L8 | **Academic Integrity / AI Use** | AC7: 3 fixes | AC13: 1 alignment | Pre-submission |
| L9 | **LaTeX / Build Compilation** | AC7: 2 fixes | 2 compilation fixes | Pre-submission |
| L10 | **Cross-Reference Integrity** | Terminology: "cluster features" | Figure/table/citation refs | Throughout |

### The Core Insight

**Each lens is a well-defined, repeatable verification pass.** They can be encoded as:
- **Generators** (produce checker scripts from template specs)
- **Prompt protocols** (structured audit prompts for AI-assisted verification)
- **Orchestrated pipelines** (run all lenses in correct order with dependency awareness)

---

## 2. Target State: The Audit Pipeline

### Architecture

```
project.yaml + filled templates + report draft + raw outputs
        │
        ▼
┌──────────────────────────────────────────────┐
│           AUDIT ORCHESTRATOR (orchestrate.py) │
│                                               │
│  Phase-Aware Lens Selection                   │
│    │                                          │
│    ├─ L1: Template-vs-Requirements  (Phase 0) │
│    ├─ L2: Code-vs-Template          (Phase 0) │
│    ├─ L3: Phase Gate Compliance     (per gate)│
│    ├─ L4: Test Coverage Audit       (Phase 2) │
│    ├─ L5: Data-vs-Report Checker    (Phase 4) │
│    ├─ L6: Rubric/FAQ Compliance     (Phase 4) │
│    ├─ L7: Ten Simple Rules Audit    (Phase 4) │
│    ├─ L8: Academic Integrity Audit  (Phase 5) │
│    ├─ L9: Build/Compilation Check   (Phase 5) │
│    └─ L10: Cross-Reference Audit    (Phase 5) │
│                                               │
│  Output: audit_report.md (per-lens verdicts)  │
│  Output: FINDINGS.md (actionable fix list)    │
│  Output: exit code 0 (all pass) or 1 (fails) │
└──────────────────────────────────────────────┘
```

### Phase-Lens Mapping

| Phase | Lenses Triggered | Rationale |
|-------|-----------------|-----------|
| 0 (Setup) | L1, L2 | Templates and scaffolding must be correct before experiments |
| 1 (Data) | L3, L4 | Data readiness and leakage gates |
| 2 (Hypothesis) | L3, L4 | Hypothesis lock + test architecture |
| 3 (Experiments) | L3, L5 (partial) | Phase gates + early data spot-check |
| 4 (Report) | L5, L6, L7, L10 | Full data-vs-report, rubric, writing quality, cross-refs |
| 5 (Submission) | L8, L9, L10 | Academic integrity, compilation, final cross-ref |
| **Full sweep** | L1-L10 | Pre-submission comprehensive audit |

---

## 3. New Templates Required

### 3.1 REPORT_CONSISTENCY_SPEC.tmpl.md (NEW — Ten Simple Rules Integration)

**Purpose:** Encode Kording & Mensh's 10 rules as verifiable checklist items with machine-checkable criteria where possible and structured prompt-audit criteria where not.

**Template Structure:**

```markdown
# Report Consistency & Writing Quality Specification

## Authority
- Source: Kording & Mensh (2016), "Ten simple rules for structuring papers"
- Enforcement: Phase 4 (Report) and Phase 5 (Submission)

## Rule 1: One Central Contribution
- [ ] Title is a declarative claim (not procedural: "Analysis of..." is FAIL)
- [ ] Title communicates the main finding, not the method
- [ ] Can summarize paper in one sentence that matches title

## Rule 2: Write for Naive Readers
- [ ] All jargon terms defined on first use (glossary or inline)
- [ ] No acronym used without expansion on first occurrence
- [ ] Domain-specific terms have parenthetical glosses
- Jargon inventory: {{JARGON_TERMS_WITH_DEFINITIONS}}

## Rule 3: Context-Content-Conclusion (CCC)
### Document-Level CCC
- [ ] Introduction = Context (gap-driven)
- [ ] Results = Content (evidence sequence)
- [ ] Discussion = Conclusion (gap filled + limitations + future)

### Paragraph-Level CCC
- [ ] Every paragraph opens with context/topic sentence
- [ ] Every paragraph closes with conclusion/takeaway sentence
- [ ] No paragraph exceeds {{MAX_PARAGRAPH_SENTENCES}} sentences without CCC checkpoint

### Abstract CCC
- [ ] Sentence 1-2: Broad context → specific gap
- [ ] Sentence 3-4: "Here we" approach + key results
- [ ] Sentence 5-6: Conclusion + broader significance

## Rule 4: Logical Flow (No Zig-Zag)
- [ ] Each concept introduced in exactly one location
- [ ] No A-B-A topic bouncing across paragraphs
- [ ] Parallel arguments use parallel syntactic structure
- [ ] One term per concept (no synonyms for technical terms)
- Terminology lock: {{TERM_CANONICAL_FORMS}}

## Rule 5: Abstract Completeness
- [ ] Abstract is self-contained (no undefined terms, no forward refs)
- [ ] Abstract covers: gap, method, results, conclusion
- [ ] Abstract length ≤ {{ABSTRACT_WORD_LIMIT}} words

## Rule 6: Introduction Gap Structure
- [ ] Paragraphs progress: broad field → subfield → specific gap
- [ ] Final intro paragraph previews results (compact summary)
- [ ] Gap statement is explicit ("However, ... remains unknown/untested")
- [ ] No literature review beyond gap motivation

## Rule 7: Results as Declarative Sequence
- [ ] Subsection headers are declarative statements (findings, not methods)
- [ ] Each results paragraph: question → data/logic → answer
- [ ] Figures tell the story without requiring legend text
- [ ] First results paragraph summarizes approach
- Caption checklist:
  - [ ] Every caption contains a takeaway interpretation
  - [ ] Seed aggregation uses median+IQR or mean±std (no bare means)
  - [ ] Method-specific settings disclosed in caption

## Rule 8: Discussion Structure
- [ ] First discussion paragraph summarizes key findings
- [ ] Limitations acknowledged with literature context
- [ ] Future directions connected to gap structure
- [ ] No new results introduced in discussion

## Rule 9: Time Allocation Evidence
- [ ] Title refined ≥3 times (tracked in CHANGELOG or git)
- [ ] Abstract refined ≥3 times
- [ ] Figures are publication-quality (labeled axes, readable fonts, proper resolution)

## Rule 10: Feedback Integration
- [ ] At least one test-reader pass (or AI audit pass) documented
- [ ] Rubric/FAQ compliance verified against assignment spec
- [ ] All audit findings resolved before submission

## Numeric Consistency Rules (from UL/RL audit findings)
- [ ] Every number in the report traces to a specific output artifact
- [ ] Artifact path documented in EXECUTION_MANIFEST
- [ ] No manually transcribed numbers (all from post_compute or verified extraction)
- [ ] Rounding rules: {{ROUNDING_PRECISION}} decimal places for {{METRIC_TYPE}}
- [ ] Percentage claims verified against raw data (UL found 8.6x error in PCA eigenvalue)
- [ ] Multiplier/ratio claims verified (UL found UMAP 4.8x→3.8x)
- [ ] "Improvement" vs "degradation" language matches sign of delta

## Cross-Reference Integrity
- [ ] Every figure referenced in text (no orphan figures)
- [ ] Every table referenced in text (no orphan tables)
- [ ] Figure/table numbers sequential and consistent
- [ ] All citations in bibliography; all bibliography entries cited
- [ ] Internal section references valid
- [ ] Terminology consistent throughout (no "cluster features" vs "cluster-derived features")

## Assignment-Specific Compliance
- [ ] All rubric items addressed (mapped in RUBRIC_TRACEABILITY)
- [ ] All FAQ items addressed (mapped in FAQ_TRACEABILITY)
- [ ] Deliverable filenames match spec: {{DELIVERABLE_NAMING_CONVENTION}}
- [ ] Author/ID format matches spec: {{AUTHOR_FORMAT}}
- [ ] AI Use Statement meets policy: {{AI_USE_POLICY_URL}}

## Build Verification
- [ ] LaTeX compiles without errors
- [ ] All figure paths resolve
- [ ] No overfull hbox warnings >10pt
- [ ] PDF page count within limit: {{PAGE_LIMIT}}
- [ ] URLs properly escaped (# → \# in LaTeX)
```

### 3.2 RUBRIC_TRACEABILITY.tmpl.md (NEW)

**Purpose:** Map every rubric/grading item to a specific report section + paragraph, ensuring 100% coverage before submission. This was the source of AC6-AC9 in RL (8 items across 4 audit cycles).

```markdown
# Rubric & FAQ Traceability Matrix

## Rubric Items
| # | Requirement | Report Section | Paragraph | Status | Verified |
|---|-------------|---------------|-----------|--------|----------|
| {{RUBRIC_ID}} | {{REQUIREMENT_TEXT}} | {{SECTION}} | {{PARA_NUM}} | {{ADDRESSED/GAP}} | {{DATE}} |

## FAQ Items
| # | Question | Report Section | Paragraph | Status | Verified |
|---|----------|---------------|-----------|--------|----------|
| {{FAQ_ID}} | {{FAQ_TEXT}} | {{SECTION}} | {{PARA_NUM}} | {{ADDRESSED/GAP}} | {{DATE}} |

## Coverage Summary
- Rubric coverage: {{COVERED}}/{{TOTAL}} ({{PERCENT}}%)
- FAQ coverage: {{COVERED}}/{{TOTAL}} ({{PERCENT}}%)
- GAP items requiring attention: {{GAP_LIST}}
```

---

## 4. New Generators Required

### 4.1 G13: `gen_report_auditor.py` — Report Consistency Auditor Generator

**Input:** Filled REPORT_CONSISTENCY_SPEC + report .tex/.md file + outputs/ directory
**Output:** `scripts/audit_report.py` — executable audit script

**Automated checks (machine-verifiable):**

| Check | Method | Source of Truth |
|-------|--------|----------------|
| Title is declarative | Regex: reject "Analysis of", "A Study of", "Investigation of" | REPORT_CONSISTENCY_SPEC Rule 1 |
| Abstract word count | Word count vs limit | REPORT_CONSISTENCY_SPEC Rule 5 |
| Jargon defined on first use | Term inventory cross-ref against first-occurrence expansion | REPORT_CONSISTENCY_SPEC Rule 2 |
| Section headers declarative | Regex: reject headers starting with verbs/gerunds without claims | Rule 7 |
| Figure/table cross-refs | Parse \ref{} and \label{} for orphans | Rule 7 / Cross-Reference |
| Citation completeness | Parse \cite{} vs \bibitem{} | Cross-Reference |
| Terminology consistency | Canonical term list vs full-text grep for variants | Rule 4 |
| Number-artifact traceability | Extract numbers from report, match against EXECUTION_MANIFEST paths | Numeric Consistency |
| LaTeX compilation | `pdflatex` + check exit code + parse warnings | Build Verification |
| Page count | `pdfinfo` page count vs limit | Build Verification |
| URL escaping | Regex for unescaped # in \url{} or \href{} | Build Verification |
| Deliverable filenames | Glob against naming convention pattern | Assignment Compliance |

**Prompt-audit checks (AI-assisted, structured output):**

| Check | Prompt Template | Expected Output |
|-------|----------------|-----------------|
| Paragraph CCC compliance | "For each paragraph, identify: context sentence, content, conclusion sentence. Flag any missing." | Per-paragraph PASS/FAIL with specific sentences |
| Abstract CCC structure | "Map abstract sentences to: broad context, specific gap, approach, results, conclusion, broader significance." | 6-slot mapping with coverage |
| Introduction gap progression | "Identify the gap narrowing: field → subfield → specific gap. Is the progression clear?" | Gap chain with verdict |
| Results question-answer | "For each results paragraph, identify: question posed, evidence presented, answer given." | Per-paragraph Q-E-A mapping |
| Discussion completeness | "Does discussion cover: summary, limitations, future directions? Any new results introduced?" | 3-item checklist |
| Zig-zag detection | "Identify any concept introduced in >1 location or A-B-A topic patterns." | Flagged violations |

### 4.2 G14: `gen_data_report_checker.py` — Data-vs-Report Consistency Checker

**Input:** outputs/ directory (CSVs, JSONs, figures) + report .tex/.md + EXECUTION_MANIFEST
**Output:** `scripts/check_data_report.py`

This is the most critical generator. The UL report had a PCA eigenvalue off by 8.6x, and the RL report had 3 critical findings. These are the errors that destroy credibility.

**Method:**
1. Parse EXECUTION_MANIFEST for artifact→report-section mappings
2. Extract all numeric claims from report (regex for numbers near metric keywords)
3. Load corresponding output artifacts (CSVs, JSONs)
4. Cross-reference extracted numbers against source data
5. Flag mismatches beyond rounding tolerance

**Checks:**
- Exact numeric match (within ROUNDING_PRECISION tolerance)
- Sign consistency ("improvement" = positive delta, "degradation" = negative)
- Magnitude plausibility (flag >2x differences as likely errors)
- Percentage base verification (% of what?)
- Min/max/mean claims verified against actual distributions
- Figure data matches underlying CSV (spot-check via data extraction)

### 4.3 G15: `gen_rubric_checker.py` — Rubric/FAQ Compliance Checker

**Input:** requirements/*.md (rubric + FAQ docs) + filled RUBRIC_TRACEABILITY + report
**Output:** `scripts/check_rubric.py`

**Method:**
1. Parse rubric items from requirements docs
2. For each item, verify the mapped report section contains relevant content
3. For FAQ items, verify explicit addressing
4. Output coverage matrix with GAP items highlighted

### 4.4 G16: `gen_integrity_checker.py` — Academic Integrity Checker

**Input:** AI_DIVISION_OF_LABOR + report AI Use Statement + ACADEMIC_INTEGRITY_FIREWALL
**Output:** `scripts/check_integrity.py`

**Checks:**
- AI Use Statement present and non-empty
- Statement format matches policy template (first-person, tool-specific, ownership declaration)
- No prohibited AI-generated content per AI_DIVISION_OF_LABOR
- Anti-ghostwriting firewall verification commands pass

---

## 5. Orchestrator Enhancements

### 5.1 Phase-Aware Audit Triggering

Extend `orchestrate.py` to support audit-mode execution:

```python
# New tool functions for orchestrate.py

def tool_run_audit(phase: int, report_path: str, outputs_dir: str) -> dict:
    """Run all audit lenses appropriate for the given phase."""
    lenses = PHASE_LENS_MAP[phase]
    results = {}
    for lens in lenses:
        results[lens.name] = lens.run(report_path, outputs_dir)
    return results

def tool_run_full_audit(report_path: str, outputs_dir: str) -> dict:
    """Run all 10 audit lenses (pre-submission comprehensive sweep)."""
    return tool_run_audit(phase="full", report_path=report_path, outputs_dir=outputs_dir)

def tool_generate_findings(audit_results: dict) -> str:
    """Convert audit results into actionable FINDINGS.md with fix priorities."""
    # Categorize: CRITICAL (data errors), HIGH (rubric gaps), MEDIUM (writing), LOW (style)
    ...
```

### 5.2 CLAUDE.md Audit Integration

Add to CLAUDE_MD.tmpl.md:

```markdown
## Audit Protocol
After completing each phase, run the phase-appropriate audit before proceeding:
- `python scripts/audit_report.py --phase {N}` (automated checks)
- Review FINDINGS.md and resolve all CRITICAL/HIGH items
- Re-run audit to verify fixes
- Only proceed to next phase when audit passes

## Pre-Submission Audit
Before final submission, run the full audit sweep:
- `python scripts/audit_report.py --phase full`
- All 10 lenses must pass
- FINDINGS.md must show 0 CRITICAL, 0 HIGH items
```

### 5.3 Audit Report Format

```markdown
# Audit Report — Phase {{PHASE}} — {{TIMESTAMP}}

## Summary
| Lens | Checks | Pass | Fail | Warn | Skip |
|------|--------|------|------|------|------|
| L1: Template-vs-Requirements | 30 | 30 | 0 | 0 | 0 |
| L5: Data-vs-Report | 45 | 43 | 2 | 0 | 0 |
| L7: Ten Simple Rules | 25 | 22 | 1 | 2 | 0 |
| **Total** | **100** | **95** | **3** | **2** | **0** |

## Verdict: FAIL (3 findings require resolution)

## Findings
### CRITICAL
- **F-001**: Section 4.2, paragraph 3: PCA explained variance = 65% in report, 7.6% in outputs/pca_results.csv
  - **Fix**: Update report to match outputs/pca_results.csv line 12
  - **Artifact**: outputs/pca_results.csv

### HIGH
- **F-002**: Rubric item #14 (distance justification) not addressed in any section
  - **Fix**: Add distance metric justification to Section 3.1

### MEDIUM
- **F-003**: Paragraph 7 of Results missing conclusion sentence (CCC Rule 3 violation)
  - **Fix**: Add concluding interpretation sentence
```

---

## 6. Implementation Roadmap

### Phase 1: Template + Prompt Protocol — COMPLETE

**Deliverables:**
1. `REPORT_CONSISTENCY_SPEC.tmpl.md` — Ten Simple Rules + numeric consistency + cross-ref rules **DONE**
2. `RUBRIC_TRACEABILITY.tmpl.md` — Rubric/FAQ coverage matrix **DONE**
3. Prompt Playbook Stage 10: "Multi-Lens Audit Protocol" — structured prompts for L5, L6, L7, L8, L10 **DONE**
4. Copy `Ten_Simple_Rules_Kording_Mensh.md` into `docs/references/` **DONE**

### Phase 2: Machine-Verifiable Generators — COMPLETE

**Deliverables:**
5. G13: `gen_report_auditor.py` — 13 machine-checkable rules (title, abstract, CCC, jargon, terminology, cross-refs, captions, build, page count, URL escaping) **DONE**
6. G14: `gen_data_report_checker.py` — numeric consistency with configurable tolerances, sign/magnitude checks, EXECUTION_MANIFEST integration **DONE**
7. G15: `gen_rubric_checker.py` — rubric/FAQ extraction, keyword-based coverage, 10 common gap patterns **DONE**
8. G16: `gen_integrity_checker.py` — AI Use Statement quality (5 checks), anti-ghostwriting, deliverable naming **DONE**

### Phase 3: Orchestrator Integration — COMPLETE

**Deliverables:**
9. `orchestrate.py` extended with `tool_run_audit()`, `tool_run_full_audit()`, and per-generator tool functions **DONE**
10. Phase-lens mapping (`PHASE_LENS_MAP`) in orchestrate.py **DONE**
11. `--audit PHASE` CLI flag for audit-only mode **DONE**
12. `generate_all.py` updated to run G13-G16 when audit config present **DONE**
13. CLAUDE.md updated with audit protocol section **DONE**
14. `project.yaml.example` extended with full `audit:` schema **DONE**
15. `init_project.sh` updated — all profiles include REPORT_CONSISTENCY_SPEC + RUBRIC_TRACEABILITY **DONE**
16. `ROADMAP.md` updated with v2.2 release notes **DONE**
17. `TEMPLATE_INDEX.md` updated (29 templates, G13-G16, profiles, dependency graph) **DONE**

### Phase 4: AI-Assisted Audit Lenses — COMPLETE

**Deliverables:**
18. Prompt template for L5 (Data-vs-Report) in Stage 10 **DONE**
19. Prompt template for L6 (Rubric/FAQ) in Stage 10 **DONE**
20. Prompt template for L7 (Ten Simple Rules — CCC, zig-zag, gap progression) in Stage 10 **DONE**
21. Prompt template for L8 (Academic Integrity) in Stage 10 **DONE**
22. Prompt template for L10 (Cross-Reference Integrity) in Stage 10 **DONE**
23. Stage 10 checkpoint with acceptance criteria **DONE**

### Phase 5: Systems Benchmark Profile — COMPLETE

**Deliverables:**
24. `BUILD_SYSTEM_CONTRACT.tmpl.md` — compiler lock, 3 build profiles, sanitizer governance, reproducible builds **DONE**
25. `PERFORMANCE_BENCHMARKING_SPEC.tmpl.md` — measurement protocol, statistical reporting, performance budgets, scaling analysis **DONE**
26. `CONCURRENCY_TESTING_SPEC.tmpl.md` — TSan integration, race condition tripwires, deadlock detection, stress testing **DONE**
27. `systems-benchmark` profile (12 templates) in `init_project.sh` **DONE**
28. ENVIRONMENT_CONTRACT Appendix D — C/C++ determinism defaults **DONE**
29. EXPERIMENT_CONTRACT §4.2 — generalized to "Baseline State Matching" **DONE**
30. TEST_ARCHITECTURE §3.4 — C/C++ synthetic fixtures + performance regression tests **DONE**
31. METRICS_CONTRACT Appendix D — systems sanity checks **DONE**
32. ADVERSARIAL_EVALUATION Appendix B — systems security (sanitizers, fuzzing, static analysis) **DONE**
33. RUBRIC_TRACEABILITY — Research Question Traceability appendix for self-directed projects **DONE**
34. project.yaml.example — systems config + security-domain dataset examples **DONE**
35. TEMPLATE_INDEX, ROADMAP, CLAUDE.md updated for v2.3 **DONE**

**Remaining (future — requires Claude Agent SDK integration):**
- Automated prompt-audit execution via orchestrate.py agent mode
- Structured output parsing for AI audit results → FINDINGS.md
- Multi-agent LangGraph pipeline with specialized audit sub-agents

---

## 7. Projected Impact

### Manual Steps Reduction

| Audit Activity | Current (Manual) | With Plan | Reduction |
|---------------|-----------------|-----------|-----------|
| Template compliance | Ask Claude, review, fix, re-ask | Automatic (G13) | ~100% |
| Data-vs-report numbers | Ask Claude, review each number, fix | Automatic (G14) | ~90% |
| Rubric/FAQ coverage | Ask Claude per FAQ, fix gaps, re-ask | Automatic (G15) | ~95% |
| Ten Simple Rules | Ask Claude, review, fix, re-ask ×3 cycles | Semi-auto (G13 + prompts) | ~80% |
| Academic integrity | Ask Claude, review, strengthen | Automatic (G16) | ~95% |
| Cross-references | Manual scan or ask Claude | Automatic (G13) | ~100% |
| Full pre-submission audit | 5-8 separate audit requests | One command | ~90% |

### Quality Consistency

| Metric | Current | Target |
|--------|---------|--------|
| Audit cycles per project | 7-14 | 2-3 (initial + final) |
| Findings caught before report draft | ~30% | ~80% |
| Numeric errors reaching submission | Possible (8.6x found late) | 0 (caught automatically) |
| Rubric gaps at submission | Possible (8 items in RL) | 0 (caught at draft time) |
| Writing quality consistency | Varies by audit thoroughness | Standardized by template |

### Brand Alignment

Every report produced with govML audit pipeline will:
- Follow Ten Simple Rules structure (professional academic quality)
- Have 100% rubric/FAQ coverage (no gaps)
- Have 0 numeric inconsistencies (data integrity)
- Have consistent terminology throughout (no drift)
- Have verified academic integrity statements
- Compile cleanly with no build errors

This is the "architect who ships" standard: **the system catches the errors, not the human**.

---

## 8. Integration with Existing govML Architecture

### Template Index Update
Add to TEMPLATE_INDEX.md:
- `templates/report/REPORT_CONSISTENCY_SPEC.tmpl.md` (new)
- `templates/report/RUBRIC_TRACEABILITY.tmpl.md` (new)

### Profile Updates
All profiles that include report templates should also include:
- REPORT_CONSISTENCY_SPEC (all profiles except Minimal)
- RUBRIC_TRACEABILITY (all profiles with academic context)

### Generator Registry Update
Add to ROADMAP.md v3.0:
- G13: `gen_report_auditor.py` (report consistency)
- G14: `gen_data_report_checker.py` (data-vs-report)
- G15: `gen_rubric_checker.py` (rubric/FAQ compliance)
- G16: `gen_integrity_checker.py` (academic integrity)

### project.yaml Schema Extension

```yaml
audit:
  ten_simple_rules:
    abstract_word_limit: 250
    max_paragraph_sentences: 8
    jargon_terms:
      - term: "PCA"
        definition: "Principal Component Analysis"
      - term: "GMM"
        definition: "Gaussian Mixture Model"
    terminology_lock:
      - canonical: "cluster-derived features"
        reject: ["cluster features", "clustering features"]
    rounding_precision:
      accuracy: 3
      percentage: 1
      p_value: 3

  rubric:
    source: "requirements/assignment_spec.md"
    faq_source: "requirements/assignment_FAQ.md"

  academic_integrity:
    policy_url: "https://example.edu/ai-policy"
    ai_tools:
      - name: "Claude Code CLI"
        role: "code generation, report structuring, audit verification"
        prohibited: "original analysis, hypothesis formulation, conclusion drawing"

  build:
    engine: "pdflatex"
    page_limit: 12
    deliverable_pattern: "{{REPORT_TYPE}}_Report_{{AUTHOR_ID}}.tex"
```

### Prompt Playbook Stage 10: Multi-Lens Audit Protocol

Add new stage to PROMPT_PLAYBOOK.md:

```markdown
## Stage 10: Multi-Lens Audit Protocol

### When to Run
- After Phase 4 (Report Draft): Run L5, L6, L7, L10
- Before Phase 5 (Submission): Run L1-L10 (full sweep)

### Structured Audit Prompts

#### L5: Data-vs-Report Consistency
"Read EXECUTION_MANIFEST. For each artifact→section mapping, extract the
numeric claims from the report section and verify against the source artifact.
Report: exact match, rounding difference, or MISMATCH with details."

#### L6: Rubric Compliance
"Read requirements/assignment_spec.md and requirements/assignment_FAQ.md.
For each rubric item and FAQ question, find the specific report paragraph
that addresses it. Output a coverage matrix. Flag any GAP items."

#### L7: Ten Simple Rules Audit
"Read REPORT_CONSISTENCY_SPEC. For each rule (1-10), evaluate the report.
For Rule 3 (CCC), check every paragraph. For Rule 4 (flow), check for
zig-zag patterns. For Rule 7, check that all section headers are declarative.
Output per-rule PASS/FAIL with specific violations."

#### L8: Academic Integrity
"Read AI_DIVISION_OF_LABOR and the AI Use Statement in the report. Verify:
(a) all permitted AI uses are disclosed, (b) no prohibited uses are present,
(c) statement is first-person and tool-specific, (d) ownership declaration
present for design, hypotheses, and conclusions."
```

---

## 9. Relationship to Existing Roadmap

This plan extends the v3.0 roadmap (12 generators → 16 generators) with an **audit-first priority**:

| Priority | Generator | Rationale |
|----------|-----------|-----------|
| **P0** | G14: Data-vs-Report | Highest-severity findings (8.6x errors) |
| **P0** | G15: Rubric Checker | Most audit cycles consumed (8 items in RL) |
| **P1** | G13: Report Auditor | Broadest coverage (cross-refs, terminology, compilation) |
| **P1** | G16: Integrity Checker | Brand-critical (academic standing) |
| **P2** | G2: Post-Compute | Feeds G14 (standardized output extraction) |
| **P2** | G8: CI Pipeline | Automates audit pipeline in CI/CD |
| **P3** | G3-G4, G7, G9-G12 | Remaining scaffolding generators |

The audit generators (G13-G16) should be implemented **before** the remaining scaffolding generators (G2-G4, G7-G12) because they deliver the highest ROI: eliminating the 14-audit-cycle pattern that currently dominates project timelines.

---

## 10. Success Criteria

The audit automation plan is successful when:

1. **Zero-surprise submissions:** No numeric error >1% found after the automated audit passes
2. **Single-command audit:** `python scripts/audit_report.py --phase full` catches ≥90% of issues previously found manually
3. **Rubric completeness:** 100% rubric/FAQ coverage verified automatically before submission
4. **Writing quality floor:** Every report follows Ten Simple Rules structure (verified by template + prompt audit)
5. **Audit cycle reduction:** From 7-14 manual cycles → 2-3 automated cycles per project
6. **Brand consistency:** Every govML-produced report meets the same quality standard regardless of which audits the user remembers to request

---

## Appendix A: Issue Taxonomy from UL + RL Commit History

### Severity: CRITICAL (Data Integrity)
- PCA eigenvalue 65% → 7.6% (8.6x error) — UL
- Wine RP std dev 0.008 → 0.027 (3.4x error) — UL
- UMAP multiplier 4.8x → 3.8x (1.25x error) — UL
- "Halves wall-clock time" → "33% faster" (false claim) — UL
- Blackjack heatmap decoding (data correctness) — RL
- Report numbers not matching actual data — RL
- F5 ablation figure accuracy — RL

### Severity: HIGH (Compliance Gaps)
- Missing distance/similarity justification — UL
- Missing PCA eigenvalue distribution discussion — UL
- Missing ICA/PCA loadings — UL
- Missing RP variation std dev values — UL
- CartPole reward not addressed — RL
- MDP motivation not addressed — RL
- DQN HP validation missing — RL
- EC seeds not documented — RL
- Replay randomization not addressed — RL
- HP search ranges/sensitivity missing — RL
- Q_0 initialization not addressed — RL
- Ablation convergence not addressed — RL

### Severity: MEDIUM (Writing Quality)
- Non-declarative title — UL
- Abstract CCC structure incomplete — UL, RL
- Introduction gap progression missing — UL
- Procedural section headers — UL, RL
- Results paragraphs lack Q-A framing — UL, RL
- Discussion not linked to literature — UL
- Jargon undefined on first use — RL
- 164x consistency claim — RL
- Paragraph CCC violations — RL (3 instances)
- Intro preview missing — RL
- Future work section missing — RL

### Severity: LOW (Technical/Style)
- Terminology drift ("cluster features" vs "cluster-derived features") — UL
- Conda env name copy-paste (cs7641-sl → cs7641-ul) — UL
- AI Use Statement vague — UL, RL
- LaTeX URL escaping — UL, RL
- graphicspath relative vs absolute — UL, RL
- gitignore negation rules — RL
- Deliverable filename format — UL, RL
- Author format inconsistency — RL
- Reference IEEE formatting — RL
- Figure caption formatting — RL

### Distribution
- CRITICAL: 7 (9%)
- HIGH: 12 (15%)
- MEDIUM: 13+ (17%)
- LOW: 10+ (13%)
- PASS (no issue): ~35+ (46%)
