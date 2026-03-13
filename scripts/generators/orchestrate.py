#!/usr/bin/env python3
"""orchestrate.py — Claude Agent SDK orchestrator for ml-governance-templates.

Replaces generate_all.py's subprocess calls with agent-driven tool-use.
The agent reads project.yaml, decides which generators to run, validates
output, and checks phase gates — with human approval at key decision points.

This is the O4 (agent-assisted orchestration) implementation.

Usage:
    # Interactive mode — agent decides what to run
    python scripts/generators/orchestrate.py project.yaml

    # With output directory
    python scripts/generators/orchestrate.py project.yaml --output-dir .

    # Dry run — agent plans but doesn't execute
    python scripts/generators/orchestrate.py project.yaml --dry-run

    # Audit mode — generate audit scripts for a specific phase
    python scripts/generators/orchestrate.py project.yaml --audit full
    python scripts/generators/orchestrate.py project.yaml --audit 4

Requirements:
    pip install claude-agent-sdk pyyaml
"""
import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Generator tool functions
# ---------------------------------------------------------------------------
# These are the same generators from gen_sweep.py, gen_manifest_verifier.py,
# gen_phase_gates.py — but exposed as callable tool functions that the agent
# can invoke. The tool functions are portable: they'll be reused as LangGraph
# node tools in Sem 7 without modification.
# ---------------------------------------------------------------------------

GENERATORS_DIR = Path(__file__).parent


def load_project(path: str) -> dict:
    """Load and return project.yaml contents."""
    with open(path) as f:
        return yaml.safe_load(f)


def tool_run_sweep_generator(project_yaml: str, output_path: str) -> dict[str, Any]:
    """Run G1: sweep.sh generator.

    Reads the experiments section of project.yaml and generates a sweep.sh
    script with nested loops for methods × datasets × seeds.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_sweep.py"),
         project_yaml, "--output", output_path],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "file": output_path,
    }


def tool_run_manifest_generator(project_yaml: str, output_path: str) -> dict[str, Any]:
    """Run G5: verify_manifests.py generator.

    Reads the artifacts section of project.yaml and generates a verification
    script that checks SHA-256 integrity of all experiment outputs.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_manifest_verifier.py"),
         project_yaml, "--output", output_path],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "file": output_path,
    }


def tool_run_phase_gate_generator(project_yaml: str, output_dir: str) -> dict[str, Any]:
    """Run G6: phase gate scripts generator.

    Reads the phases section of project.yaml and generates check_phase_{N}.sh
    for each phase plus check_all_gates.sh master runner.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_phase_gates.py"),
         project_yaml, "--output-dir", output_dir],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "directory": output_dir,
    }


def tool_check_phase_gate(gate_script: str) -> dict[str, Any]:
    """Run a phase gate check script and report pass/fail."""
    if not Path(gate_script).exists():
        return {
            "success": False,
            "error": f"Gate script not found: {gate_script}",
        }
    result = subprocess.run(
        ["bash", gate_script],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
    }


def tool_validate_generated_file(file_path: str) -> dict[str, Any]:
    """Validate that a generated file exists and has content."""
    path = Path(file_path)
    if not path.exists():
        return {"valid": False, "error": f"File not found: {file_path}"}
    content = path.read_text()
    if not content.strip():
        return {"valid": False, "error": f"File is empty: {file_path}"}

    # Basic syntax checks
    checks = []
    if file_path.endswith(".sh"):
        checks.append(("has shebang", content.startswith("#!/")))
        checks.append(("has set -euo pipefail", "set -euo pipefail" in content))
    elif file_path.endswith(".py"):
        checks.append(("has shebang or docstring", content.startswith("#!") or content.startswith('"""') or content.startswith("'''")))

    return {
        "valid": all(ok for _, ok in checks) if checks else True,
        "file": file_path,
        "size_bytes": len(content),
        "line_count": content.count("\n") + 1,
        "checks": {name: ok for name, ok in checks},
    }


