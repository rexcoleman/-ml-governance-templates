# ML Governance Templates v2.0 — Execution Plan

> **Purpose:** Step-by-step plan to upgrade `ml-governance-templates` from v1.0 (15 templates, skeleton-level) to v2.0 (25 templates, production-grade governance).
> **Source analysis:** `Moonshots_Career_Thesis_v2/analysis/personal/cs7641_a3_a4_gap_narrowing_plan.md` §5
> **Scope:** General-purpose — not tied to any specific course or project. All upgrades apply to any ML experiment project.
> **Last updated:** 2026-03-11

---

## 1. WHY v2.0

The v1.0 templates were extracted from a single production ML research project. A systematic comparison against two battle-tested project repos revealed that the templates capture the **skeleton** but miss much of what made those projects succeed:

| Gap | Impact | Example |
|-----|--------|---------|
| No authority hierarchy in any template | Users don't know what overrides what when requirements conflict | Every production doc started with a Tier 1/2/3 binding header; zero templates do |
| Templates are isolated documents | Users miss critical cross-references between contracts | Production docs contain 50+ cross-references; templates have none |
| Requirements stated but not enforceable | Users document rules but have no way to check them | Production used 5 automation hooks with named scripts and exit codes |
| No hypothesis pre-registration | Users skip the most impactful methodology innovation | Hypothesis-first temporal gating prevented post-hoc rationalization |
| No AI collaboration governance | Users have no framework for human-AI role boundaries | Production defined 8 explicit roles with "MUST NOT" lists per role |
| No reproducibility spec | Users lack a single "reproduce everything" document | Production used a 290-line REPRO.md with exact commands per phase |
| Risk register is a bare table | Users get no guidance on risk categories, automation hooks, or critical invalidators | Production had 100+ risks across 8 categories with 5 automation hooks |

**v2.0 goal:** Close these gaps so that any ML practitioner can set up production-grade governance in hours, not weeks.

---

## 2. UPGRADE INVENTORY

### 2.1 Tier A: Meta-Governance (apply to ALL existing templates)

These are systemic upgrades — patterns that must appear in every template. Do these first because every subsequent upgrade depends on them.

| ID | Upgrade | What to Do | Files Affected |
|----|---------|-----------|----------------|
| **U1** | **Authority hierarchy header** | Add a standard header block to every `.tmpl.md` file: Tier 1 (primary spec) > Tier 2 (FAQ/clarifications) > Tier 3 (advisory) > Contracts (subordinate). Include a conflict resolution rule: "When Tier 1 and this contract disagree, Tier 1 wins." Include a `{{TIER1_DOC}}`, `{{TIER2_DOC}}` placeholder. | All 15 `.tmpl.md` files |
| **U2** | **Cross-contract reference protocol** | Add a "Companion Contracts" section to each template listing which other templates it depends on and which depend on it. Use the format: `See {{COMPANION_CONTRACT}} §{{SECTION}} for {{TOPIC}}`. | All 15 `.tmpl.md` files |
| **U3** | **Enforcement mechanism pattern** | For each MUST requirement in every template, add a "Verification" annotation: script name (or manual check), exit code, and the phase gate where it's checked. Use the format: `**Verification:** {{SCRIPT_NAME}} exits 0 at Phase {{N}}` | All 15 `.tmpl.md` files |
| **U4** | **Template versioning** | Add a metadata header to every template: `version`, `created`, `last_validated_against` (which real project last tested this template). | All 15 `.tmpl.md` files + `TEMPLATE_INDEX.md` |

### 2.2 Tier B: New Templates

Templates for governance patterns that can't be patched into existing documents.

