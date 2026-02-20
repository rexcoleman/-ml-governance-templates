# Prompt Playbook

A guided prompt workflow for customizing the ML Governance Templates using an AI assistant.

---

## Overview

This playbook provides a series of copy-paste prompts that walk you from a raw problem statement through requirements extraction, template selection, full template customization, ongoing governance, and automated testing. Each stage builds on the previous one.

**Designed for:** Claude, ChatGPT, and other LLM assistants. Prompts are optimized for Claude's structured output capabilities but work with any capable model.

**How to use:**
1. **Initial setup:** Work through Stages 1 → 5 in order to go from problem statement to filled templates
2. **Ongoing governance:** Use Stage 6 (Audit) periodically and Stage 7 (Patches) when changes occur
3. **Automation:** Use Stage 8 (Test Code) to generate executable compliance tests
4. Copy each prompt, paste it into your AI assistant, and attach the required inputs
5. Review the output at each checkpoint before proceeding
6. Each stage is self-contained — you can restart any stage without losing prior work

---

## Stage 1: Problem Statement → Structured Brief

### Goal
Transform a raw problem description (assignment, RFP, research question, or project charter) into a structured project brief that captures all decision-relevant information.

### Input
- Your raw problem statement, assignment document, RFP, or research question
- Any supplementary materials (FAQs, clarifications, constraints documents)

### Prompt

```
You are a senior ML project architect. I will provide a raw problem description for an ML project. Your job is to extract and organize all decision-relevant information into a structured project brief.

Analyze the provided materials and produce a brief with EXACTLY these sections:

## 1. Objective
- Primary goal (one sentence)
- Success criteria (measurable)

## 2. Datasets
For each dataset:
- Name and source
- Task type (classification, regression, etc.)
- Size estimate (rows, features) if stated
- Any constraints on data handling

## 3. Methods / Algorithms
- Required methods (explicitly stated)
- Optional/suggested methods
- Any constraints (e.g., "must use framework X", "must compare against baseline Y")

## 4. Constraints
- Compute constraints (CPU-only, GPU allowed, cloud budget)
- Format constraints (report format, page limits, required sections)
- Reproducibility requirements
- Timeline / deadlines

## 5. Deliverables
List every required output:
- Reports, documents, presentations
- Code repositories
- Artifacts (models, figures, tables)
- Supplementary materials

## 6. Success Criteria
- How will the project be evaluated?
- What are the acceptance criteria?
- What constitutes failure?

## 7. Timeline
- Key milestones and deadlines
- Phase structure (if any)

## 8. Ambiguities & Open Questions
- List anything that is unclear, contradictory, or missing from the source materials
- For each ambiguity, suggest a conservative default interpretation

RULES:
- Do NOT invent information. If something is not stated, mark it as "[NOT SPECIFIED]".
- Quote the source material when making claims about requirements.
- Flag contradictions between documents explicitly.
- Distinguish between MUST (explicitly required) and SHOULD (implied best practice).

---

HERE IS MY PROBLEM DESCRIPTION:

[Paste your problem statement / assignment / RFP here]

SUPPLEMENTARY MATERIALS (if any):

[Paste any FAQs, clarifications, or constraints documents here]
```

### Expected Output
A 1-2 page structured brief covering all 8 sections.

### Checkpoint
Before proceeding to Stage 2, verify:
- [ ] All explicitly stated requirements are captured (not just inferred ones)
- [ ] Ambiguities are flagged, not silently resolved
- [ ] No fabricated information (datasets, metrics, deadlines)
- [ ] MUST vs SHOULD distinction is applied correctly

---

## Stage 2: Structured Brief → Requirements & Specs

### Goal
Convert the structured brief into a formal requirements document with MUST/SHOULD categorization, acceptance criteria, and an authority hierarchy mapping.

### Input
- Stage 1 output (structured brief)
- The original source materials (for cross-reference)

### Prompt

```
You are a requirements engineer for an ML project. I will provide a structured project brief. Your job is to produce a formal requirements document.

Produce a document with EXACTLY these sections:

## 1. Authority Hierarchy
Map the source documents into a tiered authority structure:
- Tier 1: Primary requirements document (highest authority — overrides everything)
- Tier 2: Clarifications and FAQ (cannot override Tier 1)
- Tier 3: Advisory/derived specifications
- Contracts: Project governance documents (subordinate to all tiers)

For each tier, name the specific document and its role.

## 2. Functional Requirements
List every functional requirement. For each:
- ID: FR-001, FR-002, etc.
- Requirement: What the system must do
- Priority: MUST (explicit Tier 1/2 requirement) or SHOULD (best practice)
- Source: Which document and section
- Acceptance test: How to verify this requirement is met

Categories to cover:
- Data handling (loading, splitting, preprocessing)
- Model training (algorithms, budgets, seeding)
- Evaluation (metrics, test protocol, baselines)
- Output generation (figures, tables, artifacts)
- Report writing (format, sections, constraints)

## 3. Non-Functional Requirements
List non-functional requirements:
- Reproducibility (environment, determinism, seeding)
- Compute constraints (platform, hardware, budget)
- Format requirements (report format, page limits)
- Compliance requirements (attribution, IP, licensing)

## 4. Acceptance Criteria Matrix
| Requirement ID | Criterion | Verification Method | Automated? |
|---|---|---|---|
| FR-001 | ... | ... | Yes/No |

## 5. Risk-Relevant Requirements
Flag any requirements where non-compliance would result in critical failure (project rejection, zero credit, contract breach). These become inputs to the Risk Register.

## 6. Open Items
Requirements that need clarification before implementation can proceed.

RULES:
- Every requirement MUST trace to a source document. No invented requirements.
- MUST vs SHOULD: Only use MUST when the source document explicitly requires it.
- Do NOT add requirements beyond what the source materials specify.
- If a common ML best practice is not explicitly required, list it as SHOULD with a note.

---

HERE IS THE STRUCTURED BRIEF:

[Paste Stage 1 output here]

ORIGINAL SOURCE MATERIALS:

[Paste original documents for cross-reference]
```