def tool_run_report_auditor(project_yaml: str, output_path: str) -> dict[str, Any]:
    """Run G13: report auditor generator.

    Reads the audit section of project.yaml and generates an audit_report.py
    script that checks Ten Simple Rules compliance, cross-refs, and build.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_report_auditor.py"),
         project_yaml, "--output", output_path],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "file": output_path,
    }


def tool_run_data_report_checker(project_yaml: str, output_path: str) -> dict[str, Any]:
    """Run G14: data-vs-report consistency checker generator.

    Generates a check_data_report.py script that cross-references numeric
    claims in the report against source data artifacts.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_data_report_checker.py"),
         project_yaml, "--output", output_path],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "file": output_path,
    }


def tool_run_rubric_checker(project_yaml: str, output_path: str) -> dict[str, Any]:
    """Run G15: rubric/FAQ compliance checker generator.

    Generates a check_rubric.py script that verifies all rubric items and
    FAQ questions are addressed in the report.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_rubric_checker.py"),
         project_yaml, "--output", output_path],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "file": output_path,
    }


def tool_run_integrity_checker(project_yaml: str, output_path: str) -> dict[str, Any]:
    """Run G16: academic integrity checker generator.

    Generates a check_integrity.py script that verifies AI Use Statement
    quality and academic integrity compliance.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATORS_DIR / "gen_integrity_checker.py"),
         project_yaml, "--output", output_path],
        capture_output=True, text=True,
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None,
        "file": output_path,
    }


# Phase-lens mapping for audit orchestration
PHASE_LENS_MAP = {
    0: ["report_auditor"],                                    # Template compliance
    1: [],                                                     # Data readiness (handled by phase gates)
    2: [],                                                     # Hypothesis lock (handled by phase gates)
    3: [],                                                     # Experiments (handled by phase gates)
    4: ["report_auditor", "data_report_checker", "rubric_checker"],  # Report draft
    5: ["integrity_checker", "report_auditor", "data_report_checker", "rubric_checker"],  # Submission
    "full": ["report_auditor", "data_report_checker", "rubric_checker", "integrity_checker"],
}


def tool_run_audit(project_yaml: str, output_dir: str, phase: str = "full") -> dict[str, Any]:
    """Run all audit generators appropriate for the given phase.

    Phase 4 (report): G13 + G14 + G15
    Phase 5 (submission): G13 + G14 + G15 + G16
    full: all audit generators
    """
    phase_key = int(phase) if phase.isdigit() else phase
    lenses = PHASE_LENS_MAP.get(phase_key, PHASE_LENS_MAP["full"])

    scripts_dir = str(Path(output_dir) / "scripts")
    results = {}

    generator_map = {
        "report_auditor": ("G13", tool_run_report_auditor, f"{scripts_dir}/audit_report.py"),
        "data_report_checker": ("G14", tool_run_data_report_checker, f"{scripts_dir}/check_data_report.py"),
        "rubric_checker": ("G15", tool_run_rubric_checker, f"{scripts_dir}/check_rubric.py"),
        "integrity_checker": ("G16", tool_run_integrity_checker, f"{scripts_dir}/check_integrity.py"),
    }

    for lens in lenses:
        if lens in generator_map:
            gid, fn, out_path = generator_map[lens]
            r = fn(project_yaml, out_path)
            results[lens] = {"generator": gid, **r}

    passed = sum(1 for r in results.values() if r.get("success"))
    return {
        "success": passed == len(results),
        "phase": str(phase_key),
        "lenses_run": len(results),
        "lenses_passed": passed,
        "results": results,
    }


