#!/usr/bin/env python3
"""gen_runtime_estimate.py (G25) — Estimate experiment wallclock time before running.

Reads project.yaml (or accepts CLI overrides) to estimate total wallclock for
the full experiment suite: baselines, learning curves, complexity curves,
ablation studies, and multi-seed runs.  Generates estimated_runtime.md with
per-experiment estimates, totals, and warnings for any experiment >2 hours.

Heuristics are conservative upper-bounds calibrated on a single-core B2ms VM.
Actual times will vary with hardware, parallelism, and data characteristics.

Usage:
    python scripts/gen_runtime_estimate.py --project-dir /path/to/project
    python scripts/gen_runtime_estimate.py --project-dir . --rows 234000 --seeds 5
    python scripts/gen_runtime_estimate.py --project-dir . --algorithms rf,xgboost,logreg,svm,lgbm,knn,mlp
    python scripts/gen_runtime_estimate.py --project-dir . --features 50 --rows 100000

Self-contained: stdlib + optional pyyaml.  No other dependencies.
"""
import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# Algorithm wallclock heuristics (minutes, single-core, single-seed)
# ---------------------------------------------------------------------------

# Each function takes rows, features, and returns estimated minutes.
# The constants are calibrated on Azure B2ms (2 vCPU, 8 GB RAM).

ALGORITHM_HEURISTICS = {
    "rf": {
        "label": "RandomForest",
        "family": "tree-ensemble",
        "fn": lambda rows, features, **kw: 0.5 * (rows / 100_000) * kw.get("n_estimators", 100) / 100,
    },
    "xgboost": {
        "label": "XGBoost",
        "family": "boosting",
        "fn": lambda rows, features, **kw: 0.3 * (rows / 100_000) * kw.get("n_rounds", 100) / 100,
    },
    "lgbm": {
        "label": "LightGBM",
        "family": "boosting",
        "fn": lambda rows, features, **kw: 0.3 * (rows / 100_000) * kw.get("n_rounds", 100) / 100,
    },
    "gradientboosting": {
        "label": "GradientBoosting (sklearn)",
        "family": "boosting",
        "fn": lambda rows, features, **kw: 0.3 * (rows / 100_000) * kw.get("n_rounds", 100) / 100,
    },
    "logreg": {
        "label": "LogisticRegression",
        "family": "linear",
        "fn": lambda rows, features, **kw: 0.1 * (rows / 100_000),
    },
    "svm": {
        "label": "SVM-RBF",
        "family": "kernel",
        "fn": lambda rows, features, **kw: 2.0 * (rows / 50_000) ** 2,
    },
    "knn": {
        "label": "k-NearestNeighbors",
        "family": "instance-based",
        "fn": lambda rows, features, **kw: 0.5 * (rows / 100_000) * (features / 50),
    },
    "mlp": {
        "label": "MLP (neural net)",
        "family": "neural",
        "fn": lambda rows, features, **kw: 0.3 * (rows / 100_000) * kw.get("epochs", 100) / 100,
    },
}

# Canonical aliases so users can type common names
ALGORITHM_ALIASES = {
    "randomforest": "rf",
    "random_forest": "rf",
    "xgb": "xgboost",
    "lightgbm": "lgbm",
    "light_gbm": "lgbm",
    "gbm": "gradientboosting",
    "gradient_boosting": "gradientboosting",
    "logistic": "logreg",
    "logistic_regression": "logreg",
    "svm_rbf": "svm",
    "svc": "svm",
    "knn_clf": "knn",
    "k_nearest": "knn",
    "neural_net": "mlp",
    "mlp_classifier": "mlp",
}

# Multiplier constants for experiment phases
LEARNING_CURVE_FRACTIONS = 5       # default: [0.2, 0.4, 0.6, 0.8, 1.0]
COMPLEXITY_CURVE_VALUES = 6        # default: 6 HP values per algorithm
ABLATION_GROUPS = 8                # default: 8 feature groups for leave-one-out

WARNING_THRESHOLD_MINUTES = 120    # flag experiments > 2 hours
SVM_SUBSAMPLE_THRESHOLD = 50_000   # suggest subsampling if SVM rows exceed this


# ---------------------------------------------------------------------------
# project.yaml loading
# ---------------------------------------------------------------------------

