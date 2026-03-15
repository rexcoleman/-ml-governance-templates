# govML — Lessons Learned & Improvement Log

> **Purpose:** Capture what works, what doesn't, and what to fix in govML — sourced from real project usage. Every entry feeds the roadmap.
> **Rule:** No entry without a concrete project source and a proposed action.

---

## Active Project Sources

| Project | ID | Profile Used | Status |
|---------|-----|-------------|--------|
| Adversarial ML on IDS | FP-01 / PUB-012 | supervised + manual additions | Phase 2d complete, findings written |
| CS 7641 SL Report | — | supervised | Complete |
| CS 7641 OL Report | — | optimization | Complete |
| CS 7641 UL Report | — | unsupervised | Complete |
| CS 7641 RL Report | — | rl-agent | Complete |
| Vuln Prioritization Engine | FP-05 / PUB-043 | security-ml (v2.4) | **Pipeline complete** — all 4 RQs answered |
| Agent Security Red-Team | FP-02 / PUB-040 | security-ml (v2.4) | **Phase 0 partial** — scaffold + env done, no code |
| CS 6200 P3 IPC (parallel) | PUB-006/007 | systems-benchmark (planned) | Not started |
| CS 6200 P4 DFS (parallel) | PUB-008/009 | systems-benchmark (planned) | Not started |

---

## Issues Found

### ISS-001: OS parallel projects lacked definition rigor vs ML parallels
- **Source:** Parallel project cluster audit (2026-03-13)
- **Problem:** ML parallels had specific dataset + technique + angle. OS parallels were vague "benchmark suites" with no thesis, no workload spec, no metrics.
- **Root cause:** govML templates govern HOW to run experiments but don't force you to define WHAT you're building. No "project definition" template exists.
- **Impact:** Projects start without clear research questions → scope creep → weak artifacts.
- **Resolution:** Manually wrote specific theses for IPC Transport Benchmark and Distributed Consistency Benchmark in the audit doc.
- **Proposed fix:** Consider a lightweight `PROJECT_BRIEF.tmpl.md` that forces: thesis statement, workload/data definition, success criteria, and cluster targets before any code is written.
- **Status:** IDENTIFIED — not yet templated

### ISS-002: systems-benchmark profile covers threads but not IPC/RPC/distributed
- **Source:** CS 6200 P3/P4 deep dive (2026-03-13)
- **Problem:** CONCURRENCY_TESTING_SPEC covers threads only. No governance for shared memory lifecycle, socket protocols, gRPC streaming patterns, or distributed consistency models.
- **Quantified gap:** 90%+ for single-machine threading, ~50% for IPC/RPC/distributed systems.
- **Impact:** OS parallel projects can't use full govML pipeline for their core contribution areas.
- **Resolution:** Documented gap. Strategy: ship projects first, extract templates second.
- **Proposed fix:** 3 new templates for v2.4/v3.0:
  - `IPC_PROTOCOL_SPEC` — resource lifecycle, naming, cleanup verification
  - `RPC_SERVICE_CONTRACT` — proto governance, streaming, deadlines, status codes
  - `DISTRIBUTED_CONSISTENCY_SPEC` — consistency model selection, conflict resolution, partition behavior
- **Status:** ON ROADMAP (v3.0)

### ISS-003: PERFORMANCE_BENCHMARKING_SPEC assumes local-only timing
- **Source:** CS 6200 P4 deep dive (2026-03-13)
- **Problem:** Template has no guidance for RPC round-trip measurement, network jitter, or client-server clock skew.
- **Impact:** Distributed systems benchmarks need different measurement methodology than local micro-benchmarks.
- **Proposed fix:** Add network latency measurement addendum to existing template.
- **Status:** ON ROADMAP (v2.4)

### ISS-004: supervised profile missing ADVERSARIAL_EVALUATION for security projects
- **Source:** FP-01 setup (2026-03-13)
- **Problem:** Had to manually copy ADVERSARIAL_EVALUATION, DECISION_LOG, and TEST_ARCHITECTURE beyond the supervised profile. Security ML projects need adversarial evaluation by default.
- **Impact:** Extra manual step, easy to forget.
- **Proposed fix:** Either (a) create a `security-ml` profile that extends supervised with ADVERSARIAL_EVALUATION + TEST_ARCHITECTURE, or (b) add a `--extras` flag to init_project.sh for adding individual templates on top of a profile.
- **Status:** RESOLVED (implemented in govML templates, 2026-03-14)

### ISS-005: No profile covers self-directed research projects (no rubric/FAQ)
- **Source:** Parallel project planning (2026-03-13)
- **Problem:** RUBRIC_TRACEABILITY assumes an external rubric. Self-directed projects (parallel projects, portfolio pieces) have research questions instead. The Research Question Traceability appendix was added (v2.3) but it's buried in an appendix, not the default flow.
- **Impact:** Self-directed projects skip traceability entirely because the template looks academic.
- **Proposed fix:** Either (a) auto-detect from project.yaml (if no `rubric` section → use RQ traceability), or (b) create separate `RESEARCH_QUESTION_TRACEABILITY.tmpl.md` that's the default for non-academic profiles.
- **Status:** IDENTIFIED

### ISS-006: project.yaml.example uses academic examples only
- **Source:** FP-01 setup (2026-03-13)
- **Problem:** The example shows CS 7643 homework structure. Non-academic projects (frontier pipeline, open-source research) have different authority hierarchies, no course field, different phase structures.
- **Impact:** Had to rewrite project.yaml from scratch rather than adapting the example.
- **Proposed fix:** Add a second example: `project.yaml.research-example` showing a self-directed security ML project.
- **Status:** IDENTIFIED

---

## What's Working Well

### WIN-001: Template reuse across 4 ML projects (SL, OL, UL, RL)
- **Source:** CS 7641 all 4 reports
- **Evidence:** Same template set, same governance patterns, different data/techniques. Templates required zero modification across projects.
- **Lesson:** The abstraction level is right for ML projects. Don't over-specialize.

### WIN-002: CLAUDE_MD.md is the highest-leverage single template
- **Source:** All projects
- **Evidence:** When CLAUDE_MD is filled, every Claude Code session starts context-aware. When it's a raw placeholder, the first 10 minutes of every session are wasted on orientation.
- **Lesson:** Filling CLAUDE_MD should be the FIRST thing done after init, not the last. Consider making init_project.sh prompt for key values interactively.

### WIN-003: Audit generators (G13-G16) eliminated manual audit cycles
- **Source:** CS 7641 UL (7 cycles, 49+ findings) vs RL (14 cycles, 30+ findings)
- **Evidence:** UL/RL audit cycles were the dominant workflow bottleneck. Automated auditors catch the same issues in seconds.
- **Lesson:** Automate the pain. The audit generators were built because manual auditing was miserable.

### WIN-004: systems-benchmark profile shipped in one session
- **Source:** govML v2.3 development (2026-03-13)
- **Evidence:** 3 new templates + 5 adaptations + profile + all supporting files in a single focused session.
- **Lesson:** The template structure is composable enough to extend quickly. Good sign for IPC/RPC/distributed templates.

### WIN-005: Seed protocol + sanity checks catch real bugs
- **Source:** CS 7641 UL (8.6x eigenvalue transcription error caught by G14)
- **Evidence:** Data-report consistency checker found a number in the report that didn't match the actual output.
- **Lesson:** Numeric consistency checking is not optional. It catches errors humans miss.

### WIN-006: Parallel agent execution dramatically speeds scaffolding
- **Source:** FP-01 setup + parallel project audit (2026-03-13)
- **Evidence:** Launched 3-4 Explore agents in parallel to review frameworks, personal docs, frontier theses simultaneously. Audit of 2 OS projects (P3/P4) ran in parallel with govML readiness check and existing audit review. Saved ~20 minutes per round.
- **Lesson:** Any phase with independent research tasks should spawn parallel agents. The pattern: "gather from N sources → synthesize → write."

---

## Parallelization Opportunities

Places where Claude Code agents can run in parallel for maximum throughput:

### Project Setup Phase
| Parallel Group | Agent 1 | Agent 2 | Agent 3 |
|---------------|---------|---------|---------|
| Scaffolding | `init_project.sh` + template copy | Write project.yaml | Write CLAUDE_MD.md |
| Data acquisition | Download/transfer data | Create env (conda) | Write preprocessing code |
| Validation | Run `check_data_ready.py` | Run `verify_env.sh` | Write leakage/determinism tests |

### Research / Audit Phase
| Parallel Group | Agent 1 | Agent 2 | Agent 3 |
|---------------|---------|---------|---------|
| Framework review | Read problem statement + frontier | Read frameworks + governance | Read personal docs + brand |
| Project deep dive | Read project A source docs | Read project B source docs | Read govML readiness |
| Audit update | Update audit doc | Update frontier pipeline | Update LESSONS_LEARNED |

### Experiment Phase
| Parallel Group | Agent 1 | Agent 2 | Agent 3 |
|---------------|---------|---------|---------|
| Baseline training | Train classifier models | Train anomaly detectors | Write evaluation metrics code |
| Adversarial | Run unconstrained attacks | Run constrained attacks | Write budget curve plotting |
| Defense eval | Train adversarial defenses | Run adaptive attacks | Generate figures |

### Key Rule
**Never parallelize tasks with data dependencies.** E.g., don't run adversarial attacks before baselines are trained. But DO parallelize independent seeds, independent model types, and research/write tasks.

---