def tool_read_project_yaml(project_yaml: str) -> dict[str, Any]:
    """Read and summarize project.yaml for the agent to reason about."""
    try:
        project = load_project(project_yaml)
    except Exception as e:
        return {"success": False, "error": str(e)}

    summary = {
        "project_name": project.get("project", {}).get("name", "Unknown"),
        "profile": project.get("project", {}).get("profile", "Unknown"),
        "has_experiments": bool(project.get("experiments", {}).get("parts")),
        "experiment_count": len(project.get("experiments", {}).get("parts", [])),
        "has_artifacts": bool(project.get("artifacts")),
        "has_phases": bool(project.get("phases")),
        "phase_count": len(project.get("phases", [])),
        "has_datasets": bool(project.get("datasets")),
        "has_config": bool(project.get("config")),
        "has_leakage_rules": bool(project.get("leakage", {}).get("rules")),
        "has_ai_governance": bool(project.get("ai_governance")),
    }
    return {"success": True, "summary": summary, "raw": project}


# ---------------------------------------------------------------------------
# Tool registry — maps tool names to functions + metadata
# ---------------------------------------------------------------------------
# This registry is the portable interface. Claude Agent SDK wraps these as
# agent tools; LangGraph (Sem 7) wraps them as node tool functions.
# The functions themselves never change.
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "read_project_yaml": {
        "function": tool_read_project_yaml,
        "description": "Read and summarize project.yaml to understand what generators are needed",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
        },
    },
    "run_sweep_generator": {
        "function": tool_run_sweep_generator,
        "description": "Generate sweep.sh experiment orchestration script from project.yaml experiments section",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_path": {"type": "string", "description": "Output path for sweep.sh"},
        },
    },
    "run_manifest_generator": {
        "function": tool_run_manifest_generator,
        "description": "Generate verify_manifests.py artifact integrity checker from project.yaml artifacts section",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_path": {"type": "string", "description": "Output path for verify_manifests.py"},
        },
    },
    "run_phase_gate_generator": {
        "function": tool_run_phase_gate_generator,
        "description": "Generate phase gate check scripts from project.yaml phases section",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_dir": {"type": "string", "description": "Output directory for gate scripts"},
        },
    },
    "check_phase_gate": {
        "function": tool_check_phase_gate,
        "description": "Run a phase gate check script and report pass/fail status",
        "parameters": {
            "gate_script": {"type": "string", "description": "Path to check_phase_N.sh script"},
        },
    },
    "validate_generated_file": {
        "function": tool_validate_generated_file,
        "description": "Validate that a generated file exists, has content, and passes basic syntax checks",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the generated file"},
        },
    },
    "run_report_auditor": {
        "function": tool_run_report_auditor,
        "description": "Generate audit_report.py — Ten Simple Rules compliance, cross-refs, terminology, build checks",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_path": {"type": "string", "description": "Output path for audit_report.py"},
        },
    },
    "run_data_report_checker": {
        "function": tool_run_data_report_checker,
        "description": "Generate check_data_report.py — numeric consistency between report claims and source artifacts",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_path": {"type": "string", "description": "Output path for check_data_report.py"},
        },
    },
    "run_rubric_checker": {
        "function": tool_run_rubric_checker,
        "description": "Generate check_rubric.py — rubric and FAQ coverage verification",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_path": {"type": "string", "description": "Output path for check_rubric.py"},
        },
    },
    "run_integrity_checker": {
        "function": tool_run_integrity_checker,
        "description": "Generate check_integrity.py — academic integrity and AI Use Statement compliance",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_path": {"type": "string", "description": "Output path for check_integrity.py"},
        },
    },
    "run_audit": {
        "function": tool_run_audit,
        "description": "Run all audit generators appropriate for a given phase (0-5 or 'full')",
        "parameters": {
            "project_yaml": {"type": "string", "description": "Path to project.yaml"},
            "output_dir": {"type": "string", "description": "Project root directory"},
            "phase": {"type": "string", "description": "Phase number (0-5) or 'full' for all lenses"},
        },
    },
}


# ---------------------------------------------------------------------------
# Standalone mode — runs without Agent SDK (fallback / CI)
# ---------------------------------------------------------------------------