### Expected Output
A formal requirements document with 30-60 numbered requirements, an authority hierarchy, and acceptance criteria.

### Checkpoint
Before proceeding to Stage 3, verify:
- [ ] Every MUST requirement traces to a specific source document
- [ ] No invented requirements — everything is grounded in source materials
- [ ] Acceptance criteria are testable (not vague)
- [ ] Risk-relevant requirements are flagged

---

## Stage 3: Requirements → Template Selection & Tier Recommendation

### Goal
Determine which governance tier to use, which templates to deploy, and the optimal customization order.

### Input
- Stage 2 output (requirements document)
- Familiarity with the template suite (or paste the TEMPLATE_INDEX.md)

### Prompt

```
You are an ML governance consultant. I will provide a requirements document for an ML project and a template index describing available governance templates. Your job is to recommend a governance configuration.

## Available Template Tiers

### Minimal (3 templates)
- ENVIRONMENT_CONTRACT, DATA_CONTRACT, METRICS_CONTRACT
- For: Simple, single-part experiments

### Standard (11 templates)
- All 7 core contracts + IMPLEMENTATION_PLAYBOOK + RISK_REGISTER + REPORT_ASSEMBLY_PLAN + PRE_SUBMISSION_CHECKLIST
- For: Multi-phase projects with delivery requirements

### Full (15 templates)
- All templates including TASK_BOARD, DECISION_LOG, CHANGELOG, PRIOR_WORK_REUSE
- For: Complex multi-phase projects with prior work reuse and strict compliance

## Your Task

Produce a recommendation with these sections:

### 1. Tier Recommendation
- Recommended tier and rationale
- Which project characteristics drove the recommendation

### 2. Template Selection
For each selected template:
- Why it's needed (trace to specific requirements)
- Which requirements it addresses
- Priority: Critical (must customize first) / Important / Nice-to-have

### 3. Customization Order
Ordered list of templates to customize, with rationale for the ordering.
The order should respect dependencies (e.g., ENVIRONMENT_CONTRACT before EXPERIMENT_CONTRACT).

### 4. Templates NOT Selected (if not Full tier)
For each excluded template:
- Why it's not needed
- Under what conditions you would add it

### 5. Cross-Template Dependencies
Map which templates reference each other and what values must be consistent across templates.

RULES:
- Match governance overhead to project complexity. Don't recommend Full tier for a simple experiment.
- Every recommendation must trace to a specific requirement.
- Consider the team size and project timeline when recommending.

---

HERE IS THE REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

HERE IS THE TEMPLATE INDEX:

[Paste TEMPLATE_INDEX.md here, or provide a summary]
```

### Expected Output
A governance configuration recommendation with tier, template list, customization order, and dependency map.

### Checkpoint
Before proceeding to Stage 4, verify:
- [ ] Tier matches project complexity (not over-engineered or under-governed)
- [ ] Every selected template traces to at least one requirement
- [ ] Customization order respects template dependencies
- [ ] Cross-template consistency points are identified

---

## Stage 4: Requirements → Template Customization

### Goal
Fill all `{{PLACEHOLDER}}` values in each selected template using the requirements document.

This stage has sub-prompts for each template group. Run them in the order recommended by Stage 3.

---

### Stage 4a: Environment + Data Contracts

#### Input
- Stage 2 output (requirements document)
- Blank `ENVIRONMENT_CONTRACT.tmpl.md`
- Blank `DATA_CONTRACT.tmpl.md`

#### Prompt

```
You are an ML infrastructure engineer. I will provide a requirements document and two blank governance templates. Your job is to fill in all {{PLACEHOLDER}} values to produce ready-to-commit governance documents.

TEMPLATE 1: ENVIRONMENT_CONTRACT
TEMPLATE 2: DATA_CONTRACT

For each template:
1. Read the Customization Guide table at the top
2. Determine the correct value for each {{PLACEHOLDER}} from the requirements document
3. Fill in all placeholders throughout the document
4. Fill in any example tables or lists with project-specific values
5. Add contextual notes where the template says "*(Fill in...)*"

RULES:
- Every value MUST come from the requirements document. Do NOT invent datasets, versions, or metrics.
- If a value is not specified in the requirements, mark it as "[TODO: specify]" — do NOT guess.
- Preserve all template structure (sections, tables, checklists).
- Do NOT delete sections. If a section doesn't apply, add a note: "Not applicable for this project because [reason]."
- For the authority hierarchy, use the mapping from the requirements document.
- Output each completed template as a separate markdown document.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

TEMPLATE 1 — ENVIRONMENT_CONTRACT:

[Paste blank ENVIRONMENT_CONTRACT.tmpl.md here]

TEMPLATE 2 — DATA_CONTRACT:

[Paste blank DATA_CONTRACT.tmpl.md here]
```

