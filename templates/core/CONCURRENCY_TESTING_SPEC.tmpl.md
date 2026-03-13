# CONCURRENCY TESTING SPEC

<!-- version: 1.0 -->
<!-- created: 2026-03-13 -->
<!-- last_validated_against: none -->

> **Activation:** This template is OPTIONAL. Include it when your project uses threads,
> processes, or any shared-state concurrency (mutexes, condition variables, barriers,
> lock-free data structures). Delete if not applicable.

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
- See [BUILD_SYSTEM_CONTRACT](BUILD_SYSTEM_CONTRACT.tmpl.md) §5 for sanitizer governance (TSan, ASan)
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §2 for target platform thread support
- See [PERFORMANCE_BENCHMARKING_SPEC](PERFORMANCE_BENCHMARKING_SPEC.tmpl.md) §6.2 for thread scalability measurement

**Downstream (depends on this contract):**
- See [TEST_ARCHITECTURE](TEST_ARCHITECTURE.tmpl.md) §3.4 for concurrency test fixtures
- See [RISK_REGISTER](../management/RISK_REGISTER.tmpl.md) for concurrency-specific risks

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Barrier Synchronization Library |
| `{{MAX_THREADS}}` | Maximum thread count under test | 16 |
| `{{THREAD_COUNTS}}` | Thread counts for concurrency tests | [1, 2, 4, 8, 16] |
| `{{STRESS_ITERATIONS}}` | Iterations per stress test | 10000 |
| `{{STRESS_DURATION_SEC}}` | Duration for time-based stress tests | 30 |
| `{{SYNC_PRIMITIVES}}` | Synchronization primitives used | mutex, condition_variable, barrier, atomic |
| `{{DEADLOCK_TIMEOUT_SEC}}` | Deadlock detection timeout | 10 |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose

This spec defines the concurrency testing protocol for the **{{PROJECT_NAME}}** project. It governs how race conditions, deadlocks, and synchronization correctness are detected and verified.

**Core principle:** Concurrency bugs are non-deterministic. A single passing test run does NOT prove correctness. Testing MUST use multiple strategies: sanitizers, stress testing, and systematic exploration.

---

## 2) ThreadSanitizer (TSan) Integration

### 2.1 Mandatory TSan Pass

All code with shared-state concurrency MUST pass a full test suite run under ThreadSanitizer with zero findings.

**Build:**
```bash
make clean
make PROFILE=debug SANITIZERS="-fsanitize=thread" test
```

**Rule:** TSan MUST NOT be combined with ASan in the same build. Run them in separate CI passes.

**Verification:** CI pipeline includes a dedicated TSan pass. Build logs confirm `-fsanitize=thread` was active. TSan output contains zero warnings.

### 2.2 TSan Suppression Policy

TSan false positives MUST be handled through suppression files, not by disabling TSan:

- Suppression file: `tests/tsan_suppressions.txt`
- Each suppression MUST include a comment explaining why it is a false positive
- Suppressions MUST be reviewed before final submission
- Suppressions for third-party libraries are acceptable; suppressions for project code require justification in the Decision Log

```
# tsan_suppressions.txt
# False positive: benign race in logging (write-only, no reader dependency)
race:logger::write_timestamp
```

---

## 3) Race Condition Detection

### 3.1 Data Race Tripwires

For each shared data structure, define explicit tripwire tests that expose races when synchronization is removed:

| Tripwire ID | Shared State | Test Strategy | Expected Behavior (Correct) | Expected Behavior (Buggy) |
|-------------|-------------|---------------|---------------------------|--------------------------|
| RC-1 | *(e.g., shared counter)* | N threads increment simultaneously | Final count = N × iterations | Final count < N × iterations |
| RC-2 | *(e.g., shared queue)* | Producer-consumer stress | All items consumed exactly once | Lost or duplicated items |
| RC-3 | *(e.g., shared buffer)* | Concurrent read-write | No torn reads | Corrupted or partial values |
| *(add project-specific)* | | | | |

### 3.2 Stress Testing Protocol

Each tripwire MUST be stress-tested:

```
For each thread_count in {{THREAD_COUNTS}}:
    For each iteration in range({{STRESS_ITERATIONS}}):
        Run tripwire test with thread_count threads
        Assert correctness invariant
    Record: pass_count, fail_count, elapsed_time
```

**Rule:** Stress tests MUST run for at least {{STRESS_ITERATIONS}} iterations OR {{STRESS_DURATION_SEC}} seconds (whichever is longer). A single failure in any iteration means the test FAILS.

**Verification:** Stress test output logs iteration count, thread count, and pass/fail status. CI runs stress tests at the maximum thread count.

### 3.3 Interleaving Amplification

To increase the probability of exposing races:

| Technique | Implementation | Purpose |
|-----------|---------------|---------|
| **Yield injection** | Insert `sched_yield()` at synchronization boundaries | Force context switches at critical points |
| **Random delays** | `usleep(rand() % 100)` at critical sections | Vary thread timing |
| **CPU affinity rotation** | Vary `taskset` across runs | Expose cache coherence issues |

---

## 4) Deadlock Detection

### 4.1 Deadlock Timeout

