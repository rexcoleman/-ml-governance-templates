#!/usr/bin/env python3
"""gen_voice_lint.py — Publication voice linter for ML project deliverables.

Scans FINDINGS.md, README.md, and blog drafts for overclaiming language.
Checks quantitative claims, novelty assertions, and statistical language
against evidence standards.

Usage:
    python scripts/gen_voice_lint.py --project-dir /path/to/project [--strict] [--fix-suggestions]
"""
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class Finding(NamedTuple):
    file: str
    line: int
    severity: str  # ERROR | WARNING
    rule: str
    text: str
    suggestion: Optional[str] = None


# ---------------------------------------------------------------------------
# Target files (relative to project dir)
# ---------------------------------------------------------------------------

TARGET_FILES = [
    "FINDINGS.md",
    "README.md",
    "blog/draft.md",
    "blog/conference_abstract.md",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _window(lines: List[str], idx: int, radius: int = 2) -> str:
    """Return a joined window of lines around *idx*."""
    lo = max(0, idx - radius)
    hi = min(len(lines), idx + radius + 1)
    return "\n".join(lines[lo:hi])


def _has_tag_nearby(lines: List[str], idx: int, tag: str, radius: int = 1) -> bool:
    """Check if *tag* appears on the same line or within *radius* lines above."""
    lo = max(0, idx - radius)
    hi = idx + 1  # include current line
    window = "\n".join(lines[lo:hi])
    return tag in window


def _has_within_lines(lines: List[str], idx: int, term: str, radius: int = 2) -> bool:
    """Check if *term* appears within *radius* lines of *idx*."""
    lo = max(0, idx - radius)
    hi = min(len(lines), idx + radius + 1)
    window = "\n".join(lines[lo:hi]).lower()
    return term.lower() in window


# ---------------------------------------------------------------------------
# Data-type detection
# ---------------------------------------------------------------------------

SYNTHETIC_MARKERS = [
    "synthetic", "paysim", "simulated", "generated data",
    "simulation", "artificially generated",
]


def detect_data_type(project_dir: Path) -> str:
    """Return 'synthetic', 'real', or 'unknown'."""
    # Try project.yaml first
    if yaml is not None:
        yaml_path = project_dir / "project.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                proj = yaml.safe_load(f) or {}
            dt = proj.get("data_type", "")
            if dt:
                return dt.lower()
            # Also check nested structures
            data = proj.get("data", {})
            if isinstance(data, dict):
                dt = data.get("type", "")
                if dt:
                    return dt.lower()

    # Fall back to FINDINGS.md content scan
    findings_path = project_dir / "FINDINGS.md"
    if findings_path.exists():
        content = findings_path.read_text().lower()
        for marker in SYNTHETIC_MARKERS:
            if marker in content:
                return "synthetic"

    return "unknown"


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------

# Pre-compiled patterns
RE_NOVEL = re.compile(r"\bnovel\b", re.IGNORECASE)
RE_FIRST = re.compile(r"\bfirst\b", re.IGNORECASE)
RE_VALIDATED = re.compile(r"\bvalidated\b", re.IGNORECASE)
RE_PROVED = re.compile(r"\bprov(?:ed|en)\b", re.IGNORECASE)
RE_BREAKTHROUGH = re.compile(r"\bbreakthrough\b", re.IGNORECASE)
RE_SIGNIFICANT = re.compile(r"\bsignificant(?:ly)?\b", re.IGNORECASE)
RE_OUTPERFORMS = re.compile(r"\boutperform(?:s|ed|ing)?\b", re.IGNORECASE)
RE_METRIC = re.compile(r"\b0\.\d{2,}")  # 0.XXX numbers
RE_SEED = re.compile(r"\bseed\b", re.IGNORECASE)

# Landscape-evidence markers (for rule 2)
LANDSCAPE_MARKERS = [
    "landscape", "prior work", "existing", "compared to",
    "literature", "baseline", "state-of-the-art", "sota",
    "previous", "related work",
]

# Statistical test markers (for rule 7)
STAT_MARKERS = [
    "p-value", "p =", "p<", "p >", "t-test", "mann-whitney",
    "wilcoxon", "chi-squared", "anova", "bonferroni",
    "confidence interval", "ci ", "statistical test",
    "fisher", "kolmogorov", "kruskal",
]

# Fix suggestion templates
FIX_TEMPLATES = {
    "R1-novel": 'Add [DEMONSTRATED] tag or replace "novel" with "proposed" / "alternative"',
    "R2-first": 'Add competitive landscape evidence or replace "first" with "an early" / "one of"',
    "R3-validated": 'Add multi-seed evidence or replace "validated" with "evaluated" / "assessed"',
    "R4-proved": 'Replace "proved"/"proven" with "demonstrated" / "showed" / "provided evidence for"',
    "R5-breakthrough": 'Replace "breakthrough" with "finding" / "result" / "improvement"',
    "R6-synthetic-qual": 'Add "synthetic" / "simulated" qualifier within 2 lines of the claim',
    "R7-significant": 'Add statistical test reference or replace "significant" with "notable" / "substantial"',
    "R8-outperforms": 'Add confidence interval or statistical comparison, or use "achieves higher X than"',
    "R9-untagged-metric": "Add [DEMONSTRATED], [SUGGESTED], or [EXPLORATORY] tag near the metric",
}


def check_line(
    lines: List[str],
    idx: int,
    filename: str,
    data_type: str,
    fix_suggestions: bool,
) -> List[Finding]:
    """Run all rules against a single line. Return findings."""
    line = lines[idx]
    results: List[Finding] = []

    def _add(severity: str, rule: str, suggestion_key: Optional[str] = None) -> None:
        suggestion = FIX_TEMPLATES.get(suggestion_key or "") if fix_suggestions else None
        results.append(Finding(
            file=filename,
            line=idx + 1,
            severity=severity,
            rule=rule,
            text=line.strip()[:120],
            suggestion=suggestion,
        ))

    # R1: "novel" without [DEMONSTRATED]
    if RE_NOVEL.search(line):
        if not _has_tag_nearby(lines, idx, "[DEMONSTRATED]", radius=1):
            _add("WARNING", "R1: 'novel' without [DEMONSTRATED] tag", "R1-novel")

    # R2: "first" without landscape evidence
    if RE_FIRST.search(line):
        window = _window(lines, idx, radius=3).lower()
        if not any(m in window for m in LANDSCAPE_MARKERS):
            _add("WARNING", "R2: 'first' without competitive landscape evidence", "R2-first")

    # R3: "validated" without multi-seed evidence
    if RE_VALIDATED.search(line):
        window = _window(lines, idx, radius=3).lower()
        if "seed" not in window and "seeds" not in window:
            _add("WARNING", "R3: 'validated' without multi-seed evidence", "R3-validated")

    # R4: "proved"/"proven" in ML context → ERROR
    if RE_PROVED.search(line):
        _add("ERROR", "R4: 'proved'/'proven' in ML context (use 'demonstrated')", "R4-proved")

    # R5: "breakthrough" in FINDINGS.md → ERROR
    if RE_BREAKTHROUGH.search(line) and filename == "FINDINGS.md":
        _add("ERROR", "R5: 'breakthrough' in FINDINGS.md", "R5-breakthrough")

    # R6: Quantitative claim on synthetic data without qualifier
    if data_type == "synthetic" and RE_METRIC.search(line):
        if not _has_within_lines(lines, idx, "synthetic", radius=2):
            if not _has_within_lines(lines, idx, "simulated", radius=2):
                if not _has_within_lines(lines, idx, "paysim", radius=2):
                    _add("ERROR", "R6: metric on synthetic data without qualifier", "R6-synthetic-qual")

    # R7: "significant" without statistical test
    if RE_SIGNIFICANT.search(line):
        window = _window(lines, idx, radius=3).lower()
        if not any(m in window for m in STAT_MARKERS):
            _add("WARNING", "R7: 'significant' without statistical test", "R7-significant")

    # R8: "outperforms" without CI or statistical comparison
    if RE_OUTPERFORMS.search(line):
        window = _window(lines, idx, radius=3).lower()
        if not any(m in window for m in STAT_MARKERS + ["confidence interval", "ci ", "±"]):
            _add("WARNING", "R8: 'outperforms' without CI or statistical comparison", "R8-outperforms")

    # R9: Untagged metrics (0.XXX)
    if RE_METRIC.search(line):
        evidence_tags = ["[DEMONSTRATED]", "[SUGGESTED]", "[EXPLORATORY]", "[BASELINE]"]
        if not any(_has_tag_nearby(lines, idx, tag, radius=1) for tag in evidence_tags):
            _add("WARNING", "R9: untagged metric (0.XXX) without evidence tag", "R9-untagged-metric")

    return results


# ---------------------------------------------------------------------------
# File scanner
# ---------------------------------------------------------------------------

def scan_file(
    project_dir: Path,
    rel_path: str,
    data_type: str,
    fix_suggestions: bool,
) -> Tuple[bool, List[Finding]]:
    """Scan a single file. Returns (file_existed, findings)."""
    full_path = project_dir / rel_path
    if not full_path.exists():
        return False, []

    content = full_path.read_text()
    lines = content.splitlines()
    findings: List[Finding] = []

    for idx in range(len(lines)):
        findings.extend(check_line(lines, idx, rel_path, data_type, fix_suggestions))

    return True, findings


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    project_dir: Path,
    findings: List[Finding],
    files_scanned: int,
    strict: bool,
    fix_suggestions: bool,
    data_type: str,
) -> str:
    """Generate the markdown lint report."""
    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARNING"]

    if strict:
        errors = errors + warnings
        warnings = []

    lines: List[str] = []
    lines.append("# Publication Voice Lint Report")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Project: {project_dir}")
    lines.append(f"Data type detected: {data_type}")
    if strict:
        lines.append("Mode: **STRICT** (warnings promoted to errors)")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- Files scanned: {files_scanned}")
    lines.append(f"- Errors: {len(errors)} (must fix before publication)")
    lines.append(f"- Warnings: {len(warnings)} (review recommended)")
    lines.append("")

    # Errors table
    lines.append("## Errors")
    if errors:
        lines.append("")
        lines.append("| File | Line | Rule | Text |")
        lines.append("|------|------|------|------|")
        for f in errors:
            escaped = f.text.replace("|", "\\|")
            lines.append(f"| {f.file} | {f.line} | {f.rule} | {escaped} |")
        lines.append("")
        if fix_suggestions:
            lines.append("### Fix Suggestions (Errors)")
            lines.append("")
            for f in errors:
                if f.suggestion:
                    lines.append(f"- **{f.file}:{f.line}** — {f.suggestion}")
            lines.append("")
    else:
        lines.append("")
        lines.append("None.")
        lines.append("")

    # Warnings table
    lines.append("## Warnings")
    if warnings:
        lines.append("")
        lines.append("| File | Line | Rule | Text |")
        lines.append("|------|------|------|------|")
        for f in warnings:
            escaped = f.text.replace("|", "\\|")
            lines.append(f"| {f.file} | {f.line} | {f.rule} | {escaped} |")
        lines.append("")
        if fix_suggestions:
            lines.append("### Fix Suggestions (Warnings)")
            lines.append("")
            for f in warnings:
                if f.suggestion:
                    lines.append(f"- **{f.file}:{f.line}** — {f.suggestion}")
            lines.append("")
    else:
        lines.append("")
        lines.append("None.")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    recommendations = _generate_recommendations(errors, warnings, data_type)
    for rec in recommendations:
        lines.append(f"- {rec}")
    if not recommendations:
        lines.append("- All checks passed. Ready for publication review.")
    lines.append("")

    return "\n".join(lines)


