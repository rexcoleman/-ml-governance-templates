#!/usr/bin/env python3
"""gen_learning_curves.py (G20) — Generate learning curve figures from experiment outputs.

Reads learning curve JSON data (or model seed outputs as fallback), plots
train + validation metrics vs training fraction with ±1 std shading across
seeds, and saves the figure plus a JSON manifest for traceability.

Usage:
    python scripts/gen_learning_curves.py --project-dir /path/to/project
    python scripts/gen_learning_curves.py --project-dir . --metric accuracy
    python scripts/gen_learning_curves.py --project-dir . --output figures/learning_curves.png
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_json(filepath):
    """Load a JSON file, return None on failure."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError) as exc:
        print(f"WARNING: Could not parse {filepath}: {exc}", file=sys.stderr)
        return None


def find_learning_curve_files(project_dir, verbose=False):
    """Find learning curve JSON files. Returns (files, source_type)."""
    # Primary: outputs/diagnostics/learning_curves_*.json
    diag_pattern = os.path.join(project_dir, "outputs", "diagnostics",
                                "learning_curves_*.json")
    diag_files = sorted(glob.glob(diag_pattern))
    if diag_files:
        if verbose:
            print(f"Found {len(diag_files)} learning curve file(s) in diagnostics/")
        return diag_files, "learning_curves"

    # Fallback: outputs/models/*seed*.json
    seed_pattern = os.path.join(project_dir, "outputs", "models", "*seed*.json")
    seed_files = sorted(glob.glob(seed_pattern))
    if seed_files:
        if verbose:
            print(f"Found {len(seed_files)} seed model file(s) as fallback")
        return seed_files, "seed_models"

    return [], None


def parse_learning_curve_data(files, metric, verbose=False):
    """Parse learning curve files into structured data.

    Expected JSON format per file:
    {
        "algorithm": "RandomForest",
        "train_fractions": [0.1, 0.2, ...],
        "train_scores": [[seed1_scores], [seed2_scores], ...],
        "val_scores": [[seed1_scores], [seed2_scores], ...],
        "metric": "accuracy"
    }

    Returns dict: algorithm -> {fractions, train_mean, train_std, val_mean, val_std}
    """
    import statistics

    results = {}
    for fp in files:
        data = _load_json(fp)
        if data is None:
            continue

        algo = data.get("algorithm", os.path.basename(fp).replace(".json", ""))
        fractions = data.get("train_fractions", [])
        metric_key = data.get("metric", metric)

        # Support both nested (multi-seed) and flat formats
        train_scores = data.get("train_scores", [])
        val_scores = data.get("val_scores", data.get("test_scores", []))

        if not fractions or not train_scores:
            if verbose:
                print(f"  Skipping {fp}: missing fractions or scores")
            continue

        # Compute mean and std across seeds
        n_fractions = len(fractions)
        train_mean, train_std = [], []
        val_mean, val_std = [], []

        for i in range(n_fractions):
            # Gather scores at fraction i across seeds
            t_scores = [s[i] for s in train_scores if i < len(s)]
            v_scores = [s[i] for s in val_scores if i < len(s)]

            if t_scores:
                train_mean.append(statistics.mean(t_scores))
                train_std.append(statistics.stdev(t_scores) if len(t_scores) > 1 else 0.0)
            if v_scores:
                val_mean.append(statistics.mean(v_scores))
                val_std.append(statistics.stdev(v_scores) if len(v_scores) > 1 else 0.0)

        results[algo] = {
            "fractions": fractions,
            "train_mean": train_mean,
            "train_std": train_std,
            "val_mean": val_mean,
            "val_std": val_std,
            "metric": metric_key,
            "n_seeds": len(train_scores),
            "source_file": os.path.basename(fp),
        }
        if verbose:
            print(f"  Parsed {algo}: {n_fractions} fractions, "
                  f"{len(train_scores)} seeds")

    return results


