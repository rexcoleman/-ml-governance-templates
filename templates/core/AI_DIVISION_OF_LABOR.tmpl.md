# AI DIVISION OF LABOR

<!-- version: 1.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_SL_Report -->

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §5 for evaluation rules that constrain AI-assisted analysis
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §4 for leakage prevention rules AI tools must respect

**Downstream (depends on this contract):**
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) §3 for report writing rules derived from the anti-ghostwriting firewall
- See [PRE_SUBMISSION_CHECKLIST](../report/PRE_SUBMISSION_CHECKLIST.tmpl.md) §6 for AI attribution verification

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{TOOL_N_NAME}}` | Name of AI tool | Claude Code, ChatGPT, Copilot |
| `{{TOOL_N_ROLE}}` | Primary role for this tool | Coding copilot, QA reviewer, literature search |
| `{{TOOL_N_MUST}}` | Required behaviors for this tool | Review all generated code before committing |
| `{{TOOL_N_MUST_NOT}}` | Prohibited behaviors for this tool | Must not produce standalone report paragraphs |
| `{{PRIVATE_DATA_POLICY}}` | What data must not be uploaded to AI tools | Course datasets, proprietary data, API keys |
| `{{CITATION_POLICY}}` | Organization's citation/attribution requirements | IEEE citation style; AI tools are not citable |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines the human-AI collaboration boundaries for the **{{PROJECT_NAME}}** project. It specifies which tasks each AI tool may perform, what outputs are permitted, and what guardrails prevent integrity violations.

**Core principle:** AI tools accelerate implementation and review. The human is the author, decision-maker, and owner of all deliverables. AI outputs are inputs to human judgment, never final products.

---

## 2) Global Non-Negotiables

These rules apply to **all** AI tools used in this project. They are non-negotiable regardless of tool capabilities.

### 2.1 Anti-Ghostwriting Firewall

AI tools MUST NOT produce standalone narrative paragraphs intended for direct inclusion in the final report's Results, Discussion, or Conclusion sections.

**Permitted AI output formats:**
- Checklists and verification prompts
- Claim templates requiring human insertion of artifact-backed numbers
- Questions and interpretation prompts (e.g., "What does the gap in Fig X imply?")
- Code, scripts, and technical scaffolding
- Bullet-point outlines and section skeletons (headings + topic sentences only)
- Redline edits on text the human wrote first (reviewer mode)

**Prohibited AI output formats:**
- Paste-ready interpretive paragraphs written from scratch
- Analysis narratives not grounded in the human's own artifacts
- Claims not backed by experimental evidence or primary sources

**If an AI tool produces paragraphs:** treat them as non-usable notes and rewrite from scratch in your own words.

### 2.2 Citation Chain Rule

AI tool outputs are NOT citable sources. The report cites only:

1. **Primary sources** — peer-reviewed papers, course materials, official documentation
2. **Your experimental artifacts** — figures, tables, logs, manifests

AI tools may help you find, organize, or verify sources, but the citation points to the original work, never to "ChatGPT says" or "Claude suggests."

### 2.3 Data Privacy Rule

Do NOT upload the following to external AI tools:

- {{PRIVATE_DATA_POLICY}}
- Raw datasets (unless explicitly public and permitted)
- Credentials, API keys, or access tokens

**Allowed uploads:** public papers, your own notes, your own generated EDA summaries and plots.

### 2.4 Test Set Barrier

No AI tool interaction may access, reference, or reason about test set results until the single authorized final evaluation. This applies to:
- Prompts that include test metrics
- Requests to interpret test performance for tuning decisions
- Any workflow that leaks test information into experiment design

---

## 3) Tool Roster

List every AI tool used in this project with its role and boundaries.

| # | Tool | Role | Output Types | Leakage Risk |
|---|------|------|-------------|--------------|
| 1 | {{TOOL_1_NAME}} | {{TOOL_1_ROLE}} | *(e.g., code, checklists, redlines)* | *(e.g., Low — no data access)* |
| 2 | {{TOOL_2_NAME}} | {{TOOL_2_ROLE}} | *(e.g., notes, summaries)* | *(e.g., Medium — has retrieval)* |
| 3 | {{TOOL_3_NAME}} | {{TOOL_3_ROLE}} | *(e.g., code completions)* | *(e.g., Low — inline only)* |
| *(add rows)* | | | | |

---

## 4) Per-Tool Governance

Define MUST and MUST NOT rules for each tool. Copy this block per tool.

### Tool {{N}}: {{TOOL_N_NAME}} — "{{TOOL_N_ROLE}}"

**What this tool does:**
- *(List specific permitted tasks)*

**MUST:**
- {{TOOL_N_MUST}}
- *(Add rules)*

**MUST NOT:**
- {{TOOL_N_MUST_NOT}}
- *(Add rules)*

**Output format rule:**
*(Define what output formats are acceptable from this tool — e.g., "checklists and code only," "redlines on existing text only," "notes and bullet summaries only.")*

---

## 5) Human Role — "Principal Investigator / Author"

The human owns all decisions, experiments, and deliverables.

**Responsibilities:**
- Implement or direct implementation of all code, then verify correctness
- Run EDA, define hypotheses, execute experiments, and produce final artifacts
- Make all final choices (preprocessing, hyperparameters, model selection, thresholds)
- Write all interpretive prose (Results, Discussion, Conclusion) in paragraph form
- Ensure reproducibility: commit hash, commands, environment, seeds
- Maintain AI provenance and the AI Use Statement (§7)

**Ownership rule:** The human MUST review and verify every AI-generated output before it enters the project. "AI wrote it" is not a defense for errors, leakage, or integrity violations.

---

## 6) Information Flow Controls

### 6.1 What Each Tool May See

| Tool | Source Code | Experiment Outputs | Raw Data | Report Drafts | Authority Docs |
|------|:-----------:|:-----------------:|:--------:|:-------------:|:--------------:|
| *(tool name)* | *(Yes/No)* | *(Yes/No)* | *(Yes/No)* | *(Yes/No)* | *(Yes/No)* |
| *(add rows)* | | | | | |

### 6.2 Cross-Tool Isolation

- Tool outputs MUST NOT be passed between tools without human review
- No tool may see another tool's raw output as if it were a primary source
- The human is the integration point — all information flows through human judgment

---

## 7) AI Use Statement Template

Include this statement in the final deliverable (before References). Fill in the tool-specific details.

```markdown
## AI Use Statement