## Improvement Backlog (prioritized)

| Priority | Issue | Effort | Impact | Target |
|----------|-------|--------|--------|--------|
| ~~HIGH~~ | ~~ISS-004: `security-ml` profile~~ | ~~Small~~ | ~~Removes friction for security ML projects~~ | ~~RESOLVED 2026-03-14~~ |
| ~~HIGH~~ | ~~ISS-006: Non-academic project.yaml example~~ | ~~Small~~ | ~~Removes "blank page" problem for research projects~~ | ~~RESOLVED v2.4 (2026-03-14) — `project.yaml.research-example` shipped~~ |
| ~~MEDIUM~~ | ~~ISS-001: PROJECT_BRIEF template~~ | ~~Small~~ | ~~Forces project definition before code~~ | ~~RESOLVED v2.4 (2026-03-14) — `PROJECT_BRIEF.tmpl.md` shipped~~ |
| MEDIUM | ISS-005: Separate RQ traceability template | Small | Better UX for self-directed projects | v2.5 (extract from FP-05) |
| MEDIUM | ISS-002: IPC/RPC/distributed templates | Large | Extends govML to distributed systems | v3.0 |
| LOW | ISS-003: Network latency addendum | Small | Completes PERFORMANCE_BENCHMARKING_SPEC | v3.0 |
| ~~HIGH~~ | ~~ISS-007: Download script assumes direct URLs~~ | ~~Small~~ | ~~Data acquisition blocked on first real project~~ | ~~RESOLVED v2.4 (2026-03-14) — `download_method` field added to project.yaml.research-example~~ |
| MEDIUM | ISS-008: No disk/resource pre-flight check | Small | Env creation fails silently when disk full | v2.5 |
| ~~LOW~~ | ~~ISS-009: init_project.sh doesn't create project.yaml~~ | ~~Small~~ | ~~Key Layer 2 artifact missing from scaffolding~~ | ~~RESOLVED v2.4 (2026-03-14) — `--fill` flag copies + pre-fills project.yaml~~ |
| ~~MEDIUM~~ | ~~ISS-010: Feature Controllability Matrix~~ | ~~Medium~~ | ~~Security ML projects need this~~ | ~~RESOLVED 2026-03-14~~ |
| LOW | ISS-011: CICIDS2017 column names have leading spaces | Tiny | Known issue, should be in DATA_CONTRACT common pitfalls | v2.5 |
| ~~**HIGH**~~ | ~~**ISS-012: Bulk placeholder fill missing from init_project.sh**~~ | ~~**Medium**~~ | ~~**20+ min wasted per project on mechanical replacement**~~ | ~~**RESOLVED v2.4 (2026-03-14) — `--fill` reads project.yaml, substitutes across all templates**~~ |
| ~~**HIGH**~~ | ~~**ISS-020: ART gradient attacks fail on sklearn**~~ | ~~**Small**~~ | ~~**30 min wasted; redesigned attack pipeline**~~ | ~~**RESOLVED 2026-03-14**~~ |
| ~~**HIGH**~~ | ~~**ISS-021: No attack selection guide by model type**~~ | ~~**Small**~~ | ~~**Users pick wrong attack, waste time on errors**~~ | ~~**RESOLVED 2026-03-14**~~ |
| MEDIUM | ISS-013: setuptools ≥72 breaks ART (pkg_resources) | Tiny | Pin in env template known-issues section | v2.5 |
| MEDIUM | ISS-014: PyTorch default install pulls CUDA on CPU VMs | Small | Add GPU checkbox + CPU-only pattern to ENV_CONTRACT | v2.5 |
| ~~MEDIUM~~ | ~~ISS-015: No decision-logging reminder at phase gates~~ | ~~Small~~ | ~~Add DECISION_LOG checklist item to each phase~~ | ~~RESOLVED v2.4 (2026-03-14) — mandatory at every phase gate~~ |
| MEDIUM | ISS-022: Attack code duplicated between attack + defense scripts | Small | Factor shared attack generation into utility module | v2.5 |
| LOW | ISS-023: Stratified split min-class formula in DATA_CONTRACT | Tiny | Prevents multi-seed crash on rare classes | v2.5 |
| ~~**CRITICAL**~~ | ~~**ISS-024: Publication pipeline template**~~ | ~~**Small**~~ | ~~**Governance for the highest-leverage brand activity**~~ | ~~**RESOLVED v2.4 (2026-03-14) — `PUBLICATION_PIPELINE.tmpl.md` shipped, reprioritized LOW→CRITICAL**~~ |
| MEDIUM | ISS-025: SSH key / git push not checked in Phase 0 preflight | Tiny | Blocks push at end of project (ISS-017 recurrence) | v2.5 |
| MEDIUM | ISS-026: No CLAUDE.md auto-fill from project.yaml | Small | CLAUDE_MD.md still has raw placeholders after --fill | v2.5 |
| LOW | ISS-027: No `--sample-frac` convention in SCRIPT_ENTRYPOINTS_SPEC | Tiny | Smoke testing pattern (WIN-011) not codified in templates | v2.5 |
| **HIGH** | **ISS-039: No compute/storage assessment before project kickoff** | **Medium** | **Disk full 3x (FP-01, FP-02, FP-05). 75+ min wasted + mid-project Azure disk provisioning. Blocks Phase 0.** | **v2.5 — ENV_CONTRACT §2b + project.yaml infra section + G6 preflight** |

---

## Issues Found (continued)

### ISS-007: Data download scripts assume direct URLs
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Problem:** `download_data.sh` assumed CICIDS2017 has stable direct-download URLs. The official CIC portal requires a registration form; the old iscxdownloads URLs are dead.
- **Impact:** Phase 0 gate blocked. Had to manually download from browser and scp to VM.
- **Proposed fix:** DATA_CONTRACT should document the download method (direct URL, API, manual portal, Kaggle CLI) as a first-class field. `download_data.sh` template should include a manual download fallback path as the PRIMARY path, not a last resort.
- **Status:** IDENTIFIED

### ISS-008: No disk/resource pre-flight check in Phase 0
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Problem:** `conda env create` ran for minutes then failed with "No space left on device." No pre-check warned about insufficient disk space. Wasted time + left a partial env that had to be cleaned up.
- **Impact:** 30+ minutes wasted. Had to manually diagnose, clean cache, remove old envs, retry.
- **Proposed fix:** Add a disk space check to `verify_env.sh` or create a `scripts/preflight.sh` that checks: (1) available disk ≥ N GB, (2) available RAM ≥ N GB, (3) conda/pip cache size, (4) no partial envs from failed installs. Run this BEFORE `conda env create`.
- **Status:** IDENTIFIED

### ISS-009: init_project.sh doesn't scaffold project.yaml
- **Source:** FP-01 setup (2026-03-13)
- **Problem:** `init_project.sh --profile supervised` copies 12 templates to `docs/` but does NOT copy `project.yaml.example` to the project root. The `--generate` flag exists but requires project.yaml to already be filled — chicken-and-egg. Had to manually write project.yaml from scratch.
- **Impact:** Layer 2 (generators) is invisible to new projects. Most users will never discover it.
- **Proposed fix:** `init_project.sh` should always copy `project.yaml.example` → `project.yaml` with profile-appropriate defaults pre-filled (project name from dirname, profile from flag, seeds from default). The `--generate` flag then runs generators on this pre-filled yaml.
- **Status:** IDENTIFIED

### ISS-012: Filling 16 templates with project-specific values is tedious and error-prone
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Problem:** After `init_project.sh`, every template has `{{PLACEHOLDER}}` values. Filling authority hierarchy, project name, seeds, and tier docs across 16 files required 30+ individual find-and-replace operations. Easy to miss one, inconsistent if done manually.
- **Root cause:** init_project.sh copies templates verbatim — it doesn't accept project metadata and substitute.
- **Impact:** 20+ minutes of mechanical replacement. ISS-009 (no project.yaml scaffolding) compounds this — if project.yaml existed, a script could read it and fill all templates automatically.
- **Proposed fix:** `init_project.sh --fill` flag that reads project.yaml and performs bulk substitution of common placeholders (PROJECT_NAME, TIER1/2/3_DOC, PYTHON_VERSION, ENV_NAME, ENV_FILE, DEFAULT_SEED, SEED_LIST) across all copied templates. Remaining content placeholders stay as `{{...}}` for phase-specific filling.
- **Status:** IDENTIFIED — highest-leverage UX improvement for govML

### ISS-010: No template for adversarial feature controllability analysis
- **Source:** FP-01 Phase 1 preprocessing (2026-03-13)
- **Problem:** ADVERSARIAL_EVALUATION template covers attack methods and evaluation protocol but doesn't have a section for documenting which features are attacker-controllable vs defender-observable. Had to hand-code `ATTACKER_CONTROLLABLE_FEATURES` and `DEFENDER_OBSERVABLE_ONLY` lists in preprocessing.py. This is the core differentiator of the project (realistic constraints) but has no governance structure.
- **Impact:** The most important domain knowledge in the project (which features an attacker can actually manipulate) is buried in source code instead of a governed document.
- **Proposed fix:** Add a "§3.1 Feature Controllability Matrix" section to ADVERSARIAL_EVALUATION template: table of features with controllability classification (attacker-controlled, defender-only, environment), rationale for each, and reference to domain expertise source.
- **Status:** RESOLVED (implemented in govML templates, 2026-03-14)