def parse_seed_model_data(files, metric, verbose=False):
    """Parse seed model files as fallback (limited learning curve info).

    Expected JSON format per file:
    {
        "algorithm": "...",
        "seed": 42,
        "metrics": {"accuracy": 0.85, "f1": 0.82, ...},
        "train_metrics": {"accuracy": 0.92, ...}
    }

    Returns dict with single-point data (not real curves).
    """
    import statistics

    by_algo = {}
    for fp in files:
        data = _load_json(fp)
        if data is None:
            continue
        algo = data.get("algorithm", data.get("model", "unknown"))
        if algo not in by_algo:
            by_algo[algo] = {"train": [], "val": []}

        metrics = data.get("metrics", data.get("test_metrics", {}))
        train_metrics = data.get("train_metrics", {})

        val_score = metrics.get(metric)
        train_score = train_metrics.get(metric)

        if val_score is not None:
            by_algo[algo]["val"].append(val_score)
        if train_score is not None:
            by_algo[algo]["train"].append(train_score)

    results = {}
    for algo, scores in by_algo.items():
        if not scores["val"]:
            continue
        results[algo] = {
            "fractions": [1.0],
            "train_mean": [statistics.mean(scores["train"])] if scores["train"] else [],
            "train_std": [statistics.stdev(scores["train"]) if len(scores["train"]) > 1 else 0.0] if scores["train"] else [],
            "val_mean": [statistics.mean(scores["val"])],
            "val_std": [statistics.stdev(scores["val"]) if len(scores["val"]) > 1 else 0.0],
            "metric": metric,
            "n_seeds": len(scores["val"]),
            "source_file": "seed_models (aggregated)",
        }
        if verbose:
            print(f"  Parsed seed data for {algo}: {len(scores['val'])} seeds")

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_learning_curves(curve_data, metric, output_path, verbose=False):
    """Plot learning curves for all algorithms."""
    if not HAS_MATPLOTLIB:
        print("ERROR: matplotlib is required for plotting. Install with:\n"
              "  pip install matplotlib", file=sys.stderr)
        sys.exit(1)

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    colors = plt.cm.tab10.colors

    for i, (algo, data) in enumerate(sorted(curve_data.items())):
        color = colors[i % len(colors)]
        fracs = data["fractions"]

        # Train scores
        if data["train_mean"]:
            t_mean = data["train_mean"]
            t_std = data["train_std"]
            ax.plot(fracs[:len(t_mean)], t_mean,
                    color=color, linestyle="--", alpha=0.7,
                    label=f"{algo} (train)")
            if any(s > 0 for s in t_std):
                lower = [m - s for m, s in zip(t_mean, t_std)]
                upper = [m + s for m, s in zip(t_mean, t_std)]
                ax.fill_between(fracs[:len(t_mean)], lower, upper,
                                color=color, alpha=0.1)

        # Validation scores
        if data["val_mean"]:
            v_mean = data["val_mean"]
            v_std = data["val_std"]
            ax.plot(fracs[:len(v_mean)], v_mean,
                    color=color, linestyle="-", marker="o", markersize=4,
                    label=f"{algo} (val)")
            if any(s > 0 for s in v_std):
                lower = [m - s for m, s in zip(v_mean, v_std)]
                upper = [m + s for m, s in zip(v_mean, v_std)]
                ax.fill_between(fracs[:len(v_mean)], lower, upper,
                                color=color, alpha=0.15)

    ax.set_xlabel("Training Fraction")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title("Learning Curves")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out), dpi=150)
    plt.close(fig)
    print(f"Generated: {output_path}")


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def write_manifest(curve_data, source_type, output_path, manifest_path, verbose=False):
    """Write a JSON manifest of what was plotted."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "generated": now,
        "generator": "gen_learning_curves.py (G20)",
        "figure_path": output_path,
        "source_type": source_type,
        "algorithms": {},
    }
    for algo, data in curve_data.items():
        manifest["algorithms"][algo] = {
            "n_fractions": len(data["fractions"]),
            "n_seeds": data["n_seeds"],
            "metric": data["metric"],
            "source_file": data["source_file"],
            "val_range": [min(data["val_mean"]), max(data["val_mean"])] if data["val_mean"] else [],
        }

    out = Path(manifest_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if verbose:
        print(f"Manifest: {manifest_path}")


# ---------------------------------------------------------------------------
# Instructions fallback
# ---------------------------------------------------------------------------

def print_generation_instructions():
    """Print instructions for generating learning curve data."""
    print("""
