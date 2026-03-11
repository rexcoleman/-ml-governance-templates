# ENVIRONMENT CONTRACT

<!-- version: 1.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_OL_Report -->

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
- None — this is a foundational contract.

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §4 for seeding and initialization protocol
- See [PRIOR_WORK_REUSE](../management/PRIOR_WORK_REUSE.tmpl.md) §3 for environment compatibility assessment
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §3 for environment verification scripts (`verify_env.sh`)
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for Phase 0 environment lock gate

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Sentiment Analysis Benchmark |
| `{{PYTHON_VERSION}}` | Pinned Python version | 3.10.13 |
| `{{ENV_MANAGER}}` | Environment manager | mamba / conda / pip+venv |
| `{{ENV_NAME}}` | Environment name | my-ml-project |
| `{{ENV_FILE}}` | Environment definition file | environment.yml / requirements.txt |
| `{{PLATFORM}}` | Target platform | Linux CPU-only |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Course TAs' Piazza clarifications |
| `{{REPRO_COMMANDS}}` | Exact reproduction command sequence | See §7 |

---

## 1) Purpose

This contract locks the compute environment for the **{{PROJECT_NAME}}** project. It ensures that all artifacts are reproducible on the target platform by any reviewer.

---

## 2) Target Platform

- **OS:** {{PLATFORM}}
- **Hardware:** *(e.g., CPU-only, GPU optional for exploration)*
- **Constraint:** All final deliverables MUST be reproducible on the target platform. GPU may be used for exploration but MUST NOT be required for release artifacts.

---

## 3) Locked Language & Runtime

- **Language:** Python {{PYTHON_VERSION}}
- **Package manager:** {{ENV_MANAGER}}
- **Environment name:** {{ENV_NAME}}

---

## 4) Dependencies

All dependencies are locked in `{{ENV_FILE}}`. Key packages:

| Package | Version | Purpose |
|---------|---------|---------|
| *(e.g.)* numpy | 1.26.4 | Numerical computation |
| *(e.g.)* pandas | 2.1.4 | Data manipulation |
| *(e.g.)* scikit-learn | 1.7.2 | ML utilities |
| *(e.g.)* pytorch | 2.2.2 | Neural network framework |
| *(e.g.)* matplotlib | 3.8.2 | Plotting |

*(Fill in actual pinned versions from your environment file.)*

---

## 5) Environment Setup

```bash
# Create environment
{{ENV_MANAGER}} env create -f {{ENV_FILE}}
conda activate {{ENV_NAME}}

# Verify environment
bash scripts/verify_env.sh
```

The verification script MUST:
- Print Python version and confirm it matches {{PYTHON_VERSION}}
- Print versions of all key packages
- Confirm target platform compatibility (e.g., `cuda_available: False` is acceptable for CPU-only)
- Exit 0 on success, 1 on any mismatch

---

## 6) Data Placement

*(Reference DATA_CONTRACT for canonical paths. Provide copy-paste instructions for the REPRO document.)*

```
data/raw/{{DATASET_1_FILE}}  — {{DATASET_1_DESCRIPTION}}
data/raw/{{DATASET_2_FILE}}  — {{DATASET_2_DESCRIPTION}}
```

Data source: {{DATA_SOURCE}} *(e.g., "download from Kaggle", "download from UCI ML Repository")*

---

## 7) Reproduction Commands

All commands run from repository root. These are the canonical commands that appear in the REPRO document.

```bash
# Phase 0: Environment
{{ENV_MANAGER}} env create -f {{ENV_FILE}}
conda activate {{ENV_NAME}}
bash scripts/verify_env.sh

# Phase 1: Data verification & EDA
# (Fill in project-specific commands)

# Phase 2-N: Experiments
# (Fill in project-specific commands)

# Final: Evaluation & artifact generation
# (Fill in project-specific commands)
```

---

## 8) Determinism Defaults

The following determinism settings MUST be applied in all experiment scripts:

```python
import random
import numpy as np
import torch

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

- **Default seed:** {{DEFAULT_SEED}} *(e.g., 42)*
- **Stability seed list:** {{SEED_LIST}} *(e.g., [42, 123, 456, 789, 1024])*
- **n_jobs:** Always 1 (no parallel workers) unless explicitly justified and documented

---

## 9) Provenance Outputs

The first experiment run MUST produce:

| File | Path | Contents |
|------|------|----------|
| `versions.txt` | `outputs/provenance/versions.txt` | Package versions at runtime |
| `git_commit_sha.txt` | `outputs/provenance/git_commit_sha.txt` | Current git SHA |
| `run_log.json` | `outputs/provenance/run_log.json` | Append-only log of all runs |

---

## 10) CPU Reproducibility Rule

ALL report artifacts MUST be reproducible on CPU. This is non-negotiable for independent verification.

- Environment file MUST include a CPU-only build of the ML framework
- Scripts MUST NOT fail if GPU is unavailable
- Final artifacts MUST be generated on CPU

---

## 11) Change Control

The following changes require a `CONTRACT_CHANGE` commit:

- Python version (including patch)
- Any dependency in `{{ENV_FILE}}` (add, remove, or version change)
- Determinism or leakage guardrails
- Seed policy
- `n_jobs` settings
- Script filenames, CLI parameters, or entrypoint paths
- Data paths
- Budget values