| ID | Template | Directory | Purpose |
|----|----------|-----------|---------|
| **U5** | `HYPOTHESIS_CONTRACT.tmpl.md` | `templates/core/` | Hypothesis pre-registration: prediction, EDA evidence, theory link, failure mode, resolution protocol. Temporal gate: experiments MUST NOT begin before hypotheses are locked. Includes a per-hypothesis template and a resolution table (Confirmed / Refuted / Partially Confirmed with evidence). |
| **U6** | `AI_DIVISION_OF_LABOR.tmpl.md` | `templates/core/` | Human-AI collaboration governance: tool roster with per-role "MUST" and "MUST NOT" lists, anti-ghostwriting firewall ("AI must not produce standalone narrative paragraphs"), citation rules (AI tools are not citable sources), AI Use Statement template. Applicable to any project using AI coding assistants, chat-based QA, or retrieval tools. |
| **U7** | `REPRODUCIBILITY_SPEC.tmpl.md` | `templates/report/` | Single document enabling anyone to reproduce all artifacts from a fresh clone: environment setup commands, data acquisition steps, single-command reproduction sequence (or per-phase commands), verification steps (expected outputs, hash comparisons), hardware note requirement. |
| **U8** | `CONFIGURATION_SPEC.tmpl.md` | `templates/core/` | Config-as-code governance: hierarchy diagram (base → dataset → component → resolved), resolution rules (CLI > config file > hardcoded defaults), `config_resolved.yaml` dump requirement per run, scoring metric as first-class config value with test enforcement, change triggers (any config edit = re-run + CONTRACT_CHANGE). |
| **U9** | `TEST_ARCHITECTURE.tmpl.md` | `templates/core/` | Testing philosophy and structure: test categories (leakage, determinism, sanity, integration, artifact integrity, initialization matching), synthetic fixture pattern (conftest.py generating fake data matching real column types), marker-based skipping for private data tests, minimum coverage expectations per category. |
| **U10** | `ADVERSARIAL_EVALUATION.tmpl.md` | `templates/core/` | Adversarial robustness evaluation: threat model definition, perturbation types (input, reward, environment, data poisoning), robustness metrics and baselines, adversarial budget accounting, disclosure rules. Optional — activate when the project includes adversarial analysis. |
| **U11** | `ENVIRONMENT_SPEC.tmpl.md` | `templates/core/` | Simulation / environment definition for RL or agent-based projects: state space, action space, reward function, transition dynamics, discount factor, termination conditions, environment visualization, reward sensitivity analysis protocol. Optional — activate for RL, multi-agent, or simulation-based projects. |
| **U29** | `PUBLICATION_BRIEF.tmpl.md` | `templates/publishing/` | Publication message governance: primary demonstration ("what this artifact proves about the author"), target reader + takeaway table, portfolio property alignment checklist, narrative constraint ("reader understands X by paragraph 3"), anti-claims ("what this artifact does NOT prove"). Locked before implementation. |
| **U30** | `ACADEMIC_INTEGRITY_FIREWALL.tmpl.md` | `templates/publishing/` | Structural separation between course work and published work: three walls (data separation, code independence, content isolation), executable verification commands (grep-based checks), transferable-vs-prohibited list, pre-publication checklist. Required for any project derived from coursework or employer IP. |
| **U31** | `LEAN_HYPOTHESIS.tmpl.md` | `templates/publishing/` | Market validation for parallel projects: customer-problem hypothesis, pain statement (severity, frequency, workaround, cost), solution hypothesis, lean validation plan (build → publish → share → pilot), play/strategy alignment, kill criteria. Optional — activate when the project is also testing a market opportunity. |

### 2.3 Tier C: Major Upgrades to Existing Templates

Specific sections and appendices to add to the 15 existing templates.