### ISS-011: Known dataset quirks not captured in DATA_CONTRACT
- **Source:** FP-01 Phase 1 preprocessing (2026-03-13)
- **Problem:** CICIDS2017 has well-known issues: leading spaces in column names, inf values in Flow Bytes/s and Flow Packets/s, inconsistent label whitespace. These are documented in dozens of papers but not in any govML template.
- **Impact:** Every new user of this dataset wastes 30 minutes rediscovering the same cleaning steps.
- **Proposed fix:** Add a "Known Dataset Issues" section to DATA_CONTRACT template (or a companion `DATA_ERRATA.md`) for recording dataset-specific quirks discovered during EDA.
- **Status:** IDENTIFIED

### ISS-013: setuptools ≥72 breaks ART import (pkg_resources removed)
- **Source:** FP-01 Phase 0 env creation (2026-03-13)
- **Problem:** conda installed setuptools 82.0.1 which removed `pkg_resources`. ART 1.17.1 imports `from pkg_resources import packaging` during its init chain (via `pytorch_deep_speech.py`). Import fails with `ModuleNotFoundError`.
- **Impact:** `verify_env.sh` fails even though pip reports ART installed successfully. Confusing for users.
- **Proposed fix:** Pin `setuptools<72` in environment.yml for any project using ART. Consider adding a "known compatibility issues" section to ENVIRONMENT_CONTRACT for documenting package interaction bugs.
- **Status:** RESOLVED (pinned setuptools<72 in FP-01)

### ISS-014: PyTorch default pip install pulls CUDA (~2GB) on CPU-only VMs
- **Source:** FP-01 Phase 0 env creation (2026-03-13)
- **Problem:** `torch==2.1.2` via pip defaults to CUDA build (~2GB). On a CPU-only Azure B2ms (29GB disk), this fills the disk. CPU-only variant (`torch==2.1.2+cpu` with `--extra-index-url`) is 185MB — 10x smaller.
- **Impact:** Two failed env creation attempts, ~45 minutes wasted on disk cleanup.
- **Proposed fix:** ENVIRONMENT_CONTRACT should have a checkbox: "Is GPU required? If No, use CPU-only PyTorch variant." Template should include the `--extra-index-url` pattern for CPU-only installs.
- **Status:** RESOLVED (switched to CPU-only in FP-01)

### ISS-015: No DECISION_LOG template usage guidance in IMPLEMENTATION_PLAYBOOK
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Problem:** Made 3+ tradeoff decisions during Phase 0 (dataset source, CPU-only torch, setuptools pin) but the IMPLEMENTATION_PLAYBOOK doesn't remind you to log decisions at each phase gate. Decisions get buried in conversation history instead of the governed log.
- **Impact:** Decision rationale lost; future sessions can't understand why choices were made.
- **Proposed fix:** Add "Log decisions made this phase in DECISION_LOG" as a checklist item to every phase gate in IMPLEMENTATION_PLAYBOOK.
- **Status:** IDENTIFIED

---

## What's Working Well (continued)

### WIN-007: CPU-only PyTorch variant enables small-VM development
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Evidence:** After switching from default torch (2GB) to torch+cpu (185MB), env creation succeeded on a 29GB disk with 6.1GB free. 10x size reduction with zero functionality loss for this project.
- **Lesson:** Always start CPU-only. Only add CUDA when GPU experiments are planned.

### WIN-008: verify_env.sh catches real issues early
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Evidence:** Script caught ART import failure immediately, which led to the setuptools fix. Without it, the failure would have surfaced during experiment execution (harder to debug).
- **Lesson:** Environment verification scripts are highest-leverage Phase 0 artifact. The 5 minutes to write them saves hours of debugging later.

### WIN-009: DECISION_LOG (ADR format) forces structured thinking on tradeoffs
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Evidence:** Writing ADR-0001–0003 (data source, CPU torch, setuptools pin) exposed that the TRADEOFF_LOG captured the "what" but not the "consequences" or "contracts affected." ADR format is richer.
- **Lesson:** For publication-track projects, use full ADR format (DECISION_LOG) not just TRADEOFF_LOG. The "Contracts Affected" section is the key differentiator — it forces you to think about what else breaks.

### WIN-011: Smoke testing with --sample-frac 0.01 catches bugs 10x faster
- **Source:** FP-01 Phase 2a (2026-03-14)
- **Evidence:** Running baselines on 1% data (28K rows, ~4 min) caught 3 bugs: missing return values, non-contiguous labels, label_names mismatch. Full data (283K) would have taken 30+ minutes per failed attempt.
- **Lesson:** Always smoke test with tiny data before full runs. Add `--sample-frac` flag to every experiment script as a standard pattern.

### WIN-012: Full adversarial ML pipeline (EDA → baselines → attacks → defenses → findings) in one session
- **Source:** FP-01 Phases 1-2d (2026-03-14)
- **Evidence:** Completed entire pipeline from raw data to FINDINGS.md in a single 3-hour session. 7 commits, all hypotheses resolved, 3 defenses evaluated, publication-ready findings written.
- **Lesson:** govML templates + Claude Code agents + smoke testing pattern = research velocity multiplier. The key accelerators: (1) smoke test at 1% data first, (2) parallelize independent seeds, (3) fix bugs on small data before scaling up.

### WIN-013: Feature controllability as a novel defense pattern for security ML
- **Source:** FP-01 Phase 2d (2026-03-14)
- **Evidence:** The 57/14 controllable/observable feature split enabled constraint-aware detection (100% detection rate on noise attacks). This is the project's core insight: splitting features by who controls them creates an architectural defense that doesn't depend on learned patterns.
- **Lesson:** Security ML projects should always analyze feature controllability BEFORE designing attacks. This should be a first-class concept in ADVERSARIAL_EVALUATION (ISS-010). The "Feature Controllability Matrix" is now the most valuable section we could add to the template.

### WIN-014: 16/32 templates activated = right-sized governance for single-person research
- **Source:** FP-01 template utilization audit (2026-03-14)
- **Evidence:** Used all 11 supervised profile templates + 5 manual additions. Did NOT force-fit systems-benchmark, RL, or management templates. The 16 unused templates were correctly identified as not applicable.
- **Lesson:** Profile system works as designed. Don't chase 100% template coverage — chase 100% of RELEVANT template coverage. The supervised + security-ml combo is the right profile for adversarial ML projects.

### WIN-015: Feature Controllability Matrix (§3.2) is publishable govML IP
- **Source:** FP-01 ADVERSARIAL_EVALUATION §3.2 (2026-03-14)
- **Evidence:** The 57/14 controllable/observable feature split section we added to ADVERSARIAL_EVALUATION doesn't exist in any standard adversarial ML framework (ART, CleverHans, Foolbox). It's a novel contribution that maps domain knowledge (TCP/IP protocol constraints) to adversarial ML threat modeling.
- **Lesson:** The highest-value govML additions come from encoding domain expertise that generic ML frameworks miss. Feature controllability should be promoted to a first-class template section in ADVERSARIAL_EVALUATION v2.4.

### WIN-010: check_data_ready.py with SHA-256 checksums creates reproducibility anchor
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Evidence:** Script validated all 8 CSVs (2.83M rows) and wrote checksums to `data/checksums.sha256`. Any future data corruption or accidental modification will be caught instantly.
- **Lesson:** Data validation + checksum on first load should be a Phase 0 gate for every project. 5 minutes of script writing saves hours of debugging "why did my results change?"

---

## Issues Found (continued, Phase 0 → Phase 1 transition)

### ISS-016: No govML template for EDA artifact governance
- **Source:** FP-01 Phase 1 (2026-03-13)
- **Problem:** EDA produces plots and summary JSON but there's no template governing what EDA artifacts MUST contain. Each project invents its own EDA structure.
- **Impact:** Hypothesis formulation has no checklist of EDA evidence to cite.
- **Proposed fix:** Add an EDA_ARTIFACT_SPEC template: required plots (class distribution, correlation, feature importance), required summary fields, link to HYPOTHESIS_CONTRACT §4 evidence requirements.
- **Status:** IDENTIFIED

### ISS-018: Preprocessing pipeline returned metadata only, not arrays
- **Source:** FP-01 Phase 2a baseline training (2026-03-14)
- **Problem:** `run_preprocessing_pipeline()` returned a metadata dict (row counts, label map) but not the actual X/y arrays needed for model training. Had to retrofit return values after train_baselines.py failed.
- **Impact:** Extra debugging cycle. Every downstream script needs the actual data, not just metadata.
- **Proposed fix:** SCRIPT_ENTRYPOINTS_SPEC should define the return contract for preprocessing pipelines: must return at minimum X_train, y_train, X_test, y_test, label_names, feature_cols.
- **Status:** RESOLVED (retrofitted in FP-01)

### ISS-019: XGBoost requires contiguous class labels after rare class removal
- **Source:** FP-01 Phase 2a baseline training (2026-03-14)
- **Problem:** After dropping Infiltration class (1 sample at 1% sample rate), label_encoded had a gap (0-7, 9-12). XGBoost expects 0..N-1 contiguous labels. Had to add label remapping.
- **Impact:** Runtime crash during training. Required understanding XGBoost internals to diagnose.
- **Proposed fix:** Add "Class Label Remapping" section to DATA_CONTRACT §4: when dropping rare classes, always remap to contiguous integers.
- **Status:** RESOLVED (added remap in preprocessing.py)