def run_standalone(project_yaml: str, output_dir: str, dry_run: bool = False) -> None:
    """Run generators without the Agent SDK — deterministic, no LLM calls.

    This is the fallback for CI environments or when you don't want agent
    reasoning overhead. Equivalent to generate_all.py but using the tool
    registry for consistency.
    """
    print("=" * 60)
    print("ml-governance-templates — Standalone Generator (no agent)")
    print("=" * 60)

    # Step 1: Read project
    result = tool_read_project_yaml(project_yaml)
    if not result["success"]:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    summary = result["summary"]
    print(f"Project: {summary['project_name']}")
    print(f"Profile: {summary['profile']}")
    print()

    has_audit = bool(result["raw"].get("audit"))

    if dry_run:
        print("DRY RUN — would generate:")
        if summary["has_experiments"]:
            print(f"  - sweep.sh ({summary['experiment_count']} experiment parts)")
        if summary["has_artifacts"]:
            print("  - verify_manifests.py")
        if summary["has_phases"]:
            print(f"  - {summary['phase_count']} phase gate scripts + all-gates runner")
        if has_audit:
            print("  - audit_report.py (G13: Ten Simple Rules + cross-refs)")
            print("  - check_data_report.py (G14: data-vs-report consistency)")
            print("  - check_rubric.py (G15: rubric/FAQ coverage)")
            print("  - check_integrity.py (G16: academic integrity)")
        return

    scripts_dir = str(Path(output_dir) / "scripts")
    results = {}

    # Step 2: Run applicable generators
    if summary["has_experiments"]:
        print("--- G1: Generating sweep.sh ---")
        r = tool_run_sweep_generator(project_yaml, f"{scripts_dir}/sweep.sh")
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["sweep"] = r
    else:
        print("--- G1: Skipped (no experiment parts) ---")

    if summary["has_artifacts"]:
        print("--- G5: Generating verify_manifests.py ---")
        r = tool_run_manifest_generator(project_yaml, f"{scripts_dir}/verify_manifests.py")
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["manifest"] = r
    else:
        print("--- G5: Skipped (no artifacts config) ---")

    if summary["has_phases"]:
        print("--- G6: Generating phase gate scripts ---")
        r = tool_run_phase_gate_generator(project_yaml, scripts_dir)
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["gates"] = r
    else:
        print("--- G6: Skipped (no phases defined) ---")

    # Step 2b: Run audit generators if audit config present
    if has_audit:
        print("--- G13: Generating audit_report.py ---")
        r = tool_run_report_auditor(project_yaml, f"{scripts_dir}/audit_report.py")
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["audit_report"] = r

        print("--- G14: Generating check_data_report.py ---")
        r = tool_run_data_report_checker(project_yaml, f"{scripts_dir}/check_data_report.py")
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["data_report"] = r

        print("--- G15: Generating check_rubric.py ---")
        r = tool_run_rubric_checker(project_yaml, f"{scripts_dir}/check_rubric.py")
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["rubric"] = r

        print("--- G16: Generating check_integrity.py ---")
        r = tool_run_integrity_checker(project_yaml, f"{scripts_dir}/check_integrity.py")
        print(f"  {'OK' if r['success'] else 'FAIL'}: {r.get('output', r.get('error', ''))}")
        results["integrity"] = r
    else:
        print("--- G13-G16: Skipped (no audit config) ---")

    # Step 3: Validate
    print()
    print("--- Validating generated files ---")
    for name, r in results.items():
        if r["success"]:
            file_path = r.get("file") or r.get("directory")
            if file_path and Path(file_path).is_file():
                v = tool_validate_generated_file(file_path)
                status = "VALID" if v["valid"] else "INVALID"
                print(f"  [{status}] {file_path} ({v.get('line_count', '?')} lines)")

    # Summary
    print()
    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results.values() if r["success"])
    print(f"Generators: {passed}/{total} succeeded")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Agent mode — uses Claude Agent SDK for intelligent orchestration
# ---------------------------------------------------------------------------