def _load_yaml(filepath):
    """Load a YAML file, return dict or None."""
    if yaml is None:
        # Fallback: very basic key-value extraction for simple YAML
        return _load_yaml_fallback(filepath)
    try:
        with open(filepath, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as exc:
        print(f"WARNING: Could not parse {filepath}: {exc}", file=sys.stderr)
        return None


def _load_yaml_fallback(filepath):
    """Minimal YAML parser for flat key: value files (no pyyaml)."""
    data = {}
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if val:
                        data[key] = val
    except FileNotFoundError:
        return None
    return data if data else None


def _extract_from_yaml(data):
    """Extract rows, algorithms, seeds, features from project.yaml dict."""
    rows = None
    algorithms = []
    seeds = None
    features = None

    if not data:
        return rows, algorithms, seeds, features

    # dataset_size / rows
    for key in ("dataset_size", "rows", "n_rows", "num_rows"):
        val = data.get(key)
        if val is not None:
            try:
                rows = int(str(val).replace(",", "").replace("_", ""))
            except ValueError:
                pass
            break

    # Check nested data section
    if rows is None and isinstance(data.get("data"), dict):
        for key in ("rows", "dataset_size", "n_rows"):
            val = data["data"].get(key)
            if val is not None:
                try:
                    rows = int(str(val).replace(",", "").replace("_", ""))
                except ValueError:
                    pass
                break

    # algorithms
    alg_val = data.get("algorithms") or data.get("models")
    if isinstance(alg_val, list):
        algorithms = [str(a).strip().lower() for a in alg_val]
    elif isinstance(alg_val, str):
        algorithms = [a.strip().lower() for a in alg_val.split(",")]

    # seeds
    seed_val = data.get("seeds") or data.get("n_seeds") or data.get("num_seeds")
    if isinstance(seed_val, list):
        seeds = len(seed_val)
    elif seed_val is not None:
        try:
            seeds = int(str(seed_val))
        except ValueError:
            pass

    # features
    for key in ("features", "n_features", "num_features"):
        val = data.get(key)
        if val is not None:
            try:
                features = int(str(val).replace(",", "").replace("_", ""))
            except ValueError:
                pass
            break

    return rows, algorithms, seeds, features


# ---------------------------------------------------------------------------
# Estimation engine
# ---------------------------------------------------------------------------

def resolve_algorithm(name):
    """Map an algorithm name/alias to a canonical key."""
    name_lower = name.lower().strip()
    if name_lower in ALGORITHM_HEURISTICS:
        return name_lower
    if name_lower in ALGORITHM_ALIASES:
        return ALGORITHM_ALIASES[name_lower]
    return None


def estimate_single(algo_key, rows, features, **kwargs):
    """Estimate minutes for one algorithm, one seed, one full-data run."""
    entry = ALGORITHM_HEURISTICS[algo_key]
    return entry["fn"](rows, features, **kwargs)


def estimate_all(algorithms, rows, features, seeds,
                 include_learning_curves=True,
                 include_complexity_curves=True,
                 include_ablation=True):
    """Build a list of (experiment_name, algo, minutes, warning) tuples."""
    results = []

    for algo_key in algorithms:
        entry = ALGORITHM_HEURISTICS[algo_key]
        label = entry["label"]

        # --- Baseline training (all seeds) ---
        base_min = estimate_single(algo_key, rows, features)
        total_base = base_min * seeds
        results.append({
            "experiment": f"Baseline training",
            "algorithm": label,
            "per_unit_min": base_min,
            "units": seeds,
            "unit_label": "seeds",
            "total_min": total_base,
            "warning": total_base > WARNING_THRESHOLD_MINUTES,
        })

        # --- Learning curves (fractions x seeds) ---
        if include_learning_curves:
            # Each fraction trains on a subset; average cost ~ 0.6x of full
            avg_fraction_cost = base_min * 0.6
            lc_total = avg_fraction_cost * LEARNING_CURVE_FRACTIONS * seeds
            results.append({
                "experiment": f"Learning curves",
                "algorithm": label,
                "per_unit_min": avg_fraction_cost,
                "units": LEARNING_CURVE_FRACTIONS * seeds,
                "unit_label": f"{LEARNING_CURVE_FRACTIONS} fractions x {seeds} seeds",
                "total_min": lc_total,
                "warning": lc_total > WARNING_THRESHOLD_MINUTES,
            })

        # --- Complexity curves (HP values x seeds) ---
        if include_complexity_curves:
            cc_total = base_min * COMPLEXITY_CURVE_VALUES * seeds
            results.append({
                "experiment": f"Complexity curves",
                "algorithm": label,
                "per_unit_min": base_min,
                "units": COMPLEXITY_CURVE_VALUES * seeds,
                "unit_label": f"{COMPLEXITY_CURVE_VALUES} HP values x {seeds} seeds",
                "total_min": cc_total,
                "warning": cc_total > WARNING_THRESHOLD_MINUTES,
            })

        # --- Ablation (groups x seeds) — only once per algo set, not per algo ---
        # We'll add ablation separately below

    # --- Ablation study (once, using the fastest algorithm as proxy) ---
    if include_ablation and algorithms:
        # Use median algorithm cost as proxy for ablation
        costs = [estimate_single(a, rows, features) for a in algorithms]
        median_cost = sorted(costs)[len(costs) // 2]
        # Each ablation group trains the model once per seed
        ablation_total = median_cost * ABLATION_GROUPS * seeds
        results.append({
            "experiment": "Ablation study (leave-one-group-out)",
            "algorithm": "median model",
            "per_unit_min": median_cost,
            "units": ABLATION_GROUPS * seeds,
            "unit_label": f"{ABLATION_GROUPS} groups x {seeds} seeds",
            "total_min": ablation_total,
            "warning": ablation_total > WARNING_THRESHOLD_MINUTES,
        })

    return results


# ---------------------------------------------------------------------------
# SVM subsampling advisory
# ---------------------------------------------------------------------------

def svm_advisory(rows, algorithms):
    """Return advisory string if SVM is used on large dataset, else None."""
    svm_present = any(resolve_algorithm(a) == "svm" for a in algorithms)
    if not svm_present:
        return None
    if rows <= SVM_SUBSAMPLE_THRESHOLD:
        return None

    subsampled_min = 2.0 * (SVM_SUBSAMPLE_THRESHOLD / 50_000) ** 2
    full_min = 2.0 * (rows / 50_000) ** 2
    return (
        f"SVM-RBF on {rows:,} rows is O(n^2): estimated {full_min:.1f} min per seed.\n"
        f"Recommendation: subsample to {SVM_SUBSAMPLE_THRESHOLD:,} rows "
        f"(estimated {subsampled_min:.1f} min per seed).\n"
        f"Speedup: {full_min / max(subsampled_min, 0.01):.0f}x.\n"
        f"Document the subsampling decision in ENVIRONMENT_CONTRACT §compute constraints."
    )


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------

def _fmt_minutes(minutes):
    """Format minutes as human-readable string."""
    if minutes < 1:
        return f"{minutes * 60:.0f}s"
    if minutes < 60:
        return f"{minutes:.1f} min"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f} hr"
    days = hours / 24
    return f"{days:.1f} days"


def generate_report(results, rows, features, seeds, algorithms,
                    svm_advice, project_dir):
    """Generate the estimated_runtime.md markdown content."""
    lines = []
    lines.append("# Estimated Experiment Runtime")
    lines.append("")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(f"> Generated by `gen_runtime_estimate.py` (G25) on {now}")
    lines.append(f"> Calibrated for single-core execution on Azure B2ms (2 vCPU, 8 GB RAM).")
    lines.append(f"> Actual times may be lower with parallelism or faster hardware.")
    lines.append("")

    # --- Parameters ---
    lines.append("## Parameters")
    lines.append("")
    lines.append(f"| Parameter | Value |")
    lines.append(f"|-----------|-------|")
    lines.append(f"| Dataset rows | {rows:,} |")
    lines.append(f"| Features | {features} |")
    lines.append(f"| Seeds | {seeds} |")
    algo_labels = []
    for a in algorithms:
        key = resolve_algorithm(a)
        if key:
            algo_labels.append(ALGORITHM_HEURISTICS[key]["label"])
        else:
            algo_labels.append(f"{a} (unknown)")
    lines.append(f"| Algorithms | {', '.join(algo_labels)} ({len(algorithms)}) |")
    lines.append(f"| Learning curve fractions | {LEARNING_CURVE_FRACTIONS} |")
    lines.append(f"| Complexity curve HP values | {COMPLEXITY_CURVE_VALUES} |")
    lines.append(f"| Ablation groups | {ABLATION_GROUPS} |")
    lines.append("")

    # --- Per-experiment table ---
    lines.append("## Per-Experiment Estimates")
    lines.append("")
    lines.append("| Experiment | Algorithm | Per-Unit | Units | Total | Status |")
    lines.append("|------------|-----------|----------|-------|-------|--------|")

    grand_total = 0.0
    warning_count = 0

    for r in results:
        status = "WARNING >2hr" if r["warning"] else "OK"
        if r["warning"]:
            warning_count += 1
        grand_total += r["total_min"]
        lines.append(
            f"| {r['experiment']} | {r['algorithm']} | "
            f"{_fmt_minutes(r['per_unit_min'])} | "
            f"{r['unit_label']} | "
            f"**{_fmt_minutes(r['total_min'])}** | "
            f"{status} |"
        )

    lines.append("")

    # --- Totals ---
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| **Grand total (sequential)** | **{_fmt_minutes(grand_total)}** |")
    lines.append(f"| Experiments with warnings (>2hr) | {warning_count} |")

    # Parallel estimate: assume seeds can run in parallel
    if seeds > 1:
        parallel_total = grand_total / seeds
        lines.append(f"| Estimated with {seeds}-way seed parallelism | ~{_fmt_minutes(parallel_total)} |")

    lines.append("")

    # --- Warnings ---
    if warning_count > 0:
        lines.append("## Warnings")
        lines.append("")
        for r in results:
            if r["warning"]:
                lines.append(
                    f"- **{r['experiment']} / {r['algorithm']}**: "
                    f"{_fmt_minutes(r['total_min'])} exceeds 2-hour threshold. "
                    f"Consider subsampling, reducing seeds, or skipping complexity curves."
                )
        lines.append("")

    # --- SVM advisory ---
    if svm_advice:
        lines.append("## SVM Subsampling Advisory")
        lines.append("")
        for line in svm_advice.split("\n"):
            lines.append(f"- {line}")
        lines.append("")

    # --- Recommendations ---
    lines.append("## Recommendations")
    lines.append("")
    if grand_total > 480:  # >8 hours
        lines.append("1. **Total exceeds 8 hours.** Consider:")
        lines.append("   - Reducing seeds from {0} to 3 for initial runs".format(seeds))
        lines.append("   - Skipping complexity curves for expensive algorithms")
        lines.append("   - Subsampling dataset for SVM/kNN")
        lines.append("   - Running seeds in parallel (`--parallel` flag)")
    elif grand_total > 120:
        lines.append("1. **Total exceeds 2 hours.** Consider running seeds in parallel.")
    else:
        lines.append("1. Total runtime is manageable for sequential execution.")

    lines.append("2. Run smoke test with `--sample-frac 0.01` before full experiments.")
    lines.append("3. Document any subsampling decisions in ENVIRONMENT_CONTRACT §compute constraints.")
    lines.append("")

    # --- Heuristic reference ---
    lines.append("## Heuristic Reference")
    lines.append("")
    lines.append("| Algorithm | Formula (minutes, single seed) | Complexity |")
    lines.append("|-----------|-------------------------------|------------|")
    lines.append("| RandomForest | 0.5 * (rows/100K) * (n_estimators/100) | O(n * trees * log n) |")
    lines.append("| XGBoost/LightGBM/GBM | 0.3 * (rows/100K) * (n_rounds/100) | O(n * rounds * depth) |")
    lines.append("| LogisticRegression | 0.1 * (rows/100K) | O(n * features * iters) |")
    lines.append("| SVM-RBF | 2.0 * (rows/50K)^2 | **O(n^2) to O(n^3)** |")
    lines.append("| k-NN | 0.5 * (rows/100K) * (features/50) | O(n * features) at predict |")
    lines.append("| MLP | 0.3 * (rows/100K) * (epochs/100) | O(n * layers * epochs) |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Estimate experiment wallclock time before running (G25).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/gen_runtime_estimate.py --project-dir .
  python scripts/gen_runtime_estimate.py --project-dir . --rows 234000 --seeds 5
  python scripts/gen_runtime_estimate.py --project-dir . --algorithms rf,xgboost,svm,logreg
        """,
    )
    p.add_argument("--project-dir", required=True, help="Project root directory")
    p.add_argument("--rows", type=int, default=None,
                   help="Dataset row count (overrides project.yaml)")
    p.add_argument("--algorithms", type=str, default=None,
                   help="Comma-separated algorithm list (overrides project.yaml). "
                        "Options: rf, xgboost, lgbm, gradientboosting, logreg, svm, knn, mlp")
    p.add_argument("--seeds", type=int, default=None,
                   help="Number of random seeds (overrides project.yaml)")
    p.add_argument("--features", type=int, default=None,
                   help="Number of features (overrides project.yaml)")
    p.add_argument("--n-estimators", type=int, default=100,
                   help="RF n_estimators (default: 100)")
    p.add_argument("--n-rounds", type=int, default=100,
                   help="Boosting n_rounds (default: 100)")
    p.add_argument("--epochs", type=int, default=100,
                   help="MLP epochs (default: 100)")
    p.add_argument("--no-learning-curves", action="store_true",
                   help="Exclude learning curve estimates")
    p.add_argument("--no-complexity-curves", action="store_true",
                   help="Exclude complexity curve estimates")
    p.add_argument("--no-ablation", action="store_true",
                   help="Exclude ablation study estimates")
    p.add_argument("--output", type=str, default=None,
                   help="Output filepath (default: <project-dir>/docs/estimated_runtime.md)")
    p.add_argument("--quiet", action="store_true",
                   help="Suppress stdout summary")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.is_dir():
        print(f"ERROR: Project directory does not exist: {project_dir}", file=sys.stderr)
        sys.exit(1)

    # --- Load project.yaml ---
    yaml_rows, yaml_algos, yaml_seeds, yaml_features = None, [], None, None
    for candidate in ("project.yaml", "project.yml"):
        yaml_path = project_dir / candidate
        if yaml_path.is_file():
            data = _load_yaml(str(yaml_path))
            yaml_rows, yaml_algos, yaml_seeds, yaml_features = _extract_from_yaml(data)
            if not args.quiet:
                print(f"Loaded {yaml_path}")
            break

    # --- Resolve parameters (CLI overrides YAML) ---
    rows = args.rows or yaml_rows
    seeds = args.seeds or yaml_seeds or 5
    features = args.features or yaml_features or 50

    if args.algorithms:
        algorithms_raw = [a.strip() for a in args.algorithms.split(",")]
    elif yaml_algos:
        algorithms_raw = yaml_algos
    else:
        # Default: the standard 7-algorithm suite
        algorithms_raw = ["rf", "xgboost", "lgbm", "logreg", "svm", "knn", "mlp"]

    if rows is None:
        print("ERROR: Dataset row count required. Provide --rows N or set dataset_size in project.yaml.",
              file=sys.stderr)
        sys.exit(1)

    # --- Resolve algorithm names ---
    algorithms = []
    for a in algorithms_raw:
        key = resolve_algorithm(a)
        if key is None:
            print(f"WARNING: Unknown algorithm '{a}' — skipping. "
                  f"Known: {', '.join(sorted(ALGORITHM_HEURISTICS.keys()))}",
                  file=sys.stderr)
        else:
            algorithms.append(key)

    if not algorithms:
        print("ERROR: No valid algorithms specified.", file=sys.stderr)
        sys.exit(1)

    # --- Run estimation ---
    results = estimate_all(
        algorithms=algorithms,
        rows=rows,
        features=features,
        seeds=seeds,
        include_learning_curves=not args.no_learning_curves,
        include_complexity_curves=not args.no_complexity_curves,
        include_ablation=not args.no_ablation,
    )

    svm_advice = svm_advisory(rows, algorithms)

    # --- Generate report ---
    report = generate_report(
        results=results,
        rows=rows,
        features=features,
        seeds=seeds,
        algorithms=algorithms,
        svm_advice=svm_advice,
        project_dir=str(project_dir),
    )

    # --- Write output ---
    if args.output:
        output_path = Path(args.output)
    else:
        docs_dir = project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        output_path = docs_dir / "estimated_runtime.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    # --- Summary to stdout ---
    if not args.quiet:
        grand_total = sum(r["total_min"] for r in results)
        warning_count = sum(1 for r in results if r["warning"])
        print(f"\nRuntime estimate written to: {output_path}")
        print(f"  Algorithms: {len(algorithms)}")
        print(f"  Rows: {rows:,}  Features: {features}  Seeds: {seeds}")
        print(f"  Grand total (sequential): {_fmt_minutes(grand_total)}")
        if seeds > 1:
            print(f"  Estimated with {seeds}-way parallelism: ~{_fmt_minutes(grand_total / seeds)}")
        if warning_count:
            print(f"  WARNING: {warning_count} experiment(s) exceed 2-hour threshold")
        if svm_advice:
            print(f"  SVM ADVISORY: Subsample to {SVM_SUBSAMPLE_THRESHOLD:,} rows recommended")


if __name__ == "__main__":
    main()
