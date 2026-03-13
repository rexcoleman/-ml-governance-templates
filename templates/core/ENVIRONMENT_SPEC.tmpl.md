# ENVIRONMENT SPECIFICATION (RL / Simulation)

<!-- version: 1.0 -->
<!-- created: 2026-03-11 -->
<!-- last_validated_against: none -->

> **Activation:** This template is OPTIONAL. Include it when your project involves reinforcement
> learning, simulation-based optimization, or any task where an agent interacts with a dynamic
> environment. Delete if not applicable.

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
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §4 for dependency versions (e.g., Gymnasium, MuJoCo)

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) Appendix A for episode-based budget accounting
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) Appendix C for RL policy evaluation metrics
- See [ADVERSARIAL_EVALUATION](ADVERSARIAL_EVALUATION.tmpl.md) §3.3-3.4 for reward/environment perturbation protocols
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §8.5 for RL-specific visualization types

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | GridWorld Navigation Study |
| `{{ENV_ID}}` | Environment identifier | `FrozenLake-v1`, `CartPole-v1`, custom |
| `{{ENV_LIBRARY}}` | Environment library | Gymnasium 0.29.1, PettingZoo 1.24.0 |
| `{{STATE_SPACE}}` | State space description | Discrete(16), Box(4,), Dict(...) |
| `{{ACTION_SPACE}}` | Action space description | Discrete(4), Box(2,) |
| `{{REWARD_RANGE}}` | Reward bounds | [-1, 1], [0, ∞), unbounded |
| `{{DISCOUNT_FACTOR}}` | Gamma (γ) | 0.99 |
| `{{MAX_EPISODE_STEPS}}` | Episode step limit | 200, 1000, unlimited |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose & Scope

This specification defines the environment(s) used in the **{{PROJECT_NAME}}** project. It provides the formal MDP definition, implementation details, and reproducibility requirements needed to fully specify the learning problem.

---

## 2) Environment Identity

| Property | Value |
|----------|-------|
| **Environment ID** | `{{ENV_ID}}` |
| **Library** | {{ENV_LIBRARY}} |
| **Version** | *(exact version string or commit SHA for custom envs)* |
| **Type** | *(single-agent / multi-agent / cooperative / competitive)* |
| **Deterministic** | *(yes / no — does the same action from the same state always produce the same next state?)* |

For custom environments, the source code MUST be committed to the repository and referenced here.

**Verification:** `python -c "import {{ENV_MODULE}}; env = {{ENV_CONSTRUCTOR}}; print(env.spec)"` succeeds.

---

## 3) MDP Definition

### 3.1 State Space

| Property | Value |
|----------|-------|
| **Type** | {{STATE_SPACE}} *(Discrete, Box, Dict, Tuple, MultiBinary, MultiDiscrete)* |
| **Dimensionality** | *(e.g., 4 continuous, 16 discrete states, 84×84×3 image)* |
| **Bounds** | *(min/max for continuous; enumeration for small discrete)* |
| **Observation preprocessing** | *(e.g., normalization, frame stacking, flattening — if any)* |

### 3.2 Action Space

| Property | Value |
|----------|-------|
| **Type** | {{ACTION_SPACE}} *(Discrete, Box, MultiDiscrete)* |
| **Dimensionality** | *(e.g., 4 discrete actions, 2 continuous controls)* |
| **Bounds** | *(min/max for continuous; enumeration for discrete)* |
| **Action semantics** | *(what each action means — e.g., 0=left, 1=down, 2=right, 3=up)* |

### 3.3 Transition Dynamics

| Property | Value |
|----------|-------|
| **Stochasticity** | *(deterministic / stochastic with probability p)* |
| **Slip probability** | *(if applicable — e.g., FrozenLake is_slippery=True → 1/3 chance of intended direction)* |
| **Physics engine** | *(if applicable — e.g., MuJoCo, PyBullet, Box2D)* |
| **Time discretization** | *(dt for continuous-time systems)* |

### 3.4 Reward Function

| Property | Value |
|----------|-------|
| **Reward range** | {{REWARD_RANGE}} |
| **Reward type** | *(sparse / dense / shaped)* |
| **Reward definition** | *(exact formula or table)* |

**Reward table** *(for discrete/sparse rewards):*

| Condition | Reward | Notes |
|-----------|--------|-------|
| *(e.g.)* Reach goal | +1.0 | Terminal |
| *(e.g.)* Fall in hole | -1.0 | Terminal |
| *(e.g.)* Each step | -0.01 | Encourages efficiency |
| *(add rows)* | | |

**Reward formula** *(for continuous/shaped rewards):*

```
r(s, a, s') = {{REWARD_FORMULA}}
```

**Rule:** The reward function MUST be fully specified here. If reward shaping is used, both the original and shaped rewards MUST be documented, and the shaping potential function MUST be shown to preserve the optimal policy.

**Verification:** Inspect environment source code or `env.step()` output to confirm reward matches specification. For shaped rewards, verify potential function satisfies F(s,a,s') = γΦ(s') - Φ(s).

### 3.5 Discount Factor

| Property | Value |
|----------|-------|
| **γ (gamma)** | {{DISCOUNT_FACTOR}} |
| **Justification** | *(why this value — e.g., "standard for episodic tasks", "problem-specific horizon")* |

### 3.6 Termination Conditions