The following AI tools were used during this project:

| Tool | Role | What It Did | Human Verification |
|------|------|-------------|-------------------|
| {{TOOL_1_NAME}} | {{TOOL_1_ROLE}} | *(Specific tasks performed)* | *(How outputs were verified)* |
| {{TOOL_2_NAME}} | {{TOOL_2_ROLE}} | *(Specific tasks performed)* | *(How outputs were verified)* |
| *(add rows)* | | | |

All AI-assisted content was reviewed and verified by the author. AI tools are not
cited as sources; all citations reference primary peer-reviewed publications or
experimental artifacts. The final report's analysis, interpretation, and conclusions
are the author's own work.
```

---

## 8) Audit Artifacts

Maintain these artifacts for provenance tracking:

| Artifact | Path | Purpose |
|----------|------|---------|
| AI Use Statement | *(in report)* | Disclose all AI tool usage per policy |
| Tool interaction log | `docs/ai_tool_log.md` *(optional)* | Record significant AI interactions and decisions |

---

## 9) Acceptance Gate

Before delivery, the following MUST pass:

- [ ] AI Use Statement is present in the deliverable
- [ ] Every AI tool used is listed with its role and verification method
- [ ] No AI-generated prose appears verbatim in Results/Discussion/Conclusion
- [ ] All citations reference primary sources, not AI tool outputs
- [ ] No private data was uploaded to external AI tools
- [ ] Test set barrier was maintained throughout all AI interactions

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Adding a new AI tool to the project
- Changing a tool's permitted role or output types
- Modifying the anti-ghostwriting firewall rules
- Changing the data privacy policy
- Modifying the citation chain rule
- Changing information flow controls (§6)
