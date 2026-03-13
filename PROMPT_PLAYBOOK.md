# Prompt Playbook

A guided prompt workflow for customizing the ML Governance Templates using an AI assistant.

---

## Overview

This playbook provides a series of copy-paste prompts that walk you from a raw problem statement through requirements extraction, template selection, full template customization, ongoing governance, and automated testing. Each stage builds on the previous one.

**Designed for:** Claude, ChatGPT, and other LLM assistants. Prompts are optimized for Claude's structured output capabilities but work with any capable model.

**How to use:**
1. **Initial setup:** Work through Stages 1 → 1b → 2 → 3 → 4a → 4b → 4c → 4c2 → 4d → 4d2 → 4e → 5 in order to go from problem statement to filled templates
2. **Specialized templates:** Use Stages 4f-4k as needed for hypothesis pre-registration, unsupervised evaluation, RL environments, adversarial evaluation, publication briefs, and academic integrity
3. **Source fidelity:** Run Stage 6 (RFP Traceability Audit) after every batch of template work — this is the hallucination firewall
4. **Ongoing governance:** Use Stage 7 (Governance Audit) periodically and Stage 8 (Patches) when changes occur
5. **Automation:** Use Stage 9 (Test Code) to generate executable compliance tests
6. **Quality assurance:** Use Stage 10 (Multi-Lens Audit) after report draft and before submission — this catches the issues that 7-14 manual audit cycles found in UL/RL projects
7. Copy each prompt, paste it into your AI assistant, and attach the required inputs
7. Review the output at each checkpoint before proceeding
8. Each stage is self-contained — you can restart any stage without losing prior work

**On hallucination risk:** AI assistants will confidently fabricate metric values, dataset statistics, budget numbers, and deadline dates. This playbook treats hallucination as a governance-level threat. Every prompt includes "do not invent" guardrails, and Stage 6 exists specifically to cross-check AI outputs against the original source documents. Do not skip it.

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

## Stage 1b: Authority Hierarchy Setup

### Goal
Establish the tiered authority hierarchy for the project before any template customization begins. This hierarchy determines which documents take precedence when conflicts arise, and is referenced by every governance template.

### Input
- Stage 1 output (structured brief)
- All source documents (RFP, specification, FAQ, clarifications, advisory notes)

### Prompt

```
You are an ML governance architect. I will provide a structured project brief and all source documents. Your job is to establish the authority hierarchy that governs all project decisions.

Produce a document with EXACTLY these sections:

## 1. Document Inventory
List every source document with:
- Document name
- Document type (specification, FAQ, email, advisory, etc.)
- Date / version
- Author / authority

## 2. Authority Tier Assignment
Assign each document to a tier:

| Tier | Role | Assigned Document(s) |
|------|------|---------------------|
| Tier 1 | Primary specification — highest authority, overrides everything | *(name the document)* |
| Tier 2 | Clarifications — supplements Tier 1, cannot override it | *(name the document(s))* |
| Tier 3 | Advisory — non-binding if inconsistent with Tier 1/2 | *(name the document(s))* |
| Contracts | Project governance documents (subordinate to all tiers above) | All governance templates |

## 3. Conflict Resolution Rules
For each pair of adjacent tiers, provide an example of how a conflict would be resolved:
- Tier 1 vs Tier 2 conflict → Tier 1 wins; example: ...
- Tier 2 vs Tier 3 conflict → Tier 2 wins; example: ...
- Tier 3 vs Contract conflict → Tier 3 wins; example: ...

## 4. Placeholder Values
Provide the exact strings to use for these placeholders across all governance templates:
- {{TIER1_DOC}} = ...
- {{TIER2_DOC}} = ...
- {{TIER3_DOC}} = ...

## 5. Authority Gaps
Flag any areas where no source document provides guidance. These become DECISION_LOG entries where the project team must make autonomous decisions.

RULES:
- Every document MUST be assigned to exactly one tier.
- Tier 1 MUST be a single document (or tightly coupled set with no internal conflicts).
- Do NOT invent documents or promote advisory materials to Tier 1/2 status.
- If only one source document exists, it is Tier 1 and Tiers 2-3 are "N/A".

---

HERE IS THE STRUCTURED BRIEF:

[Paste Stage 1 output here]

SOURCE DOCUMENTS:

[Paste or list all source documents with their full text]
```

### Expected Output
A 1-page authority hierarchy document with tier assignments, conflict resolution rules, and placeholder values for all templates.

### Checkpoint
Before proceeding to Stage 2, verify:
- [ ] Every source document is assigned to exactly one tier
- [ ] Tier 1 is the most authoritative document (not an FAQ or advisory)
- [ ] No document is assigned to a higher tier than warranted by its actual authority
- [ ] {{TIER1_DOC}}, {{TIER2_DOC}}, {{TIER3_DOC}} placeholder values are defined
- [ ] Authority gaps are flagged (not silently filled)

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
- [ ] Every MUST requirement traces to a specific source document with a direct quote or close paraphrase
- [ ] No invented requirements — everything is grounded in source materials
- [ ] No semantic reinterpretation of ambiguous language — ambiguities are flagged as open items, not silently resolved
- [ ] Acceptance criteria are testable (not vague)
- [ ] Risk-relevant requirements are flagged
- [ ] Spot-check 5 requirements against the original RFP: does the requirement accurately reflect the source, or has the AI subtly shifted the meaning?

**Hallucination warning:** This stage is the highest-risk for hallucination. The Stage 2 output becomes the single source of truth for Stages 3-5. If the AI misinterprets a requirement here, that error propagates through every template. Always verify the output against the original RFP before proceeding.

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

### Stage 4c2: Configuration & Test Architecture

#### Goal
Design the configuration hierarchy and test architecture for the project. These two templates govern how experiment parameters are managed as code and how governance rules are enforced through automated tests.

#### Input
- Stage 2 output (requirements document)
- Completed Environment, Data, Experiment, and Metrics contracts
- Blank `CONFIGURATION_SPEC.tmpl.md`
- Blank `TEST_ARCHITECTURE.tmpl.md`

#### Prompt