| ID | Template | Additions |
|----|----------|-----------|
| **U12** | `DATA_CONTRACT.tmpl.md` | (a) **Leakage tripwire appendix** — table of tripwire IDs (LT-1 fit isolation, LT-2 test access enforcement, LT-3 transform-only on val/test), each with: detection test, code pattern, automation hook, failure behavior. (b) **Split hash algorithm** — deterministic hash using sorted indices with explicit dtype (`int64`), cross-platform safe. (c) **Prior-project split inheritance** — procedure for deriving validation splits from inherited train/test, with hash verification. (d) **"No-change confirmation"** — if preprocessing matches prior project, require explicit statement. |
| **U13** | `EXPERIMENT_CONTRACT.tmpl.md` | (a) **Multi-part experiment matrix** — table template: Part × Dataset × Methods × Techniques. (b) **Init-weight matching protocol** — save `state_dict` once per seed, load before each method, verify via forward-pass equality within tolerance. (c) **Budget type distinction** — func-evals (black-box optimization) vs grad-evals (gradient-based), with cross-part equality rules and over-budget exclusion policy. (d) **Pipeline composition section** — governing multi-stage methods (e.g., dimensionality reduction → clustering): stage ordering, intermediate artifact logging, ablation protocol. (e) **Sequential/RL appendix** — episode budget, exploration schedule, convergence criterion, checkpoint strategy, multi-seed stability for non-batch methods. |
| **U14** | `METRICS_CONTRACT.tmpl.md` | (a) **Threshold governance** — lock-after-baseline procedure: run baseline → record metric → set threshold → lock in config → any change = CONTRACT_CHANGE. (b) **Sanity check protocol** — dummy baseline (majority class) + shuffled-label baseline, expected behavior, pass/fail criteria. (c) **Per-class behavior requirement** — when to require per-class metrics vs aggregate only; prohibit silently averaging away tail-class failures. (d) **Budget-matched claims rule** — require dispersion (median + IQR or mean ± std), prohibit point-estimate-only claims. (e) **Delta reporting** — for technique comparison studies, require Δ(metric) relative to baseline. (f) **Unsupervised evaluation menu** — internal validity (silhouette, elbow), external validity (ARI, NMI), stability (bootstrap), guidance on when to use each. (g) **Sequential/RL policy evaluation** — evaluation episode count, reward statistics (mean, std, min, max), policy visualization requirements. |
| **U15** | `FIGURES_TABLES_CONTRACT.tmpl.md` | (a) **Caption takeaway rule** — every caption MUST include an interpretation of what the figure/table reveals; prohibit legend-only captions. (b) **Operator/hyperparameter disclosure** — captions for method-comparison figures must include key method-specific settings (extracted from `config_resolved.yaml`). (c) **Summary table locked-columns pattern** — template for standard summary tables with required column definitions. (d) **Seed aggregation rule** — report median + IQR or mean ± std; never bare means. (e) **Visualization catalog** — recommended plot types by method family (supervised curves, optimization progress, cluster plots, policy heatmaps, etc.). |
| **U16** | `ARTIFACT_MANIFEST_SPEC.tmpl.md` | (a) **Provenance triplet** — `versions.txt` (first run only), `git_commit_sha.txt` (first run only), `run_log.json` (appended per run). (b) **Run ID naming convention** — deterministic scheme: `{part}_{dataset}_{method}_seed{seed}`. (c) **`config_resolved.yaml` schema** — require per-run resolved config dump with all hyperparameters, method settings, budget values, seed, split ID. (d) **Determinism requirement** — same seed + same env + same code = byte-identical outputs (excluding timestamps). |
| **U17** | `PRIOR_WORK_REUSE.tmpl.md` | (a) **3-option evaluation framework** — vendor snapshot, shared package, git subtree; decision criteria (self-containment, grader portability, change control). (b) **File inventory with per-file SHA-256** — template table for listing reused files with hashes. (c) **Verification script pattern** — describe a verify script that checks N integrity conditions and exits non-zero on failure. (d) **"Frozen upstream" documentation** — explicitly state whether the upstream project is still evolving or frozen. (e) **Format conversion guidance** — for data format changes between projects (e.g., NPZ → JSON). |
| **U18** | `RISK_REGISTER.tmpl.md` | (a) **Critical invalidator list** — top 10 issues that cause project failure or major point loss. (b) **8-category risk taxonomy** — Data & Leakage, Evaluation Discipline, Compute Fairness, Method-Specific (×N per project), Artifact & Reproducibility, Report Compliance. (c) **Automation hooks section** — table mapping risks to executable checks: Risk ID → Script → Exit Code → Phase Gate. (d) **Phase-gate ownership** — each risk assigned to a phase where it's verified. |
| **U19** | `DECISION_LOG.tmpl.md` | (a) **"Alternatives Considered"** — per ADR section documenting options evaluated and why rejected. (b) **"Contracts Affected"** — list of downstream contracts/specs impacted by the decision. (c) **"Evidence Plan"** — what artifacts or scripts validate that the decision was implemented correctly. |
| **U20** | `CHANGELOG.tmpl.md` | (a) **Backward-compatibility field** — per entry: "compatible" or "breaking" with explanation. (b) **Artifacts impacted + regeneration tracking** — which outputs need re-running. (c) **Risk mitigation cross-reference** — which RISK_REGISTER entries this change addresses. (d) **Change trigger taxonomy** — categorized list of common triggers: environment (deps, Python version), data (paths, splits, preprocessing), experiments (budgets, method list, init protocol), metrics (thresholds, metric definitions), scripts (CLI flags, output schemas), figures/tables (columns, captions), manifests (run IDs, hashing rules). |
| — | `SCRIPT_ENTRYPOINTS_SPEC.tmpl.md` | No Tier C upgrade needed — v1.0 coverage is sufficient. Receives only Tier A meta-governance (U1-U4). |
| **U21** | `IMPLEMENTATION_PLAYBOOK.tmpl.md` | (a) **Detailed Phase 0 template** — environment verify, data check, leakage tripwires, prior-work verification (if applicable), split confirmation, baseline recording, governance commit. (b) **Phase gate DoD checklists** — per-phase verification commands (not just prose). (c) **Integration hooks** — explicit references to TASK_BOARD (update status), RISK_REGISTER (re-scan high-severity), DECISION_LOG (record ADRs triggered during phase). |