---

### Stage 4b: Experiment + Metrics Contracts

#### Input
- Stage 2 output (requirements document)
- Completed Environment and Data contracts (from Stage 4a)
- Blank `EXPERIMENT_CONTRACT.tmpl.md`
- Blank `METRICS_CONTRACT.tmpl.md`

#### Prompt

```
You are an ML experiment design specialist. I will provide a requirements document, two already-completed governance contracts (for cross-reference), and two blank templates to fill.

COMPLETED CONTRACTS (for cross-reference only — do not modify):
- ENVIRONMENT_CONTRACT (completed)
- DATA_CONTRACT (completed)

TEMPLATES TO FILL:
- EXPERIMENT_CONTRACT
- METRICS_CONTRACT

For each template:
1. Read the Customization Guide table
2. Fill all {{PLACEHOLDER}} values from the requirements document
3. Ensure cross-references to ENVIRONMENT_CONTRACT and DATA_CONTRACT are consistent
4. Fill per-part protocol sections for each experimental phase
5. Define concrete metrics, thresholds, and sanity checks

RULES:
- Dataset names, seed values, and budget references MUST match the completed contracts.
- Do NOT invent metric values, thresholds, or budget numbers. Use values from requirements or mark as "[TODO: specify]".
- Per-part protocols: create one section per experimental phase identified in the requirements.
- Cross-references: verify section numbers when referencing companion contracts.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED ENVIRONMENT_CONTRACT:

[Paste completed Environment Contract here]

COMPLETED DATA_CONTRACT:

[Paste completed Data Contract here]

TEMPLATE — EXPERIMENT_CONTRACT:

[Paste blank EXPERIMENT_CONTRACT.tmpl.md here]

TEMPLATE — METRICS_CONTRACT:

[Paste blank METRICS_CONTRACT.tmpl.md here]
```

---

### Stage 4c: Figures/Tables + Artifact + Script Specs

#### Input
- Stage 2 output (requirements document)
- All previously completed contracts (for cross-reference)
- Blank `FIGURES_TABLES_CONTRACT.tmpl.md`
- Blank `ARTIFACT_MANIFEST_SPEC.tmpl.md`
- Blank `SCRIPT_ENTRYPOINTS_SPEC.tmpl.md`

#### Prompt

```
You are an ML systems engineer. I will provide a requirements document, previously completed contracts, and three blank templates to fill.

TEMPLATES TO FILL:
- FIGURES_TABLES_CONTRACT
- ARTIFACT_MANIFEST_SPEC
- SCRIPT_ENTRYPOINTS_SPEC

For each template:
1. Fill all {{PLACEHOLDER}} values from the requirements document
2. For FIGURES_TABLES_CONTRACT: define one row per required figure/table. Include figure IDs (F1, F2, ...), data sources, and interpretation goals.
3. For ARTIFACT_MANIFEST_SPEC: define the run ID format, hashing algorithm, and per-run output schema.
4. For SCRIPT_ENTRYPOINTS_SPEC: define one section per script. Include filename, CLI flags, inputs, outputs, and exit codes.

RULES:
- All references to datasets, methods, metrics, and budgets MUST match previously completed contracts.
- For scripts: derive the script list from the experiment protocol in EXPERIMENT_CONTRACT.
- For figures/tables: derive the list from the report requirements and metrics definitions.
- Do NOT invent script names or figure specifications not grounded in requirements.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

PREVIOUSLY COMPLETED CONTRACTS:

[Paste all completed contracts here]

TEMPLATE — FIGURES_TABLES_CONTRACT:

[Paste blank template here]

TEMPLATE — ARTIFACT_MANIFEST_SPEC:

[Paste blank template here]

TEMPLATE — SCRIPT_ENTRYPOINTS_SPEC:

[Paste blank template here]
```

---

### Stage 4d: Management Templates

#### Input
- Stage 2 output (requirements document)
- All previously completed contracts
- Blank management templates: `IMPLEMENTATION_PLAYBOOK.tmpl.md`, `TASK_BOARD.tmpl.md`, `RISK_REGISTER.tmpl.md`, `DECISION_LOG.tmpl.md`, `CHANGELOG.tmpl.md`, `PRIOR_WORK_REUSE.tmpl.md`

#### Prompt