```
You are an ML infrastructure engineer specializing in configuration management and test design. I will provide a requirements document, completed contracts, and two blank templates to fill.

COMPLETED CONTRACTS (for cross-reference only — do not modify):
- ENVIRONMENT_CONTRACT (completed)
- DATA_CONTRACT (completed)
- EXPERIMENT_CONTRACT (completed)
- METRICS_CONTRACT (completed)

TEMPLATES TO FILL:
- CONFIGURATION_SPEC
- TEST_ARCHITECTURE

For CONFIGURATION_SPEC:
1. Fill all {{PLACEHOLDER}} values from the requirements document
2. Design the config hierarchy: base.yaml → dataset/{name}.yaml → component/{name}.yaml → CLI overrides
3. Define resolution rules: later layers override earlier; CLI overrides are highest priority
4. Specify config_resolved.yaml requirements: every run MUST write a fully resolved config snapshot before training starts
5. Define locked keys: budget values, seed lists, metric thresholds — keys that require CONTRACT_CHANGE to modify
6. If the project uses a scoring metric, fill the scoring metric as config pattern: metric name in config, test assertion verifying config matches code computation
7. Define config validation rules: required keys, type constraints, range constraints

For TEST_ARCHITECTURE:
1. Fill all {{PLACEHOLDER}} values from the requirements document
2. Select test categories from:
   - Leakage tests: split overlap, fit-on-train enforcement, test set barrier
   - Determinism tests: same seed → identical output, eval mode verification
   - Sanity tests: dummy baseline ≈ chance, shuffled labels ≈ chance
   - Integration tests: end-to-end pipeline on synthetic data
   - Artifact integrity tests: manifest hashes, figure existence, schema validation
3. For each test category: define specific test functions with docstrings referencing the contract section they enforce
4. Define synthetic fixture guidance: how to generate small, fast test fixtures that exercise the full pipeline without real data
5. Define marker-based skipping: @pytest.mark.slow for tests requiring trained models, @pytest.mark.gpu for GPU-only tests, @pytest.mark.skipif for tests requiring completed outputs

RULES:
- Config keys MUST trace to EXPERIMENT_CONTRACT budget definitions and METRICS_CONTRACT metric definitions. Do NOT invent config keys not grounded in these contracts.
- Locked keys MUST match the values in EXPERIMENT_CONTRACT (budgets, seeds) and METRICS_CONTRACT (thresholds). Do NOT allow locked keys to have default values that differ from the contracted values.
- Test categories MUST map to RISK_REGISTER automation hooks where applicable. If a risk has an automation hook, there MUST be a corresponding test.
- Do NOT invent test functions for features or rules not specified in the contracts. Every test MUST reference a specific contract section.
- Synthetic fixtures MUST be deterministic (seeded) and fast (< 5 seconds per test).
- If a value is not specified in the requirements or completed contracts, mark it as "[TODO: specify]" — do NOT guess.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste all completed contracts here]

TEMPLATE — CONFIGURATION_SPEC:

[Paste blank CONFIGURATION_SPEC.tmpl.md here]

TEMPLATE — TEST_ARCHITECTURE:

[Paste blank TEST_ARCHITECTURE.tmpl.md here]
```

#### Expected Output
Two completed templates: a configuration spec with hierarchy design, resolution rules, and locked keys; and a test architecture with categorized test functions, fixtures, and markers.

#### Checkpoint
Before proceeding to Stage 4d, verify:
- [ ] Config hierarchy layers are defined with clear precedence rules
- [ ] Every locked key traces to a specific EXPERIMENT_CONTRACT or METRICS_CONTRACT value
- [ ] config_resolved.yaml is required before training starts (not after)
- [ ] Every test category maps to at least one contract section
- [ ] Synthetic fixtures are defined with deterministic seeds
- [ ] Marker-based skipping is defined for slow, GPU, and output-dependent tests
- [ ] No invented config keys or test functions — everything traces to contracts

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
- Do NOT invent phase gates, task descriptions, timelines, or risk scenarios. All phases MUST derive from EXPERIMENT_CONTRACT and SCRIPT_ENTRYPOINTS_SPEC. All tasks MUST tie to concrete requirements. All risks MUST trace to specific requirement IDs.
- Phase commands MUST match SCRIPT_ENTRYPOINTS_SPEC exactly.
- Risk sources MUST reference specific requirements by ID.
- Task dependencies MUST form a valid DAG (no circular dependencies).
- If a value is not specified in the requirements or completed contracts, mark it as "[TODO: specify]" — do NOT guess.
- PRIOR_WORK_REUSE: only fill if the requirements specify prior work reuse. Otherwise, write: "Not applicable — this is a standalone project."

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste all completed contracts here]

[Paste each blank management template here]
```

---

### Stage 4d2: AI Collaboration Setup

#### Goal
Define the human-AI collaboration boundaries for the project. This template governs how AI tools are used, what they may produce, and how their contributions are disclosed.

#### Input
- Stage 2 output (requirements document)
- Any AI usage policy from Tier 1/2 authority documents
- Completed Data Contract (for data privacy alignment)
- Blank `AI_DIVISION_OF_LABOR.tmpl.md`

#### Prompt

```
You are an AI governance specialist for ML projects. I will provide a requirements document, any AI usage policies from the project's authority documents, the completed Data Contract (for privacy alignment), and a blank AI Division of Labor template. Your job is to define the human-AI collaboration boundaries.

COMPLETED CONTRACTS (for cross-reference only — do not modify):
- DATA_CONTRACT (completed) — needed for data privacy alignment

TEMPLATE TO FILL:
- AI_DIVISION_OF_LABOR

Fill the template by completing these sections:

1. **Tool Roster (§3):**
   - List every AI tool that will be used in the project
   - For each tool: name, primary role, permitted output types, leakage risk level
   - If the requirements or authority documents restrict AI tool usage, reflect those restrictions here

2. **Per-Tool Governance (§4):**
   - For each tool, define MUST and MUST NOT rules
   - Define acceptable output formats (e.g., "checklists and code only," "redlines on existing text only")
   - MUST rules should include: review all generated code before committing, verify any factual claims against primary sources
   - MUST NOT rules should include: produce standalone report paragraphs for Results/Discussion/Conclusion

3. **Anti-Ghostwriting Firewall (§2.1):**
   - Activate with project-specific boundaries
   - Define which report sections are human-write-only (at minimum: Results, Discussion, Conclusion)
   - Define permitted AI output formats (checklists, claim templates, code, outlines, redline edits)
   - Define prohibited AI output formats (paste-ready interpretive paragraphs, unsupported claims)

4. **Citation Chain Rule (§2.2):**
   - Configure based on the project's citation policy (from requirements or Tier 1/2 docs)
   - Rule: AI tools are NOT citable sources; citations point to primary publications or experimental artifacts only

5. **Information Flow Controls (§6):**
   - Fill the "What Each Tool May See" matrix for every tool in the roster
   - Define cross-tool isolation rules
   - If the project uses multiple AI tools, define the human integration point explicitly

6. **AI Use Statement Template (§7):**
   - Customize the disclosure template with project-specific tool names and roles
   - Ensure the format matches any requirements from Tier 1/2 authority documents