### 2.4 Tier D: Structural & Infrastructure Improvements

| ID | Improvement | Where |
|----|------------|-------|
| **U22** | **Quickstart profiles** — pre-selected template subsets for common project types with guidance on which Tier C appendices to activate. Profiles: Minimal (3 templates), Supervised ML (9), Optimization Benchmark (11), Unsupervised Analysis (10), RL / Agent Study (11), Full + Publishing (all 25). | `TEMPLATE_INDEX.md` |
| **U23** | **Worked examples per profile** — for each quickstart profile, a sample `README.md` showing placeholder fills for a representative project. No course-specific content — use generic, illustrative examples. | `examples/` subdirectories |
| **U24** | **Prompt Playbook update** — add stages: authority hierarchy setup (1b), hypothesis pre-registration (4b), unsupervised evaluation selection (4c), RL environment design (4d), adversarial evaluation setup (4e), publication brief drafting (4f), academic integrity verification (4g). | `PROMPT_PLAYBOOK.md` |
| **U25** | **Execution manifest template** — `EXECUTION_MANIFEST.tmpl.md`: auto-generated methods summary + results index pattern. "Report numbers must come from these artifacts, not manually copied from plots." | `templates/report/` |
| **U26** | **Research tool organization guide** — appendix to `AI_DIVISION_OF_LABOR.tmpl.md` covering information flow controls between research tools (retrieval tools, chat assistants, coding copilots, note-taking tools). | Appendix in U6 |
| **U27** | **Template dependency graph** — Mermaid diagram showing which templates depend on which. | `TEMPLATE_INDEX.md` |
| **U28** | **Scoring metric config pattern** — appendix to `CONFIGURATION_SPEC.tmpl.md` showing how to encode metric selection in YAML with test enforcement (assert statements verifying the config value matches what the code computes). | Appendix in U8 |
| **—** | **README.md rewrite** — update to reflect 25 templates, new directory structure, 4 tiers, quickstart profiles, publishing tier. | `README.md` |
| **—** | **`init_project.sh` update** — add profile-based init: `init_project.sh /path --profile supervised` copies only the relevant subset. | `scripts/init_project.sh` |

---

## 3. EXECUTION PHASES

### Phase 1: Foundation (Tier A + High-Priority Tier B)

**Goal:** Every existing template gains the meta-governance patterns. Core new templates created. After this phase, the framework is usable for any new ML project at a higher quality level than v1.0.

**Estimated scope:** ~15 existing files edited + 6 new files created.