```
You are an ML project manager. I will provide a requirements document, completed contracts, and blank management templates.

TEMPLATES TO FILL:
- IMPLEMENTATION_PLAYBOOK — Phase plan with gates, iteration loop, stop-ship checks
- TASK_BOARD — Task tracking with dependencies and critical path
- RISK_REGISTER — Risk table with detection tests and automation hooks
- DECISION_LOG — Seed with initial architectural decisions already made
- CHANGELOG — Initialize with the governance setup entry
- PRIOR_WORK_REUSE — Only if reusing prior project artifacts (otherwise mark as N/A)

For each template:
1. Fill all {{PLACEHOLDER}} values
2. For IMPLEMENTATION_PLAYBOOK: create one phase per experimental part, with concrete commands from SCRIPT_ENTRYPOINTS_SPEC
3. For TASK_BOARD: create tasks that map to playbook phases, with dependencies
4. For RISK_REGISTER: populate risks based on the "Risk-Relevant Requirements" from the requirements document
5. For DECISION_LOG: record any decisions already made during template customization
6. For CHANGELOG: record the initial governance setup as the first entry

RULES:
- Phase commands MUST match SCRIPT_ENTRYPOINTS_SPEC exactly.
- Risk sources MUST reference specific requirements by ID.
- Task dependencies MUST form a valid DAG (no circular dependencies).
- PRIOR_WORK_REUSE: only fill if the requirements specify prior work reuse. Otherwise, write: "Not applicable — this is a standalone project."

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste all completed contracts here]

[Paste each blank management template here]
```

---

### Stage 4e: Report Templates

#### Input
- Stage 2 output (requirements document)
- All previously completed contracts
- Blank `REPORT_ASSEMBLY_PLAN.tmpl.md`
- Blank `PRE_SUBMISSION_CHECKLIST.tmpl.md`

#### Prompt

```
You are a technical writing specialist for ML projects. I will provide a requirements document, completed contracts, and two blank report templates.

TEMPLATES TO FILL:
- REPORT_ASSEMBLY_PLAN — Section outline, page budget, hypothesis templates, pre-flight checklist
- PRE_SUBMISSION_CHECKLIST — Attribution, compliance, and delivery readiness audit

For each template:
1. Fill all {{PLACEHOLDER}} values
2. For REPORT_ASSEMBLY_PLAN:
   - Set page budget per section based on report constraints
   - Map each figure/table (from FIGURES_TABLES_CONTRACT) to its report section
   - Customize hypothesis templates with project-specific datasets and metrics
   - Set reference requirements based on the requirements document
3. For PRE_SUBMISSION_CHECKLIST:
   - Customize the repository hygiene section for your project's file structure
   - Set the delivery platform and repository details
   - Adapt the attribution section to your organization's policy

RULES:
- Page budgets MUST sum to ≤ the page limit specified in requirements.
- Figure/table mappings MUST match FIGURES_TABLES_CONTRACT IDs exactly.
- Hypothesis templates MUST use actual dataset names and metric names.
- Do NOT add checklist items not grounded in requirements.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste all completed contracts here]

TEMPLATE — REPORT_ASSEMBLY_PLAN:

[Paste blank template here]

TEMPLATE — PRE_SUBMISSION_CHECKLIST:

[Paste blank template here]
```

---

## Stage 5: Cross-Template Consistency Audit

### Goal
Verify that all filled templates are internally consistent: cross-references are valid, placeholder values match across documents, and the authority hierarchy is coherent.

### Input
- All completed templates from Stage 4

### Prompt

```
You are a quality assurance auditor for ML project governance documents. I will provide a complete set of filled governance templates. Your job is to audit them for cross-template consistency.

Check ALL of the following:

## 1. Placeholder Consistency
- Are {{PROJECT_NAME}}, {{DEFAULT_SEED}}, {{SEED_LIST}}, and other shared values identical across all templates?
- Are dataset names, file paths, and method names consistent?
- Are budget values consistent (especially cross-part constraints)?

## 2. Cross-Reference Validity
- Do section number references (e.g., "see DATA_CONTRACT §4") point to the correct sections?
- Do companion contract lists match bidirectionally? (If A references B, does B reference A?)
- Are figure/table IDs (F1, T1, etc.) consistent between FIGURES_TABLES_CONTRACT and REPORT_ASSEMBLY_PLAN?

## 3. Authority Hierarchy Coherence
- Is the authority hierarchy identical across all templates that define it?
- Are MUST/SHOULD designations consistent?
- Do Tier 1/2/3 document names match?

## 4. Script Consistency
- Do script names in IMPLEMENTATION_PLAYBOOK match SCRIPT_ENTRYPOINTS_SPEC?
- Do CLI flags referenced in playbook commands match the spec?
- Does the reproduction sequence match the phase plan?

## 5. Risk Coverage
- Does every "critical" requirement have a corresponding RISK_REGISTER entry?
- Do automation hooks reference existing scripts?

## 6. Completeness
- Are there any remaining {{PLACEHOLDER}} values or "[TODO: specify]" markers?
- Are there any empty sections that should have been filled?

OUTPUT FORMAT:
For each issue found:
- **Issue:** [Description]
- **Files affected:** [List]
- **Severity:** Critical / Warning / Info
- **Suggested fix:** [How to resolve]

If no issues are found in a category, state: "No issues found."

End with a summary: X critical issues, Y warnings, Z info items.

---

HERE ARE ALL COMPLETED TEMPLATES:

[Paste all completed templates here, clearly labeled]
```

### Expected Output
A consistency report with categorized issues and suggested fixes.

### Checkpoint
Before finalizing your governance setup:
- [ ] Zero critical issues
- [ ] All warnings reviewed and either fixed or accepted with documented rationale
- [ ] No remaining `{{PLACEHOLDER}}` or `[TODO: specify]` markers
- [ ] Cross-references validated