RULES:
- The data privacy policy (§2.3) MUST match DATA_CONTRACT §4 leakage prevention rules. Do NOT allow uploads that would violate data handling constraints.
- The test set barrier (§2.4) MUST match the leakage prevention rules in DATA_CONTRACT and EXPERIMENT_CONTRACT. If those contracts prohibit test set access before final evaluation, this template MUST enforce the same barrier for all AI tool interactions.
- If Tier 1/2 documents specify AI usage restrictions (e.g., "AI may not write report prose," "must disclose all AI usage"), those restrictions take precedence over template defaults.
- Do NOT invent AI tools the project will not use. Only list tools that are actually planned.
- Do NOT relax restrictions beyond what Tier 1/2 documents permit. When in doubt, be more restrictive.
- If the requirements do not mention AI usage at all, apply conservative defaults: code assistance and debugging permitted, report prose prohibited, full disclosure required.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

AI USAGE POLICY (from Tier 1/2 documents, if any):

[Paste any AI usage policy text, or state "No explicit AI policy in authority documents"]

COMPLETED DATA_CONTRACT:

[Paste completed Data Contract here]

TEMPLATE — AI_DIVISION_OF_LABOR:

[Paste blank AI_DIVISION_OF_LABOR.tmpl.md here]
```

#### Expected Output
A completed AI Division of Labor contract with tool roster, per-tool governance rules, activated anti-ghostwriting firewall, and AI Use Statement template.

#### Checkpoint
Before proceeding to Stage 4e, verify:
- [ ] Every AI tool actually planned for the project is listed (no invented tools)
- [ ] Per-tool MUST NOT rules include anti-ghostwriting constraints
- [ ] Data privacy policy aligns with DATA_CONTRACT §4 (no contradictions)
- [ ] Test set barrier aligns with leakage prevention rules
- [ ] Citation chain rule matches the project's citation policy
- [ ] Information flow matrix is filled for every tool
- [ ] AI Use Statement template is customized with actual tool names
- [ ] If Tier 1/2 docs restrict AI usage, those restrictions are reflected (not relaxed)

---

### Stage 4e: Report & Delivery Templates

#### Goal
Fill all four report and delivery templates: the report assembly plan, reproducibility specification, pre-submission checklist, and execution manifest. These templates govern how the project's results are assembled, reproduced, verified, and traced.

#### Input
- Stage 2 output (requirements document)
- All previously completed contracts (especially FIGURES_TABLES_CONTRACT, SCRIPT_ENTRYPOINTS_SPEC, ARTIFACT_MANIFEST_SPEC, EXPERIMENT_CONTRACT, METRICS_CONTRACT)
- Blank `REPORT_ASSEMBLY_PLAN.tmpl.md`
- Blank `REPRODUCIBILITY_SPEC.tmpl.md`
- Blank `EXECUTION_MANIFEST.tmpl.md`
- Blank `PRE_SUBMISSION_CHECKLIST.tmpl.md`

#### Prompt

```
You are a technical writing and reproducibility specialist for ML projects. I will provide a requirements document, completed contracts, and four blank report/delivery templates. Your job is to fill all four templates to produce a complete delivery governance suite.

COMPLETED CONTRACTS (for cross-reference only — do not modify):
- All previously completed contracts

TEMPLATES TO FILL:
- REPORT_ASSEMBLY_PLAN
- REPRODUCIBILITY_SPEC
- EXECUTION_MANIFEST
- PRE_SUBMISSION_CHECKLIST

For each template:

## REPORT_ASSEMBLY_PLAN:
1. Fill all {{PLACEHOLDER}} values
2. Set page budget per section based on report constraints from requirements
3. Map each figure/table (from FIGURES_TABLES_CONTRACT) to its report section
4. Customize hypothesis templates with project-specific datasets and metrics
5. Set reference requirements based on the requirements document

## REPRODUCIBILITY_SPEC:
1. Fill all {{PLACEHOLDER}} values
2. Environment setup commands: exact sequence to recreate the environment (clone, create env, install deps, verify)
3. Data acquisition: commands to download/prepare raw data, verify hashes, generate splits
4. Per-phase reproduction sequence: for each experiment phase in IMPLEMENTATION_PLAYBOOK, list the exact commands from SCRIPT_ENTRYPOINTS_SPEC in execution order
5. Verification steps: after each phase, specify the verification command and expected outcome (e.g., "pytest tests/test_data_integrity.py exits 0")
6. Hardware note: document any hardware-specific considerations (GPU requirements, expected runtime, memory, tolerance for non-determinism across hardware)

## EXECUTION_MANIFEST:
1. Fill all {{PLACEHOLDER}} values
2. Methods summary table (§3.1): auto-generated experiment matrix showing what was actually run — parts, datasets, methods, seeds, budget type, budget value, runs completed
3. Results index (§4): per-run results table with run IDs from ARTIFACT_MANIFEST_SPEC, seed-aggregated results with median + IQR, final evaluation results
4. Figure registry (§5): every figure from FIGURES_TABLES_CONTRACT with figure ID, source data, producer script, SHA-256 placeholder, and target report section
5. Table registry (§6): same format for tables
6. Claim-to-evidence traceability (§7): for each anticipated quantitative claim, map to the specific figure, table, or results index entry that provides the evidence
7. Baseline reference (§8): define comparison baselines with source and metric values

## PRE_SUBMISSION_CHECKLIST:
1. Fill all {{PLACEHOLDER}} values
2. Customize the repository hygiene section for your project's file structure
3. Set the delivery platform and repository details
4. Adapt the attribution section to your organization's policy

RULES:
- Page budgets MUST sum to ≤ the page limit specified in requirements.
- Figure/table mappings MUST match FIGURES_TABLES_CONTRACT IDs exactly.
- Hypothesis templates MUST use actual dataset names and metric names.
- Reproduction commands MUST match SCRIPT_ENTRYPOINTS_SPEC exactly — same script names, same CLI flags, same argument order. Do NOT invent commands not defined in the script spec.
- Results index run IDs MUST use the run ID format from ARTIFACT_MANIFEST_SPEC. Do NOT invent run ID formats.
- Claim-to-evidence entries MUST reference specific figure IDs (F1, F2, ...) or table IDs (T1, T2, ...) from FIGURES_TABLES_CONTRACT, or specific results index sections (§4.1, §4.2, §4.3). Do NOT reference evidence sources that don't exist in other contracts.
- Baseline metric values: if known from prior work or requirements, fill them in. If unknown, mark as "[TODO: fill after baseline runs]" — do NOT invent baseline numbers.
- Do NOT add checklist items not grounded in requirements.
- Do NOT invent verification commands, environment setup steps, or hardware specs. Derive everything from completed contracts or mark as "[TODO: specify]".

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste all completed contracts here]

TEMPLATE — REPORT_ASSEMBLY_PLAN:

[Paste blank REPORT_ASSEMBLY_PLAN.tmpl.md here]

TEMPLATE — REPRODUCIBILITY_SPEC:

[Paste blank REPRODUCIBILITY_SPEC.tmpl.md here]

TEMPLATE — EXECUTION_MANIFEST:

[Paste blank EXECUTION_MANIFEST.tmpl.md here]