| Step | Action | Deliverable | Depends On |
|------|--------|------------|------------|
| 1.1 | **U4: Template versioning** | Add metadata header (`version: 1.0`, `created: 2026-02-20`, `last_validated_against: OL Report`) to all 15 templates. | — |
| 1.2 | **U1: Authority hierarchy header** | Design a standard header block (8-12 lines). Apply to all 15 templates below the version header. Include `{{TIER1_DOC}}`, `{{TIER2_DOC}}` placeholders and conflict resolution rule. | 1.1 |
| 1.3 | **U2: Cross-contract references** | Add "Companion Contracts" section to each template. Use the dependency graph from `TEMPLATE_INDEX.md` as the source of truth. | 1.1 |
| 1.4 | **U5: HYPOTHESIS_CONTRACT.tmpl.md** | Create new template in `templates/core/`. Include: hypothesis template (prediction + EDA evidence + theory link + failure mode), temporal gate language, resolution table format (Confirmed / Refuted / Partial + evidence), per-dataset hypothesis example. | 1.2 |
| 1.5 | **U6: AI_DIVISION_OF_LABOR.tmpl.md** | Create new template in `templates/core/`. Include: tool roster table, per-role MUST/MUST NOT sections (with `{{TOOL_N}}` placeholders), anti-ghostwriting firewall section, citation rules, AI Use Statement template. | 1.2 |
| 1.6 | **U7: REPRODUCIBILITY_SPEC.tmpl.md** | Create new template in `templates/report/`. Include: environment setup, data acquisition, reproduction sequence (per-phase commands), verification steps, hardware note requirement. | 1.2 |
| 1.7 | **U8: CONFIGURATION_SPEC.tmpl.md** | Create new template in `templates/core/`. Include: hierarchy diagram, resolution rules, `config_resolved.yaml` dump requirement, scoring metric config pattern (U28 folded in). | 1.2 |
| 1.8 | **U9: TEST_ARCHITECTURE.tmpl.md** | Create new template in `templates/core/`. Include: test category table, synthetic fixture guidance, marker-based skipping, minimum coverage expectations. | 1.2 |
| 1.9 | **Update TEMPLATE_INDEX.md** | Add all 6 new templates. Update starter configurations. Add dependency graph (U27). | 1.4–1.8 |
| 1.10 | **Commit + tag `v1.5-foundation`** | All Tier A applied, 6 new core templates, updated index. | 1.1–1.9 |

### Phase 2: Deepen Existing Templates (Tier C)

**Goal:** Upgrade all 15 existing templates with the governance innovations discovered in the repo comparison. After this phase, each template is 50-100% larger and includes enforcement mechanisms, not just requirements.

**Estimated scope:** ~15 files edited, each gaining 1-5 new sections or appendices.

| Step | Action | Deliverable | Depends On |
|------|--------|------------|------------|
| 2.1 | **U12: DATA_CONTRACT upgrades** | Add leakage tripwire appendix, split hash algorithm, prior-project split inheritance, no-change confirmation. | Phase 1 |
| 2.2 | **U13: EXPERIMENT_CONTRACT upgrades** | Add multi-part matrix, init-weight matching protocol, budget type distinction, over-budget exclusion, pipeline composition, RL/sequential appendix. | Phase 1 |
| 2.3 | **U14: METRICS_CONTRACT upgrades** | Add threshold governance, sanity check protocol, per-class behavior, budget-matched claims, delta reporting, unsupervised evaluation menu, RL policy evaluation. | Phase 1 |
| 2.4 | **U15: FIGURES_TABLES_CONTRACT upgrades** | Add caption takeaway rule, operator disclosure, summary table pattern, seed aggregation, visualization catalog. | Phase 1 |
| 2.5 | **U16: ARTIFACT_MANIFEST_SPEC upgrades** | Add provenance triplet, run ID convention, `config_resolved.yaml` schema, determinism requirement. | 1.7 (U8) |
| 2.6 | **U17: PRIOR_WORK_REUSE upgrades** | Add 3-option framework, file inventory with SHA-256, verification script pattern, frozen upstream, format conversion. | Phase 1 |
| 2.7 | **U18: RISK_REGISTER upgrades** | Add critical invalidator list, 8-category taxonomy, automation hooks section, phase-gate ownership. | Phase 1 |
| 2.8 | **U19: DECISION_LOG upgrades** | Add alternatives considered, contracts affected, evidence plan. | Phase 1 |
| 2.9 | **U20: CHANGELOG upgrades** | Add backward-compatibility field, impact tracking, risk cross-reference, trigger taxonomy. | Phase 1 |
| 2.10 | **U21: IMPLEMENTATION_PLAYBOOK upgrades** | Add detailed Phase 0, DoD checklists with verification commands, integration hooks to TASK_BOARD/RISK_REGISTER/DECISION_LOG. | 2.7, 2.8 |
| 2.11 | **U3: Enforcement mechanisms** | Systematic pass across ALL templates: add `**Verification:**` annotations to every MUST requirement. This is done last because Tier C additions created new MUST requirements. | 2.1–2.10 |
| 2.12 | **Commit + tag `v1.8-deepened`** | All 15 existing templates upgraded with production-grade governance. | 2.1–2.11 |

