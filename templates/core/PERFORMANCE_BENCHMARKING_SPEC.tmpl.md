# PERFORMANCE BENCHMARKING SPEC

<!-- version: 1.0 -->
<!-- created: 2026-03-13 -->
<!-- last_validated_against: none -->

> **Activation:** This template is OPTIONAL. Include it when your project involves performance
> measurement (latency, throughput, memory), comparative benchmarking of systems implementations,
> or when claims depend on quantitative performance data. Delete if not applicable.

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
- See [BUILD_SYSTEM_CONTRACT](BUILD_SYSTEM_CONTRACT.tmpl.md) §3.3 for Benchmark build profile and §9 for ASLR/CPU controls
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §2 for target platform

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §2 for budget accounting (wall-clock)
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §3 for performance figures
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) Appendix C for systems sanity checks

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Thread Pool Benchmark |
| `{{PRIMARY_METRIC}}` | Primary performance metric | Median wall-clock latency (μs) |
| `{{SECONDARY_METRICS}}` | Secondary metrics | Throughput (ops/sec), peak RSS (KB) |
| `{{BENCHMARK_TOOL}}` | Benchmarking framework | Google Benchmark / custom / hyperfine |
| `{{WARMUP_ITERATIONS}}` | Warmup iteration count | 5 |
| `{{MEASUREMENT_ITERATIONS}}` | Measurement iteration count | 30 |
| `{{INPUT_SIZES}}` | Input sizes for scaling analysis | [100, 1000, 10000, 100000, 1000000] |
| `{{THREAD_COUNTS}}` | Thread counts for scalability | [1, 2, 4, 8, 16] |
| `{{LATENCY_BUDGET_US}}` | Latency budget in microseconds | 100 |
| `{{MEMORY_BUDGET_KB}}` | Memory budget in kilobytes | 10240 |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose

This spec defines the performance benchmarking protocol for the **{{PROJECT_NAME}}** project. It governs how performance is measured, what constitutes a valid measurement, and how results are reported.

---

## 2) Measurement Environment

### 2.1 Hardware Specification

All benchmarks MUST run on the same hardware configuration:

| Property | Value |
|----------|-------|
| **CPU** | *(e.g., Intel Xeon E5-2690 v4, 14 cores)* |
| **Memory** | *(e.g., 64 GB DDR4-2400)* |
| **OS** | *(e.g., Ubuntu 22.04 LTS, kernel 5.15)* |
| **Disk** | *(e.g., NVMe SSD for I/O benchmarks)* |

### 2.2 Environment Controls

The following controls MUST be applied before every benchmark run:

| Control | Command | Purpose |
|---------|---------|---------|
| **ASLR off** | `setarch $(uname -m) -R ./benchmark` | Eliminate address randomization noise |
| **CPU governor** | `cpupower frequency-set -g performance` | Lock CPU frequency |
| **Turbo boost off** | *(platform-specific)* | Eliminate frequency scaling |
| **Isolate CPUs** | `taskset -c {{BENCHMARK_CPUS}}` | Pin benchmark to dedicated cores |
| **Minimize interference** | Stop non-essential services | Reduce scheduling noise |

**Verification:** Benchmark runner logs all control states in `benchmark_env.json`. Script checks controls before measurement and fails if not applied.

---

## 3) Measurement Protocol

### 3.1 Warmup

- **Warmup iterations:** {{WARMUP_ITERATIONS}}
- Warmup results MUST be discarded — they MUST NOT appear in reported statistics
- Warmup ensures caches are hot, branch predictors are trained, and JIT (if applicable) has stabilized

### 3.2 Measurement

- **Measurement iterations:** {{MEASUREMENT_ITERATIONS}}
- Minimum 30 iterations for statistical validity (Central Limit Theorem)
- Each iteration MUST be independent (fresh state, no accumulated side effects)

### 3.3 Timing Method

| Method | When to Use | Resolution |
|--------|-------------|-----------|
| `clock_gettime(CLOCK_MONOTONIC)` | Wall-clock timing (C/C++) | Nanosecond |
| `std::chrono::steady_clock` | Wall-clock timing (C++) | Nanosecond |
| `rdtsc` / `rdtscp` | Cycle-accurate microbenchmarks | CPU cycles |
| `getrusage(RUSAGE_SELF)` | User/system CPU time | Microsecond |

**Rule:** MUST use monotonic clocks. `gettimeofday()` and `time()` are PROHIBITED for benchmarking (wall-clock drift, NTP adjustments).

**Verification:** Grep source for prohibited timing calls. Assert timing function matches this spec.

### 3.4 Compiler Optimization Barrier

Prevent the compiler from optimizing away the measured code:

```cpp
// Use volatile sink or benchmark::DoNotOptimize
static void escape(void* p) {
    asm volatile("" : : "g"(p) : "memory");
}
static void clobber() {
    asm volatile("" : : : "memory");
}
```

**Rule:** Every benchmark MUST include an optimization barrier. Without it, the compiler may eliminate the code under test entirely.

---

## 4) Statistical Reporting

### 4.1 Required Statistics

Every benchmark result MUST report:

| Statistic | Definition | Why |
|-----------|-----------|-----|
| **Median** | 50th percentile | Robust to outliers (primary reporting metric) |
| **P95** | 95th percentile | Tail latency |
| **P99** | 99th percentile | Worst-case behavior |
| **IQR** | P75 − P25 | Dispersion measure |
| **Min** | Minimum observed | Best-case |
| **Max** | Maximum observed | Worst-case |
| **n** | Iteration count | Sample size |