### ISS-020: ART gradient-based attacks (FGSM/PGD) fail on sklearn models
- **Source:** FP-01 Phase 2b adversarial attacks (2026-03-14)
- **Problem:** `art.attacks.evasion.FastGradientMethod` and `ProjectedGradientDescent` require models that implement `LossGradientsMixin`. sklearn's RF and XGBoost don't provide gradients — they're tree ensembles, not differentiable. ART raises `EstimatorError: FastGradientMethod requires a classifier that provides loss gradients`.
- **Impact:** Had to redesign the entire attack pipeline. Switched from gradient-based to zeroth-order (ZOO, HopSkipJump) and noise baseline. Lost ~30 minutes debugging before understanding the root cause.
- **Root cause:** ADVERSARIAL_EVALUATION template lists FGSM/PGD/AutoAttack as default attacks but doesn't warn that these are white-box-only and require differentiable models.
- **Proposed fix:** Add a "Model Compatibility" column to §3.1 attack table showing which attacks work with which model types. Add a decision tree: "Is your model differentiable? → Yes: use FGSM/PGD → No: use ZOO/HSJ/noise."
- **Status:** RESOLVED (implemented in govML templates, 2026-03-14)

### ISS-021: No guidance on selecting attack method by model type
- **Source:** FP-01 Phase 2b (2026-03-14)
- **Problem:** Template tells you WHAT attacks exist but not WHICH to use for your specific model type. For tabular ML with sklearn, the correct choice is ZOO/HopSkipJump (query-based) or noise baseline — but the template doesn't encode this knowledge.
- **Impact:** User picks FGSM because it's listed first, wastes time on import errors.
- **Proposed fix:** Add an "Attack Selection Guide" section to ADVERSARIAL_EVALUATION: model type → compatible attacks → recommended primary attack. E.g., "sklearn tree ensemble → ZOO (primary), HopSkipJump (validation), noise (sanity check)."
- **Status:** RESOLVED (implemented in govML templates, 2026-03-14)

### ISS-022: Attack code duplicated between adversarial_attacks.py and defenses.py
- **Source:** FP-01 Phase 2d defense evaluation (2026-03-14)
- **Problem:** Both `adversarial_attacks.py` and `defenses.py` independently generate noise perturbations. The noise generation code (rng.uniform, feature mask application) is duplicated. When we fixed the gradient attack issue in one file, had to fix it in the other too.
- **Impact:** Bug fixes must be applied twice. Risk of divergent attack implementations between attack and defense scripts.
- **Proposed fix:** SCRIPT_ENTRYPOINTS_SPEC should recommend factoring shared attack generation into a utility module (e.g., `src/attacks_utils.py`) that both attack and defense scripts import.
- **Status:** IDENTIFIED

### ISS-023: Stratified split minimum class threshold too low for multi-seed
- **Source:** FP-01 multi-seed baselines (2026-03-14)
- **Problem:** `min_members=3` threshold worked for seed=42 but failed for seed=456. Heartbleed class had 3 samples; after the 70/30 train/(val+test) split, only 1 sample landed in val+test, breaking the second stratified split. Had to raise threshold to 7.
- **Impact:** Multi-seed runs crashed at seed 456. Required code fix and full re-run.
- **Root cause:** Threshold was based on "at least 1 per split" but didn't account for the two-stage split (70/30 then 50/50 of remainder). With 3 samples and 30% test allocation, you can get 0 or 1 in the smaller portion.
- **Proposed fix:** DATA_CONTRACT §4 should include a formula: `min_members >= ceil(1 / min(split_ratios)) * 2`. For 70/15/15 splits, that's `ceil(1/0.15) * 2 = 14`. Or simpler: just use `min_members=10` as a safe default for any 3-way stratified split.
- **Status:** RESOLVED (raised to 7 in FP-01; formula not yet in template)

### ISS-024: No govML template for blog/talk publication pipeline
- **Source:** FP-01 Phase 2d completion (2026-03-14)
- **Problem:** PUBLICATION_BRIEF covers project metadata (audience, competencies) but not the content pipeline for shipping a blog post or conference talk. Portfolio projects need: draft skeleton → review → submit workflow. Had to create blog/ directory and draft ad-hoc.
- **Impact:** Publication is the highest-leverage brand activity but has no governance support.
- **Proposed fix:** Lightweight `PUBLICATION_PIPELINE.tmpl.md` template: target venue, submission deadline, draft outline, review checklist, submission tracker.
- **Status:** IDENTIFIED

### ISS-017: Git + GitHub setup not part of Phase 0 gate
- **Source:** FP-01 Phase 0 (2026-03-13)
- **Problem:** Got to end of Phase 0 with all gates passed but couldn't push to GitHub — SSH key not registered. Git init and remote setup should be a Phase 0 checklist item.
- **Impact:** Provenance tracking (git SHA) and collaboration blocked until SSH is configured.
- **Proposed fix:** Add "Git remote configured and test push succeeds" to Phase 0 gate in IMPLEMENTATION_PLAYBOOK.
- **Status:** IDENTIFIED

---

## What's Working Well (continued — v2.4 session)

### WIN-016: --fill bulk substitution works on first test — 20 files filled in <1 second
- **Source:** govML v2.4 development (2026-03-14)
- **Evidence:** `init_project.sh --profile security-ml --fill` on FP-05: 21 templates copied, 20 files had common placeholders filled, 158 unique content placeholders remain for phase-specific filling. Total wall time: <1 second for substitution.
- **Lesson:** The project.yaml → template substitution design was correct. Reading YAML with grep/sed (no Python dependency) keeps init_project.sh portable.

### WIN-017: PROJECT_BRIEF forces thesis-first thinking — changes how projects start
- **Source:** FP-05 scaffolding (2026-03-14)
- **Evidence:** FP-05 PROJECT_BRIEF was filled with thesis, 4 RQs, scope, 4 data sources, cluster targets, architecture diagram, and pre-project technical decisions BEFORE any code was written. Contrast with FP-01 where we jumped to code and wrote the thesis retroactively.
- **Lesson:** The template doesn't just document — it changes behavior. "What am I proving and who is it for?" before "what code do I write?" is the difference between building artifacts and building a brand. PROJECT_BRIEF should be the FIRST document filled in every project, before ENVIRONMENT_CONTRACT.

### WIN-018: PUBLICATION_PIPELINE governs the entire distribution workflow
- **Source:** govML v2.4 design (2026-03-14)
- **Evidence:** PUBLICATION_PIPELINE includes: voice check (builder not pundit), architecture diagram requirement, distribution checklist (Hugo → Substack → dev.to → Hashnode → LinkedIn → Mastodon → HN), post-publication engagement checklist. This is the template that was most conspicuously missing from FP-01.
- **Lesson:** ISS-024 was rated LOW in the original backlog because it was classified as "publishing" not "governance." Reprioritizing to CRITICAL was the right call — publication is the highest-leverage brand activity and had ZERO governance. The irony of a governance framework that doesn't govern its own distribution was the key insight.

### WIN-019: Brand strategy analysis revealed 3 critical govML gaps simultaneously
- **Source:** Brand strategy v2.0 development (2026-03-14)
- **Evidence:** Reviewing the brand strategy through a skills lens simultaneously revealed: (1) ISS-024 as CRITICAL (no publication governance), (2) ISS-001 as HIGH (no thesis-first project definition), (3) ISS-012 as HIGH (placeholder tedium blocks rapid project iteration). All three were resolved in v2.4 in a single session.
- **Lesson:** Cross-referencing govML gaps against external frameworks (brand strategy, skills guide) surfaces priorities that pure internal usage doesn't reveal. The "does govML govern the thing that matters most?" question is more powerful than "what friction did I feel during experiments?"

### WIN-020: FP-05 scaffolded in <5 minutes — first full v2.4 flywheel test
- **Source:** FP-05 initialization (2026-03-14)
- **Evidence:** `init_project.sh --fill` → 21 templates copied and bulk-filled → project.yaml from research example → PROJECT_BRIEF filled with full thesis/RQs/scope/data → GitHub repo created and pushed. Total time from `mkdir` to `git push`: ~30 minutes (mostly writing the brief, not fighting tooling).
- **Lesson:** The automation flywheel is working. Compare to FP-01 where setup took most of a session due to placeholder tedium, missing project.yaml, and no publication governance. The v2.4 improvements removed all three bottlenecks.

---

## Issues Found (continued — v2.4 session)

### WIN-021: Feature controllability transfers across projects (FP-01 → FP-05)
- **Source:** FP-05 adversarial evaluation design (2026-03-14)
- **Evidence:** The attacker-controllable vs defender-observable feature split from FP-01 (network features: 57/14) transferred directly to FP-05 (CVE features: 13/11). Same conceptual framework, different domain. The adversarial_eval.py was written in ~30 minutes because the pattern was already understood.
- **Lesson:** Feature controllability is a general adversarial ML methodology, not a dataset-specific trick. Two projects demonstrating cross-domain transfer = publishable methodology.

### WIN-022: Writing all experiment scripts before data arrives maximizes parallelism
- **Source:** FP-05 Phase 0 (2026-03-14)
- **Evidence:** While NVD API download ran (~3 hours), wrote: train_baselines.py, train_models.py, run_explainability.py, adversarial_eval.py, check_data_ready.py, verify_env.sh, .gitignore — 7 scripts before any data available. When NVD finishes, entire pipeline is ready.
- **Lesson:** Script writing doesn't depend on data. Feature engineering does. Optimal Phase 0: (data download ‖ script writing ‖ governance filling). Document in IMPLEMENTATION_PLAYBOOK.

