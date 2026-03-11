# Worked Example: Optimization Benchmark — Optimizer Comparison on CIFAR-10

This example shows representative placeholder fills for the **Optimization Benchmark** quickstart profile (11 templates).

---

## Project Overview

| Property | Value |
|----------|-------|
| **Project name** | Optimizer Comparison on CIFAR-10 |
| **Datasets** | CIFAR-10 (50K train, 10K test) |
| **Task** | Compare convergence behavior of 6 optimizers on ResNet-18 |
| **Methods** | SGD, SGD+Momentum, Nesterov, Adam, AdamW, LAMB |
| **Seeds** | 5 (42, 123, 456, 789, 1024) |
| **Budget** | 50,000 gradient evaluations per method per seed |

---

## Key Placeholder Fills

### ENVIRONMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | Optimizer Comparison on CIFAR-10 |
| `{{PYTHON_VERSION}}` | 3.11.7 |
| `{{PLATFORM}}` | Ubuntu 22.04, NVIDIA A100 40GB, CUDA 12.1 |
| `{{DETERMINISM_SETTINGS}}` | `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8` |

### DATA_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{DATASET_NAME}}` | CIFAR-10 |
| `{{SPLIT_STRATEGY}}` | Standard split; 45K/5K/10K (train/val/test) from official split |
| `{{LEAKAGE_RULE}}` | Normalization stats computed on train only |
| `{{AUGMENTATION}}` | RandomCrop(32, padding=4), RandomHorizontalFlip — train only |

### METRICS_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{PRIMARY_METRIC}}` | val_loss (cross-entropy) |
| `{{SECONDARY_METRICS}}` | val_accuracy, train_loss, time_to_threshold |
| `{{CONVERGENCE_THRESHOLD}}` | val_loss <= 0.50 (threshold ℓ) |
| `{{BUDGET_TYPE}}` | grad_evals |
| `{{BUDGET_VALUE}}` | 50,000 |

### EXPERIMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{EXPERIMENT_PARTS}}` | Part 1: Full comparison (6 optimizers × 5 seeds) |
| `{{COMPARISON_RULE}}` | Budget-matched at 50K grad_evals; convergence speed = first eval reaching ℓ |
| `{{OUTPUT_DIR}}` | `outputs/part1/{optimizer}/seed_{seed}/` |
| `{{LOGGING_INTERVAL}}` | Every 100 grad_evals |

### CONFIGURATION_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{CONFIG_FORMAT}}` | YAML |
| `{{CONFIG_LAYERS}}` | `config/base.yaml` → `config/optimizer/{name}.yaml` → CLI overrides |
| `{{LOCKED_KEYS}}` | `budget.grad_evals`, `threshold.val_loss`, `seeds.list` |
| `{{CONFIG_RESOLVED_PATH}}` | `outputs/{run_id}/config_resolved.yaml` |

### HYPOTHESIS_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{H1_PREDICTION}}` | Adam converges fastest (fewest grad_evals to ℓ) |
| `{{H1_MECHANISM}}` | Adaptive per-parameter learning rates compensate for gradient magnitude variation across layers |
| `{{H2_PREDICTION}}` | AdamW achieves lowest final val_loss |
| `{{H2_MECHANISM}}` | Decoupled weight decay provides better regularization than L2 in Adam |

### FIGURES_TABLES_CONTRACT (with §8 visualization catalog activated)

| Placeholder | Fill |
|-------------|------|
| `{{FIGURE_LIST}}` | F1: Convergence curves (val_loss vs grad_evals), F2: Time-to-threshold box plots, F3: Final val_loss box plots, F4: Learning rate sensitivity sweep |
| `{{CONVERGENCE_VIZ}}` | Log-scale y-axis, shaded IQR bands, vertical line at ℓ |
| `{{SENSITIVITY_VIZ}}` | Heatmap: optimizer × learning_rate → final val_loss |

### ARTIFACT_MANIFEST_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{RUN_ID_FORMAT}}` | `part1_{optimizer}_seed{seed}` |
| `{{ARTIFACT_LIST}}` | `summary.json`, `curves.csv`, `config_resolved.yaml`, `checkpoint_best.pt` |
| `{{HASH_ALGORITHM}}` | SHA-256 |

### SCRIPT_ENTRYPOINTS_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{SCRIPTS}}` | `train.py --optimizer {name} --seed {s} --budget 50000`, `evaluate.py --run-dir {path}`, `make_report_artifacts.py` |
| `{{SWEEP_COMMAND}}` | `bash scripts/sweep.sh` (iterates all optimizers × seeds) |

### IMPLEMENTATION_PLAYBOOK

| Placeholder | Fill |
|-------------|------|
| `{{PHASES}}` | Phase 0: Setup + baseline SGD, Phase 1: Full sweep, Phase 2: Analysis + figures, Phase 3: Report |
| `{{PHASE_GATES}}` | Gate 0→1: SGD baseline reaches ℓ; Gate 1→2: All 30 runs complete; Gate 2→3: All figures pass hash check |

### RISK_REGISTER

| Placeholder | Fill |
|-------------|------|
| `{{R1}}` | GPU memory overflow on ResNet-18 with large batch → Mitigation: gradient accumulation |
| `{{R2}}` | Optimizer fails to converge within budget → Mitigation: report as negative result |
| `{{R3}}` | Non-determinism across GPU runs → Mitigation: enforce deterministic mode; report variance |

---

## Profile Command

```bash
bash scripts/init_project.sh /path/to/optimizer-comparison --profile optimization
```