**Rule:** DO NOT report mean for latency measurements. Latency distributions are typically skewed; median + percentiles are more informative.

**Verification:** Every `benchmark_results.json` contains all fields above. No `mean` field in latency results.

### 4.2 Outlier Handling

- Outliers MUST NOT be silently removed
- If outliers are excluded, the exclusion criterion MUST be documented (e.g., > 3σ from median)
- Report both with-outlier and without-outlier statistics

### 4.3 Confidence Intervals

For comparisons between implementations, report:
- Median difference with 95% bootstrap confidence interval
- Or Mann-Whitney U test p-value (non-parametric, no normality assumption)

---

## 5) Performance Budgets

### 5.1 Budget Definitions

| Metric | Budget | Unit | Enforcement |
|--------|--------|------|-------------|
| **Latency** | {{LATENCY_BUDGET_US}} | microseconds (median) | Hard cap — implementation fails gate if exceeded |
| **Memory** | {{MEMORY_BUDGET_KB}} | kilobytes (peak RSS) | Hard cap |
| **Throughput** | *(project-specific)* | ops/sec | Soft target — documented if missed |

### 5.2 Budget Verification

Budget checks MUST be automated:

```python
# In benchmark analysis script
assert result["median_us"] <= LATENCY_BUDGET, \
    f"Latency budget exceeded: {result['median_us']}μs > {LATENCY_BUDGET}μs"
assert result["peak_rss_kb"] <= MEMORY_BUDGET, \
    f"Memory budget exceeded: {result['peak_rss_kb']}KB > {MEMORY_BUDGET}KB"
```

---

## 6) Scaling Analysis

### 6.1 Input-Size Scaling

For algorithms with complexity claims, measure across input sizes:

- **Input sizes:** {{INPUT_SIZES}}
- Plot: median latency vs input size (log-log scale)
- Fit: empirical complexity curve (e.g., O(n), O(n log n), O(n²))
- Compare empirical scaling against theoretical complexity

**Verification:** Scaling plot exists in `outputs/figures/`. Empirical fit exponent documented in results.

### 6.2 Thread Scalability (if applicable)

For concurrent implementations:

- **Thread counts:** {{THREAD_COUNTS}}
- Measure: throughput vs thread count
- Compute: speedup = T(1) / T(n) for each thread count
- Compute: efficiency = speedup / n
- Identify: saturation point (where adding threads stops helping)

---

## 7) Memory Profiling

### 7.1 Required Measurements

| Metric | Tool | When Required |
|--------|------|---------------|
| **Peak RSS** | `/usr/bin/time -v` or `getrusage` | Always |
| **Heap allocations** | Valgrind `massif` or custom allocator tracking | When memory is a constraint |
| **Cache misses** | `perf stat` (L1/LLC misses) | When cache behavior is relevant |

### 7.2 Memory Budget Enforcement

- Peak RSS MUST be measured for every benchmark configuration
- Heap allocation count SHOULD be measured for allocation-sensitive workloads
- Results MUST be logged in `benchmark_results.json`

---

## 8) Comparative Benchmarking Rules

### 8.1 Fair Comparison Requirements

When comparing implementations:

| Requirement | Rule |
|-------------|------|
| **Same build profile** | All implementations use Benchmark profile (BUILD_SYSTEM_CONTRACT §3.3) |
| **Same input data** | Identical input for all implementations in each comparison |
| **Same hardware** | No comparisons across different machines |
| **Same measurement protocol** | Identical warmup, iterations, timing method |
| **Same thread count** | Unless thread scalability is the variable under study |

**Verification:** `benchmark_config.json` records profile, input hash, hardware ID, and protocol for each run. Assert equality across compared implementations.

### 8.2 Baseline Requirement

Every comparative benchmark MUST include a baseline:

| Baseline Type | Purpose |
|---------------|---------|
| **Null baseline** | Empty operation — measures timing overhead |
| **Sequential baseline** | Single-threaded implementation — measures parallelism benefit |
| **Reference implementation** | Known-correct implementation — validates correctness |

---

## 9) Output Schema

### 9.1 Per-Run Output (`benchmark_results.json`)

```json
{
  "benchmark": "{{BENCHMARK_NAME}}",
  "implementation": "{{IMPLEMENTATION_NAME}}",
  "input_size": 10000,
  "threads": 4,
  "iterations": 30,
  "warmup_iterations": 5,
  "profile": "benchmark",
  "latency_us": {
    "median": 0.0,
    "p95": 0.0,
    "p99": 0.0,
    "iqr": 0.0,
    "min": 0.0,
    "max": 0.0
  },
  "throughput_ops_sec": 0.0,
  "peak_rss_kb": 0,
  "build_manifest_sha": "abc123...",
  "benchmark_env_sha": "def456..."
}
```

### 9.2 Environment Snapshot (`benchmark_env.json`)

```json
{
  "hostname": "",
  "cpu_model": "",
  "cpu_cores": 0,
  "memory_gb": 0,
  "os": "",
  "kernel": "",
  "aslr_disabled": true,
  "cpu_governor": "performance",
  "turbo_boost_disabled": true,
  "taskset_cpus": "0-3",
  "timestamp": "2026-03-13T10:00:00Z"
}
```

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Measurement protocol (warmup, iterations, timing method)
- Statistical reporting requirements
- Performance budgets (latency, memory, throughput)
- Scaling analysis input sizes or thread counts
- Comparative benchmarking rules
- Output schema fields
- Environment control requirements
- Memory profiling requirements
