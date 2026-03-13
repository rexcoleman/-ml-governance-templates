#!/usr/bin/env python3
"""generate_all.py — Run all generators from a single project.yaml.

Usage:
    python scripts/generators/generate_all.py project.yaml [--output-dir <project-root>]

This is the single entry point for v3.0 scaffolding. It reads project.yaml
and runs each available generator to produce working scripts and tests.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

GENERATORS_DIR = Path(__file__).parent


def load_project(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_generator(script: str, project_yaml: str, extra_args: list[str] | None = None) -> int:
    """Run a single generator script."""
    cmd = [sys.executable, str(GENERATORS_DIR / script), project_yaml]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        print(f"  WARNING: {script} exited with code {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"  {result.stderr.strip()}", file=sys.stderr)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all generators from project.yaml")
    parser.add_argument("project_yaml", help="Path to project.yaml")
    parser.add_argument("--output-dir", default=".", help="Project root for output files")
    args = parser.parse_args()

    project_yaml = args.project_yaml
    output_dir = Path(args.output_dir)
    project = load_project(project_yaml)

    print("=" * 60)
    print("ml-governance-templates v3.0 — Scaffolding Generator")
    print("=" * 60)
    print(f"Project: {project.get('project', {}).get('name', 'Unknown')}")
    print(f"Profile: {project.get('project', {}).get('profile', 'Unknown')}")
    print(f"Output:  {output_dir.resolve()}")
    print()

    results = {}
    scripts_dir = output_dir / "scripts"

    # G1: Sweep script
    if project.get("experiments", {}).get("parts"):
        print("--- G1: Generating sweep.sh ---")
        results["sweep"] = run_generator(
            "gen_sweep.py", project_yaml,
            ["--output", str(scripts_dir / "sweep.sh")]
        )
    else:
        print("--- G1: Skipped (no experiment parts defined) ---")

    print()

    # G5: Manifest verifier
    if project.get("artifacts"):
        print("--- G5: Generating verify_manifests.py ---")
        results["manifest"] = run_generator(
            "gen_manifest_verifier.py", project_yaml,
            ["--output", str(scripts_dir / "verify_manifests.py")]
        )
    else:
        print("--- G5: Skipped (no artifacts config) ---")

    print()

    # G6: Phase gates
    if project.get("phases"):
        print("--- G6: Generating phase gate scripts ---")
        results["gates"] = run_generator(
            "gen_phase_gates.py", project_yaml,
            ["--output-dir", str(scripts_dir)]
        )
    else:
        print("--- G6: Skipped (no phases defined) ---")

    print()

    # G13: Report auditor
    if project.get("audit"):
        print("--- G13: Generating audit_report.py ---")
        results["audit_report"] = run_generator(
            "gen_report_auditor.py", project_yaml,
            ["--output", str(scripts_dir / "audit_report.py")]
        )
    else:
        print("--- G13: Skipped (no audit config) ---")

    print()

    # G14: Data-vs-report checker
    if project.get("audit"):
        print("--- G14: Generating check_data_report.py ---")
        results["data_report"] = run_generator(
            "gen_data_report_checker.py", project_yaml,
            ["--output", str(scripts_dir / "check_data_report.py")]
        )
    else:
        print("--- G14: Skipped (no audit config) ---")

    print()

    # G15: Rubric checker
    if project.get("authority"):
        print("--- G15: Generating check_rubric.py ---")
        results["rubric"] = run_generator(
            "gen_rubric_checker.py", project_yaml,
            ["--output", str(scripts_dir / "check_rubric.py")]
        )
    else:
        print("--- G15: Skipped (no authority config) ---")

    print()

    # G16: Integrity checker
    if project.get("ai_governance"):
        print("--- G16: Generating check_integrity.py ---")
        results["integrity"] = run_generator(
            "gen_integrity_checker.py", project_yaml,
            ["--output", str(scripts_dir / "check_integrity.py")]
        )
    else:
        print("--- G16: Skipped (no ai_governance config) ---")

    print()
    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results.values() if r == 0)
    print(f"Generators: {passed}/{total} succeeded")
    if passed < total:
        print("Check warnings above for details.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review generated scripts in scripts/")
    print("  2. Fill remaining {{PLACEHOLDER}} values in docs/")
    print("  3. Run: bash scripts/check_phase_0.sh")
    print("  4. After report draft: python scripts/audit_report.py --report-path <report>")
    print("  5. Commit: git add scripts/ && git commit -m 'Add generated scaffolding'")


if __name__ == "__main__":
    main()
