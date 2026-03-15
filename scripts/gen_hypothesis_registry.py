#!/usr/bin/env python3
"""gen_hypothesis_registry.py (G24) — Initialize and manage hypothesis registry.

Creates, checks, and extends a HYPOTHESIS_REGISTRY.md file that tracks
experimental hypotheses, their status, and resolution.

Usage:
    python scripts/gen_hypothesis_registry.py --project-dir /path/to/project --init
    python scripts/gen_hypothesis_registry.py --project-dir . --check
    python scripts/gen_hypothesis_registry.py --project-dir . --add
"""
import argparse
import json
import os
import re
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
# Registry schema
# ---------------------------------------------------------------------------

_HEADER = """# Hypothesis Registry

| ID | Hypothesis | Type | Priority | Status | Resolution | Evidence | Notes |
|----|-----------|------|----------|--------|------------|----------|-------|"""

_STATUS_VALUES = {"PENDING", "TESTING", "RESOLVED", "DEFERRED", "DROPPED"}
_RESOLUTION_VALUES = {"PENDING", "SUPPORTED", "REFUTED", "INCONCLUSIVE", "N/A"}
_TYPE_VALUES = {"PRIMARY", "SECONDARY", "EXPLORATORY"}
_PRIORITY_VALUES = {"HIGH", "MEDIUM", "LOW"}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_table_row(line):
    """Parse a markdown table row into a dict."""
    # Skip separator rows
    if re.match(r"^\|[-\s|]+\|$", line.strip()):
        return None
    # Skip header
    if "| ID |" in line or "| Hypothesis |" in line:
        return None

    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 8:
        return None

    return {
        "id": cells[0].strip(),
        "hypothesis": cells[1].strip(),
        "type": cells[2].strip(),
        "priority": cells[3].strip(),
        "status": cells[4].strip(),
        "resolution": cells[5].strip(),
        "evidence": cells[6].strip(),
        "notes": cells[7].strip() if len(cells) > 7 else "",
    }


def parse_registry(filepath, verbose=False):
    """Parse an existing HYPOTHESIS_REGISTRY.md. Returns list of dicts."""
    entries = []
    try:
        text = Path(filepath).read_text(encoding="utf-8")
    except FileNotFoundError:
        if verbose:
            print(f"  Registry not found: {filepath}")
        return entries

    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip().startswith("|"):
            continue
        row = _parse_table_row(line)
        if row is not None:
            row["_line_no"] = line_no
            entries.append(row)
            if verbose:
                print(f"  Parsed {row['id']}: {row['status']} / {row['resolution']}")

    return entries


# ---------------------------------------------------------------------------
# Init mode
# ---------------------------------------------------------------------------

def _load_hypotheses_from_yaml(project_dir):
    """Try to read hypotheses from project.yaml."""
    yaml_path = os.path.join(project_dir, "project.yaml")
    if not HAS_YAML or not os.path.isfile(yaml_path):
        return []

    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return []

    hypotheses = data.get("hypotheses", [])
    if not isinstance(hypotheses, list):
        return []

    results = []
    for i, h in enumerate(hypotheses, start=1):
        if isinstance(h, str):
            results.append({
                "id": f"H-{i:03d}",
                "hypothesis": h,
                "type": "PRIMARY",
                "priority": "MEDIUM",
                "status": "PENDING",
                "resolution": "PENDING",
                "evidence": "",
                "notes": "From project.yaml",
            })
        elif isinstance(h, dict):
            results.append({
                "id": h.get("id", f"H-{i:03d}"),
                "hypothesis": h.get("hypothesis", h.get("text", "")),
                "type": h.get("type", "PRIMARY").upper(),
                "priority": h.get("priority", "MEDIUM").upper(),
                "status": h.get("status", "PENDING").upper(),
                "resolution": h.get("resolution", "PENDING").upper(),
                "evidence": h.get("evidence", ""),
                "notes": h.get("notes", "From project.yaml"),
            })

    return results


def _format_row(entry):
    """Format a hypothesis entry as a markdown table row."""
    return (f"| {entry['id']} "
            f"| {entry['hypothesis']} "
            f"| {entry['type']} "
            f"| {entry['priority']} "
            f"| {entry['status']} "
            f"| {entry['resolution']} "
            f"| {entry['evidence']} "
            f"| {entry['notes']} |")


def init_registry(project_dir, verbose=False):
    """Create HYPOTHESIS_REGISTRY.md from project.yaml or template."""
    registry_path = os.path.join(project_dir, "HYPOTHESIS_REGISTRY.md")

    if os.path.isfile(registry_path):
        print(f"WARNING: Registry already exists at {registry_path}",
              file=sys.stderr)
        print("Use --check to inspect or --add to extend it.")
        return

    hypotheses = _load_hypotheses_from_yaml(project_dir)

    if not hypotheses:
        # Generate template entries
        hypotheses = [
            {
                "id": "H-001",
                "hypothesis": "Model X outperforms baseline by >5% on metric Y",
                "type": "PRIMARY",
                "priority": "HIGH",
                "status": "PENDING",
                "resolution": "PENDING",
                "evidence": "",
                "notes": "Template — replace with actual hypothesis",
            },
            {
                "id": "H-002",
                "hypothesis": "Feature set A contributes more than feature set B",
                "type": "SECONDARY",
                "priority": "MEDIUM",
                "status": "PENDING",
                "resolution": "PENDING",
                "evidence": "",
                "notes": "Template — replace with actual hypothesis",
            },
            {
                "id": "H-003",
                "hypothesis": "Performance degrades gracefully under distribution shift",
                "type": "EXPLORATORY",
                "priority": "LOW",
                "status": "PENDING",
                "resolution": "PENDING",
                "evidence": "",
                "notes": "Template — replace with actual hypothesis",
            },
        ]
        if verbose:
            print("  No hypotheses in project.yaml; using template entries")
    else:
        if verbose:
            print(f"  Loaded {len(hypotheses)} hypotheses from project.yaml")

    lines = [_HEADER]
    for entry in hypotheses:
        lines.append(_format_row(entry))

    # Add footer
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append("")
    lines.append(f"---")
    lines.append(f"Generated: {now} by gen_hypothesis_registry.py (G24)")
    lines.append("")
    lines.append("## Status Values")
    lines.append(f"- Status: {', '.join(sorted(_STATUS_VALUES))}")
    lines.append(f"- Resolution: {', '.join(sorted(_RESOLUTION_VALUES))}")
    lines.append(f"- Type: {', '.join(sorted(_TYPE_VALUES))}")
    lines.append(f"- Priority: {', '.join(sorted(_PRIORITY_VALUES))}")

    content = "\n".join(lines) + "\n"
    Path(registry_path).write_text(content, encoding="utf-8")
    print(f"Generated: {registry_path}")
    print(f"Hypotheses: {len(hypotheses)}")


