#!/usr/bin/env python3
"""gen_complexity_curves.py (G21) — Generate model complexity curve figures from HP sweep outputs.

Reads hyperparameter sweep data, plots train + validation metric vs HP value
per algorithm with ±1 std shading, annotates the sweet spot (max validation
metric), and saves the figure.

Usage:
    python scripts/gen_complexity_curves.py --project-dir /path/to/project
    python scripts/gen_complexity_curves.py --project-dir . --output figures/complexity_curves.png
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


def find_complexity_files(project_dir, verbose=False):
    """Find complexity curve / HP sweep JSON files. Returns (files, source_type)."""
    # Primary: outputs/diagnostics/complexity_curves_*.json
    diag_pattern = os.path.join(project_dir, "outputs", "diagnostics",
                                "complexity_curves_*.json")
    diag_files = sorted(glob.glob(diag_pattern))
    if diag_files:
        if verbose:
            print(f"Found {len(diag_files)} complexity curve file(s) in diagnostics/")
        return diag_files, "complexity_curves"

    # Fallback: outputs/sweeps/*.json
    sweep_pattern = os.path.join(project_dir, "outputs", "sweeps", "*.json")
    sweep_files = sorted(glob.glob(sweep_pattern))
    if sweep_files:
        if verbose:
            print(f"Found {len(sweep_files)} sweep file(s) as fallback")
        return sweep_files, "sweeps"

    return [], None


def parse_complexity_data(files, source_type, verbose=False):
    """Parse complexity/sweep files into structured data.

    Expected complexity_curves format:
    {
        "algorithm": "RandomForest",
        "hp_name": "n_estimators",
        "hp_values": [10, 50, 100, 200, 500],
        "train_scores": [[seed1], [seed2], ...],
        "val_scores": [[seed1], [seed2], ...],
        "metric": "accuracy"
    }

    Expected sweeps format:
    {
        "algorithm": "...",
        "hp_name": "...",
        "results": [
            {"hp_value": 10, "train_score": 0.9, "val_score": 0.85, "seed": 42},
            ...
        ]
    }

    Returns dict: algorithm -> {hp_name, hp_values, train_mean, train_std,
                                val_mean, val_std, metric, sweet_spot_idx}
    """
    import statistics

    results = {}
    for fp in files:
        data = _load_json(fp)
        if data is None:
            continue

        algo = data.get("algorithm", os.path.basename(fp).replace(".json", ""))
        hp_name = data.get("hp_name", data.get("hyperparameter", "hp"))
        metric = data.get("metric", "accuracy")

        if source_type == "complexity_curves":
            hp_values = data.get("hp_values", [])
            train_scores = data.get("train_scores", [])
            val_scores = data.get("val_scores", data.get("test_scores", []))

            if not hp_values or not val_scores:
                if verbose:
                    print(f"  Skipping {fp}: missing hp_values or scores")
                continue

            n_hps = len(hp_values)
            train_mean, train_std = [], []
            val_mean, val_std = [], []

            for i in range(n_hps):
                t_scores = [s[i] for s in train_scores if i < len(s)]
                v_scores = [s[i] for s in val_scores if i < len(s)]

                if t_scores:
                    train_mean.append(statistics.mean(t_scores))
                    train_std.append(statistics.stdev(t_scores) if len(t_scores) > 1 else 0.0)
                if v_scores:
                    val_mean.append(statistics.mean(v_scores))
                    val_std.append(statistics.stdev(v_scores) if len(v_scores) > 1 else 0.0)

            n_seeds = len(train_scores) if train_scores else len(val_scores)

        elif source_type == "sweeps":
            sweep_results = data.get("results", [])
            if not sweep_results:
                if verbose:
                    print(f"  Skipping {fp}: no results")
                continue

            # Group by hp_value, then compute stats across seeds
            by_hp = {}
            for r in sweep_results:
                hpv = r.get("hp_value", r.get(hp_name))
                if hpv is None:
                    continue
                by_hp.setdefault(hpv, {"train": [], "val": []})
                ts = r.get("train_score", r.get("train_" + metric))
                vs = r.get("val_score", r.get("val_" + metric, r.get("test_score")))
                if ts is not None:
                    by_hp[hpv]["train"].append(ts)
                if vs is not None:
                    by_hp[hpv]["val"].append(vs)

            hp_values = sorted(by_hp.keys())
            train_mean, train_std = [], []
            val_mean, val_std = [], []

            max_seeds = 0
            for hpv in hp_values:
                ts = by_hp[hpv]["train"]
                vs = by_hp[hpv]["val"]
                max_seeds = max(max_seeds, len(ts), len(vs))

                if ts:
                    train_mean.append(statistics.mean(ts))
                    train_std.append(statistics.stdev(ts) if len(ts) > 1 else 0.0)
                if vs:
                    val_mean.append(statistics.mean(vs))
                    val_std.append(statistics.stdev(vs) if len(vs) > 1 else 0.0)

            n_seeds = max_seeds
        else:
            continue

        # Find sweet spot (max validation metric)
        sweet_spot_idx = val_mean.index(max(val_mean)) if val_mean else 0

        results[algo] = {
            "hp_name": hp_name,
            "hp_values": hp_values,
            "train_mean": train_mean,
            "train_std": train_std,
            "val_mean": val_mean,
            "val_std": val_std,
            "metric": metric,
            "n_seeds": n_seeds,
            "sweet_spot_idx": sweet_spot_idx,
            "source_file": os.path.basename(fp),
        }
        if verbose:
            sweet_hp = hp_values[sweet_spot_idx] if hp_values else "?"
            print(f"  Parsed {algo}: {len(hp_values)} HP values, "
                  f"sweet spot at {hp_name}={sweet_hp}")

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_complexity_curves(curve_data, output_path, verbose=False):
    """Plot complexity curves for all algorithms."""
    if not HAS_MATPLOTLIB:
        print("ERROR: matplotlib is required for plotting. Install with:\n"
              "  pip install matplotlib", file=sys.stderr)
        sys.exit(1)

    n_algos = len(curve_data)
    if n_algos == 0:
        print("WARNING: No data to plot.", file=sys.stderr)
        return

    # One subplot per algorithm (stacked vertically)
    fig, axes = plt.subplots(n_algos, 1, figsize=(10, 5 * n_algos),
                             squeeze=False)
    colors = plt.cm.tab10.colors

    for i, (algo, data) in enumerate(sorted(curve_data.items())):
        ax = axes[i, 0]
        hp_vals = data["hp_values"]
        hp_name = data["hp_name"]
        metric = data["metric"]

        # Use numeric x positions; label with actual HP values
        x = list(range(len(hp_vals)))

        # Train scores
        if data["train_mean"]:
            t_mean = data["train_mean"]
            t_std = data["train_std"]
            ax.plot(x[:len(t_mean)], t_mean,
                    color=colors[0], linestyle="--", alpha=0.7,
                    label="Train")
            if any(s > 0 for s in t_std):
                lower = [m - s for m, s in zip(t_mean, t_std)]
                upper = [m + s for m, s in zip(t_mean, t_std)]
                ax.fill_between(x[:len(t_mean)], lower, upper,
                                color=colors[0], alpha=0.1)

        # Validation scores
        if data["val_mean"]:
            v_mean = data["val_mean"]
            v_std = data["val_std"]
            ax.plot(x[:len(v_mean)], v_mean,
                    color=colors[1], linestyle="-", marker="o", markersize=5,
                    label="Validation")
            if any(s > 0 for s in v_std):
                lower = [m - s for m, s in zip(v_mean, v_std)]
                upper = [m + s for m, s in zip(v_mean, v_std)]
                ax.fill_between(x[:len(v_mean)], lower, upper,
                                color=colors[1], alpha=0.15)

            # Annotate sweet spot
            ss_idx = data["sweet_spot_idx"]
            if ss_idx < len(v_mean):
                ss_val = v_mean[ss_idx]
                ss_hp = hp_vals[ss_idx] if ss_idx < len(hp_vals) else "?"
                ax.annotate(
                    f"Best: {hp_name}={ss_hp}\n{metric}={ss_val:.4f}",
                    xy=(ss_idx, ss_val),
                    xytext=(ss_idx + 0.5, ss_val + 0.02),
                    fontsize=8,
                    arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
                    color="red", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
                              edgecolor="red", alpha=0.8),
                )
                ax.axvline(x=ss_idx, color="red", linestyle=":", alpha=0.4)

        ax.set_xticks(x)
        ax.set_xticklabels([str(v) for v in hp_vals], rotation=45, ha="right",
                           fontsize=8)
        ax.set_xlabel(hp_name)
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.set_title(f"{algo} — Model Complexity Curve")
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

def write_manifest(curve_data, source_type, output_path, manifest_path):
    """Write a JSON manifest of what was plotted."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "generated": now,
        "generator": "gen_complexity_curves.py (G21)",
        "figure_path": output_path,
        "source_type": source_type,
        "algorithms": {},
    }
    for algo, data in curve_data.items():
        ss_idx = data["sweet_spot_idx"]
        manifest["algorithms"][algo] = {
            "hp_name": data["hp_name"],
            "n_hp_values": len(data["hp_values"]),
            "n_seeds": data["n_seeds"],
            "metric": data["metric"],
            "sweet_spot_hp_value": data["hp_values"][ss_idx] if data["hp_values"] else None,
            "sweet_spot_val_score": data["val_mean"][ss_idx] if data["val_mean"] else None,
            "source_file": data["source_file"],
        }

    out = Path(manifest_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
        description="Generate model complexity curve figures from HP sweep outputs."
    )
    parser.add_argument(
        "--project-dir", required=True,
        help="Root directory of the project."
    )
    parser.add_argument(
        "--output", default=None,
        help="Output path for figure (default: <project-dir>/figures/complexity_curves.png)."
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
                                               "complexity_curves.png")
    if not os.path.isabs(output_path):
        output_path = os.path.join(project_dir, output_path)

    project_name = _load_project_name(project_dir)

    if args.verbose:
        print(f"Project: {project_name}")
        print(f"Output:  {output_path}")
        print()

    # Step 1: Find data files
    files, source_type = find_complexity_files(project_dir, verbose=args.verbose)

    if not files:
        print("No complexity curve or HP sweep data found.")
        print("\nTo generate complexity curve data, run an HP sweep and save results as:")
        print("  outputs/diagnostics/complexity_curves_<Algorithm>.json")
        print("  OR outputs/sweeps/<sweep_name>.json")
        print("\nExpected JSON format:")
        print(json.dumps({
            "algorithm": "RandomForest",
            "hp_name": "n_estimators",
            "hp_values": [10, 50, 100, 200, 500],
            "train_scores": [[0.95, 0.96], [0.97, 0.98]],
            "val_scores": [[0.85, 0.86], [0.87, 0.88]],
            "metric": "accuracy",
        }, indent=2))
        sys.exit(0)

    # Step 2: Parse data
    if args.verbose:
        print(f"\n--- Parsing {source_type} data ---")
    curve_data = parse_complexity_data(files, source_type, verbose=args.verbose)

    if not curve_data:
        print("WARNING: No usable complexity data found.", file=sys.stderr)
        sys.exit(1)

    print(f"Algorithms parsed: {len(curve_data)}")

    # Step 3: Plot
    if args.verbose:
        print("\n--- Generating figure ---")
    plot_complexity_curves(curve_data, output_path, verbose=args.verbose)

    # Step 4: Write manifest
    manifest_path = output_path.replace(".png", "_manifest.json")
    write_manifest(curve_data, source_type, output_path, manifest_path)
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