def _generate_recommendations(
    errors: List[Finding],
    warnings: List[Finding],
    data_type: str,
) -> List[str]:
    """Auto-generate recommendations based on findings."""
    recs: List[str] = []
    all_findings = errors + warnings
    rules_hit = {f.rule.split(":")[0] for f in all_findings}

    if any("R4" in r for r in rules_hit):
        recs.append(
            'Replace all "proved"/"proven" with "demonstrated" or "showed". '
            "ML findings provide evidence; they do not constitute mathematical proof."
        )
    if any("R5" in r for r in rules_hit):
        recs.append(
            'Remove "breakthrough" from FINDINGS.md. '
            "Reserve this term for external validation, not self-description."
        )
    if any("R6" in r for r in rules_hit):
        recs.append(
            "Add synthetic-data qualifiers near all quantitative claims. "
            'Example: "On synthetic PaySim data, the model achieved 0.94 F1."'
        )
    if any("R1" in r for r in rules_hit):
        recs.append(
            "Tag novelty claims with [DEMONSTRATED] or soften to "
            '"proposed" / "alternative approach".'
        )
    if any("R9" in r for r in rules_hit):
        recs.append(
            "Add evidence-tier tags ([DEMONSTRATED], [SUGGESTED], [EXPLORATORY]) "
            "near all reported metrics."
        )
    if any("R7" in r or "R8" in r for r in rules_hit):
        recs.append(
            "Add statistical test references or confidence intervals "
            "alongside performance comparison claims."
        )
    if data_type == "unknown":
        recs.append(
            "Could not detect data type. Add data_type field to project.yaml "
            "or ensure FINDINGS.md mentions data provenance."
        )

    return recs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publication voice linter — scan for overclaiming language"
    )
    parser.add_argument(
        "--project-dir",
        required=True,
        help="Path to the project directory to scan",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (non-zero exit on any finding)",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Include suggested corrections for each finding",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for report (default: stdout)",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"Error: {project_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    # FINDINGS.md is required
    if not (project_dir / "FINDINGS.md").exists():
        print(f"Error: {project_dir / 'FINDINGS.md'} not found (required)", file=sys.stderr)
        sys.exit(2)

    # Detect data type
    data_type = detect_data_type(project_dir)

    # Scan all target files
    all_findings: List[Finding] = []
    files_scanned = 0

    for rel_path in TARGET_FILES:
        existed, findings = scan_file(project_dir, rel_path, data_type, args.fix_suggestions)
        if existed:
            files_scanned += 1
            all_findings.extend(findings)

    # Generate report
    report = generate_report(
        project_dir, all_findings, files_scanned,
        args.strict, args.fix_suggestions, data_type,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

    # Exit code
    error_count = sum(1 for f in all_findings if f.severity == "ERROR")
    if args.strict:
        error_count = len(all_findings)

    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