TEMPLATE — PRE_SUBMISSION_CHECKLIST:

[Paste blank PRE_SUBMISSION_CHECKLIST.tmpl.md here]
```

#### Expected Output
Four completed report/delivery templates: a report assembly plan with page budgets and figure mappings, a reproducibility spec with exact commands, an execution manifest with results index and traceability, and a pre-submission checklist.

#### Checkpoint
Before proceeding to specialized stages (4f-4k), verify:
- [ ] Page budgets sum to ≤ page limit
- [ ] Every figure/table ID in REPORT_ASSEMBLY_PLAN matches FIGURES_TABLES_CONTRACT
- [ ] Reproduction commands match SCRIPT_ENTRYPOINTS_SPEC (script names, flags, arguments)
- [ ] Environment setup produces the same environment as ENVIRONMENT_CONTRACT
- [ ] Results index run IDs match ARTIFACT_MANIFEST_SPEC format
- [ ] Claim-to-evidence table references only existing figure/table IDs or results sections
- [ ] Baseline values are either sourced from requirements/prior work or marked "[TODO]"
- [ ] No invented commands, run IDs, or metric values

---

### Stage 4f: Hypothesis Pre-Registration

#### Input
- Stage 2 output (requirements document)
- Completed Metrics and Data contracts
- Blank `HYPOTHESIS_CONTRACT.tmpl.md`
- *(Optional)* Blank `LEAN_HYPOTHESIS.tmpl.md` (if using publishing profile)

#### Prompt

```
You are a research methodology specialist. I will provide a requirements document, completed contracts, and blank hypothesis templates. Your job is to define pre-registered hypotheses with temporal gating.

TEMPLATES TO FILL:
- HYPOTHESIS_CONTRACT — Technical hypotheses with prediction, mechanism, and evidence format
- LEAN_HYPOTHESIS (optional) — Strategic hypothesis framing with kill criteria

For HYPOTHESIS_CONTRACT:
1. Define one hypothesis per experimental question
2. Each hypothesis MUST have: prediction (specific, measurable), mechanism (why you expect this), evidence required (what data would confirm/refute)
3. Set temporal gate: hypotheses MUST be registered BEFORE any experiment runs
4. Define the statistical test or comparison method for each hypothesis

For LEAN_HYPOTHESIS (if applicable):
1. Define the customer-problem hypothesis (who benefits, what problem, why it matters)
2. Fill the assumptions register (each assumption with type and test method)
3. Define kill criteria with specific thresholds and actions
4. Design the Minimum Viable Experiment (MVE) — smallest experiment testing the core hypothesis
5. Set resource allocation priorities for experiment parts

RULES:
- Hypotheses MUST be falsifiable. If you can't specify what would refute it, it's not a hypothesis.
- Do NOT define hypotheses that simply restate the experimental procedure.
- Predictions MUST reference specific metrics from METRICS_CONTRACT.
- Kill criteria thresholds MUST be concrete numbers, not qualitative ("too high").
- If the requirements don't specify hypotheses, derive them from the experimental questions — but flag them as "[DERIVED — not in source requirements]".

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste completed Metrics and Data contracts here]

TEMPLATE — HYPOTHESIS_CONTRACT:

[Paste blank template here]

TEMPLATE — LEAN_HYPOTHESIS (if using):

[Paste blank template here]
```

#### Expected Output
Completed hypothesis contracts with 2-6 pre-registered hypotheses and (optionally) kill criteria and MVE definition.

---

### Stage 4g: Unsupervised Evaluation Selection

#### Input
- Stage 2 output (requirements document)
- Completed Data and Metrics contracts
- `METRICS_CONTRACT.tmpl.md` Appendix B (unsupervised evaluation menu)
- Completed Figures/Tables contract

#### Prompt

```
You are an unsupervised ML evaluation specialist. I will provide a requirements document and completed contracts for a clustering, dimensionality reduction, or density estimation project. Your job is to activate and customize the unsupervised-specific appendices.

TASKS:
1. **METRICS_CONTRACT Appendix B activation:**
   - Select internal validation metrics (Silhouette, Calinski-Harabasz, Davies-Bouldin, etc.)
   - Select external validation metrics if labels are available (ARI, NMI, etc.)
   - Define stability metrics (Jaccard across seeds, cluster membership consistency)
   - Set sanity baselines (random assignment expected scores)

2. **FIGURES_TABLES_CONTRACT §8.5 activation:**
   - Define elbow plot specifications (metric vs K, with knee annotation)
   - Define silhouette plot specifications (per-cluster silhouette coefficients)
   - Define cluster visualization (PCA/t-SNE/UMAP with cluster coloring)
   - Define cluster profile visualizations (radar charts, parallel coordinates)

3. **Cross-reference consistency:**
   - Verify metric names in Appendix B match METRICS_CONTRACT §2 definitions
   - Verify figure specifications reference correct metric names
   - Verify K-selection methodology is consistent across all documents

RULES:
- Select metrics appropriate to the clustering method (e.g., Silhouette is not ideal for DBSCAN with noise points).
- Define K-selection methodology explicitly (elbow + silhouette gap, or other method).
- External validation metrics ONLY if ground-truth labels are available — do NOT assume labels exist.
- All metric thresholds must be justified (e.g., "Silhouette > 0.5 indicates reasonable structure").

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste completed Data, Metrics, and Figures/Tables contracts here]
```

#### Expected Output
Activated unsupervised appendices with metric selections, visualization specs, and K-selection methodology.

---

### Stage 4h: RL Environment Design

#### Input
- Stage 2 output (requirements document)
- Completed Environment Contract
- Blank `ENVIRONMENT_SPEC.tmpl.md`
- Completed Metrics Contract (with Appendix C activated for RL policy evaluation)

#### Prompt

```
You are an RL environment specialist. I will provide a requirements document, a completed Environment Contract, and a blank RL Environment Spec template. Your job is to fully specify the MDP and environment configuration.

TEMPLATE TO FILL:
- ENVIRONMENT_SPEC — Full MDP definition with state/action/transition/reward/discount/termination

For each environment in the project:
1. **MDP Definition:**
   - State space: dimensions, ranges, meaning of each component
   - Action space: discrete/continuous, dimensions, meaning of each action
   - Transition dynamics: deterministic/stochastic, reference to simulator
   - Reward function: formula AND tabular format for clarity
   - Discount factor: value and justification
   - Termination conditions: distinguish termination (failure) vs truncation (time limit)

2. **Environment Configuration:**
   - List all configurable parameters with defaults and valid ranges
   - Define wrapper stack (observation wrappers, reward shaping, action clipping)
   - Lock environment version to specific library release

3. **Reproducibility:**
   - Seeding protocol (where and how seeds are applied)
   - Version locking (exact library + commit hash if custom)
   - Determinism verification command

