#!/usr/bin/env python3
"""gen_findings_audit.py — Audit FINDINGS.md claims against raw JSON outputs.

Parses numeric claims from FINDINGS.md, cross-references them against all
JSON files in the outputs directory, and generates a FINDINGS_AUDIT_REPORT.md
flagging unmatched claims, rounding mismatches, untagged claims, and seed counts.

Usage:
    python scripts/gen_findings_audit.py --project-dir /path/to/project
    python scripts/gen_findings_audit.py --project-dir . --findings FINDINGS.md --outputs-dir outputs/
    python scripts/gen_findings_audit.py --project-dir . --verbose
"""
import argparse
import glob
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# Number extraction from FINDINGS.md
# ---------------------------------------------------------------------------

# Patterns that capture numeric claims in findings prose.
# Order matters: more specific patterns first.
_NUM_PATTERNS = [
    # 0.XXXX style metrics (precision/recall/F1/AUC etc.)
    re.compile(r"(?P<num>[01]\.\d{2,6})"),
    # Percentages like 85%, 85.3%
    re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*%"),
    # Percentage-point deltas like 4.2pp, 12pp
    re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*pp"),
    # Plain decimals (e.g. 3.14, 12.5)
    re.compile(r"(?P<num>\d+\.\d+)"),
    # Integers followed by a unit-like word (e.g. "3 seeds", "128 features")
    re.compile(r"(?P<num>\d+)\s+(?:seeds?|features?|samples?|epochs?|layers?|"
               r"classes?|clusters?|iterations?|runs?|folds?|models?|"
               r"scenarios?|attacks?|methods?|datasets?|experiments?)"),
    # Standalone integers >= 2 digits (skip single-digit noise like "a 1-layer")
    re.compile(r"(?<!\w)(?P<num>\d{2,})(?!\w)"),
]

# Claim strength tags
_STRENGTH_TAGS = {"[DEMONSTRATED]", "[SUGGESTED]", "[PROJECTED]", "[HYPOTHESIZED]"}
_TAG_PATTERN = re.compile(r"\[(DEMONSTRATED|SUGGESTED|PROJECTED|HYPOTHESIZED)\]")


def _context_window(line: str, start: int, end: int, width: int = 10) -> str:
    """Return up to *width* words before and after the span [start, end)."""
    before = line[:start].split()
    after = line[end:].split()
    before_ctx = " ".join(before[-width:])
    after_ctx = " ".join(after[:width])
    snippet = line[start:end]
    return f"{before_ctx} **{snippet}** {after_ctx}".strip()


class Claim:
    """A single numeric claim extracted from FINDINGS.md."""

    def __init__(self, line_no: int, raw_line: str, number: float,
                 number_str: str, context: str, has_tag: bool):
        self.line_no = line_no
        self.raw_line = raw_line.rstrip()
        self.number = number
        self.number_str = number_str
        self.context = context
        self.has_tag = has_tag

    def __repr__(self):
        return f"Claim(L{self.line_no}, {self.number_str})"


def parse_findings(findings_path: str, verbose: bool = False) -> list:
    """Extract all numeric claims from FINDINGS.md."""
    claims = []
    try:
        text = Path(findings_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"WARNING: {findings_path} not found — skipping findings parse.",
              file=sys.stderr)
        return claims

    for line_no, line in enumerate(text.splitlines(), start=1):
        # Skip blank lines and markdown headers that are just titles
        stripped = line.strip()
        if not stripped:
            continue

        has_tag = bool(_TAG_PATTERN.search(line))

        # Track positions already consumed to avoid double-counting
        consumed = set()
        for pat in _NUM_PATTERNS:
            for m in pat.finditer(line):
                start, end = m.span("num")
                # Skip if overlapping with an already-consumed span
                span_range = range(start, end)
                if any(pos in consumed for pos in span_range):
                    continue
                for pos in span_range:
                    consumed.add(pos)

                num_str = m.group("num")
                try:
                    num_val = float(num_str)
                except ValueError:
                    continue

                ctx = _context_window(line, m.start(), m.end())
                claims.append(Claim(
                    line_no=line_no,
                    raw_line=line,
                    number=num_val,
                    number_str=num_str,
                    context=ctx,
                    has_tag=has_tag,
                ))
                if verbose:
                    print(f"  [claim] L{line_no}: {num_str} -> {num_val}")

    return claims


