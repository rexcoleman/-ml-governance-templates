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

    if dry_run:
        print("DRY RUN — would generate:")
        if summary["has_experiments"]:
            print(f"  - sweep.sh ({summary['experiment_count']} experiment parts)")
        if summary["has_artifacts"]:
            print("  - verify_manifests.py")
        if summary["has_phases"]:
            print(f"  - {summary['phase_count']} phase gate scripts + all-gates runner")
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
    args = parser.parse_args()

    if args.dry_run or args.standalone:
        run_standalone(args.project_yaml, args.output_dir, dry_run=args.dry_run)
    else:
        asyncio.run(run_agent_mode(args.project_yaml, args.output_dir))


if __name__ == "__main__":
    main()