---

### WIN-023: Full FP-05 pipeline (ingest → features → baselines → models → SHAP → adversarial) in one session
- **Source:** FP-05 (2026-03-14)
- **Evidence:** 338K CVEs ingested from 3 sources, 49 features engineered, temporal split, 3 baselines + 3 ML models + SHAP + adversarial eval — all in one session. PROJECT_BRIEF + CLAUDE_MD + govML v2.4 --fill eliminated all setup friction.
- **Lesson:** govML v2.4 + thesis-first PROJECT_BRIEF + pre-written scripts = research velocity multiplier. FP-01 took multiple sessions for a simpler pipeline. FP-05 completed end-to-end in one session with a larger dataset. The flywheel is compounding.

### WIN-024: Ground truth lag as a research finding, not a failure
- **Source:** FP-05 RQ1 results (2026-03-14)
- **Evidence:** Test set (2024+ CVEs) has only 0.3% exploit rate vs 10.5% in train. ExploitDB labels for recent CVEs are incomplete — exploits exist but haven't been catalogued yet. This depresses F1 for all models. Rather than treating this as a methodological flaw, it's a finding: temporal splits expose ground truth lag, which is a real problem for production vuln prioritization systems.
- **Lesson:** Negative or unexpected results are findings if you can explain the mechanism. The blog post angle shifts from "we beat EPSS" to "here's what happens when you apply temporal discipline to vuln prediction" — more honest, more interesting, more consistent with builder-showing-work voice.

### WIN-025: Post-pipeline audit found scaler bug that improved results
- **Source:** FP-05 comprehensive audit (2026-03-14)
- **Evidence:** LogReg model was trained on scaled features but evaluated on unscaled data. Fixing the scaler persistence + application changed SHAP rankings: kw_sql_injection jumped from #16 to #8, kw_remote_code_execution from #18 to #12. The corrected results tell a BETTER story for the blog — practitioner keywords are more important than the broken version showed.
- **Lesson:** The audit caught a bug that made results WORSE for the narrative. Auditing after pipeline completion is not just quality assurance — it can improve the story. Add "post-pipeline audit" as a Phase gate before publication.

### ISS-032: StandardScaler not persisted with LogReg model
- **Source:** FP-05 audit (2026-03-14)
- **Problem:** train_models.py saved the model pickle but not the scaler. Downstream scripts (SHAP, adversarial) loaded the model and predicted on unscaled data. Results were "valid" (AUC unchanged) but SHAP attributions were wrong.
- **Impact:** SHAP feature importance was suppressed for all features — especially binary keyword features whose relative importance changes dramatically when other features are standardized. Bug made practitioner keywords look less important than they are.
- **Proposed fix:** RESOLVED — scaler now saved in pickle bundle. All consumers load and apply it.
- **Status:** RESOLVED

### ISS-033: Governance templates left partially filled after rapid pipeline execution
- **Source:** FP-05 audit (2026-03-14)
- **Problem:** HYPOTHESIS_CONTRACT, EXPERIMENT_CONTRACT, METRICS_CONTRACT, DATA_CONTRACT all still have raw placeholders. Pipeline executed correctly without filling these docs because the scripts don't read from governance docs — they read from project.yaml and hardcoded values.
- **Impact:** Governance docs are decoration, not functional. The "governance lock" step in IMPLEMENTATION_PLAYBOOK was skipped.
- **Root cause:** The rapid single-session pipeline prioritized execution velocity over governance compliance. When the CLAUDE_MD and PROJECT_BRIEF are filled, Claude Code has enough context to run experiments without the intermediate contracts.
- **Lesson:** There's a tension between govML's governance depth and single-session research velocity. For blog-track projects, consider a "lite governance" profile that requires only PROJECT_BRIEF + DECISION_LOG + PUBLICATION_PIPELINE + FINDINGS — skip the full contract suite. The full suite is for multi-week academic projects where governance prevents drift.
- **Status:** IDENTIFIED — consider "blog-track" profile for v2.5

### ISS-034: HYPOTHESIS_CONTRACT not filled before experiments (Phase 2 gate violation)
- **Source:** FP-05 audit (2026-03-14)
- **Problem:** IMPLEMENTATION_PLAYBOOK requires hypotheses committed before experiments run (Phase 2 gate). FP-05 had research questions in PROJECT_BRIEF but never translated them into formal hypotheses in HYPOTHESIS_CONTRACT.
- **Impact:** RQs were answered, but the hypothesis-first methodology (predict → experiment → resolve) was not followed. Results are valid but the process is out of compliance.
- **Proposed fix:** For blog-track projects, either (a) treat RQs in PROJECT_BRIEF as sufficient (they serve the same purpose), or (b) add a quick "hypothesis lock" step to the blog-track profile.
- **Status:** IDENTIFIED — design decision for v2.5

---

### WIN-026: govML v2.4 flywheel confirmed — FP-05 faster than FP-01
- **Source:** FP-05 completion assessment (2026-03-14)
- **Evidence:** FP-01 took multiple sessions over 2 days. FP-05 went from `mkdir` to complete FINDINGS.md with all 4 RQs answered, SHAP plots, adversarial eval, 11 ADRs, and 4 distribution formats — in a single session. The velocity improvement came from: (1) --fill eliminating placeholder tedium, (2) PROJECT_BRIEF forcing thesis-first thinking, (3) patterns transferring (smoke testing, feature controllability), (4) CLAUDE_MD giving Claude Code full context from first command.
- **Lesson:** The govML flywheel is real. Each project is faster than the last because governance patterns compound. v2.4 was the inflection point — PROJECT_BRIEF + PUBLICATION_PIPELINE changed how projects start and end. The next inflection will be v3.0 (CI/CD + agent orchestration) for P3/L4 gates.

### ISS-035: govML needs a "blog-track" lite profile
- **Source:** FP-05 governance audit + ISS-033/034 (2026-03-14)
- **Problem:** FP-05 used security-ml profile (21 templates) but only ~8 were meaningfully filled. HYPOTHESIS_CONTRACT, EXPERIMENT_CONTRACT, METRICS_CONTRACT, DATA_CONTRACT remained mostly template placeholders. The PROJECT_BRIEF + DECISION_LOG + PUBLICATION_PIPELINE + FINDINGS.md carried the project.
- **Impact:** 13 unfilled governance docs create noise in the repo. For blog-track projects (3-4 week scope, single researcher, publication as primary output), the full contract suite is overhead.
- **Proposed fix:** Create a `blog-track` profile with: PROJECT_BRIEF, DECISION_LOG, IMPLEMENTATION_PLAYBOOK (simplified), ADVERSARIAL_EVALUATION (if security), PUBLICATION_PIPELINE, CLAUDE_MD. ~8 templates instead of 21. Full profiles reserved for academic and multi-week projects.
- **Status:** IDENTIFIED — v2.5

---

### ISS-031: pyarrow missing from environment.yml
- **Source:** FP-05 build_features.py (2026-03-14)
- **Problem:** `to_parquet()` failed because pyarrow wasn't in the conda env. Had to `pip install pyarrow` ad-hoc.
- **Impact:** 5 minutes wasted on debugging. Should be in environment.yml or project.yaml known issues.
- **Proposed fix:** Add pyarrow to environment.yml for any project using parquet. Or switch to CSV (simpler, no extra dependency).
- **Status:** RESOLVED (installed manually for FP-05)

---

### ISS-028: No govML template for multi-source data ingestion
- **Source:** FP-05 Phase 0 (2026-03-14)
- **Problem:** FP-05 requires 4 data sources (NVD API, ExploitDB CSV, EPSS API, GitHub Advisory API), each with different download methods (REST API, git clone, CSV dump). No govML template captures the ingestion pattern: source → download method → rate limits → known issues → local path → metadata.json → checksum.
- **Impact:** Had to write 3 custom ingestion scripts from scratch. The pattern (paginated API → save batches → metadata.json) is reusable across projects.
- **Proposed fix:** Either (a) add an "Ingestion Sources" section to DATA_CONTRACT with fields: source name, download method, rate limits, known issues, checksum, or (b) create a `DATA_INGESTION_SPEC.tmpl.md` template for multi-source projects.
- **Status:** IDENTIFIED

### ISS-029: Feature controllability from FP-01 is a reusable cross-project pattern
- **Source:** FP-05 adversarial evaluation (2026-03-14)
- **Problem:** FP-05 reuses the feature controllability matrix from FP-01 (ATTACKER_CONTROLLABLE vs DEFENDER_OBSERVABLE_ONLY). This pattern is now in two projects but still hand-coded in each adversarial_eval.py. It should be a first-class concept in ADVERSARIAL_EVALUATION template.
- **Impact:** Code duplication across projects. New adversarial projects must rediscover the pattern.
- **Proposed fix:** The Feature Controllability Matrix section added to ADVERSARIAL_EVALUATION in v2.4 covers the documentation side. But the code-side pattern (splitting features into controllable/observable lists, evaluating defender-only models) should be a generator or utility function.
- **Status:** IDENTIFIED — extract utility after FP-05 completes

### ISS-030: project.yaml should support multiple datasets with different download methods
- **Source:** FP-05 project.yaml (2026-03-14)
- **Problem:** project.yaml.research-example has a `datasets` array but the `download_method` field was added ad-hoc. The schema isn't formalized — generators don't read it, init_project.sh doesn't use it.
- **Proposed fix:** Formalize the dataset schema in project.yaml with: name, source, download_method (enum: direct_url, api, git_clone, kaggle_cli, manual), known_issues (list), local_path, sha256. Create a `gen_data_ingestion.py` generator that reads this and produces download scripts.
- **Status:** IDENTIFIED — v3.0 candidate (G9 enhancement)

