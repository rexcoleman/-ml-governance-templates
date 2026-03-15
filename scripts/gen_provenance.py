#!/usr/bin/env python3
"""gen_provenance.py (G22) — Capture full reproducibility snapshot.

Generates config_resolved.yaml, versions.txt, output_manifest.json, and
git_info.txt to ensure complete experiment provenance and reproducibility.

Usage:
    python scripts/gen_provenance.py --project-dir /path/to/project
    python scripts/gen_provenance.py --project-dir . --output-dir provenance/
    python scripts/gen_provenance.py --project-dir . --verify
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Config resolution
# ---------------------------------------------------------------------------

def _flatten_dict(d, prefix=""):
    """Recursively flatten a dict into dot-separated keys."""
    items = {}
    if not isinstance(d, dict):
        return {prefix: d} if prefix else {}
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key))
        elif isinstance(v, list):
            items[new_key] = v
        else:
            items[new_key] = v
    return items


def generate_config_resolved(project_dir, output_dir, verbose=False):
    """Read project.yaml, flatten configs, add git SHA + branch."""
    yaml_path = os.path.join(project_dir, "project.yaml")
    out_path = os.path.join(output_dir, "config_resolved.yaml")

    config = {}
    if os.path.isfile(yaml_path):
        if HAS_YAML:
            try:
                with open(yaml_path, encoding="utf-8") as f:
                    raw = yaml.safe_load(f) or {}
                config = _flatten_dict(raw)
                if verbose:
                    print(f"  Read {len(config)} config keys from project.yaml")
            except Exception as exc:
                print(f"WARNING: Could not parse project.yaml: {exc}",
                      file=sys.stderr)
                config = {"_error": str(exc)}
        else:
            # Fallback: read raw text
            with open(yaml_path, encoding="utf-8") as f:
                config = {"_raw_yaml": f.read()}
            print("NOTE: pyyaml not installed; config saved as raw text.",
                  file=sys.stderr)
    else:
        config = {"_note": "No project.yaml found"}
        if verbose:
            print("  No project.yaml found")

    # Add git info
    git_sha = _run_git(project_dir, ["rev-parse", "HEAD"])
    git_branch = _run_git(project_dir, ["rev-parse", "--abbrev-ref", "HEAD"])
    config["_git.sha"] = git_sha.strip() if git_sha else "unknown"
    config["_git.branch"] = git_branch.strip() if git_branch else "unknown"
    config["_generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    if HAS_YAML:
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=True)
    else:
        with open(out_path, "w", encoding="utf-8") as f:
            for k, v in sorted(config.items()):
                f.write(f"{k}: {v}\n")

    print(f"Generated: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------

def generate_versions(output_dir, verbose=False):
    """Generate versions.txt with Python version + pip freeze."""
    out_path = os.path.join(output_dir, "versions.txt")
    lines = []

    # Python version
    lines.append(f"python: {sys.version}")
    lines.append(f"platform: {sys.platform}")
    lines.append("")

    # pip freeze
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            lines.append("# pip freeze")
            lines.append(result.stdout.strip())
        else:
            lines.append("# pip freeze failed")
            lines.append(result.stderr.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        lines.append(f"# pip freeze unavailable: {exc}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines) + "\n"
    Path(out_path).write_text(content, encoding="utf-8")
    if verbose:
        pkg_count = sum(1 for l in lines if "==" in l)
        print(f"  Captured {pkg_count} package versions")
    print(f"Generated: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Output manifest
# ---------------------------------------------------------------------------

def _sha256_file(filepath):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError) as exc:
        return f"error: {exc}"


def generate_output_manifest(project_dir, output_dir, verbose=False):
    """Walk outputs/ directory, compute SHA-256 hash for every file."""
    outputs_dir = os.path.join(project_dir, "outputs")
    out_path = os.path.join(output_dir, "output_manifest.json")

    manifest = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "gen_provenance.py (G22)",
        "outputs_dir": outputs_dir,
        "files": [],
    }

    if not os.path.isdir(outputs_dir):
        manifest["_note"] = "outputs/ directory not found"
        print("WARNING: outputs/ directory not found", file=sys.stderr)
    else:
        file_count = 0
        for root, _dirs, files in os.walk(outputs_dir):
            for fname in sorted(files):
                filepath = os.path.join(root, fname)
                rel_path = os.path.relpath(filepath, project_dir)
                stat = os.stat(filepath)
                entry = {
                    "path": rel_path,
                    "sha256": _sha256_file(filepath),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                manifest["files"].append(entry)
                file_count += 1

        if verbose:
            print(f"  Hashed {file_count} files in outputs/")

    manifest["total_files"] = len(manifest["files"])
    total_size = sum(f["size_bytes"] for f in manifest["files"])
    manifest["total_size_bytes"] = total_size

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated: {out_path}")
    return out_path, manifest


# ---------------------------------------------------------------------------
# Git info
# ---------------------------------------------------------------------------

def _run_git(project_dir, git_args):
    """Run a git command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + git_args,
            capture_output=True, text=True, timeout=10,
            cwd=project_dir,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def generate_git_info(project_dir, output_dir, verbose=False):
    """Generate git_info.txt with SHA, branch, status, remotes."""
    out_path = os.path.join(output_dir, "git_info.txt")
    lines = []

    sha = _run_git(project_dir, ["rev-parse", "HEAD"])
    lines.append(f"commit: {sha or 'not a git repo'}")

    branch = _run_git(project_dir, ["rev-parse", "--abbrev-ref", "HEAD"])
    lines.append(f"branch: {branch or 'unknown'}")

    status = _run_git(project_dir, ["status", "--porcelain"])
    if status is None:
        lines.append("dirty: unknown (not a git repo)")
    elif status:
        lines.append(f"dirty: yes ({len(status.splitlines())} modified files)")
        lines.append("")
        lines.append("# git status --porcelain")
        lines.append(status)
    else:
        lines.append("dirty: no (clean working tree)")

    lines.append("")
    remotes = _run_git(project_dir, ["remote", "-v"])
    if remotes:
        lines.append("# git remote -v")
        lines.append(remotes)
    else:
        lines.append("# no remotes configured")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines) + "\n"
    Path(out_path).write_text(content, encoding="utf-8")
    if verbose:
        print(f"  Git SHA: {sha or 'N/A'}")
        is_dirty = bool(status) if status is not None else "unknown"
        print(f"  Dirty: {is_dirty}")
    print(f"Generated: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Verification mode
# ---------------------------------------------------------------------------

def verify_manifest(project_dir, output_dir, verbose=False):
    """Compare existing manifest against current files, report drift."""
    manifest_path = os.path.join(output_dir, "output_manifest.json")
    if not os.path.isfile(manifest_path):
        print(f"ERROR: No existing manifest at {manifest_path}", file=sys.stderr)
        print("Run without --verify first to generate the baseline manifest.")
        sys.exit(1)

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    old_files = {entry["path"]: entry for entry in manifest.get("files", [])}
    outputs_dir = os.path.join(project_dir, "outputs")

    # Collect current files
    current_files = {}
    if os.path.isdir(outputs_dir):
        for root, _dirs, files in os.walk(outputs_dir):
            for fname in sorted(files):
                filepath = os.path.join(root, fname)
                rel_path = os.path.relpath(filepath, project_dir)
                current_files[rel_path] = _sha256_file(filepath)

    # Compare
    added = []
    removed = []
    changed = []
    unchanged = 0

    for path, sha in current_files.items():
        if path not in old_files:
            added.append(path)
        elif old_files[path]["sha256"] != sha:
            changed.append((path, old_files[path]["sha256"][:12], sha[:12]))
        else:
            unchanged += 1

    for path in old_files:
        if path not in current_files:
            removed.append(path)

    # Report
    print("=== Provenance Verification Report ===")
    print(f"Baseline manifest: {manifest.get('generated', 'unknown')}")
    print(f"Unchanged: {unchanged}")
    print(f"Added:     {len(added)}")
    print(f"Removed:   {len(removed)}")
    print(f"Changed:   {len(changed)}")
    print()

    if added:
        print("NEW FILES (not in manifest):")
        for p in added:
            print(f"  + {p}")
        print()

    if removed:
        print("MISSING FILES (in manifest but not on disk):")
        for p in removed:
            print(f"  - {p}")
        print()

    if changed:
        print("CHANGED FILES (hash mismatch):")
        for p, old_h, new_h in changed:
            print(f"  ~ {p}  ({old_h}... -> {new_h}...)")
        print()

    drift = len(added) + len(removed) + len(changed)
    if drift == 0:
        print("STATUS: CLEAN — no drift detected.")
    else:
        print(f"STATUS: DRIFT — {drift} file(s) differ from manifest.")

    return drift


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Capture full reproducibility snapshot (provenance)."
    )
    parser.add_argument(
        "--project-dir", required=True,
        help="Root directory of the project."
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory for provenance files (default: <project-dir>/provenance/)."
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Verify existing manifest against current files (detect drift)."
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

    output_dir = args.output_dir or os.path.join(project_dir, "provenance")
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(project_dir, output_dir)

    if args.verbose:
        print(f"Project:    {project_dir}")
        print(f"Output dir: {output_dir}")
        print()

    if args.verify:
        drift = verify_manifest(project_dir, output_dir, verbose=args.verbose)
        sys.exit(1 if drift > 0 else 0)

    # Generate all provenance files
    print("--- Generating provenance snapshot ---")
    print()

    if args.verbose:
        print("1. Config resolution")
    generate_config_resolved(project_dir, output_dir, verbose=args.verbose)

    if args.verbose:
        print("\n2. Package versions")
    generate_versions(output_dir, verbose=args.verbose)

    if args.verbose:
        print("\n3. Output manifest")
    generate_output_manifest(project_dir, output_dir, verbose=args.verbose)

    if args.verbose:
        print("\n4. Git info")
    generate_git_info(project_dir, output_dir, verbose=args.verbose)

    print(f"\nProvenance snapshot complete: {output_dir}/")


if __name__ == "__main__":
    main()