---

## Stage 6: Governance Audit

### Goal
Audit an existing project's governance documents against the framework to find gaps, stale references, and policy violations. Use this after initial setup to verify completeness, or periodically during the project to catch drift.

### Input
- All filled governance documents from the project's `docs/` directory
- The project's current codebase (or a summary of scripts, configs, and output directories)
- Optionally: recent git log showing CONTRACT_CHANGE commits

### Prompt

```
You are an ML governance auditor. I will provide a project's governance documents and codebase context. Your job is to perform a comprehensive audit and produce a findings report.

Perform ALL of the following audit checks:

## 1. Coverage Audit
For each governance template in the framework, check:
- Is there a corresponding filled document in the project?
- Are all sections populated (no empty placeholder tables, no "*(Fill in...)*" markers)?
- Are there any remaining {{PLACEHOLDER}} or [TODO] values?

Report: List of documents with coverage percentage (sections filled / total sections).

## 2. Staleness Audit
Check for governance documents that have drifted from the actual codebase:
- Do script names in SCRIPT_ENTRYPOINTS_SPEC match actual files in `scripts/`?
- Do data paths in DATA_CONTRACT match the actual `data/` directory layout?
- Do figure/table IDs in FIGURES_TABLES_CONTRACT match files in `outputs/figures/` and `outputs/tables/`?
- Does the budget config referenced in EXPERIMENT_CONTRACT exist and contain the expected keys?
- Do environment dependencies in ENVIRONMENT_CONTRACT match the actual environment file?

Report: For each stale item, state what the document says vs what the codebase shows.

## 3. CONTRACT_CHANGE Compliance
Check whether material changes were properly tracked:
- Are there code changes that should have triggered a CONTRACT_CHANGE but didn't?
- Does every CONTRACT_CHANGE commit have a corresponding CHANGELOG entry?
- Does every CHANGELOG entry with an ADR reference have a matching DECISION_LOG entry?

Report: List of suspected untracked changes and missing log entries.

## 4. Risk Register Effectiveness
- Are all High-severity risks in the RISK_REGISTER covered by an automation hook or manual check?
- Do the automation hook scripts actually exist?
- Are there risks that should be CLOSED but aren't (mitigation already implemented)?
- Are there new risks visible in the codebase that aren't registered?

Report: Risk coverage matrix with gaps highlighted.

## 5. Phase Gate Readiness
For the project's current phase:
- Which phase gate checks have passing evidence?
- Which checks are blocked or failing?
- What is the critical path to the next gate?

Report: Phase gate status dashboard.

## 6. Leakage & Integrity Spot-Check
Scan for common violations:
- Any `.fit()` or `.fit_transform()` calls on non-training data in preprocessing code
- Any test-split access outside the designated final eval script
- Any hardcoded budget values that bypass the config file
- Any missing `set_seed()` calls before experiment runs

Report: List of suspected violations with file paths and line numbers.

OUTPUT FORMAT:
For each finding:
- **Finding ID:** AUDIT-001, AUDIT-002, etc.
- **Category:** Coverage | Staleness | Compliance | Risk | Gate | Integrity
- **Severity:** Critical / Warning / Info
- **Description:** What was found
- **Evidence:** Specific file, line, or document reference
- **Recommended action:** How to fix it
- **Effort estimate:** Trivial / Small / Medium / Large

End with:
- Executive summary (1 paragraph)
- Counts: X critical, Y warnings, Z info
- Top 3 priority actions

---

HERE ARE THE GOVERNANCE DOCUMENTS:

[Paste all governance docs from your project's docs/ directory]

CODEBASE CONTEXT:

[Paste or describe: directory listing of scripts/, config files, output directory structure, and recent git log]
```

### Expected Output
A structured audit report with 20-50 findings, severity ratings, and prioritized remediation actions.

### Checkpoint
After receiving the audit report:
- [ ] All Critical findings have an assigned owner and target date
- [ ] No false positives (verify each Critical finding against actual codebase)
- [ ] Remediation plan created for Warning findings
- [ ] Info findings reviewed and accepted or promoted to Warning

---

## Stage 7: Targeted Patches (CONTRACT_CHANGE Workflow)

### Goal
When a mid-project change occurs (new dependency, budget adjustment, added method, schema change), generate the minimal set of edits across all affected governance documents. This ensures CONTRACT_CHANGE discipline is maintained without manually hunting through every template.

### Input
- Description of the change (what changed and why)
- All current governance documents
- The CHANGELOG and DECISION_LOG (for context on prior changes)

---

### Stage 7a: Impact Analysis

#### Prompt