# ---------------------------------------------------------------------------
# JSON output parsing
# ---------------------------------------------------------------------------

class JsonValue:
    """A single numeric value found inside a JSON output file."""

    def __init__(self, filepath: str, key_path: str, value: float):
        self.filepath = filepath
        self.key_path = key_path
        self.value = value

    def __repr__(self):
        return f"JsonValue({self.key_path}={self.value})"


def _flatten_json(obj, prefix: str = "") -> list:
    """Recursively flatten a JSON object into (key_path, value) pairs."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            results.extend(_flatten_json(v, new_key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{prefix}[{i}]"
            results.extend(_flatten_json(v, new_key))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        results.append((prefix, float(obj)))
    return results


def parse_json_outputs(outputs_dir: str, verbose: bool = False) -> list:
    """Load all JSON files under outputs_dir and extract numeric values."""
    values = []
    pattern = os.path.join(outputs_dir, "**", "*.json")
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        print(f"WARNING: No JSON files found in {outputs_dir}", file=sys.stderr)
        return values

    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"WARNING: Could not parse {fp}: {exc}", file=sys.stderr)
            continue

        rel_path = os.path.relpath(fp, outputs_dir)
        flat = _flatten_json(data)
        for key_path, val in flat:
            values.append(JsonValue(filepath=rel_path, key_path=key_path, value=val))
            if verbose:
                print(f"  [json] {rel_path} :: {key_path} = {val}")

    return values


def count_seeds(outputs_dir: str) -> list:
    """Find files matching *seed* patterns and extract unique seed identifiers."""
    pattern = os.path.join(outputs_dir, "**", "*seed*")
    seed_files = sorted(glob.glob(pattern, recursive=True))
    # Also check JSON files for seed keys
    json_pattern = os.path.join(outputs_dir, "**", "*.json")
    json_files = sorted(glob.glob(json_pattern, recursive=True))

    seeds_found = set()

    # Extract seed numbers from filenames
    seed_in_name = re.compile(r"seed[_-]?(\d+)", re.IGNORECASE)
    for fp in seed_files:
        basename = os.path.basename(fp)
        m = seed_in_name.search(basename)
        if m:
            seeds_found.add(int(m.group(1)))

    # Also scan JSON filenames even if they don't have "seed" in the path
    for fp in json_files:
        basename = os.path.basename(fp)
        m = seed_in_name.search(basename)
        if m:
            seeds_found.add(int(m.group(1)))

    # Check inside JSON files for seed keys
    for fp in json_files:
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, dict):
            for key in ("seed", "random_seed", "random_state"):
                if key in data and isinstance(data[key], (int, float)):
                    seeds_found.add(int(data[key]))

    return sorted(seeds_found), seed_files


# ---------------------------------------------------------------------------
# Cross-referencing
# ---------------------------------------------------------------------------

_ROUNDING_TOLERANCE = 0.015  # 1.5% relative or 0.005 absolute


def _is_close(a: float, b: float) -> bool:
    """Check if two numbers are close but not exactly equal."""
    if a == b:
        return False  # exact match, not a rounding issue
    if a == 0.0 and b == 0.0:
        return False
    abs_diff = abs(a - b)
    # Absolute tolerance for small numbers
    if abs_diff < 0.006:
        return True
    # Relative tolerance
    denom = max(abs(a), abs(b), 1e-12)
    return (abs_diff / denom) < _ROUNDING_TOLERANCE


def cross_reference(claims: list, json_values: list, verbose: bool = False):
    """Match claims against JSON values. Returns (matched, close, unmatched)."""
    matched = []   # (claim, json_value)
    close = []     # (claim, json_value, delta)
    unmatched = [] # claim

    # Build a lookup: value -> list of JsonValue
    exact_lookup = {}
    for jv in json_values:
        # Round to 6 decimal places to handle float precision
        key = round(jv.value, 6)
        exact_lookup.setdefault(key, []).append(jv)

    for claim in claims:
        claim_val = round(claim.number, 6)

        # 1. Exact match
        if claim_val in exact_lookup:
            matched.append((claim, exact_lookup[claim_val][0]))
            if verbose:
                print(f"  [match] L{claim.line_no} {claim.number_str} == "
                      f"{exact_lookup[claim_val][0]}")
            continue

        # 2. Close match
        best_close = None
        best_delta = float("inf")
        for jv in json_values:
            if _is_close(claim.number, jv.value):
                delta = abs(claim.number - jv.value)
                if delta < best_delta:
                    best_delta = delta
                    best_close = jv

        if best_close is not None:
            close.append((claim, best_close, best_delta))
            if verbose:
                print(f"  [close] L{claim.line_no} {claim.number_str} ~ "
                      f"{best_close.value} (delta={best_delta:.6f})")
            continue

        # 3. Unmatched
        unmatched.append(claim)
        if verbose:
            print(f"  [unmatched] L{claim.line_no} {claim.number_str}")

    return matched, close, unmatched


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _escape_pipe(s: str) -> str:
    """Escape pipe characters for markdown tables."""
    return s.replace("|", "\\|")


def _truncate(s: str, maxlen: int = 80) -> str:
    if len(s) <= maxlen:
        return s
    return s[:maxlen - 3] + "..."


def generate_report(
    project_name: str,
    claims: list,
    matched: list,
    close: list,
    unmatched: list,
    seeds: list,
    seed_files: list,
    output_path: str,
):
    """Write the FINDINGS_AUDIT_REPORT.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_claims = len(claims)
    tagged_claims = sum(1 for c in claims if c.has_tag)
    # Only count claims on lines that have a number (all claims qualify)
    tag_pct = (tagged_claims / total_claims * 100) if total_claims else 0
    seed_pass = len(seeds) >= 3

    lines = []
    lines.append("# Findings Audit Report")
    lines.append(f"Generated: {now}")
    lines.append(f"Project: {project_name}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Claims found: {total_claims}")
    lines.append(f"- Claims with JSON match: {len(matched)}")
    lines.append(f"- Claims without JSON match: {len(unmatched)}"
                 + (" (REVIEW NEEDED)" if unmatched else ""))
    lines.append(f"- Close but not exact: {len(close)}"
                 + (" (CHECK ROUNDING)" if close else ""))
    lines.append(f"- Claim strength tags: {tagged_claims}/{total_claims} "
                 f"claims tagged ({tag_pct:.0f}%)")
    lines.append(f"- Seeds found: {len(seeds)}")
    lines.append("")

    # Unmatched claims
    lines.append("## Unmatched Claims (review required)")
    if unmatched:
        lines.append("| Line | Claim Text | Number | Status |")
        lines.append("|------|-----------|--------|--------|")
        for c in unmatched:
            text = _escape_pipe(_truncate(c.context))
            lines.append(f"| {c.line_no} | {text} | {c.number_str} | NO MATCH |")
    else:
        lines.append("*All numeric claims matched a JSON output.*")
    lines.append("")

    # Close matches
    lines.append("## Close Matches (check rounding)")
    if close:
        lines.append("| Line | FINDINGS Value | JSON Value | JSON Path | Delta |")
        lines.append("|------|---------------|-----------|-----------|-------|")
        for c, jv, delta in close:
            json_path = _escape_pipe(f"{jv.filepath}::{jv.key_path}")
            lines.append(f"| {c.line_no} | {c.number_str} | {jv.value:.6g} "
                         f"| {json_path} | {delta:.6f} |")
    else:
        lines.append("*No rounding mismatches detected.*")
    lines.append("")

    # Untagged claims
    lines.append("## Untagged Claims")
    untagged = [c for c in claims if not c.has_tag]
    if untagged:
        # Deduplicate by line number
        seen_lines = set()
        lines.append("| Line | Claim Text |")
        lines.append("|------|-----------|")
        for c in untagged:
            if c.line_no in seen_lines:
                continue
            seen_lines.add(c.line_no)
            text = _escape_pipe(_truncate(c.raw_line.strip()))
            lines.append(f"| {c.line_no} | {text} |")
    else:
        lines.append("*All quantitative claims have strength tags.*")
    lines.append("")

    # Seed analysis
    lines.append("## Seed Analysis")
    if seeds:
        lines.append(f"Seeds found: {seeds}")
    else:
        lines.append("Seeds found: *none detected*")
    lines.append(f"Minimum required: 3")
    lines.append(f"Status: {'PASS' if seed_pass else 'FAIL'}")
    if seed_files:
        lines.append("")
        lines.append("Seed-related files:")
        for sf in seed_files:
            lines.append(f"- `{sf}`")
    lines.append("")

    content = "\n".join(lines)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"Generated: {output_path}")
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _load_project_name(project_dir: str) -> str:
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit FINDINGS.md claims against raw JSON outputs."
    )
    parser.add_argument(
        "--project-dir", required=True,
        help="Root directory of the project."
    )
    parser.add_argument(
        "--findings", default=None,
        help="Path to FINDINGS.md (default: <project-dir>/FINDINGS.md)."
    )
    parser.add_argument(
        "--outputs-dir", default=None,
        help="Path to outputs directory (default: <project-dir>/outputs/)."
    )
    parser.add_argument(
        "--output", default=None,
        help="Output path for report (default: <project-dir>/FINDINGS_AUDIT_REPORT.md)."
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

    findings_path = args.findings or os.path.join(project_dir, "FINDINGS.md")
    outputs_dir = args.outputs_dir or os.path.join(project_dir, "outputs")
    output_path = args.output or os.path.join(project_dir, "FINDINGS_AUDIT_REPORT.md")
    project_name = _load_project_name(project_dir)

    if args.verbose:
        print(f"Project: {project_name}")
        print(f"Findings: {findings_path}")
        print(f"Outputs:  {outputs_dir}")
        print(f"Report:   {output_path}")
        print()

    # Step 1: Parse FINDINGS.md
    if args.verbose:
        print("--- Parsing FINDINGS.md ---")
    claims = parse_findings(findings_path, verbose=args.verbose)
    print(f"Claims extracted: {len(claims)}")

    # Step 2: Parse JSON outputs
    if args.verbose:
        print("\n--- Parsing JSON outputs ---")
    json_values = parse_json_outputs(outputs_dir, verbose=args.verbose)
    print(f"JSON values extracted: {len(json_values)}")

    # Step 3: Cross-reference
    if args.verbose:
        print("\n--- Cross-referencing ---")
    matched, close, unmatched = cross_reference(
        claims, json_values, verbose=args.verbose
    )
    print(f"Matched: {len(matched)}, Close: {len(close)}, Unmatched: {len(unmatched)}")

    # Step 4: Seed analysis
    seeds, seed_files = count_seeds(outputs_dir)
    print(f"Seeds found: {seeds if seeds else 'none'}")

    # Step 5: Generate report
    if args.verbose:
        print("\n--- Generating report ---")
    generate_report(
        project_name=project_name,
        claims=claims,
        matched=matched,
        close=close,
        unmatched=unmatched,
        seeds=seeds,
        seed_files=seed_files,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
