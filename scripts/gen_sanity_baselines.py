#!/usr/bin/env python3
"""gen_sanity_baselines.py (G23) — Run DummyClassifier and shuffled-label baselines.

Runs stratified and most-frequent DummyClassifiers plus a shuffled-label
baseline to establish sanity floors for classification tasks.

Usage:
    python scripts/gen_sanity_baselines.py --project-dir /path/to/project --data-path data/train.csv --target label
    python scripts/gen_sanity_baselines.py --project-dir . --data-path data.csv --target y --seeds 42,123,456
    python scripts/gen_sanity_baselines.py --project-dir . --data-path data.csv --target y --model-type logistic_regression
"""
import argparse
import csv
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
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn import metrics as sk_metrics
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# ---------------------------------------------------------------------------
# Data loading (stdlib fallback for CSV)
# ---------------------------------------------------------------------------

def _load_csv_stdlib(filepath, target_col):
    """Load a CSV file using stdlib csv module. Returns X (list of lists), y (list)."""
    rows = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if target_col not in reader.fieldnames:
            print(f"ERROR: Target column '{target_col}' not found in CSV. "
                  f"Available columns: {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)
        feature_cols = [c for c in reader.fieldnames if c != target_col]
        for row in reader:
            rows.append(row)

    X = []
    y = []
    for row in rows:
        y.append(row[target_col])
        feat_row = []
        for col in feature_cols:
            try:
                feat_row.append(float(row[col]))
            except (ValueError, TypeError):
                feat_row.append(0.0)  # Encode non-numeric as 0
        X.append(feat_row)

    return X, y, feature_cols


def load_data(data_path, target_col, verbose=False):
    """Load dataset and return numpy arrays (if sklearn available) or lists."""
    if not os.path.isfile(data_path):
        print(f"ERROR: Data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    X, y, feature_cols = _load_csv_stdlib(data_path, target_col)

    if verbose:
        print(f"  Loaded {len(y)} samples, {len(feature_cols)} features")
        unique_y = sorted(set(y))
        print(f"  Target classes: {unique_y[:10]}"
              + ("..." if len(unique_y) > 10 else ""))

    if HAS_SKLEARN:
        X = np.array(X, dtype=float)
        # Keep y as array (may be string labels)
        y = np.array(y)

    return X, y


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------

def compute_metrics(y_true, y_pred, y_proba=None):
    """Compute classification metrics. Returns dict."""
    if not HAS_SKLEARN:
        # Minimal stdlib fallback
        n = len(y_true)
        correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
        return {"accuracy": correct / n if n > 0 else 0.0}

    result = {
        "accuracy": float(sk_metrics.accuracy_score(y_true, y_pred)),
        "f1_weighted": float(sk_metrics.f1_score(y_true, y_pred,
                                                  average="weighted",
                                                  zero_division=0)),
        "precision_weighted": float(sk_metrics.precision_score(y_true, y_pred,
                                                                average="weighted",
                                                                zero_division=0)),
        "recall_weighted": float(sk_metrics.recall_score(y_true, y_pred,
                                                          average="weighted",
                                                          zero_division=0)),
    }

    # AUC for binary classification
    unique_classes = sorted(set(y_true))
    if len(unique_classes) == 2 and y_proba is not None:
        try:
            result["auc"] = float(sk_metrics.roc_auc_score(y_true, y_proba))
        except (ValueError, TypeError):
            pass

    return result


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------

def run_dummy_baseline(X_train, X_test, y_train, y_test, strategy, seed,
                       verbose=False):
    """Run a DummyClassifier with the given strategy."""
    if not HAS_SKLEARN:
        print("ERROR: scikit-learn is required for baselines. Install with:\n"
              "  pip install scikit-learn", file=sys.stderr)
        sys.exit(1)

    clf = DummyClassifier(strategy=strategy, random_state=seed)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    y_proba = None
    try:
        proba = clf.predict_proba(X_test)
        if proba.shape[1] == 2:
            y_proba = proba[:, 1]
    except Exception:
        pass

    result = compute_metrics(y_test, y_pred, y_proba)
    if verbose:
        print(f"    {strategy} seed={seed}: accuracy={result['accuracy']:.4f}")
    return result


def run_shuffled_baseline(X_train, X_test, y_train, y_test, model_type, seed,
                          verbose=False):
    """Train a model on shuffled labels to establish noise floor."""
    if not HAS_SKLEARN:
        print("ERROR: scikit-learn is required for baselines. Install with:\n"
              "  pip install scikit-learn", file=sys.stderr)
        sys.exit(1)

    rng = np.random.RandomState(seed)
    y_shuffled = y_train.copy()
    rng.shuffle(y_shuffled)

    if model_type == "logistic_regression":
        clf = LogisticRegression(random_state=seed, max_iter=1000,
                                 solver="lbfgs")
    else:
        clf = LogisticRegression(random_state=seed, max_iter=1000,
                                 solver="lbfgs")

    try:
        clf.fit(X_train, y_shuffled)
    except Exception as exc:
        if verbose:
            print(f"    WARNING: Shuffled baseline training failed: {exc}")
        return {"accuracy": 0.0, "_error": str(exc)}

    y_pred = clf.predict(X_test)

    y_proba = None
    try:
        proba = clf.predict_proba(X_test)
        if proba.shape[1] == 2:
            y_proba = proba[:, 1]
    except Exception:
        pass

    result = compute_metrics(y_test, y_pred, y_proba)
    if verbose:
        print(f"    shuffled seed={seed}: accuracy={result['accuracy']:.4f}")
    return result


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def write_baseline_result(output_path, strategy, seeds, all_results, verbose=False):
    """Write aggregated baseline result to JSON."""
    import statistics

    # Aggregate across seeds
    metric_keys = set()
    for r in all_results:
        metric_keys.update(k for k in r.keys() if not k.startswith("_"))

    aggregated = {"strategy": strategy, "seeds": seeds}
    for key in sorted(metric_keys):
        values = [r[key] for r in all_results if key in r]
        if values:
            aggregated[key] = {
                "mean": statistics.mean(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "values": values,
            }

    aggregated["n_seeds"] = len(seeds)
    aggregated["generated"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(aggregated, indent=2) + "\n", encoding="utf-8")
    print(f"Generated: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run DummyClassifier and shuffled-label sanity baselines."
    )
    parser.add_argument(
        "--project-dir", required=True,
        help="Root directory of the project."
    )
    parser.add_argument(
        "--data-path", required=True,
        help="Path to CSV dataset (absolute or relative to project-dir)."
    )
    parser.add_argument(
        "--target", required=True,
        help="Name of the target column."
    )
    parser.add_argument(
        "--model-type", default="logistic_regression",
        choices=["logistic_regression"],
        help="Model type for shuffled-label baseline (default: logistic_regression)."
    )
    parser.add_argument(
        "--seeds", default="42,123,456",
        help="Comma-separated list of random seeds (default: 42,123,456)."
    )
    parser.add_argument(
        "--test-size", type=float, default=0.2,
        help="Test set fraction (default: 0.2)."
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed debug information during processing."
    )
    args = parser.parse_args()

    if not HAS_SKLEARN:
        print("ERROR: scikit-learn is required for this generator. Install with:\n"
              "  pip install scikit-learn numpy", file=sys.stderr)
        sys.exit(1)

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"ERROR: Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    data_path = args.data_path
    if not os.path.isabs(data_path):
        data_path = os.path.join(project_dir, data_path)

    seeds = [int(s.strip()) for s in args.seeds.split(",")]

    if args.verbose:
        print(f"Project:    {project_dir}")
        print(f"Data:       {data_path}")
        print(f"Target:     {args.target}")
        print(f"Model type: {args.model_type}")
        print(f"Seeds:      {seeds}")
        print(f"Test size:  {args.test_size}")
        print()

    # Step 1: Load data
    if args.verbose:
        print("--- Loading data ---")
    X, y = load_data(data_path, args.target, verbose=args.verbose)
    print(f"Dataset: {len(y)} samples")

    baselines_dir = os.path.join(project_dir, "outputs", "baselines")

    # Step 2: Stratified DummyClassifier
    if args.verbose:
        print("\n--- Stratified DummyClassifier ---")
    strat_results = []
    for seed in seeds:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=seed, stratify=y
        )
        result = run_dummy_baseline(X_train, X_test, y_train, y_test,
                                    "stratified", seed, verbose=args.verbose)
        strat_results.append(result)

    write_baseline_result(
        os.path.join(baselines_dir, "sanity_stratified.json"),
        "stratified", seeds, strat_results, verbose=args.verbose,
    )

    # Step 3: Most-frequent DummyClassifier
    if args.verbose:
        print("\n--- Most-frequent DummyClassifier ---")
    mf_results = []
    for seed in seeds:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=seed, stratify=y
        )
        result = run_dummy_baseline(X_train, X_test, y_train, y_test,
                                    "most_frequent", seed, verbose=args.verbose)
        mf_results.append(result)

    write_baseline_result(
        os.path.join(baselines_dir, "sanity_most_frequent.json"),
        "most_frequent", seeds, mf_results, verbose=args.verbose,
    )

    # Step 4: Shuffled-label baseline
    if args.verbose:
        print("\n--- Shuffled-label baseline ---")
    shuf_results = []
    for seed in seeds:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=seed, stratify=y
        )
        result = run_shuffled_baseline(X_train, X_test, y_train, y_test,
                                       args.model_type, seed,
                                       verbose=args.verbose)
        shuf_results.append(result)

    write_baseline_result(
        os.path.join(baselines_dir, "sanity_shuffled.json"),
        f"shuffled_{args.model_type}", seeds, shuf_results,
        verbose=args.verbose,
    )

    print(f"\nAll sanity baselines complete: {baselines_dir}/")


if __name__ == "__main__":
    main()