```
You are an ML governance change analyst. A change has occurred in a project that is governed by a set of contracts and specifications. Your job is to identify every document, section, and cross-reference affected by this change.

THE CHANGE:
[Describe: what changed, why, and what the new value/state is]

ANALYSIS TASKS:

## 1. Direct Impact
Which governance documents directly reference the changed item?
For each:
- Document name
- Section number(s) affected
- Current value (quote the text)
- Required new value

## 2. Transitive Impact
Which documents cross-reference the directly affected documents?
For each:
- Document name
- Section that cross-references the affected document
- Whether the cross-reference text needs updating

## 3. Downstream Artifacts
What scripts, configs, or outputs are affected?
- Scripts that read the changed value
- Config files that contain the changed value
- Output schemas that may change
- Figures/tables that may need regeneration

## 4. Risk Assessment
- Does this change introduce new risks? (Propose RISK_REGISTER entries)
- Does this change close existing risks?
- Could this change break any phase gate checks?

## 5. Change Record Draft
Draft the required records:
- DECISION_LOG ADR entry (if architectural decision)
- CHANGELOG entry
- CONTRACT_CHANGE commit message

OUTPUT FORMAT:
A numbered list of required edits, ordered by dependency (edit X before Y if Y cross-references X).
Each edit should specify: file, section, old text (quoted), new text, and rationale.

---

HERE ARE THE CURRENT GOVERNANCE DOCUMENTS:

[Paste all governance docs]

RECENT CHANGELOG:

[Paste CHANGELOG.md]

RECENT DECISION LOG:

[Paste DECISION_LOG.md]
```

#### Expected Output
An ordered list of 5-30 edits with exact old/new text, plus draft CHANGELOG and DECISION_LOG entries.

---

### Stage 7b: Patch Generation

#### Input
- Stage 7a output (impact analysis)
- The specific governance documents that need editing

#### Prompt

```
You are an ML governance editor. I will provide an impact analysis describing required changes to governance documents, and the current text of each affected document. Your job is to produce the patched versions.

For EACH affected document:
1. Apply all edits from the impact analysis
2. Verify internal consistency after edits (section numbering, cross-references)
3. Output the complete patched document (not just diffs)

ALSO produce:
- A DECISION_LOG ADR entry for the change (if applicable)
- A CHANGELOG entry for the change
- A suggested commit message with the CONTRACT_CHANGE: prefix

RULES:
- Apply ONLY the edits specified in the impact analysis. Do not make additional changes.
- Preserve all formatting, section numbers, and structure.
- If an edit would break a cross-reference in a document NOT in the edit list, flag it as a warning.
- Verify that budget values, dataset names, seed lists, and method names remain consistent across all patched documents.

---

IMPACT ANALYSIS:

[Paste Stage 7a output here]

DOCUMENTS TO PATCH:

[Paste each affected document, clearly labeled]
```

#### Expected Output
Complete patched documents ready to commit, plus CHANGELOG and DECISION_LOG entries.

#### Checkpoint
After applying patches:
- [ ] All edits from the impact analysis are applied
- [ ] No new inconsistencies introduced (run Stage 5 or Stage 6 to verify)
- [ ] CHANGELOG entry accurately describes the change
- [ ] DECISION_LOG entry (if applicable) captures rationale and alternatives
- [ ] Commit message follows `CONTRACT_CHANGE:` convention

---

## Stage 8: Test Code Generation

### Goal
Generate pytest test code that programmatically validates governance compliance: leakage prevention, budget enforcement, schema validation, determinism, and artifact integrity. These tests turn governance rules into executable checks.

### Input
- All filled governance documents
- The project's script and source code structure
- The project's config files (budget config, environment file)

---

### Stage 8a: Leakage & Data Integrity Tests

#### Prompt

```
You are an ML test engineer specializing in data integrity. I will provide a project's DATA_CONTRACT and EXPERIMENT_CONTRACT. Your job is to generate pytest test code that validates every leakage prevention rule and data integrity invariant.

Generate a test module `tests/test_data_integrity.py` with these test functions:

## Split Integrity Tests
- test_split_no_overlap: For each dataset, verify train ∩ val = ∅, train ∩ test = ∅, val ∩ test = ∅
- test_split_full_coverage: len(train) + len(val) + len(test) == n_total
- test_split_valid_range: All indices in range(0, n_total)
- test_split_deterministic: Given the same seed, split is identical on re-generation
- test_split_hash_matches: split_hash matches recomputed value

## Leakage Prevention Tests
- test_fit_on_train_only: Verify that preprocessing pipeline's .fit() is called exclusively on training data
  - Strategy: Monkey-patch or wrap the scaler/encoder to record what data .fit() was called on
- test_no_test_access_outside_final_eval: Import each experiment script module and verify it does not load test indices
  - Strategy: Mock the data loader's allow_test parameter; verify ValueError is raised
- test_no_fit_transform_on_val_test: Verify .fit_transform() is never called on validation or test data

## Data Provenance Tests
- test_raw_data_hashes: Verify SHA-256 hashes of raw data files match recorded values
- test_eda_summaries_exist: Verify EDA summary JSON files exist for each dataset
- test_split_files_exist: Verify split JSON files exist at canonical paths

RULES:
- Use pytest fixtures for dataset loading and split loading
- Use parametrize decorators for multi-dataset tests
- Tests MUST be runnable with `pytest tests/test_data_integrity.py -v`
- Read actual values (dataset names, paths, seeds, hashes) from the governance documents — do NOT hardcode
- If a value must be read from a config file, show the config-reading code
- Include docstrings explaining what governance rule each test enforces
- Reference the specific contract section (e.g., "DATA_CONTRACT §3.3 invariant #1")

---

DATA_CONTRACT:

[Paste your filled DATA_CONTRACT.md]

EXPERIMENT_CONTRACT:

[Paste your filled EXPERIMENT_CONTRACT.md]

PROJECT STRUCTURE:

[Describe or paste: directory listing, key source files, data loader module path]
```