---

### ISS-025: SSH key / git push not verified in Phase 0
- **Source:** FP-05 Phase 0 (2026-03-14)
- **Problem:** Same issue as ISS-017 — `git push` failed due to SSH key not loaded in agent. Phase 0 gate in IMPLEMENTATION_PLAYBOOK now includes "Git remote configured" but doesn't verify the push actually succeeds.
- **Impact:** Blocks provenance tracking and GitHub deployment. Discovered at end of setup, not beginning.
- **Proposed fix:** Phase 0 gate should include `git push --dry-run` or `ssh -T git@github.com` as a verification command. Or add to `preflight.sh`.
- **Status:** IDENTIFIED

### ISS-026: CLAUDE_MD.md not fully auto-filled by --fill
- **Source:** FP-05 scaffolding (2026-03-14)
- **Problem:** `--fill` correctly fills PROJECT_NAME and TIER docs in CLAUDE_MD.md but the template has additional context fields (Current Phase, Phase Commands, AI Division of Labor) that are project-specific. After --fill, CLAUDE_MD still needs significant manual editing.
- **Impact:** CLAUDE_MD is the highest-leverage single template (WIN-002). If it's not filled, every Claude Code session wastes 10 minutes on orientation.
- **Proposed fix:** Either (a) generate CLAUDE_MD from project.yaml (read phases, experiments, authority) or (b) add a `gen_claude_md.py` generator that reads project.yaml and produces a fully-filled CLAUDE_MD.
- **Status:** IDENTIFIED — high value for v2.5

### ISS-027: Smoke testing pattern (--sample-frac) not codified in templates
- **Source:** FP-01 WIN-011 + FP-05 PROJECT_BRIEF (2026-03-14)
- **Problem:** The `--sample-frac 0.01` pattern was the single most impactful development practice discovered in FP-01. It catches bugs 10x faster. But it's not mentioned in SCRIPT_ENTRYPOINTS_SPEC, IMPLEMENTATION_PLAYBOOK, or any template — it only exists in LESSONS_LEARNED.
- **Impact:** Future projects won't discover this pattern unless they read LESSONS_LEARNED. It should be a first-class recommendation.
- **Proposed fix:** Add "Smoke Test Convention" section to SCRIPT_ENTRYPOINTS_SPEC: "Every experiment script SHOULD accept `--sample-frac` (default 1.0). Before running any full experiment, smoke test with `--sample-frac 0.01` to catch bugs on 1% data."
- **Status:** IDENTIFIED

---

## Resolved Issues Summary (v2.4)

v2.4 resolved **9 issues** in a single session:

| Issue | Resolution |
|-------|-----------|
| ISS-001 | PROJECT_BRIEF.tmpl.md — forces thesis, RQs, scope, cluster targets before code |
| ISS-006 | project.yaml.research-example — non-academic self-directed research config |
| ISS-007 | download_method field in project.yaml.research-example (direct_url/api/manual/kaggle) |
| ISS-009 | --fill flag copies project.yaml automatically |
| ISS-012 | --fill reads project.yaml, bulk-substitutes common placeholders across all templates |
| ISS-015 | Decision logging mandatory at every phase gate in IMPLEMENTATION_PLAYBOOK |
| ISS-017 | Git remote check added to Phase 0 gate |
| ISS-024 | PUBLICATION_PIPELINE.tmpl.md — governs entire blog workflow from draft to distribution |
| security-ml | Profile updated: 19 → 21 templates (added PROJECT_BRIEF + PUBLICATION_PIPELINE) |

**Open issues remaining: 14** (ISS-002, 003, 005, 008, 011, 013, 014, 022, 023, 025, 026, 027, 036, 037, 038, 039)

---

## Issues Found (continued — FP-02 scaffolding session)

### ISS-036: Web fetch during scaffolding killed session momentum
- **Source:** FP-02 Phase 0 scaffolding (2026-03-14)
- **Problem:** Session attempted to web-fetch external resources (likely OWASP/ATLAS taxonomy or agent framework docs) during Phase 0 scaffolding. The fetch hung, user quit the session, and all in-flight work (generator runs, code scaffolding) was lost.
- **Impact:** Phase 0 left 60% complete — conda env and directory structure survived (committed), but generators never ran and no code was written.
- **Root cause:** No separation between "scaffolding" (zero internet needed) and "research" (internet required). IMPLEMENTATION_PLAYBOOK doesn't distinguish these sub-phases.
- **Proposed fix:** Split Phase 0 into two explicit sub-phases in IMPLEMENTATION_PLAYBOOK:
  - **Phase 0a (Scaffold — offline):** conda env, directory structure, govML generators, base code templates. Zero internet.
  - **Phase 0b (Research — online):** taxonomy review, framework docs, literature survey. Tolerates fetch failures.
- **Lesson:** Never mix scaffolding and research in the same session. Scaffold first (commit), research second.
- **Status:** IDENTIFIED — IMPLEMENTATION_PLAYBOOK enhancement

### ISS-037: govML generators not run despite project.yaml being ready
- **Source:** FP-02 Phase 0 (2026-03-14)
- **Problem:** project.yaml was written and committed, but `generate_all.py` / `init_project.sh --generate` was never run. The scripts/ directory is empty. Generators would have produced sweep.sh, verify_manifests.py, and check_phase_*.sh for free.
- **Impact:** Lost ~10 minutes of generated infrastructure. Next session must run generators before writing any manual scripts.
- **Root cause:** The scaffolding session jumped from "docs deployed" to "let me research attacks" without running the generators in between. No checklist enforced the generator step.
- **Proposed fix:** Add "Run generators (G1/G5/G6)" as an explicit Phase 0 gate item in IMPLEMENTATION_PLAYBOOK, immediately after project.yaml is written.
- **Status:** IDENTIFIED — IMPLEMENTATION_PLAYBOOK gate enhancement

### ISS-038: ISS-035 (blog-track profile) directly relevant to FP-02
- **Source:** FP-02 scaffolding audit (2026-03-14)
- **Problem:** FP-02 deployed 22 governance docs but is a blog-track project (4-6 week scope, single researcher, publication as primary output). ISS-033/034 from FP-05 showed that intermediate contracts (HYPOTHESIS_CONTRACT, EXPERIMENT_CONTRACT, METRICS_CONTRACT) stay unfilled in rapid single-session execution. FP-02 will likely repeat this pattern.
- **Impact:** If FP-02 follows the FP-05 pattern, ~13 of 22 governance docs will be decoration. The core 8 (PROJECT_BRIEF, DECISION_LOG, IMPLEMENTATION_PLAYBOOK, ADVERSARIAL_EVALUATION, CLAUDE_MD, PUBLICATION_PIPELINE, RISK_REGISTER, TEST_ARCHITECTURE) will do the actual governance work.
- **Proposed fix:** Don't retroactively strip FP-02's docs — they're already deployed and committed. Instead, use FP-02 as the third data point for the blog-track profile decision. If the same ~8 docs carry the project (as in FP-05), that confirms the profile scope for v2.5.
- **Lesson:** Three projects (FP-01, FP-05, FP-02) will have demonstrated the same "8 docs do the work, 13 are decoration" pattern. That's enough evidence to ship blog-track profile in v2.5.
- **Status:** IDENTIFIED — tracks ISS-035

---

## What's Working Well (continued — FP-02 scaffolding)

### WIN-027: govML v2.4 --fill + security-ml scaffolded FP-02 in minutes
- **Source:** FP-02 initialization (2026-03-14)
- **Evidence:** 22 docs deployed, project.yaml written, CLAUDE_MD customized, PROJECT_BRIEF filled with thesis/RQs/scope — all in the first portion of the session before the web fetch failure. Compare to FP-01 where this took most of a session.
- **Lesson:** The scaffolding flywheel continues accelerating. FP-01 (manual) → FP-05 (v2.4, fast) → FP-02 (v2.4, even faster because the pattern is internalized). The bottleneck has shifted from "setup" to "research + code."

### WIN-028: Conda env + directory structure survived session crash
- **Source:** FP-02 session recovery (2026-03-14)
- **Evidence:** After session quit, `conda env list` shows agent-redteam, `ls` shows all directories, `git log` shows the initial commit. Everything committed survived. Everything not committed (in-flight generator runs, code plans) was lost.
- **Lesson:** Commit early, commit often. The govML governance docs were committed → survived. The generator outputs were planned but not committed → lost. Phase 0 should have intermediate commits: (1) after init, (2) after generators, (3) after first smoke test.

---

## Issues Found (continued — FP-02 infrastructure session)

### ISS-039: No compute/storage requirements assessment before project kickoff
- **Source:** FP-02 Phase 0 infrastructure (2026-03-14)
- **Problem:** FP-02 scaffolding filled a 29GB OS disk to 97% (1.1GB free) before any code ran. Required emergency disk cleanup (removing completed envs, conda/pip caches) and adding a 32GB Azure data disk mid-project. The ENVIRONMENT_CONTRACT has a "Target Platform" section (§2) but it only captures OS and CPU/GPU — it doesn't assess whether the platform has enough disk, RAM, or cores for the project's workload BEFORE starting.
- **Root cause:** No template forces a compute resource assessment at project definition time. PROJECT_BRIEF defines what you'll build but not what infrastructure it needs. ENVIRONMENT_CONTRACT defines the runtime but not the capacity. The gap is between "what platform" and "is this platform big enough."
- **Impact across projects:**
  - FP-01: disk full during `conda env create` (ISS-008, ISS-014) — 45 min wasted
  - FP-02: disk 97% full, required mid-project Azure disk provisioning — 30 min wasted
  - FP-05: NVD API download (338K CVEs) nearly filled disk — caught just in time
