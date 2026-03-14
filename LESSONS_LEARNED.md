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

**Open issues remaining: 10** (ISS-002, 003, 005, 008, 011, 013, 014, 022, 023 + 3 new: 025, 026, 027)

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