No learning curve data found. To generate it, add a learning curve sweep
to your training script. Example:

    from sklearn.model_selection import learning_curve

    train_sizes, train_scores, val_scores = learning_curve(
        estimator, X, y,
        train_sizes=[0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0],
        cv=5, scoring='accuracy', n_jobs=-1
    )

    # Save as JSON for this generator:
    import json
    result = {
        "algorithm": "YourModel",
        "train_fractions": train_sizes.tolist(),
        "train_scores": train_scores.tolist(),
        "val_scores": val_scores.tolist(),
        "metric": "accuracy"
    }
    with open("outputs/diagnostics/learning_curves_YourModel.json", "w") as f:
        json.dump(result, f, indent=2)

Then re-run:
    python scripts/gen_learning_curves.py --project-dir <path>
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _load_project_name(project_dir):
    """Try to read project name from project.yaml; fall back to dir name."""
    yaml_path = os.path.join(project_dir, "project.yaml")
    if yaml is not None and os.path.isfile(yaml_path):
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                proj = data.get("project", {})
                if isinstance(proj, dict) and "name" in proj:
                    return proj["name"]
        except Exception:
            pass
    return os.path.basename(os.path.abspath(project_dir))


def main():
    parser = argparse.ArgumentParser(
        description="Generate learning curve figures from experiment outputs."
    )
    parser.add_argument(
        "--project-dir", required=True,
        help="Root directory of the project."
    )
    parser.add_argument(
        "--metric", default="accuracy",
        help="Metric to plot (default: accuracy)."
    )
    parser.add_argument(
        "--output", default=None,
        help="Output path for figure (default: <project-dir>/figures/learning_curves.png)."
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed debug information during processing."
    )
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"ERROR: Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or os.path.join(project_dir, "figures",
                                               "learning_curves.png")
    # Make output path absolute if relative
    if not os.path.isabs(output_path):
        output_path = os.path.join(project_dir, output_path)

    project_name = _load_project_name(project_dir)

    if args.verbose:
        print(f"Project: {project_name}")
        print(f"Metric:  {args.metric}")
        print(f"Output:  {output_path}")
        print()

    # Step 1: Find data files
    files, source_type = find_learning_curve_files(project_dir, verbose=args.verbose)

    if not files:
        print("No learning curve data found.")
        print_generation_instructions()
        sys.exit(0)

    # Step 2: Parse data
    if args.verbose:
        print(f"\n--- Parsing {source_type} data ---")

    if source_type == "learning_curves":
        curve_data = parse_learning_curve_data(files, args.metric,
                                               verbose=args.verbose)
    else:
        curve_data = parse_seed_model_data(files, args.metric,
                                           verbose=args.verbose)

    if not curve_data:
        print(f"WARNING: No usable data found for metric '{args.metric}'.",
              file=sys.stderr)
        print_generation_instructions()
        sys.exit(0)

    print(f"Algorithms parsed: {len(curve_data)}")

    # Step 3: Plot
    if args.verbose:
        print("\n--- Generating figure ---")
    plot_learning_curves(curve_data, args.metric, output_path,
                         verbose=args.verbose)

    # Step 4: Write manifest
    manifest_path = output_path.replace(".png", "_manifest.json")
    write_manifest(curve_data, source_type, output_path, manifest_path,
                   verbose=args.verbose)
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