4. **Visualization Requirements:**
   - State space diagram
   - Policy overlay visualization
   - Value/reward heatmaps (if applicable)

5. **Reward Sensitivity Analysis:**
   - Define scale sensitivity protocol
   - Define discount sweep range
   - Define reward shaping ablation (if applicable)

RULES:
- Every state dimension MUST have a physical meaning and unit (if applicable).
- Reward function MUST be specified both as a formula and as a lookup table (for discrete cases).
- Termination vs truncation MUST be explicitly distinguished — this affects bootstrapping in policy gradient methods.
- Custom environments MUST include version-locking to a specific git SHA.
- Do NOT use environment wrappers without documenting their effect on the MDP.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED ENVIRONMENT_CONTRACT:

[Paste completed Environment Contract here]

TEMPLATE — ENVIRONMENT_SPEC:

[Paste blank template here]
```

#### Expected Output
A fully specified RL environment document with MDP definition, configuration, seeding protocol, and visualization requirements.

---

### Stage 4i: Adversarial Evaluation Setup

#### Input
- Stage 2 output (requirements document)
- Completed Experiment, Metrics, and Data contracts
- Blank `ADVERSARIAL_EVALUATION.tmpl.md`

#### Prompt

```
You are an adversarial ML evaluation specialist. I will provide a requirements document, completed contracts, and a blank adversarial evaluation template. Your job is to define the threat model and evaluation protocol.

TEMPLATE TO FILL:
- ADVERSARIAL_EVALUATION — Threat model, perturbation types, robustness metrics, evaluation protocol

1. **Threat Model Definition:**
   - Attacker knowledge level (white-box, black-box, grey-box)
   - Attacker goal (targeted, untargeted, availability)
   - Perturbation norm (L∞, L2, L0, semantic)
   - Perturbation budget (ε value and justification)
   - Attack surface (input, training data, reward, environment)

2. **Perturbation Type Selection:**
   - Activate relevant sections: input evasion (§3.1), data poisoning (§3.2), reward perturbation (§3.3, RL only), environment modification (§3.4, RL only)
   - For each active section: select attack methods, define parameters, set iteration counts

3. **Robustness Metrics:**
   - Define clean accuracy, robust accuracy, attack success rate, accuracy drop
   - Set certified radius (if using certified defenses)
   - Define robustness-accuracy trade-off acceptance threshold

4. **Evaluation Protocol:**
   - Define adaptive attack requirement (attacker adapts to defense)
   - Define baseline comparison (undefended, random perturbation, strongest known attack)
   - Set budget for adversarial evaluation compute

RULES:
- Threat model MUST be defined BEFORE selecting attack methods.
- Perturbation budget (ε) MUST be justified with domain reasoning (e.g., "L∞ = 8/255 is standard for CIFAR-10").
- Do NOT evaluate only weak attacks — include at least one adaptive attack.
- RL-specific sections (§3.3, §3.4) should only be activated for RL projects.
- Report adversarial results separately from clean results — never merge them.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste completed Experiment, Metrics, and Data contracts here]

TEMPLATE — ADVERSARIAL_EVALUATION:

[Paste blank template here]
```

#### Expected Output
A completed adversarial evaluation spec with threat model, attack selection, robustness metrics, and evaluation protocol.

---

### Stage 4j: Publication Brief Drafting

#### Input
- Stage 2 output (requirements document)
- Completed Report Assembly Plan and Hypothesis Contract
- Blank `PUBLICATION_BRIEF.tmpl.md`

#### Prompt

```
You are a scientific communication strategist. I will provide a requirements document, completed contracts, and a blank publication brief template. Your job is to define the communication strategy for the project deliverables.

TEMPLATE TO FILL:
- PUBLICATION_BRIEF — Target reader, takeaway, demonstration, anti-claims, portfolio alignment, message governance

1. **Target Reader & Takeaway:**
   - Define the primary reader profile (who, what they evaluate, how much time they have, technical level)
   - Craft a one-sentence takeaway — the single thought the reader should have after reading
   - Rule: every report section must contribute to this takeaway

2. **Primary Demonstration:**
   - Fill the competency-evidence table: what the project proves, how, with what evidence
   - Fill the "What This Project Does NOT Prove" table — explicit limitations to prevent overclaiming

3. **Anti-Claims:**
   - Define statements the report MUST NOT make (unbounded generalizations, proof claims, novelty claims)
   - For each anti-claim, provide the acceptable alternative phrasing
   - Define hedging requirements for comparative claims

4. **Portfolio Alignment:**
   - Place this project in the author's broader body of work
   - Define the skill narrative (what growth this project demonstrates)
   - Identify transferable artifacts with value beyond the immediate deliverable

5. **Message Governance:**
   - Define 3-5 key messages in priority order with supporting evidence
   - Map each report section to the key messages it supports
   - Set page budgets per section

RULES:
- The one-sentence takeaway MUST be achievable given the project scope — do not overpromise.
- Anti-claims are based on the project's actual limitations, not generic disclaimers.
- Every key message MUST have specific artifact evidence (figure ID, table ID, or metric).
- Page budgets MUST sum to ≤ the page limit from requirements.
- Do NOT add portfolio context that is speculative — only include confirmed career/educational goals.

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste completed Report Assembly Plan and Hypothesis Contract here]

TEMPLATE — PUBLICATION_BRIEF:

[Paste blank template here]
```

#### Expected Output
A completed publication brief with reader profile, anti-claims, message-to-section mapping, and portfolio alignment.

---

### Stage 4k: Academic Integrity Verification

#### Input
- Stage 2 output (requirements document)
- Completed AI Division of Labor and Prior Work Reuse contracts
- Blank `ACADEMIC_INTEGRITY_FIREWALL.tmpl.md`

#### Prompt

```
You are an academic integrity compliance specialist. I will provide a requirements document, completed contracts, and a blank integrity firewall template. Your job is to define the boundaries of acceptable content reuse, collaboration, and AI assistance.

TEMPLATE TO FILL:
- ACADEMIC_INTEGRITY_FIREWALL — Three walls, transferable/prohibited lists, verification commands

1. **Three Walls:**
   - Data Wall: Classify every data artifact as transferable (with conditions) or prohibited
   - Code Wall: Classify every code source (prior project, open source, AI-generated, classmate)
   - Content Wall: Classify every content type (prose, figures, analysis, AI text)

2. **Transferable vs Prohibited Lists:**
   - For each transferable artifact: specify the required documentation (provenance, disclosure, citation)
   - For each prohibited artifact: explain why and state the consequence

3. **Verification Commands:**
   - Data provenance check (hash verification of reused data)
   - Code provenance check (vendor snapshot integrity)
   - Content originality check (self-plagiarism detection)
   - AI usage verification (AI Use Statement exists and matches AI_DIVISION_OF_LABOR)

