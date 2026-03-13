# BUILD SYSTEM CONTRACT

<!-- version: 1.0 -->
<!-- created: 2026-03-13 -->
<!-- last_validated_against: none -->

> **Activation:** This template is OPTIONAL. Include it when your project uses compiled languages
> (C, C++, Rust, Go) or has build-system governance requirements (reproducible binaries,
> sanitizer enforcement, cross-platform compilation). Delete if not applicable.

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
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §2 for target platform and §3 for locked runtime

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §4 for baseline state matching (compiled binaries must be identical across method comparisons)
- See [TEST_ARCHITECTURE](TEST_ARCHITECTURE.tmpl.md) §3.4 for C/C++ synthetic fixtures and build verification tests
- See [PERFORMANCE_BENCHMARKING_SPEC](PERFORMANCE_BENCHMARKING_SPEC.tmpl.md) §2 for optimization flag governance
- See [CONCURRENCY_TESTING_SPEC](CONCURRENCY_TESTING_SPEC.tmpl.md) §2 for sanitizer integration

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | Barrier Synchronization Benchmark |
| `{{COMPILER}}` | Locked compiler | gcc-12 / clang-15 / rustc-1.75 |
| `{{COMPILER_VERSION}}` | Exact compiler version | 12.3.0 |
| `{{BUILD_SYSTEM}}` | Build tool | make / cmake / cargo / meson |
| `{{BUILD_FILE}}` | Build definition file | Makefile / CMakeLists.txt / Cargo.toml |
| `{{STD_VERSION}}` | Language standard | C11 / C++17 / C++20 |
| `{{OPT_FLAGS_DEBUG}}` | Debug optimization flags | -O0 -g -fno-omit-frame-pointer |
| `{{OPT_FLAGS_RELEASE}}` | Release optimization flags | -O2 -march=native |
| `{{OPT_FLAGS_BENCHMARK}}` | Benchmark optimization flags | -O2 -DNDEBUG |
| `{{SANITIZER_FLAGS}}` | Sanitizer compilation flags | -fsanitize=address,undefined |
| `{{TARGET_ARCH}}` | Target architecture | x86_64-linux-gnu |
| `{{TIER1_DOC}}` | Tier 1 authority document | Project requirements spec |
| `{{TIER2_DOC}}` | Tier 2 authority document | FAQ or clarifications document |
| `{{TIER3_DOC}}` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose

This contract locks the build system for the **{{PROJECT_NAME}}** project. It ensures that all compiled artifacts are reproducible, that compiler flags are governed, and that sanitizer usage is consistent across all builds.

---

## 2) Compiler Lock

The compiler MUST be locked to an exact version for all project builds.

| Property | Value |
|----------|-------|
| **Compiler** | {{COMPILER}} |
| **Version** | {{COMPILER_VERSION}} |
| **Language standard** | {{STD_VERSION}} |
| **Target architecture** | {{TARGET_ARCH}} |

**Verification:** `{{COMPILER}} --version` output matches `{{COMPILER_VERSION}}` exactly. Build scripts MUST check compiler version at invocation and fail if mismatched.

### 2.1 Compiler Version Check

The build system MUST verify the compiler version before compilation:

```bash
# Example for gcc
REQUIRED_VERSION="{{COMPILER_VERSION}}"
ACTUAL_VERSION=$({{COMPILER}} -dumpfullversion 2>/dev/null || {{COMPILER}} -dumpversion)
if [ "$ACTUAL_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Compiler version mismatch. Required: $REQUIRED_VERSION, Found: $ACTUAL_VERSION"
    exit 1
fi
```

### 2.2 Standard Library Lock

| Property | Value |
|----------|-------|
| **C standard library** | *(e.g., glibc 2.35)* |
| **C++ standard library** | *(e.g., libstdc++ 12)* |
| **Linker** | *(e.g., ld 2.38)* |

---

## 3) Build Profiles

The project MUST define exactly three build profiles. Each profile has locked flags — no ad-hoc flag modifications.

### 3.1 Debug Profile

Purpose: Development and debugging. Sanitizers enabled.

```
CFLAGS   = {{OPT_FLAGS_DEBUG}} -Wall -Wextra -Werror -pedantic -std={{STD_VERSION}}
LDFLAGS  = {{SANITIZER_FLAGS}}
DEFINES  = -DDEBUG
```

### 3.2 Release Profile

Purpose: Correctness testing without sanitizer overhead.

```
CFLAGS   = {{OPT_FLAGS_RELEASE}} -Wall -Wextra -Werror -pedantic -std={{STD_VERSION}}
LDFLAGS  =
DEFINES  = -DNDEBUG
```

### 3.3 Benchmark Profile

Purpose: Performance measurement. Optimization enabled, sanitizers disabled, assertions disabled.

```
CFLAGS   = {{OPT_FLAGS_BENCHMARK}} -Wall -Wextra -std={{STD_VERSION}}
LDFLAGS  =
DEFINES  = -DNDEBUG -DBENCHMARK
```

**Rule:** Benchmark measurements MUST use the Benchmark profile. Debug and Release profiles MUST NOT be used for performance claims.

**Verification:** Build system logs the active profile name and full resolved flags in `build_manifest.json`. Benchmark result files record the profile used.

---

## 4) Warning Governance

### 4.1 Required Warning Flags

The following warning flags MUST be enabled in all profiles:

| Flag | Purpose |
|------|---------|
| `-Wall` | Standard warnings |
| `-Wextra` | Extended warnings |
| `-pedantic` | Strict standard compliance |
| `-Werror` | Warnings treated as errors (Debug and Release profiles) |