- **Evidence of workload-to-resource mismatch patterns:**
  - **CPU-bound** (model training): FP-01 (RF/XGB on 283K rows), FP-04 (XGB on 590K rows), FP-07 (GNN) → need ≥4 cores
  - **I/O-bound** (API calls): FP-02 (agent red-teaming via Claude/OpenAI API), FP-06 (Ethereum testnet) → 2 cores fine, network is bottleneck
  - **Storage-bound** (large datasets + multiple envs): all projects on shared VM → need disk headroom assessment
  - **RAM-bound** (in-memory datasets): FP-04 (590K × 400+ features), FP-07 (molecular graphs) → need ≥16GB
- **Proposed fix:** Add a **§2b Compute Resource Assessment** section to ENVIRONMENT_CONTRACT template:

```markdown
## 2b) Compute Resource Assessment

Assess BEFORE creating the environment. If any resource is insufficient, resolve before Phase 0.

### Storage Budget
| Item | Estimated Size | Path |
|------|---------------|------|
| Conda environment | __ GB | miniconda3/envs/{{ENV_NAME}} |
| Raw data | __ GB | data/raw/ |
| Processed data | __ GB | data/processed/ |
| Model artifacts | __ GB | outputs/ |
| Experiment outputs (all seeds) | __ GB | outputs/ |
| **Total project footprint** | **__ GB** | |
| **Available disk** | **__ GB** | `df -h` |
| **Headroom after project** | **__ GB** | Must be ≥ 20% of disk |

### Compute Profile
| Dimension | Requirement | Current Platform | Sufficient? |
|-----------|-------------|-----------------|-------------|
| CPU cores | __ (CPU-bound: ≥4; I/O-bound: 2 fine) | __ cores | ☐ |
| RAM | __ GB (datasets must fit in memory for pandas) | __ GB | ☐ |
| GPU | ☐ Required ☐ Optional ☐ Not needed | __ | ☐ |
| Disk | __ GB total project footprint | __ GB free | ☐ |
| Network | ☐ API-dependent ☐ Large downloads ☐ Offline OK | __ Mbps | ☐ |

### Workload Type (check primary)
- ☐ **CPU-bound** (model training, feature engineering) → scale cores
- ☐ **I/O-bound** (API calls, web scraping) → network matters, cores don't
- ☐ **Storage-bound** (large datasets, many experiments) → add data disk
- ☐ **RAM-bound** (in-memory datasets, large feature matrices) → scale RAM

### Resolution (if insufficient)
| Gap | Fix | Cost | Time |
|-----|-----|------|------|
| Disk | Add Azure data disk / clean caches | ~$2.40/mo for 32GB SSD | 10 min |
| CPU/RAM | Resize VM (B2ms→B4ms) | ~2x monthly cost | 5 min (reboot) |
| GPU | Switch to NC-series or use cloud GPU | $$$  | 30 min |
```

- **Also add to preflight.sh generator (G6):** Auto-check disk headroom as Phase 0 gate:
  ```bash
  AVAIL_GB=$(df -BG --output=avail /home | tail -1 | tr -d ' G')
  if [ "$AVAIL_GB" -lt 5 ]; then
    echo "FAIL: Only ${AVAIL_GB}GB free. Need ≥5GB headroom."
    exit 1
  fi
  ```
- **Also add to project.yaml schema:** `infrastructure` section with storage_budget_gb, compute_profile (cpu_bound/io_bound/storage_bound/ram_bound), min_disk_gb, min_ram_gb fields. Generators can read these to produce appropriate preflight checks.
- **Status:** IDENTIFIED — ENVIRONMENT_CONTRACT §2b + project.yaml schema + G6 enhancement for v2.5

### ISS-040: Claude Code API keys cannot be reused for SDK calls
- **Source:** FP-02 Phase 0 smoke test (2026-03-14)
- **Problem:** `ANTHROPIC_API_KEY` environment variable was set by Claude Code with an internal key (starts with `sk-ant-api03-`). This key returns 401 when used by `langchain-anthropic` or the Anthropic Python SDK directly. Claude Code keys are listed on console.anthropic.com under "Claude Code" workspace but have restricted permissions — they only work for Claude Code's internal API calls.
- **Impact:** 30 minutes of debugging. User had to create a new personal API key on console.anthropic.com and update `.bashrc`. Non-obvious because the key LOOKED valid and was SET in the environment.
- **Root cause:** No govML template distinguishes between "API key for Claude Code" and "API key for your code." ENVIRONMENT_CONTRACT §API keys section doesn't exist.
- **Proposed fix:** Add "API Key Inventory" section to ENVIRONMENT_CONTRACT template for projects that make LLM API calls:
  ```markdown
  ## API Key Inventory
  | Provider | Key Type | Env Variable | Source | Verified |
  |----------|----------|-------------|--------|----------|
  | Anthropic | Personal API key | ANTHROPIC_API_KEY | console.anthropic.com → Create Key | ☐ `python -c "from anthropic import Anthropic; print(Anthropic().messages.create(...))"` |
  ```
  **Critical:** Claude Code keys (auto-created, listed under "Claude Code" workspace) ≠ personal API keys. Only personal keys work in user scripts.
- **Status:** IDENTIFIED — ENVIRONMENT_CONTRACT enhancement for v2.5

---

## What's Working Well (continued — FP-02 Phase 0 completion)

### WIN-029: --dry-run mode enables full development without API keys
- **Source:** FP-02 Phase 0 (2026-03-14)
- **Evidence:** `smoke_test_agents.py --dry-run` validated the entire framework (config loading, agent abstraction, tool registry, type system) without spending a single API call. All code was written and tested offline. API key was only needed for the final live smoke test.
- **Lesson:** Every script that makes API calls SHOULD have a `--dry-run` flag. This pattern enables: (1) offline development, (2) CI testing without API keys, (3) cost control during development. Add to SCRIPT_ENTRYPOINTS_SPEC as a recommended convention alongside `--sample-frac`.

### WIN-030: Phase 0 gate smoke test validates full stack in one command
- **Source:** FP-02 Phase 0 gate pass (2026-03-14)
- **Evidence:** `smoke_test_agents.py --agent langchain` verified: config loading → LLM client creation → tool registration → agent construction → task execution → tool calling → response capture → result parsing. One command, 2.7 seconds, complete stack validation.
- **Lesson:** Phase 0 smoke tests should exercise the FULL pipeline, not just imports. `verify_env.sh` checks imports; `smoke_test_agents.py` checks the pipeline works end-to-end. Both are needed.

### WIN-031: 3 ADRs logged at Phase 0 gate — decision discipline working
- **Source:** FP-02 DECISION_LOG (2026-03-14)
- **Evidence:** ADR-0001 (agent target abstraction), ADR-0002 (controlled tools), ADR-0003 (Claude as primary LLM). Each logged with alternatives, rationale, contracts affected, and evidence plan. ISS-015 fix (decision logging mandatory at every phase gate) is working.
- **Lesson:** Mandatory decision logging at phase gates produces D-cluster evidence (D3→D4). The "Contracts Affected" section is the highest-value part — it forces you to think about what else your decision impacts.

---

## Issues Found (continued — FP-02 full pipeline)

### ISS-041: YAML attack scenarios need parameterized payloads for multi-seed
- **Source:** FP-02 Phase 2 (2026-03-14)
- **Problem:** Attack scenarios in `attack_scenarios.yaml` use hardcoded payloads. Multi-seed runs (seed 42/123/456) replay the identical prompts — seed only affects LLM temperature randomness, not scenario variation. For true multi-seed validation, payloads should vary (e.g., different injection patterns, different target notes).
- **Impact:** Seeds 123/456 will produce correlated results, weakening the statistical claim.
- **Proposed fix:** Add a `payload_variants` list to each scenario in the YAML schema. The runner selects variant by seed index. Or: parameterize key values (target note, target file) per seed.
- **Status:** IDENTIFIED — implement before multi-seed runs

### ISS-042: Defense evaluation needs "without defense" baseline re-run in same session
- **Source:** FP-02 Phase 3 (2026-03-14)
- **Problem:** Defense comparison reads `outputs/attacks/.../summary.json` from a prior run. If attack scenarios changed between Phase 2 and Phase 3 (they did — we added scenarios and fixed evaluation), the comparison is against stale data. The "without" column may not match what the current scenarios would produce.
- **Impact:** Reduction percentages may be slightly inaccurate.
- **Proposed fix:** `run_defenses.py` should optionally re-run the undefended baseline in the same session (flag: `--with-baseline`). Or: always re-run undefended as part of defense evaluation.
- **Status:** IDENTIFIED — low priority (results are directionally correct)

---

## What's Working Well (continued — FP-02 full pipeline)