# ---------------------------------------------------------------------------
# Check mode
# ---------------------------------------------------------------------------

def check_registry(project_dir, verbose=False):
    """Read existing registry, verify completeness, print summary."""
    registry_path = os.path.join(project_dir, "HYPOTHESIS_REGISTRY.md")
    entries = parse_registry(registry_path, verbose=verbose)

    if not entries:
        print(f"No hypotheses found in {registry_path}")
        print("Run with --init to create the registry.")
        return

    total = len(entries)
    by_status = {}
    by_resolution = {}
    issues = []

    for entry in entries:
        status = entry["status"].upper()
        resolution = entry["resolution"].upper()
        by_status[status] = by_status.get(status, 0) + 1
        by_resolution[resolution] = by_resolution.get(resolution, 0) + 1

        # Validation checks
        if status not in _STATUS_VALUES:
            issues.append(f"{entry['id']}: Unknown status '{status}'")
        if resolution not in _RESOLUTION_VALUES:
            issues.append(f"{entry['id']}: Unknown resolution '{resolution}'")
        if status == "RESOLVED" and resolution == "PENDING":
            issues.append(f"{entry['id']}: Status is RESOLVED but resolution is PENDING")
        if status != "PENDING" and not entry["evidence"]:
            issues.append(f"{entry['id']}: Status is {status} but no evidence listed")

    pending_count = by_resolution.get("PENDING", 0)
    resolved_pct = ((total - pending_count) / total * 100) if total else 0

    # Print summary
    print("=== Hypothesis Registry Check ===")
    print(f"Total hypotheses: {total}")
    print(f"Resolved: {total - pending_count}/{total} ({resolved_pct:.0f}%)")
    print()

    print("By Status:")
    for status in sorted(by_status):
        print(f"  {status}: {by_status[status]}")
    print()

    print("By Resolution:")
    for res in sorted(by_resolution):
        print(f"  {res}: {by_resolution[res]}")
    print()

    if issues:
        print(f"Issues ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No issues found.")

    # Exit code: non-zero if any PENDING remain
    all_resolved = pending_count == 0
    if all_resolved:
        print("\nSTATUS: ALL RESOLVED")
    else:
        print(f"\nSTATUS: {pending_count} PENDING hypothesis(es) remain")

    return all_resolved


# ---------------------------------------------------------------------------
# Add mode
# ---------------------------------------------------------------------------

def add_hypothesis(project_dir, verbose=False):
    """Generate a new hypothesis row for piping into the registry."""
    registry_path = os.path.join(project_dir, "HYPOTHESIS_REGISTRY.md")
    entries = parse_registry(registry_path, verbose=False)

    # Determine next ID
    max_id = 0
    for entry in entries:
        m = re.match(r"H-(\d+)", entry["id"])
        if m:
            max_id = max(max_id, int(m.group(1)))

    next_id = f"H-{max_id + 1:03d}"

    # Print template to stdout (for piping or manual copy)
    row = {
        "id": next_id,
        "hypothesis": "<DESCRIBE YOUR HYPOTHESIS HERE>",
        "type": "PRIMARY",
        "priority": "MEDIUM",
        "status": "PENDING",
        "resolution": "PENDING",
        "evidence": "",
        "notes": f"Added {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
    }

    print("Add the following row to HYPOTHESIS_REGISTRY.md:")
    print()
    print(_format_row(row))
    print()
    print(f"Next available ID: {next_id}")
    print(f"Registry: {registry_path}")

    # Also output as JSON for programmatic use
    json_out = json.dumps(row, indent=2)
    if verbose:
        print(f"\nJSON representation:")
        print(json_out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Initialize and manage hypothesis registry."
    )
    parser.add_argument(
        "--project-dir", required=True,
        help="Root directory of the project."
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--init", action="store_true",
        help="Create HYPOTHESIS_REGISTRY.md from project.yaml or template."
    )
    mode_group.add_argument(
        "--check", action="store_true",
        help="Check existing registry for completeness and validity."
    )
    mode_group.add_argument(
        "--add", action="store_true",
        help="Generate a new hypothesis row (prints to stdout)."
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

    if args.verbose:
        print(f"Project: {project_dir}")
        print()

    if args.init:
        init_registry(project_dir, verbose=args.verbose)
    elif args.check:
        all_resolved = check_registry(project_dir, verbose=args.verbose)
        sys.exit(0 if all_resolved else 1)
    elif args.add:
        add_hypothesis(project_dir, verbose=args.verbose)


if __name__ == "__main__":
    main()
