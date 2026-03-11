# Worked Example: RL / Agent Study — CartPole Policy Optimization

This example shows representative placeholder fills for the **RL / Agent Study** quickstart profile (11 templates).

---

## Project Overview

| Property | Value |
|----------|-------|
| **Project name** | CartPole Policy Optimization |
| **Environment** | CartPole-v1 (Gymnasium) |
| **Task** | Compare policy gradient methods on classic control task |
| **Methods** | REINFORCE, PPO, A2C, DQN |
| **Seeds** | 10 (0–9) for statistical stability |
| **Budget** | 500,000 environment steps per method per seed |

---

## Key Placeholder Fills

### ENVIRONMENT_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{PROJECT_NAME}}` | CartPole Policy Optimization |
| `{{PYTHON_VERSION}}` | 3.11.7 |
| `{{PLATFORM}}` | Ubuntu 22.04, x86_64, 16 GB RAM (CPU-only) |
| `{{KEY_LIBRARIES}}` | gymnasium==0.29.1, stable-baselines3==2.2.1, torch==2.1.2 |

### DATA_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{DATASET_NAME}}` | N/A — environment-generated trajectories |
| `{{SPLIT_STRATEGY}}` | N/A (RL: no static train/val/test) |
| `{{DATA_NOTE}}` | Replay buffer and trajectory data are ephemeral; only aggregated metrics are persisted |

### METRICS_CONTRACT (Appendix C activated — RL policy evaluation)

| Placeholder | Fill |
|-------------|------|
| `{{PRIMARY_METRIC}}` | Mean episodic return (100-episode rolling average) |
| `{{SECONDARY_METRICS}}` | Sample efficiency (steps to solve), episode length, policy entropy |
| `{{SOLVE_CRITERION}}` | Mean return >= 475 over 100 consecutive episodes |
| `{{SANITY_BASELINE}}` | Random policy (mean return ~ 22) |
| `{{BUDGET_TYPE}}` | env_steps |

### EXPERIMENT_CONTRACT (Appendix A activated — sequential/RL protocol)

| Placeholder | Fill |
|-------------|------|
| `{{EXPERIMENT_PARTS}}` | Part 1: Method comparison (4 methods × 10 seeds) |
| `{{BUDGET_VALUE}}` | 500,000 env_steps |
| `{{COMPARISON_RULE}}` | Budget-matched at 500K steps; compare sample efficiency and final return |
| `{{LOGGING_INTERVAL}}` | Every 1,000 env_steps |
| `{{OUTPUT_DIR}}` | `outputs/part1/{method}/seed_{seed}/` |

### ENVIRONMENT_SPEC (Full activation — MDP definition)

| Placeholder | Fill |
|-------------|------|
| `{{ENV_ID}}` | CartPole-v1 |
| `{{ENV_VERSION}}` | gymnasium==0.29.1 |
| `{{STATE_SPACE}}` | Box(4,): [cart_pos, cart_vel, pole_angle, pole_angular_vel] |
| `{{ACTION_SPACE}}` | Discrete(2): {0: push_left, 1: push_right} |
| `{{REWARD_FUNCTION}}` | +1 per timestep the pole remains upright |
| `{{DISCOUNT_FACTOR}}` | γ = 0.99 |
| `{{TERMINATION}}` | pole_angle > ±12°, cart_pos > ±2.4, or episode_length >= 500 |
| `{{TRUNCATION_VS_TERMINATION}}` | episode_length >= 500 is truncation; angle/position violations are termination |
| `{{WRAPPERS}}` | None (standard CartPole-v1) |
| `{{SEEDING}}` | `env.reset(seed=seed)` at episode start |

### FIGURES_TABLES_CONTRACT (§8.5 activated — RL figures)

| Placeholder | Fill |
|-------------|------|
| `{{FIGURE_LIST}}` | F1: Learning curves (return vs env_steps), F2: Sample efficiency box plots, F3: Policy entropy over training, F4: Solved-episode fraction over time |
| `{{RL_VIZ}}` | Shaded IQR bands on learning curves, vertical line at solve threshold |

### ARTIFACT_MANIFEST_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{RUN_ID_FORMAT}}` | `part1_{method}_seed{seed}` |
| `{{ARTIFACT_LIST}}` | `summary.json`, `curves.csv`, `config_resolved.yaml`, `policy_final.pt` |

### SCRIPT_ENTRYPOINTS_SPEC

| Placeholder | Fill |
|-------------|------|
| `{{SCRIPTS}}` | `train.py --method {name} --seed {s} --steps 500000`, `evaluate.py --policy {path} --episodes 100`, `make_report_artifacts.py` |

### HYPOTHESIS_CONTRACT

| Placeholder | Fill |
|-------------|------|
| `{{H1_PREDICTION}}` | PPO solves CartPole in fewest env_steps |
| `{{H1_MECHANISM}}` | Clipped surrogate objective enables larger, more stable policy updates |
| `{{H2_PREDICTION}}` | DQN achieves highest final return but slower convergence |
| `{{H2_MECHANISM}}` | Value-based methods with replay buffers are more sample-efficient asymptotically but slower to start |

### IMPLEMENTATION_PLAYBOOK

| Placeholder | Fill |
|-------------|------|
| `{{PHASES}}` | Phase 0: Environment verification + random baseline, Phase 1: Full sweep (40 runs), Phase 2: Analysis + figures, Phase 3: Report |
| `{{PHASE_GATES}}` | Gate 0→1: Random baseline return ~ 22 confirmed; Gate 1→2: All 40 runs complete; Gate 2→3: Figures pass hash check |

### RISK_REGISTER

| Placeholder | Fill |
|-------------|------|
| `{{R1}}` | Non-determinism in environment dynamics → Mitigation: pin gymnasium version, seed every reset |
| `{{R2}}` | Policy collapse during training → Mitigation: detect via entropy monitoring; restart seed if entropy < 0.01 |
| `{{R3}}` | Evaluation variance across episodes → Mitigation: 100-episode evaluation, report median + IQR |

---

## Profile Command

```bash
bash scripts/init_project.sh /path/to/cartpole-optimization --profile rl-agent
```