#### Expected Output
A complete `tests/test_data_integrity.py` file with 10-15 test functions, fixtures, and parametrization.

---

### Stage 8b: Budget & Compute Discipline Tests

#### Prompt

```
You are an ML test engineer specializing in experiment discipline. I will provide a project's EXPERIMENT_CONTRACT, METRICS_CONTRACT, and budget config. Your job is to generate pytest test code that validates budget enforcement, metric computation, and evaluation determinism.

Generate a test module `tests/test_experiment_discipline.py` with these test functions:

## Budget Enforcement Tests
- test_budget_config_complete: All required keys present in budget config file
- test_cross_part_budget_consistency: part3.grad_evals == part2.grad_evals (or equivalent cross-part constraints)
- test_no_hardcoded_budgets: Grep experiment scripts for hardcoded numeric budget values that should come from config
- test_summary_budget_within_limit: For each completed run, verify budget_used ≤ budget_allowed
- test_budget_matched_across_methods: Within each part and seed, all methods used the same budget (within tolerance)

## Metric Computation Tests
- test_metric_centralized: Verify all metric computations go through a single module (not ad-hoc calls)
- test_metric_function_signature: Verify sklearn/torch metric calls match the exact signatures specified in METRICS_CONTRACT
- test_sanity_check_results: Verify dummy baseline accuracy ≈ majority proportion; shuffled labels ≈ chance
- test_dispersion_reported: Verify summary outputs include median + IQR (not just single-seed means)

## Evaluation Determinism Tests
- test_eval_mode_set: Verify model.eval() is called before evaluation
- test_no_grad_context: Verify torch.no_grad() wraps evaluation blocks
- test_deterministic_seeding: Run the same experiment twice with the same seed; verify outputs are identical

## Output Schema Tests
- test_metrics_csv_schema: Verify metrics.csv has required columns per METRICS_CONTRACT §9
- test_summary_json_schema: Verify summary.json has required fields
- test_config_resolved_exists: Verify config_resolved.yaml is written for every run

RULES:
- Use pytest fixtures for loading budget config and run outputs
- Parametrize over datasets, methods, and seeds where applicable
- Read budget values and metric definitions from governance docs / config files — do NOT hardcode
- Include docstrings referencing the specific contract section each test enforces
- Tests should be independent and runnable in any order

---

EXPERIMENT_CONTRACT:

[Paste your filled EXPERIMENT_CONTRACT.md]

METRICS_CONTRACT:

[Paste your filled METRICS_CONTRACT.md]

BUDGET CONFIG:

[Paste your budget config YAML/JSON]

PROJECT STRUCTURE:

[Describe or paste: key experiment scripts, metric computation module, output directory structure]
```

#### Expected Output
A complete `tests/test_experiment_discipline.py` file with 12-18 test functions.

---

### Stage 8c: Artifact Integrity & Reproducibility Tests

#### Prompt

```
You are an ML test engineer specializing in artifact integrity. I will provide a project's ARTIFACT_MANIFEST_SPEC, SCRIPT_ENTRYPOINTS_SPEC, and ENVIRONMENT_CONTRACT. Your job is to generate pytest test code that validates artifact hashing, manifest completeness, and end-to-end reproducibility.

Generate a test module `tests/test_artifacts.py` with these test functions:

## Manifest Integrity Tests
- test_run_manifests_exist: Every run directory has a run_manifest.json
- test_run_manifest_hashes_match: For each file in run_manifest.json, recompute SHA-256 and verify match
- test_global_manifest_exists: outputs/artifact_manifest.json exists
- test_global_manifest_complete: Every run directory is represented in the global manifest
- test_no_orphan_files: No files in output directories that are not recorded in a manifest

## Figure & Table Tests
- test_required_figures_exist: All figure IDs from FIGURES_TABLES_CONTRACT have corresponding files
- test_required_tables_exist: All table IDs have corresponding files
- test_figure_hashes_match: Figure file hashes match the global manifest
- test_figure_format: Figures are in the required format (e.g., PDF vector)

## Script Interface Tests
- test_all_scripts_exist: Every script listed in SCRIPT_ENTRYPOINTS_SPEC exists at the specified path
- test_scripts_have_expected_flags: For each script, verify --help output includes required CLI flags
- test_verify_env_exits_zero: verify_env.sh exits 0 in the current environment
- test_exit_codes: Scripts return correct exit codes (0 for success, 1 for error, 2 for over-budget)

## Reproducibility Tests
- test_deterministic_artifact_generation: Run the artifact producer script twice; verify byte-identical outputs
- test_provenance_files_exist: versions.txt, git_commit_sha.txt, and run_log.json exist
- test_environment_matches_contract: Installed package versions match ENVIRONMENT_CONTRACT §4

RULES:
- Use subprocess.run for script interface tests
- Use hashlib for SHA-256 verification
- Parametrize over run directories and artifact IDs
- Tests should be safe to run on an already-completed project (no re-training)
- Include skip markers for tests that require completed experiment outputs
- Reference specific contract sections in docstrings

---

ARTIFACT_MANIFEST_SPEC:

[Paste your filled ARTIFACT_MANIFEST_SPEC.md]

SCRIPT_ENTRYPOINTS_SPEC:

[Paste your filled SCRIPT_ENTRYPOINTS_SPEC.md]

ENVIRONMENT_CONTRACT:

[Paste your filled ENVIRONMENT_CONTRACT.md]

PROJECT STRUCTURE:

[Describe or paste: scripts/ listing, outputs/ listing, environment file]
```

