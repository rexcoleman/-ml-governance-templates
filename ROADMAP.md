# ML Governance Templates — Roadmap

## Version History

### v1.0 (2026-01)
- 15 core governance templates
- Manual placeholder filling
- No profiles, no init script

### v2.0 (2026-02)
- 26 templates across 4 directories (core, management, report, publishing)
- 6 quickstart profiles: minimal, supervised, optimization, unsupervised, rl-agent, full
- `init_project.sh` with `--profile` flag
- Prompt Playbook (stages 1-9) for AI-assisted customization
- Worked examples per profile
- Authority hierarchy, verification annotations, CONTRACT_CHANGE protocol

### v2.1 (2026-03) — Current
- **Layer 2: Executable scaffolding** via code generators
- `project.yaml` structured config that drives all generators
- 3 generators (G1, G5, G6) + master runner:
  - `gen_sweep.py` — experiment orchestration script from experiment matrix
  - `gen_manifest_verifier.py` — artifact integrity verification from manifest config
  - `gen_phase_gates.py` — phase gate check scripts from phase definitions
  - `generate_all.py` — single entry point that runs all generators
- **Layer 3 prototype: `orchestrate.py`** — Claude Agent SDK orchestrator
  - Agent mode: reads project.yaml, reasons about generators, validates output
  - Standalone mode: deterministic fallback (no LLM calls, works in CI)
  - Dry-run mode: shows what would be generated
  - Portable tool registry: same functions reusable in LangGraph (Sem 7)
  - Graceful fallback: if `claude-agent-sdk` not installed, runs standalone
- `CLAUDE_MD.tmpl.md` template for governed AI collaboration context
- `init_project.sh --generate` flag to run generators after template copy
- `project.yaml.example` with full schema documentation

---

## Planned: v3.0

### Layer 2 Expansion: Remaining Generators

| ID | Generator | Input Section | Output | Status |
|----|-----------|---------------|--------|--------|
| G1 | `gen_sweep.py` | `experiments` | `scripts/sweep.sh` | Done (v2.1) |
| G2 | `gen_post_compute.py` | `artifacts`, `experiments` | `scripts/post_compute.sh` | Planned |
| G3 | `gen_config_hierarchy.py` | `config` | `config/base.yaml` + layer stubs | Planned |
| G4 | `gen_leakage_tests.py` | `leakage` | `tests/test_leakage.py` | Planned |
| G5 | `gen_manifest_verifier.py` | `artifacts` | `scripts/verify_manifests.py` | Done (v2.1) |
| G6 | `gen_phase_gates.py` | `phases` | `scripts/check_phase_*.sh` | Done (v2.1) |
| G7 | `gen_determinism_tests.py` | `experiments` | `tests/test_determinism.py` | Planned |
| G8 | `gen_ci_pipeline.py` | `phases`, `experiments` | `.github/workflows/ml-gates.yml` | Planned |
| G9 | `gen_run_entrypoint.py` | `experiments` | `scripts/run_part*.py` stubs | Planned |
| G10 | `gen_report_artifacts.py` | `artifacts`, `experiments` | `scripts/make_report_artifacts.py` | Planned |
| G11 | `gen_env_setup.py` | `project` | `scripts/verify_env.sh` | Planned |
| G12 | `gen_data_loader.py` | `datasets` | `scripts/check_data_ready.py` | Planned |

### Layer 3: Agent Orchestration

Two layers of agent orchestration, progressing from lightweight to full state machine:

#### Phase 1: Claude Agent SDK (v3.0-alpha, Semester 5)

`orchestrate.py` replaces `generate_all.py` subprocess calls with Claude Agent SDK tool-use:

```python
# Instead of subprocess.run(["python", "gen_sweep.py", ...])
# The agent reads project.yaml, decides which generators to run,
# validates output, and checks phase gates — with human approval.
```

- Agent reads `project.yaml` and reasons about which generators are needed
- Generator functions exposed as agent tools (not subprocess calls)
- Agent validates generated output (file exists, syntax check, gate passes)
- Human-in-the-loop: agent reports status, human approves before experiments run
- CLAUDE.md template provides authority hierarchy and phase awareness

**Why Claude Agent SDK first:**
- Lightest-weight agent framework (Anthropic-native, single dependency)
- Natural upgrade from subprocess — same tool functions, agent decides sequencing
- Tool functions are portable to LangGraph later (no rewrite)

#### Phase 2: LangGraph State Machine (v3.0, Semester 7)

For complex multi-agent workflows (RL experiment pipelines, team governance):

```
setup → sweep → monitor_convergence → analyze → report_scaffold → verify
                      ↓ (if fails)
                 diagnose → fix → retry
```

- State machine with LLM decision nodes for conditional branching
- Specialized sub-agents: experiment-executor, audit-agent, report-scaffolder
- Shared state between graph nodes (experiment results, metrics, artifact hashes)
- Phase-locked authority: agent cannot advance past gate without human approval
- Tool functions from Phase 1 reused as LangGraph node tools

**Why LangGraph (not vanilla LangChain):**
- LangGraph = orchestration state machines. LangChain = prompt template wrappers.
- State machines match the phase-gated governance model exactly
- Conditional branching ("if gate fails → diagnose → fix → retry") is a graph, not a chain
- Skip list: vanilla LangChain (unnecessary abstraction), CrewAI (role-play paradigm doesn't match governed workflows), AutoGen (ecosystem lock-in)

### Orchestration Maturity Model

| Level | Name | Description | Version | Framework |
|-------|------|-------------|---------|-----------|
| O1 | Manual | Copy templates, fill placeholders by hand | v1.0 | — |
| O2 | Script | `init_project.sh` copies templates per profile | v2.0 | Bash |
| O3 | Gate-checked | Generators produce executable gate scripts | v2.1 | Python generators |
| O4 | Agent-assisted | Claude Agent SDK orchestrator with human-in-the-loop | v3.0-alpha | Claude Agent SDK |
| O5 | Multi-agent | LangGraph state machine with specialized sub-agents | v3.0 | LangGraph |

---

## Design Principles

1. **YAML drives code** — `project.yaml` is the single source of truth for generators. No markdown parsing.
2. **Generators are independent** — Each generator reads project.yaml and writes its output. No inter-generator dependencies.
3. **Templates stay human-readable** — Generators complement templates, they don't replace them.
4. **Progressive adoption** — v2.0 templates work without generators. Generators add automation on top.
5. **Profile-aware defaults** — Generators inherit sensible defaults from the profile when sections are omitted.