### Phase 3: Specialized & Publishing Templates (Tier B remainder + Tier D)

**Goal:** Add optional specialized templates (adversarial, RL, publishing) and structural improvements. After this phase, the framework covers the full lifecycle from project setup through publication.

**Estimated scope:** ~4 new template files + 3 new example directories + Playbook update + README rewrite.

| Step | Action | Deliverable | Depends On |
|------|--------|------------|------------|
| 3.1 | **U10: ADVERSARIAL_EVALUATION.tmpl.md** | Create in `templates/core/`. Threat model, perturbation types, robustness metrics, adversarial budget, disclosure rules. | Phase 2 |
| 3.2 | **U11: ENVIRONMENT_SPEC.tmpl.md** | Create in `templates/core/`. MDP/simulation definition, state/action spaces, reward function, dynamics, termination, visualization. | Phase 2 |
| 3.3 | **Create `templates/publishing/` directory** | New tier for publication-related templates. | — |
| 3.4 | **U29: PUBLICATION_BRIEF.tmpl.md** | Create in `templates/publishing/`. Primary demonstration, target reader + takeaway, portfolio alignment, narrative constraint, anti-claims. | 3.3 |
| 3.5 | **U30: ACADEMIC_INTEGRITY_FIREWALL.tmpl.md** | Create in `templates/publishing/`. Three walls (data, code, content), executable verification commands, transferable-vs-prohibited list, pre-publication checklist. | 3.3 |
| 3.6 | **U31: LEAN_HYPOTHESIS.tmpl.md** | Create in `templates/publishing/`. Customer-problem hypothesis, pain statement, solution hypothesis, validation plan, strategy alignment, kill criteria. | 3.3 |
| 3.7 | **U25: EXECUTION_MANIFEST.tmpl.md** | Create in `templates/report/`. Auto-generated methods summary + results index. "Report numbers must come from these." | Phase 2 |
| 3.8 | **U22: Quickstart profiles** | Update `TEMPLATE_INDEX.md` with 6 profiles: Minimal, Supervised, Optimization, Unsupervised, RL/Agent, Full + Publishing. Each lists templates + which appendices to activate. | 3.1–3.7 |
| 3.9 | **U23: Worked examples** | Create `examples/{supervised,optimization,unsupervised,rl-agent,publishing}/README.md` with representative placeholder fills. No course-specific content. | 3.8 |
| 3.10 | **U24: Prompt Playbook update** | Add stages 1b (authority hierarchy), 4b-4g (hypothesis, unsupervised eval, RL env, adversarial, publication brief, integrity verification). | 3.1–3.7 |
| 3.11 | **U26: Research tool organization guide** | Add as appendix to `AI_DIVISION_OF_LABOR.tmpl.md`. | 1.5 |
| 3.12 | **README.md rewrite** | Update to reflect 25 templates, 4 tiers, new directory structure, quickstart profiles, publishing tier. | 3.1–3.11 |
| 3.13 | **`init_project.sh` update** | Add `--profile` flag for profile-based template copying. | 3.8 |
| 3.14 | **Commit + tag `v2.0`** | Full v2.0 release: 25 templates, 6 quickstart profiles, updated Playbook, examples, infrastructure. | 3.1–3.13 |