4. **AI Tool Boundaries:**
   - Summarize the AI tool usage rules from AI_DIVISION_OF_LABOR
   - Define the AI Use Statement format for the report
   - Ensure consistency between this firewall and the AI Division of Labor contract

5. **Pre-Submission Checklist:**
   - Customize the 10-item integrity checklist for the specific project
   - Add any institution-specific requirements from {{HONOR_CODE_REF}}

RULES:
- Wall classifications MUST be conservative — when in doubt, classify as prohibited.
- Verification commands MUST be executable (not pseudocode).
- If no prior work reuse exists, state explicitly: "No prior work reuse — Wall 1 and Wall 2 prior-project sections are N/A."
- AI boundaries MUST match AI_DIVISION_OF_LABOR exactly — no unilateral relaxation.
- Honor code reference MUST be a specific policy document, not a generic "follow your institution's rules."

---

REQUIREMENTS DOCUMENT:

[Paste Stage 2 output here]

COMPLETED CONTRACTS:

[Paste completed AI Division of Labor and Prior Work Reuse contracts here]

TEMPLATE — ACADEMIC_INTEGRITY_FIREWALL:

[Paste blank template here]
```

#### Expected Output
A completed academic integrity firewall with wall classifications, verification commands, and pre-submission checklist.

#### Checkpoint
After completing all specialized stages (4f-4k):
- [ ] All activated templates are consistent with the core templates from Stages 4a-4e
- [ ] Hypothesis predictions reference metrics from METRICS_CONTRACT
- [ ] Kill criteria reference budgets from EXPERIMENT_CONTRACT
- [ ] Anti-claims reference actual project limitations
- [ ] Verification commands are executable (not pseudocode)
- [ ] No conflicts between ACADEMIC_INTEGRITY_FIREWALL and AI_DIVISION_OF_LABOR

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

## Stage 6: RFP Traceability Audit

### Goal
Cross-check AI-generated governance documents against the original source materials (RFP, project specification, SOW, or assignment) line-by-line. This is the hallucination firewall — it catches cases where the AI subtly shifted a requirement's meaning, invented a constraint, or dropped a critical detail during Stages 1-4.

**When to run:**
- After completing Stages 1-5 (before committing governance docs)
- After every Stage 8 patch cycle (to verify patches didn't introduce drift)
- At every phase gate (to verify ongoing alignment)
- Whenever you suspect an AI output "sounds right but might not be"

### Input
- The **original source documents** (RFP, project specification, SOW — the raw, unprocessed Tier 1/2 authority)
- The Stage 2 requirements document
- All filled governance templates from Stage 4

### Prompt

```
You are an independent verification auditor. Your SOLE job is to check whether a set of project governance documents accurately reflect the original source materials. You are looking for hallucinations, semantic drift, and silent reinterpretations.

I will provide:
1. ORIGINAL SOURCE MATERIALS — the raw, authoritative documents (RFP, project specification, SOW, etc.)
2. REQUIREMENTS DOCUMENT — the AI-extracted requirements from Stage 2
3. FILLED GOVERNANCE TEMPLATES — the customized project governance documents

Perform ALL of the following checks:

## 1. Requirements Fidelity (Stage 2 vs Original)
For EVERY MUST requirement in the requirements document:
- Find the specific sentence/paragraph in the original source that justifies it
- Quote both the original text and the requirement text side by side
- Flag any semantic differences: additions, omissions, reinterpretations, or scope changes
- Flag any MUST requirement that has NO corresponding text in the original (potential hallucination)

Severity:
- **HALLUCINATION**: Requirement exists in Stage 2 output but has NO basis in the original source
- **DRIFT**: Requirement exists but the meaning has been subtly shifted
- **OMISSION**: Original source states a requirement that is missing from Stage 2 output
- **ACCURATE**: Requirement faithfully reflects the original

## 2. Numeric Value Verification
For EVERY concrete number in the governance documents (budgets, seeds, thresholds, page limits, feature counts, dataset sizes, split ratios, deadlines):
- Trace it to the original source document
- If the number is not in the original source, flag it as UNGROUNDED
- If the number is marked as "[TODO: specify]", that's acceptable
- If the number was invented by the AI without a source, flag as HALLUCINATION

## 3. Constraint Completeness
- List every constraint, rule, or requirement from the original source
- For each, verify it appears in at least one governance document
- Flag any original constraint that is not represented anywhere (OMISSION)

## 4. Authority Hierarchy Accuracy
- Verify the Tier 1/2/3 document mapping matches what the original source materials actually are
- Check that nothing has been promoted (e.g., advisory guidance treated as Tier 1) or demoted (e.g., mandatory requirement treated as SHOULD)

## 5. Scope Creep Check
- Flag any governance document content that goes beyond what the original source requires
- This includes: extra deliverables, additional methods, invented evaluation criteria, or constraints the AI added "for best practice" without marking them as SHOULD
- Scope creep is not always wrong, but it MUST be flagged and distinguished from source requirements

OUTPUT FORMAT:
For each finding:
- **ID:** RFP-001, RFP-002, etc.
- **Type:** HALLUCINATION | DRIFT | OMISSION | UNGROUNDED | SCOPE_CREEP | ACCURATE
- **Severity:** Critical (hallucination/omission of MUST) / Warning (drift/scope creep) / Info (minor)
- **Original text:** [Direct quote from source, with document name and location]
- **Governance text:** [What the governance document says]
- **Gap:** [Specific discrepancy]
- **Recommended fix:** [How to correct it]

End with:
- **Fidelity score:** X of Y requirements verified as ACCURATE
- **Hallucination count:** N items with no source basis
- **Drift count:** N items with shifted meaning
- **Omission count:** N source requirements not represented
- Summary: Is the governance suite safe to use, or does it need remediation?

---

ORIGINAL SOURCE MATERIALS:

[Paste the raw RFP, project specification, SOW, or assignment — exactly as received, unedited]

REQUIREMENTS DOCUMENT (Stage 2 output):

[Paste the AI-generated requirements document]

FILLED GOVERNANCE TEMPLATES:

[Paste all filled templates from docs/]
```

### Expected Output
A traceability report with every requirement checked against the source, a fidelity score, and hallucination/drift/omission counts.

### Checkpoint
Before proceeding (or before committing governance docs):
- [ ] Zero HALLUCINATION findings (any hallucinated content must be removed or replaced with source-grounded values)
- [ ] All DRIFT findings reviewed — either corrected to match source or accepted with explicit rationale in DECISION_LOG
- [ ] All OMISSION findings addressed — either added to governance docs or explicitly scoped out with justification
- [ ] UNGROUNDED numeric values either traced to source or changed to "[TODO: specify]"
- [ ] Fidelity score ≥ 90% (if below, re-run Stages 2-4 for affected requirements)
- [ ] SCOPE_CREEP items reviewed — acceptable additions marked as SHOULD (not MUST)

**Iteration guidance:** If this audit surfaces more than 3 Critical findings, do not patch individual docs. Instead, re-run Stage 2 with the original source, fix the requirements document, then re-run the affected Stage 4 sub-prompts. This is faster and less error-prone than cascading fixes.

---

## Stage 7: Governance Audit (Code vs Docs)

### Goal
Audit an existing project's governance documents against the actual codebase to find gaps, stale references, and policy violations. Use this after initial setup to verify completeness, or periodically during the project to catch drift.

**Distinction from Stage 6:** Stage 6 checks *docs vs original RFP* (are we governing the right things?). Stage 7 checks *code vs docs* (is the code doing what the docs say?).

### Input
- All filled governance documents from the project's `docs/` directory
- The project's current codebase (or a summary of scripts, configs, and output directories)
- The original source materials (RFP / project specification) for the source authority spot-check
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

## 7. Source Authority Spot-Check
Take 5 critical governance rules (highest-severity items from RISK_REGISTER) and trace each back to the original requirements document:
- Does the governance rule accurately reflect the original requirement?
- Has the rule drifted from its source during implementation?
- Are there any requirements from the source that were dropped or weakened?

Report: Spot-check results with quotes from both governance docs and source materials.

(For a comprehensive source fidelity audit, use Stage 6: RFP Traceability Audit.)

OUTPUT FORMAT:
For each finding:
- **Finding ID:** AUDIT-001, AUDIT-002, etc.
- **Category:** Coverage | Staleness | Compliance | Risk | Gate | Integrity | Source Fidelity
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

## Stage 8: Targeted Patches (CONTRACT_CHANGE Workflow)

### Goal
When a mid-project change occurs (new dependency, budget adjustment, added method, schema change), generate the minimal set of edits across all affected governance documents. This ensures CONTRACT_CHANGE discipline is maintained without manually hunting through every template.

### Input
- Description of the change (what changed and why)
- All current governance documents
- The CHANGELOG and DECISION_LOG (for context on prior changes)

---

### Stage 8a: Impact Analysis

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

### Stage 8b: Patch Generation

#### Input
- Stage 8a output (impact analysis)
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

[Paste Stage 8a output here]

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

## Stage 9: Test Code Generation

### Goal
Generate pytest test code that programmatically validates governance compliance: leakage prevention, budget enforcement, schema validation, determinism, and artifact integrity. These tests turn governance rules into executable checks.

### Input
- All filled governance documents
- The project's script and source code structure
- The project's config files (budget config, environment file)

---

### Stage 9a: Leakage & Data Integrity Tests

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

### Stage 9b: Budget & Compute Discipline Tests

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

### Stage 9c: Artifact Integrity & Reproducibility Tests

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

### Stage 9d: Pre-Delivery Smoke Tests

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

### Stage 9 Checkpoint

After generating all test modules:
- [ ] All test files are syntactically valid (`python -m py_compile tests/test_*.py`)
- [ ] Tests reference actual project paths, config files, and dataset names (not template placeholders)
- [ ] No test fabricates expected values — all thresholds and counts come from governance docs or config
- [ ] Test docstrings trace to specific contract sections
- [ ] `pytest tests/ --collect-only` shows all expected test functions
- [ ] Tests that require completed outputs are properly marked with `@pytest.mark.skipif` or `@pytest.mark.slow`

---

## Stage 10: Multi-Lens Audit Protocol

### Goal
Run a comprehensive, structured audit of the completed report through all 10 verification lenses. This stage replaces the ad-hoc "ask for an audit" pattern that led to 7-14 manual audit cycles in UL/RL projects.

### When to Run
- **Phase 4 (after report draft):** Lenses L5, L6, L7, L10
- **Phase 5 (pre-submission):** All lenses L1-L10
- **Any time you suspect inconsistencies:** Run individual lens prompts below

### Prerequisites
- Filled governance templates (from Stages 1-9)
- Report draft (.tex or .md)
- Experiment outputs in outputs/ directory
- Filled RUBRIC_TRACEABILITY.md (from Stage 4)
- If generators were run: scripts/audit_report.py, check_data_report.py, check_rubric.py, check_integrity.py

### Automated Checks (Run First)

If you generated audit scripts via `project.yaml`, run them before the prompt-based audits:

```bash
# Machine-verifiable checks (G13-G16)
python scripts/audit_report.py --report-path report.tex --phase full
python scripts/check_data_report.py --report-path report.tex --outputs-dir outputs/
python scripts/check_rubric.py --report-path report.tex
python scripts/check_integrity.py --report-path report.tex
```

Review FINDINGS.md output. Fix all CRITICAL and HIGH items before proceeding to prompt-based audits.

---

### Lens L5: Data-vs-Report Consistency (Prompt)

```
You are an audit agent verifying numeric consistency between a report and its source data.

I will provide:
1. The report text
2. The EXECUTION_MANIFEST mapping artifacts to report sections
3. Selected output artifacts (CSVs, JSONs)

For each artifact→section mapping in the EXECUTION_MANIFEST:
1. Extract every numeric claim from the report section (percentages, counts, ratios, metrics)
2. Find the corresponding value in the source artifact
3. Compare them. Report:
   - MATCH: values agree within rounding tolerance
   - ROUNDING: values differ only by rounding (state both values)
   - MISMATCH: values disagree (state both values, flag as CRITICAL)
   - NOT_FOUND: claimed value not found in artifact (flag as HIGH)

Also check:
- "improvement" language matches positive deltas
- "degradation" language matches negative deltas
- Multiplier claims (e.g., "3.8x faster") are arithmetically correct
- Percentage bases are correct (percent of what?)

Output a table: | Section | Claim | Report Value | Artifact Value | Verdict |

Do NOT invent or assume artifact values. If you cannot verify a claim, mark it UNVERIFIABLE.
```

**Attach:** Report text, EXECUTION_MANIFEST, relevant output CSVs/JSONs

---

### Lens L6: Rubric/FAQ Compliance (Prompt)

```
You are an audit agent verifying rubric and FAQ compliance.

I will provide:
1. The assignment specification (rubric)
2. The FAQ document
3. The report text
4. The RUBRIC_TRACEABILITY matrix (if filled)

For each rubric item:
1. Find the specific report paragraph that addresses it
2. Rate coverage: ADDRESSED (explicitly covered), PARTIAL (mentioned but incomplete), GAP (not found)
3. For GAP items: suggest which section should address it and what content is needed

For each FAQ question:
1. Find where the answer appears in the report
2. Rate: ADDRESSED or GAP
3. For GAP items: provide the answer based on the report's methodology and suggest where to add it

Pay special attention to these commonly-missed categories:
- Distance/similarity metric justification
- Hyperparameter search ranges and sensitivity
- Initialization choices (Q_0, random seeds)
- Convergence criteria
- Ablation analysis
- Noise sensitivity discussion
- Suggested improvements