### 4.2 Suppression Policy

Warning suppression MUST be documented:

- Inline suppression (`#pragma GCC diagnostic ignored`) MUST include a comment explaining why
- File-level or target-level suppression MUST be logged in the Decision Log
- Global suppression (`-Wno-*`) is PROHIBITED without a `CONTRACT_CHANGE` commit

**Verification:** `grep -rn "pragma.*diagnostic.*ignored" src/` returns only documented suppressions. Build flags do not contain `-Wno-*` unless recorded in Decision Log.

---

## 5) Sanitizer Governance

### 5.1 Required Sanitizers

The following sanitizers MUST be run during the test phase:

| Sanitizer | Flag | What It Catches | When Required |
|-----------|------|----------------|---------------|
| **AddressSanitizer (ASan)** | `-fsanitize=address` | Buffer overflows, use-after-free, double-free | Always |
| **UndefinedBehaviorSanitizer (UBSan)** | `-fsanitize=undefined` | Integer overflow, null deref, alignment | Always |
| **ThreadSanitizer (TSan)** | `-fsanitize=thread` | Data races, lock-order inversions | When project uses threads |
| **MemorySanitizer (MSan)** | `-fsanitize=memory` | Uninitialized memory reads | When clang is available |

**Rule:** TSan and ASan MUST NOT be combined in a single build (incompatible). Run them in separate build configurations.

**Verification:** CI pipeline runs the test suite under ASan+UBSan and (if threaded) TSan in separate passes. Zero sanitizer findings required before benchmark runs.

### 5.2 Sanitizer Build Targets

```makefile
# Makefile example
.PHONY: test-asan test-tsan

test-asan:
	$(MAKE) clean
	$(MAKE) PROFILE=debug SANITIZERS="-fsanitize=address,undefined"
	./run_tests

test-tsan:
	$(MAKE) clean
	$(MAKE) PROFILE=debug SANITIZERS="-fsanitize=thread"
	./run_tests
```

### 5.3 Sanitizer Suppression

Sanitizer suppressions (`__attribute__((no_sanitize(...)))` or suppression files) MUST:
- Be documented in the Decision Log with justification
- Be minimally scoped (function-level, not file-level)
- Be reviewed before final submission

---

## 6) Reproducibility Protocol

### 6.1 Deterministic Builds

All builds MUST produce bit-identical binaries given identical source and toolchain:

| Requirement | Implementation |
|-------------|----------------|
| No timestamps in binaries | `-Wdate-time` flag or `SOURCE_DATE_EPOCH` environment variable |
| Deterministic archive ordering | `ar` with `D` flag or `CMAKE_AR` configured |
| No path-dependent output | `-ffile-prefix-map=` to normalize paths |
| Fixed random seeds in build | No randomness in code generation or link order |

**Verification:** Build the project twice from clean state. `sha256sum` of all output binaries MUST match. Record hashes in `build_manifest.json`.

### 6.2 Build Manifest

Every build MUST produce `build_manifest.json`:

```json
{
  "compiler": "{{COMPILER}}",
  "compiler_version": "{{COMPILER_VERSION}}",
  "std": "{{STD_VERSION}}",
  "profile": "benchmark",
  "cflags": "-O2 -DNDEBUG -DBENCHMARK ...",
  "ldflags": "",
  "git_sha": "abc123...",
  "build_timestamp": "2026-03-13T10:00:00Z",
  "binary_hashes": {
    "bin/benchmark": "sha256:...",
    "bin/test_runner": "sha256:..."
  }
}
```

---

## 7) Dependency Management

### 7.1 External Libraries

All external dependencies MUST be locked to exact versions:

| Library | Version | Source | Purpose |
|---------|---------|--------|---------|
| *(e.g.)* pthread | system | OS package | Threading primitives |
| *(e.g.)* libcheck | 0.15.2 | apt/source | Unit test framework |
| *(e.g.)* Google Benchmark | 1.8.3 | submodule | Microbenchmark framework |

### 7.2 Vendoring Policy

- Header-only libraries SHOULD be vendored in `vendor/` with version recorded
- Shared libraries MUST be locked via package manager version pins
- Submodules MUST be pinned to exact commit SHAs (not branch names)

**Verification:** `git submodule status` shows pinned SHAs. Package versions match lockfile.

---

## 8) Build Artifacts & Directory Structure

```
build/
├── debug/          # Debug profile outputs
├── release/        # Release profile outputs
├── benchmark/      # Benchmark profile outputs
├── asan/           # ASan+UBSan build
├── tsan/           # TSan build (if applicable)
└── build_manifest.json
```

**Rule:** Build artifacts MUST NOT be committed to version control. Add `build/` to `.gitignore`.

---

## 9) ASLR & Runtime Environment

For benchmark reproducibility, the following runtime controls MUST be documented:

| Control | Value | Purpose |
|---------|-------|---------|
| **ASLR** | Disabled for benchmarks (`setarch $(uname -m) -R`) | Eliminates address-space randomization noise |
| **CPU governor** | `performance` (not `powersave`) | Consistent clock frequency |
| **Turbo boost** | Disabled for benchmarks | Eliminates frequency scaling variance |

**Verification:** Benchmark runner script logs ASLR state, CPU governor, and turbo boost status in `benchmark_env.json`.

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Compiler or compiler version
- Language standard
- Any build flag in any profile
- Sanitizer requirements or suppression policy
- Warning governance (new flags, suppressions)
- External library versions
- Build reproducibility requirements
- ASLR or runtime environment controls
- Build profile definitions