---

## 4. DIRECTORY STRUCTURE (Post v2.0)

```
ml-governance-templates/
├── README.md                                    # Updated for v2.0
├── TEMPLATE_INDEX.md                           # 25 templates + dependency graph + 6 profiles
├── PROMPT_PLAYBOOK.md                          # 9 + 7 new stages
├── EXECUTION_PLAN.md                           # This file
├── templates/
│   ├── core/                                   # 12 templates (was 7)
│   │   ├── ENVIRONMENT_CONTRACT.tmpl.md        # v2.0 (U1-U4 applied)
│   │   ├── DATA_CONTRACT.tmpl.md               # v2.0 (U1-U4 + U12)
│   │   ├── EXPERIMENT_CONTRACT.tmpl.md         # v2.0 (U1-U4 + U13)
│   │   ├── METRICS_CONTRACT.tmpl.md            # v2.0 (U1-U4 + U14)
│   │   ├── FIGURES_TABLES_CONTRACT.tmpl.md     # v2.0 (U1-U4 + U15)
│   │   ├── ARTIFACT_MANIFEST_SPEC.tmpl.md      # v2.0 (U1-U4 + U16)
│   │   ├── SCRIPT_ENTRYPOINTS_SPEC.tmpl.md     # v2.0 (U1-U4)
│   │   ├── HYPOTHESIS_CONTRACT.tmpl.md         # NEW (U5)
│   │   ├── AI_DIVISION_OF_LABOR.tmpl.md        # NEW (U6 + U26)
│   │   ├── CONFIGURATION_SPEC.tmpl.md          # NEW (U8 + U28)
│   │   ├── TEST_ARCHITECTURE.tmpl.md           # NEW (U9)
│   │   ├── ADVERSARIAL_EVALUATION.tmpl.md      # NEW (U10) — optional
│   │   └── ENVIRONMENT_SPEC.tmpl.md            # NEW (U11) — optional
│   ├── management/                             # 6 templates (unchanged count)
│   │   ├── IMPLEMENTATION_PLAYBOOK.tmpl.md     # v2.0 (U1-U4 + U21)
│   │   ├── TASK_BOARD.tmpl.md                  # v2.0 (U1-U4)
│   │   ├── RISK_REGISTER.tmpl.md               # v2.0 (U1-U4 + U18)
│   │   ├── DECISION_LOG.tmpl.md                # v2.0 (U1-U4 + U19)
│   │   ├── CHANGELOG.tmpl.md                   # v2.0 (U1-U4 + U20)
│   │   └── PRIOR_WORK_REUSE.tmpl.md            # v2.0 (U1-U4 + U17)
│   ├── report/                                 # 4 templates (was 2+1)
│   │   ├── REPORT_ASSEMBLY_PLAN.tmpl.md        # v2.0 (U1-U4)
│   │   ├── PRE_SUBMISSION_CHECKLIST.tmpl.md    # v2.0 (U1-U4)
│   │   ├── REPRODUCIBILITY_SPEC.tmpl.md        # NEW (U7)
│   │   ├── EXECUTION_MANIFEST.tmpl.md          # NEW (U25)
│   │   └── IEEE_Report_Template.tex            # Unchanged
│   └── publishing/                             # NEW directory — 3 templates
│       ├── PUBLICATION_BRIEF.tmpl.md           # NEW (U29)
│       ├── ACADEMIC_INTEGRITY_FIREWALL.tmpl.md # NEW (U30)
│       └── LEAN_HYPOTHESIS.tmpl.md             # NEW (U31)
├── examples/
│   ├── sample-project/README.md                # v1.0 example (kept)
│   ├── supervised/README.md                    # NEW (U23)
│   ├── optimization/README.md                  # NEW (U23)
│   ├── unsupervised/README.md                  # NEW (U23)
│   ├── rl-agent/README.md                      # NEW (U23)
│   └── publishing/README.md                    # NEW (U23)
└── scripts/
    └── init_project.sh                         # v2.0 (--profile flag)
```

---

## 5. QUICKSTART PROFILES (Post v2.0)