Output:
1. Coverage matrix table
2. Overall coverage percentage
3. Prioritized list of GAP items with suggested fixes

Do NOT fabricate rubric items. Use only the provided specification.
```

**Attach:** Assignment spec, FAQ, report text, RUBRIC_TRACEABILITY.md

---

### Lens L7: Ten Simple Rules Audit (Prompt)

```
You are an audit agent checking report quality against Kording & Mensh's "Ten Simple Rules for Structuring Papers" and the project's REPORT_CONSISTENCY_SPEC.

I will provide:
1. The report text
2. The REPORT_CONSISTENCY_SPEC (filled checklist)
3. The Ten Simple Rules reference

Evaluate each rule:

**Rule 1 (One Contribution):** Is the title a declarative claim? Can you state the paper's contribution in one sentence?

**Rule 2 (Naive Reader):** Are all jargon terms defined on first use? Check the jargon inventory.

**Rule 3 (CCC):** For EVERY paragraph:
- Does it open with context/topic?
- Does it close with conclusion/takeaway?
- Flag any paragraph where a reader would ask "why was I told that?" or "so what?"
For the abstract: Map sentences to broad context → specific gap → approach → results → conclusion → significance.

**Rule 4 (No Zig-Zag):** Is each concept introduced in exactly one location? Any A-B-A topic bouncing? Check the terminology lock for synonym drift.

**Rule 5 (Abstract):** Is the abstract self-contained? Does it cover gap, method, results, conclusion?

**Rule 6 (Introduction):** Do paragraphs progress from broad field → subfield → specific gap? Is the gap statement explicit? Does the final paragraph preview results?

**Rule 7 (Results):** Are section headers declarative statements (findings, not methods)? Does each paragraph follow question → evidence → answer?

**Rule 8 (Discussion):** Does the first paragraph summarize findings? Are limitations acknowledged? Any new results introduced (this is a violation)?

Output per-rule: PASS or FAIL with specific violations (quote the problematic text). Group findings by severity: CRITICAL (data integrity), HIGH (structural), MEDIUM (writing quality), LOW (style).
```

**Attach:** Report text, REPORT_CONSISTENCY_SPEC, Ten_Simple_Rules_Kording_Mensh.md

---

### Lens L8: Academic Integrity (Prompt)

```
You are an audit agent checking academic integrity and AI disclosure compliance.

I will provide:
1. The report text (specifically the AI Use Statement)
2. The AI_DIVISION_OF_LABOR template
3. The ACADEMIC_INTEGRITY_FIREWALL template
4. The institutional AI policy (if available)

Check:
1. AI Use Statement exists and is non-empty
2. Written in first-person voice ("I used..." not "The author used...")
3. Names specific tools (e.g., "Claude Code CLI" not just "AI")
4. Describes what each tool was used for (role specificity)
5. Explicitly claims ownership of design, hypotheses, and conclusions
6. Includes a verification statement (how AI output was checked)
7. All permitted uses from AI_DIVISION_OF_LABOR are disclosed
8. No prohibited uses are evident in the report

Output: Per-check PASS/FAIL with specific quotes. For FAIL items, provide corrected language.
```

**Attach:** Report text, AI_DIVISION_OF_LABOR, ACADEMIC_INTEGRITY_FIREWALL

---

### Lens L10: Cross-Reference Integrity (Prompt)

```
You are an audit agent checking cross-reference integrity in a technical report.

I will provide the report text (.tex or .md).

Check:
1. Every figure referenced in text (no orphan figures — defined but never referenced)
2. Every table referenced in text (no orphan tables)
3. Figure/table numbers are sequential and consistent
4. All citation keys in text appear in bibliography
5. All bibliography entries are cited in text (no orphan references)
6. Internal section references resolve correctly
7. Terminology is consistent throughout (check the terminology lock if provided)
8. No broken LaTeX references (?? in output)

Output: Per-category PASS/FAIL with specific items flagged.
```

**Attach:** Report text (.tex or .md)

---

### Stage 10 Checkpoint

After running all audit lenses:
- [ ] All machine-verifiable checks pass (G13-G16 scripts)
- [ ] 0 CRITICAL findings across all lenses
- [ ] 0 HIGH findings across all lenses (or documented as accepted risk)
- [ ] All MEDIUM findings reviewed (fix or accept with rationale)
- [ ] FINDINGS.md updated with resolution status
- [ ] Rubric coverage = 100% (all items ADDRESSED or N/A)
- [ ] All numeric claims verified against source artifacts
- [ ] Report compiles cleanly with no build errors

If any CRITICAL or HIGH findings remain, fix and re-run the affected lenses before submission.

---

## Tips for Best Results

1. **Provide complete source materials.** The more context you give the AI at each stage, the better the output. Don't summarize requirements — paste the full documents.

2. **Review at every checkpoint.** AI assistants can hallucinate metric values, dataset statistics, and deadline dates. Verify all factual claims against your source materials.

3. **Iterate within stages.** If Stage 1 output is incomplete, refine it before moving to Stage 2. Each stage assumes high-quality input from the previous one.

4. **Use extended thinking.** If your AI assistant supports extended thinking or chain-of-thought (e.g., Claude), enable it for Stages 2, 5, 6, and 8a where complex reasoning about requirements, consistency, and change impact is needed.

5. **Keep a "decisions made" log.** As you customize templates, note any judgment calls you make. These become seed entries for your DECISION_LOG.

6. **Don't skip Stage 5.** Cross-template consistency is where most governance failures hide. A Risk Register that references non-existent scripts or a playbook with wrong budget values will cause problems downstream.

7. **Don't skip Stage 6.** This is your hallucination firewall. AI assistants will confidently produce governance documents that *sound* authoritative but subtly deviate from the original RFP. Run Stage 6 after every batch of AI-assisted template work, and again at every phase gate. If you only run one audit, make it this one.

8. **Run Stage 7 regularly.** Code-vs-docs audits catch governance drift during implementation. Run at every phase gate and after any burst of coding to surface forgotten CONTRACT_CHANGEs.

9. **Use Stage 8 for every material change.** It's tempting to just edit one file when a budget changes. Stage 8a's impact analysis catches the 5 other files you'd forget to update.

10. **Generate tests early.** Run Stage 9 right after initial template customization. The generated tests become your automated phase gate checks and catch contract violations as you code, not at delivery time.

11. **Compile tests before trusting them.** AI-generated test code may have import errors or reference non-existent paths. Always run `python -m py_compile` and `pytest --collect-only` before relying on the test suite.

12. **Treat the original RFP as immutable ground truth.** Never let AI-generated documents replace your original source materials. The Stage 2 requirements doc is a *derivative* — always keep the original RFP accessible for re-verification.