async def run_agent_mode(project_yaml: str, output_dir: str) -> None:
    """Run generators via Claude Agent SDK — agent decides sequencing.

    The agent reads project.yaml, reasons about which generators are needed,
    runs them in appropriate order, validates output, and reports status.
    Human approves before proceeding to experiments.
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print("Claude Agent SDK not installed. Install with: pip install claude-agent-sdk")
        print("Falling back to standalone mode...")
        print()
        run_standalone(project_yaml, output_dir)
        return

    # Build tool definitions for the agent
    tools = []
    for name, spec in TOOL_REGISTRY.items():
        tools.append({
            "name": name,
            "description": spec["description"],
            "input_schema": {
                "type": "object",
                "properties": {
                    k: {"type": v["type"], "description": v["description"]}
                    for k, v in spec["parameters"].items()
                },
                "required": list(spec["parameters"].keys()),
            },
        })

    orchestration_prompt = f"""You are the ml-governance-templates orchestrator. Your job is to
set up a governed ML project by reading project.yaml and running the appropriate generators.

Project YAML path: {project_yaml}
Output directory: {output_dir}
Scripts directory: {output_dir}/scripts

Instructions:
1. First, read project.yaml using read_project_yaml to understand what's configured.
2. Based on what's present, run the appropriate generators:
   - If experiments.parts exists → run_sweep_generator
   - If artifacts exists → run_manifest_generator
   - If phases exists → run_phase_gate_generator
3. After each generator, validate the output using validate_generated_file.
4. If phase gates were generated, run check_phase_gate on phase 0 to verify setup.
5. Report a summary of what was generated, what passed validation, and what the
   human should do next (fill placeholders, edit project.yaml, etc.).

Be concise. Report results, not reasoning."""

    print("=" * 60)
    print("ml-governance-templates — Agent Orchestrator (Claude Agent SDK)")
    print("=" * 60)
    print()

    async for message in query(
        prompt=orchestration_prompt,
        options=ClaudeAgentOptions(
            tools=tools,
            max_turns=20,
        ),
    ):
        # Handle tool calls
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "name") and block.name in TOOL_REGISTRY:
                    # Execute the tool
                    tool_fn = TOOL_REGISTRY[block.name]["function"]
                    tool_input = block.input if hasattr(block, "input") else {}
                    result = tool_fn(**tool_input)
                    print(f"  [tool] {block.name} → {'OK' if result.get('success', result.get('valid', False)) else 'FAIL'}")
                elif hasattr(block, "text"):
                    print(block.text)

        # Final result
        if hasattr(message, "result"):
            print()
            print(message.result)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orchestrate ml-governance-templates generators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Default     Agent mode (Claude Agent SDK) — agent decides what to run
  --standalone  Deterministic mode — runs all applicable generators
  --dry-run     Show what would be generated without running generators
        """,
    )
    parser.add_argument("project_yaml", help="Path to project.yaml")
    parser.add_argument("--output-dir", default=".", help="Project root for output files")
    parser.add_argument("--standalone", action="store_true",
                        help="Run without Agent SDK (deterministic, no LLM calls)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without executing")
    parser.add_argument("--audit", metavar="PHASE",
                        help="Run audit generators only for given phase (0-5 or 'full')")
    args = parser.parse_args()

    if args.audit is not None:
        # Audit-only mode: generate and report
        print("=" * 60)
        print(f"ml-governance-templates — Audit Generator (phase: {args.audit})")
        print("=" * 60)
        result = tool_run_audit(args.project_yaml, args.output_dir, args.audit)
        print(f"\nLenses run: {result['lenses_run']}")
        print(f"Lenses passed: {result['lenses_passed']}")
        for name, r in result.get("results", {}).items():
            status = "OK" if r.get("success") else "FAIL"
            print(f"  [{status}] {r.get('generator', '?')}: {name} → {r.get('file', '?')}")
        sys.exit(0 if result["success"] else 1)
    elif args.dry_run or args.standalone:
        run_standalone(args.project_yaml, args.output_dir, dry_run=args.dry_run)
    else:
        asyncio.run(run_agent_mode(args.project_yaml, args.output_dir))


if __name__ == "__main__":
    main()