### WIN-032: Full FP-02 pipeline (Phase 0→3) completed in single session — govML flywheel compounds
- **Source:** FP-02 (2026-03-14)
- **Evidence:** 6 commits in one session: scaffold → generators → baselines → taxonomy → 19 attack scenarios → 3 defense layers → all 4 RQs answered. Compare: FP-01 took 2 sessions, FP-05 took 1 session, FP-02 took 1 session with MORE complexity (API calls, multi-layer defenses, YAML-driven scenarios).
- **Lesson:** The govML flywheel is compounding faster than expected. PROJECT_BRIEF's RQ success criteria drove the entire evaluation design — without it, we'd have built attacks without knowing when to stop. The 50% threshold from PROJECT_BRIEF became the actual pass/fail gate in run_attacks.py.

### WIN-033: PROJECT_BRIEF success criteria → code evaluation logic (direct governance-to-code traceability)
- **Source:** FP-02 run_attacks.py (2026-03-14)
- **Evidence:** PROJECT_BRIEF RQ2 says ">50% success rate = demonstrated." The `EvaluationSummary.demonstrated` property in types.py and the `evaluate_attack()` function in run_attacks.py both implement this threshold directly. The governance doc DROVE the code, not the other way around.
- **Lesson:** PROJECT_BRIEF success criteria should be machine-readable. If the criteria were in project.yaml (e.g., `success_threshold: 0.5`), generators could produce evaluation code that enforces them automatically. Consider for v3.0.

### WIN-034: Reasoning chain hijacking = novel finding with maximum brand value
- **Source:** FP-02 Phase 2 results (2026-03-14)
- **Evidence:** 100% success rate on reasoning chain hijacking — the agent follows structured step-by-step instructions that look completely benign. This is NOT in OWASP LLM Top 10 or MITRE ATLAS. It's agent-specific, novel, and the blog headline ("100% of agents followed my step-by-step attack plan").
- **Lesson:** The highest brand-value findings come from attack classes that existing frameworks DON'T cover. The taxonomy exercise (RQ1) wasn't just documentation — it identified WHERE to look for novel results.

### WIN-035: Layered defense architecture = "architect who ships" evidence
- **Source:** FP-02 Phase 3 (2026-03-14)
- **Evidence:** InputSanitizer alone: 47% reduction. ToolPermissionBoundary alone: ~0%. LayeredDefense (both): 60%. The defense-in-depth architecture IS the D-cluster evidence — it demonstrates architectural judgment (which layers to combine, why each is insufficient alone, where gaps remain).
- **Lesson:** Building the defenses produces better brand content than just finding the attacks. "Here's how they break" is interesting; "here's the defense architecture" is what hiring managers want to see from a security architect.

## Issues Found (continued — FP-02 completion)

### ISS-043: CrewAI tool integration doesn't expose tool_calls in response
- **Source:** FP-02 CrewAI target (2026-03-14)
- **Problem:** CrewAI's `crew.kickoff()` returns a string result but doesn't expose individual tool call records. The `AgentResponse.tool_calls` list is always empty for CrewAI targets. LangChain exposes tool calls in message metadata.
- **Impact:** Attack evaluation for CrewAI relies entirely on output keyword matching, not tool usage verification. This weakens the `success_tools` evaluation signal.
- **Proposed fix:** Either (a) parse CrewAI verbose logs for tool usage, or (b) instrument the tool functions themselves to record calls (decorator pattern). Option (b) is framework-agnostic and would work for AutoGen too.
- **Status:** IDENTIFIED — implement tool instrumentation for v0.2

---

## What's Working Well (continued — FP-02 completion)

### WIN-036: Attacks generalize across frameworks (LangChain 80% = CrewAI 80%)
- **Source:** FP-02 CrewAI prompt injection test (2026-03-14)
- **Evidence:** Prompt injection success rate on CrewAI (4/5 = 80%) matches LangChain (4/5 = 80%) exactly. The same attack payloads work on both frameworks with the same LLM backend (Claude Sonnet).
- **Lesson:** Agent vulnerabilities are LLM-level, not framework-level. This strengthens the thesis that adversarial control analysis is a general methodology — the attack surface is the LLM's reasoning, not the orchestration layer.

### WIN-037: matplotlib figures generated in <5 seconds — publication-ready
- **Source:** FP-02 generate_figures.py (2026-03-14)
- **Evidence:** 3 figures (attack success rates, defense comparison, controllability scatter) generated at 150 DPI in both outputs/figures/ and blog/images/. Script is rerunnable after multi-seed experiments.
- **Lesson:** Figure generation should be a script, not a notebook. Scripts are reproducible, rerunnable, and can be triggered by the CLI (`agent-redteam figures`).

### WIN-038: Full project shipped — scaffold to publication in one session
- **Source:** FP-02 complete (2026-03-14)
- **Evidence:** 10 commits from empty scaffold to: 7 attack classes, 19 scenarios, 2 agent frameworks, 3 defense layers, FINDINGS.md, blog draft, conference abstract, 3 figures, CLI tool, pyproject.toml, README, govML PUBLICATION_PIPELINE filled. All in one session. govML v2.4 flywheel + PROJECT_BRIEF thesis-first discipline = research velocity multiplier.
- **Lesson:** The govML flywheel is real and compounding. FP-01: 2 sessions. FP-05: 1 session. FP-02: 1 session with 2x complexity. The bottleneck has shifted from tooling to research quality (attack novelty, defense architecture).

---

## Revision Log

| Date | Entry | Source |
|------|-------|--------|
| 2026-03-13 | Initial: ISS-001–006, WIN-001–005 | Parallel project audit + FP-01 setup |
| 2026-03-13 | Added ISS-007–009: data download, disk preflight, project.yaml scaffolding | FP-01 Phase 0 execution |
| 2026-03-13 | Added WIN-006, parallelization map, ISS-010–012 | FP-01 Phase 0 continued |
| 2026-03-13 | Added ISS-013–015, WIN-007–008: setuptools/PyTorch compat, verify_env value | FP-01 Phase 0 env creation |
| 2026-03-13 | Added ISS-016–017, WIN-009–010: EDA governance gap, git setup gap, ADR value, checksum value | FP-01 Phase 0→1 transition |
| 2026-03-14 | Added ISS-018–019, WIN-011: pipeline return contract, label remapping, smoke testing pattern | FP-01 Phase 2a |
| 2026-03-14 | Added ISS-020–022, WIN-012–013: ART gradient attacks on sklearn, attack selection guide, code duplication, full pipeline velocity, feature controllability pattern | FP-01 Phase 2b-2d |
| 2026-03-14 | Added ISS-023–024, WIN-014–015: stratified split threshold, publication pipeline, right-sized governance, feature controllability as govML IP | FP-01 Phase 2d completion |
| 2026-03-14 | v2.4 shipped: 9 issues resolved (ISS-001,006,007,009,012,015,017,024 + security-ml). Added WIN-016–020, ISS-025–027. Backlog updated with resolved status. | v2.4 development + FP-05 scaffolding + brand strategy synthesis |
| 2026-03-14 | Added ISS-028–030, WIN-021–022: API ingestion pattern, feature controllability reuse, multi-source join pattern, data ingestion as generator candidate, NVD API key as Phase 0 decision | FP-05 Phase 0 execution |
| 2026-03-14 | Added WIN-023–024, ISS-031: full pipeline in single session, ground truth lag as finding, pyarrow missing from env | FP-05 full pipeline completion |
| 2026-03-14 | Added ISS-032–034, WIN-025: scaler persistence bug, SHAP correction reveals keyword importance, audit-driven quality improvement | FP-05 comprehensive audit |
| 2026-03-14 | Added WIN-026, ISS-035: govML ceiling analysis, blog-track profile need confirmed across 2 projects | FP-05 completion assessment + govML roadmap |
| 2026-03-14 | Added ISS-036–038, WIN-027–028: web fetch killed session (don't web-fetch during scaffolding), generators not run, blog-track profile confirmed for 3rd project, scaffolding flywheel accelerating, commit-early lesson | FP-02 Phase 0 scaffolding + recovery audit |
| 2026-03-14 | Added ISS-039: No compute/storage assessment before project kickoff. Proposed ENVIRONMENT_CONTRACT §2b (storage budget, compute profile, workload type, resolution table) + project.yaml infrastructure section + G6 preflight disk check. Evidenced across FP-01, FP-02, FP-05. | FP-02 infrastructure session — disk 97% full, added Azure data disk |
| 2026-03-14 | Added ISS-040, WIN-029–031: Claude Code keys ≠ API keys (needs onboarding doc), dry-run mode enables offline development, smoke test validates full stack in one command. Phase 0 complete with 3 ADRs logged. | FP-02 Phase 0 completion |
| 2026-03-14 | Added ISS-041–042, WIN-032–035: Full FP-02 pipeline (Phase 0→3) in single session. 4/4 RQs answered. govML PROJECT_BRIEF RQ criteria drove evaluation design. Layered defense = govML-inspired architecture. Reasoning hijack = novel finding. | FP-02 Phases 1-3 completion |
| 2026-03-14 | Added ISS-043, WIN-036–038: CrewAI target validates cross-framework attacks (80% prompt injection — same as LangChain). 3 publication-ready figures generated. CLI entry point + pyproject.toml + README shipped. PUBLICATION_PIPELINE voice check passes. All DoD items satisfied. | FP-02 project completion |
| 2026-03-14 | Added WIN-039–041: Multi-seed stable (3 seeds identical except prompt injection 80/80/100%). LLM-as-judge defense is the only layer that catches reasoning hijack (100%→33%). Full 3-layer defense: 67% avg reduction. Semantic > pattern for novel attacks. | FP-02 stretch goals |