| Profile | Templates | When to Use |
|---------|-----------|-------------|
| **Minimal** (3) | Environment, Data, Metrics | Quick single-experiment project, no report deliverable |
| **Supervised ML** (9) | All 7 original core + Hypothesis + Configuration | Supervised learning study with train/val/test evaluation |
| **Optimization Benchmark** (11) | All core + Hypothesis + Config + Risk Register + Playbook | Multi-method comparison study with budget matching |
| **Unsupervised Analysis** (10) | All core (minus Adversarial/Environment Spec) + Hypothesis + Config + Test Architecture | Clustering / dimensionality reduction study |
| **RL / Agent Study** (11) | All core + Environment Spec + Hypothesis + Config + Test Architecture | MDP / RL / agent-based study |
| **Full + Publishing** (all 25) | Everything | Multi-phase project with publication goal and market validation |

---

## 6. QUALITY GATES PER PHASE

### Phase 1 Exit Gate

- [ ] All 15 existing templates have: version header, authority hierarchy header, companion contracts section
- [ ] 6 new templates created with same headers
- [ ] `TEMPLATE_INDEX.md` updated with all 21 templates and dependency information
- [ ] `init_project.sh` copies new templates
- [ ] All `{{PLACEHOLDER}}` syntax is consistent (no typos, no broken references)
- [ ] At least 1 real project has been set up using the Phase 1 templates to validate usability (validation project need not be completed — a governance setup commit using the templates is sufficient)

### Phase 2 Exit Gate

- [ ] All 15 existing templates have Tier C upgrades applied
- [ ] Every MUST requirement across all templates has a `**Verification:**` annotation
- [ ] Cross-contract references are bidirectional (if A references B §3, B references A)
- [ ] No orphaned placeholders (every `{{X}}` appears in the Customization Guide)
- [ ] At least 1 real project has been set up using Phase 2 templates to validate the deeper governance

### Phase 3 Exit Gate (v2.0 Release)

- [ ] All 25 templates pass internal consistency check
- [ ] 6 quickstart profiles defined with template lists
- [ ] 5+ worked examples created (one per non-trivial profile)
- [ ] Prompt Playbook updated with new stages
- [ ] README accurately describes the full framework
- [ ] `init_project.sh --profile <name>` works for all profiles
- [ ] `TEMPLATE_INDEX.md` includes Mermaid dependency graph
- [ ] Git tag `v2.0` created

---

## 7. PRINCIPLES GOVERNING ALL UPGRADES

These principles ensure upgrades stay general-purpose and don't drift toward any specific project:

1. **No course-specific content.** Templates must work for academic ML, industry ML, and independent research equally. Use `{{PLACEHOLDER}}` for anything project-specific.

2. **Additive, not breaking.** All Tier C upgrades are new sections/appendices — existing template users can adopt incrementally. No existing placeholder is renamed or removed.

3. **Optional appendices marked clearly.** Tier C additions that only apply to certain project types (RL appendix, unsupervised eval menu, adversarial evaluation) are marked `[OPTIONAL — activate for {{PROJECT_TYPE}} projects]`.

4. **Enforcement > documentation.** Every MUST requirement should have a verification method. If a requirement can't be verified, downgrade it to SHOULD or add a verification pattern.

5. **Templates are a system.** Cross-references between templates are mandatory, not optional. If template A depends on template B, both must say so.

6. **Extracted from real projects.** Every governance pattern in v2.0 was discovered in a real project that scored in the top quartile. Nothing is theoretical.

7. **Publishing tier is opt-in.** The `templates/publishing/` directory is a separate concern from experiment governance. Projects that don't publish can ignore it entirely.

---

## 8. TRACKING

Progress tracked via git commits and tags:

| Milestone | Tag | Criteria |
|-----------|-----|----------|
| Foundation complete | `v1.5-foundation` | Phase 1 exit gate passes |
| Templates deepened | `v1.8-deepened` | Phase 2 exit gate passes |
| Full release | `v2.0` | Phase 3 exit gate passes |

Each commit during execution should reference the upgrade ID (e.g., `U12: Add leakage tripwire appendix to DATA_CONTRACT`).