| Condition | Type | Description |
|-----------|------|-------------|
| *(e.g.)* Goal reached | Success | Agent reaches target state |
| *(e.g.)* Fall in hole | Failure | Agent enters terminal failure state |
| *(e.g.)* Step limit | Truncation | Episode truncated at {{MAX_EPISODE_STEPS}} steps |

**Rule:** Distinguish between **termination** (episode ends due to environment dynamics) and **truncation** (episode ends due to step limit). This distinction affects value bootstrapping.

---

## 4) Environment Configuration

### 4.1 Configuration Parameters

| Parameter | Value | Locked? | Notes |
|-----------|-------|---------|-------|
| *(e.g.)* `map_name` | `"4x4"` | Yes | Defines grid layout |
| *(e.g.)* `is_slippery` | `True` | Yes | Stochastic transitions |
| *(e.g.)* `max_episode_steps` | {{MAX_EPISODE_STEPS}} | Yes | Truncation limit |
| *(add rows)* | | | |

**Rule:** All environment configuration parameters MUST be logged in `config_resolved.yaml` for every run. Locked parameters MUST NOT change between experiments without a `CONTRACT_CHANGE`.

### 4.2 Environment Wrappers

| Wrapper | Purpose | Parameters |
|---------|---------|-----------|
| *(e.g.)* `TimeLimit` | Episode truncation | `max_episode_steps={{MAX_EPISODE_STEPS}}` |
| *(e.g.)* `RecordVideo` | Visualization | `video_folder="outputs/videos/"` |
| *(e.g.)* `NormalizeObservation` | State normalization | Running mean/std |
| *(add rows)* | | |

---

## 5) Reproducibility Requirements

### 5.1 Seeding Protocol

- Environment MUST be seeded via `env.reset(seed=seed)` at the start of each episode during evaluation
- Training episodes MAY use sequential seeds derived from the master seed
- Evaluation episodes MUST use a fixed, separate seed set

**Verification:** Run the same evaluation episode twice with the same seed. Assert identical state sequences and rewards.

### 5.2 Version Locking

- Environment library version MUST be pinned in `{{ENV_FILE}}`
- For custom environments: source code committed and referenced by path
- For Gymnasium environments: exact `env.spec.id` logged

### 5.3 Determinism Check

For deterministic environments:
```python
env1 = gym.make("{{ENV_ID}}")
env2 = gym.make("{{ENV_ID}}")
obs1, _ = env1.reset(seed=42)
obs2, _ = env2.reset(seed=42)
assert np.array_equal(obs1, obs2)

for action in [0, 1, 2, 0]:
    obs1, r1, term1, trunc1, _ = env1.step(action)
    obs2, r2, term2, trunc2, _ = env2.step(action)
    assert np.array_equal(obs1, obs2) and r1 == r2
```

---

## 6) Environment Visualization

### 6.1 Required Visualizations

| Visualization | When Required | Purpose |
|--------------|---------------|---------|
| **State space diagram** | Always | Show environment layout / state structure |
| **Learned policy overlay** | After training | Overlay policy actions on state space |
| **Value function heatmap** | When value-based methods used | Show learned state values |
| **Reward heatmap** | When reward is state-dependent | Show reward landscape |
| **Training trajectory** | Optional | Show representative episode paths |

### 6.2 Visualization Specifications

Each visualization MUST include:
- Environment configuration parameters in the caption
- Seed and episode number (for trajectory plots)
- Color scale legend (for heatmaps)

---

## 7) Reward Sensitivity Analysis

> **Activation:** Include when reward shaping is used or when the project specification requires
> analysis of reward function design choices.

### 7.1 Protocol

| Analysis | Procedure | Expected Insight |
|----------|-----------|-----------------|
| **Reward scale sensitivity** | Multiply reward by {0.1, 1.0, 10.0}; compare learning curves | Whether algorithm is sensitive to reward magnitude |
| **Discount factor sweep** | Test γ ∈ {0.9, 0.95, 0.99, 0.999}; compare final performance | Optimal planning horizon |
| **Shaping ablation** | Compare shaped vs unshaped reward; verify optimal policy unchanged | Whether shaping helps or hurts |

### 7.2 Reporting

- Sensitivity results MUST be reported as learning curves (mean return vs episodes) with dispersion bands
- Reward shaping ablation MUST show that the optimal policy is preserved
- Include a brief discussion of which reward parameters most affect learning

---

## 8) Multi-Environment Comparison (Optional)

When comparing agent performance across multiple environments:

| Requirement | Description |
|------------|-------------|
| **Normalized scores** | Use human-normalized or random-normalized scores for cross-environment comparison |
| **Matched budgets** | Same number of training episodes/steps across environments |
| **Per-environment reporting** | Report metrics separately per environment before any aggregation |

---

## 9) Acceptance Criteria

- [ ] Environment ID and version documented
- [ ] Complete MDP definition (state, action, transition, reward, discount, termination)
- [ ] All configuration parameters logged in `config_resolved.yaml`
- [ ] Seeding protocol implemented and verified
- [ ] Environment version pinned in `{{ENV_FILE}}`
- [ ] State space visualization produced
- [ ] Reward function matches specification (verified by inspection or test)

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Environment ID or version
- State space or action space definition
- Reward function (formula, scale, shaping)
- Discount factor
- Termination conditions or step limits
- Environment configuration parameters (locked values)
- Wrapper stack
- Seeding protocol