#### Expected Output
A complete `tests/test_artifacts.py` file with 14-18 test functions.

---

### Stage 8d: Pre-Delivery Smoke Tests

#### Prompt

```
You are an ML test engineer. I will provide a project's PRE_SUBMISSION_CHECKLIST and REPORT_ASSEMBLY_PLAN. Your job is to generate a pytest test module that automates every checkable item from the pre-delivery checklist.

Generate a test module `tests/test_pre_delivery.py` with these test functions:

## Repository Hygiene Tests
- test_no_prohibited_files: Verify no source materials, internal scaffolding, or draft files are tracked in git
- test_no_compiled_files: No .pyc, __pycache__, .ipynb_checkpoints in git
- test_no_large_files: No tracked files exceed 1MB (configurable threshold)
- test_no_credentials: No .env, credentials, API keys, or tokens tracked
- test_gitignore_covers_raw_data: data/raw/ is in .gitignore

## Report Content Tests (if report PDF is parseable)
- test_report_page_count: Report PDF is within page limit
- test_report_has_ai_statement: Report contains "AI Use" (or equivalent marker)
- test_report_has_references: Report contains a references section
- test_repro_document_exists: REPRO document exists

## Delivery Readiness Tests
- test_git_sha_matches_repro: The SHA recorded in REPRO matches the current HEAD (or a specified commit)
- test_all_pytest_pass: `pytest tests/ -v` exits 0
- test_readonly_link_not_placeholder: REPRO does not contain "XXXX-REPLACE-ME" or similar placeholder patterns

## Cross-Reference Validation
- test_no_remaining_placeholders: Grep all docs/ files for {{...}} — should return zero (or only template examples)
- test_no_todo_markers: Grep all docs/ files for [TODO — should return zero

RULES:
- Use subprocess for git commands and pytest invocations
- Use pathlib for file system checks
- Make thresholds configurable via pytest fixtures or conftest.py
- Include skip markers for checks that only apply at delivery time
- Tests should be non-destructive (read-only checks)
- Reference specific checklist items in docstrings

---

PRE_SUBMISSION_CHECKLIST:

[Paste your filled PRE_SUBMISSION_CHECKLIST.md]

REPORT_ASSEMBLY_PLAN:

[Paste your filled REPORT_ASSEMBLY_PLAN.md]

PROJECT STRUCTURE:

[Describe: docs/ listing, report file location, REPRO file location]
```

#### Expected Output
A complete `tests/test_pre_delivery.py` file with 12-15 test functions plus a `conftest.py` with shared fixtures.

---

### Stage 8 Checkpoint

After generating all test modules:
- [ ] All test files are syntactically valid (`python -m py_compile tests/test_*.py`)
- [ ] Tests reference actual project paths, config files, and dataset names (not template placeholders)
- [ ] No test fabricates expected values — all thresholds and counts come from governance docs or config
- [ ] Test docstrings trace to specific contract sections
- [ ] `pytest tests/ --collect-only` shows all expected test functions
- [ ] Tests that require completed outputs are properly marked with `@pytest.mark.skipif` or `@pytest.mark.slow`

---

## Tips for Best Results

1. **Provide complete source materials.** The more context you give the AI at each stage, the better the output. Don't summarize requirements — paste the full documents.

2. **Review at every checkpoint.** AI assistants can hallucinate metric values, dataset statistics, and deadline dates. Verify all factual claims against your source materials.

3. **Iterate within stages.** If Stage 1 output is incomplete, refine it before moving to Stage 2. Each stage assumes high-quality input from the previous one.

4. **Use extended thinking.** If your AI assistant supports extended thinking or chain-of-thought (e.g., Claude), enable it for Stages 2, 5, 6, and 7a where complex reasoning about requirements, consistency, and change impact is needed.

5. **Keep a "decisions made" log.** As you customize templates, note any judgment calls you make. These become seed entries for your DECISION_LOG.

6. **Don't skip Stage 5.** Cross-template consistency is where most governance failures hide. A Risk Register that references non-existent scripts or a playbook with wrong budget values will cause problems downstream.

7. **Run audits regularly.** Stage 6 isn't just for initial setup. Run it at every phase gate to catch governance drift before it compounds. Even a quick audit after a burst of coding can surface forgotten CONTRACT_CHANGEs.

8. **Use Stage 7 for every material change.** It's tempting to just edit one file when a budget changes. Stage 7a's impact analysis catches the 5 other files you'd forget to update.

9. **Generate tests early.** Run Stage 8 right after initial template customization. The generated tests become your automated phase gate checks and catch contract violations as you code, not at delivery time.

10. **Compile tests before trusting them.** AI-generated test code may have import errors or reference non-existent paths. Always run `python -m py_compile` and `pytest --collect-only` before relying on the test suite.