Tests involving locks MUST have a deadlock timeout:

```c
// Example: pthread-based timeout
struct timespec ts;
clock_gettime(CLOCK_REALTIME, &ts);
ts.tv_sec += {{DEADLOCK_TIMEOUT_SEC}};
int rc = pthread_mutex_timedlock(&mutex, &ts);
if (rc == ETIMEDOUT) {
    // DEADLOCK DETECTED
    report_deadlock(__FILE__, __LINE__);
    abort();
}
```

**Rule:** No test may hang indefinitely. Every lock acquisition in test code MUST use a timed variant or be wrapped in a watchdog timer.

**Verification:** Test runner has a global timeout of `{{DEADLOCK_TIMEOUT_SEC}} × 2` seconds per test case. Timeout = automatic failure.

### 4.2 Lock-Order Verification

If the project uses multiple locks, document the lock acquisition order:

| Lock | Order | Must Be Held Before |
|------|-------|-------------------|
| *(e.g.)* `global_lock` | 1 | All other locks |
| *(e.g.)* `queue_lock` | 2 | `worker_lock` |
| *(e.g.)* `worker_lock` | 3 | None |

**Rule:** Lock acquisition order MUST be consistent across all code paths. Any violation is a potential deadlock.

**Verification:** TSan lock-order-inversion detection is enabled (default with `-fsanitize=thread`). Static analysis or code review confirms documented order matches implementation.

### 4.3 Deadlock Tripwires

| Tripwire ID | Scenario | Expected Behavior |
|-------------|----------|-------------------|
| DL-1 | Acquire locks in documented order | Completes within timeout |
| DL-2 | *(Intentionally)* reverse lock order under stress | TSan reports lock-order-inversion (proves detection works) |
| DL-3 | All threads request same resource simultaneously | No indefinite wait; progress guaranteed |

---

## 5) Synchronization Correctness

### 5.1 Barrier Correctness (if applicable)

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| BR-1 | All threads reach barrier before any proceed | Phase counter increments only after all threads arrive |
| BR-2 | Barrier reuse across multiple rounds | Barrier works correctly for N consecutive rounds |
| BR-3 | Barrier with variable thread counts | Barrier works for all counts in {{THREAD_COUNTS}} |

### 5.2 Condition Variable Correctness (if applicable)

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| CV-1 | Spurious wakeup handling | Wait loop re-checks predicate after wakeup |
| CV-2 | Signal vs broadcast | `signal` wakes one thread; `broadcast` wakes all |
| CV-3 | Lost wakeup prevention | Signal before wait does not cause indefinite wait |

### 5.3 Lock-Free Data Structure Correctness (if applicable)

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| LF-1 | Linearizability | Every concurrent execution has a valid sequential equivalent |
| LF-2 | ABA problem | CAS operations handle ABA correctly (tagged pointers or epoch-based reclamation) |
| LF-3 | Memory ordering | Correct use of `memory_order_acquire` / `memory_order_release` |

---

## 6) Test File Organization

```
tests/
├── conftest.c (or conftest.h)     # Shared test utilities
├── test_race_conditions.c          # RC-1, RC-2, RC-3 tripwires
├── test_deadlock_detection.c       # DL-1, DL-2, DL-3 tripwires
├── test_barrier_correctness.c      # BR-1, BR-2, BR-3 (if applicable)
├── test_condvar_correctness.c      # CV-1, CV-2, CV-3 (if applicable)
├── test_lockfree.c                 # LF-1, LF-2, LF-3 (if applicable)
├── test_stress.c                   # Long-running stress tests
├── test_scalability.c              # Thread scaling tests
└── tsan_suppressions.txt           # TSan suppression file
```

---

## 7) CI Integration

### 7.1 Concurrency Test Pipeline

```
Step 1: Build with TSan → Run full test suite → Assert zero TSan findings
Step 2: Build with ASan+UBSan → Run full test suite → Assert zero findings
Step 3: Run stress tests (release build) → Assert all pass
Step 4: Run scalability tests → Log results for report
```

### 7.2 Test Markers

| Marker | Purpose | Default |
|--------|---------|---------|
| `stress` | Long-running stress tests | Skip in fast CI, run in full CI |
| `scalability` | Thread scaling tests | Skip in fast CI |
| `tsan_required` | Tests that only make sense under TSan | Run only in TSan build |

---

## 8) Acceptance Criteria

- [ ] All tests pass under ThreadSanitizer (zero findings)
- [ ] All tests pass under AddressSanitizer + UBSan (zero findings)
- [ ] Stress tests pass at maximum thread count ({{MAX_THREADS}} threads × {{STRESS_ITERATIONS}} iterations)
- [ ] Deadlock detection timeout never triggered on correct code paths
- [ ] Lock acquisition order documented and verified
- [ ] TSan suppression file reviewed (if any suppressions exist)
- [ ] Scalability results logged for all thread counts in {{THREAD_COUNTS}}

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Thread count ranges or stress iteration counts
- Synchronization primitive usage (adding/removing locks, barriers, atomics)
- Lock acquisition order
- TSan suppression file entries
- Deadlock timeout values
- Test marker definitions
- Acceptance criteria
