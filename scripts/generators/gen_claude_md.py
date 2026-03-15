#!/usr/bin/env python
"""G17: Generate CLAUDE_MD.md from project.yaml.

CLAUDE_MD is the highest-leverage single template (WIN-002). This generator
auto-fills it from project.yaml so every Claude Code session starts context-aware.

Usage:
    python scripts/generators/gen_claude_md.py project.yaml --output-dir docs/

ISS-026 resolution: CLAUDE_MD.md still had raw placeholders after --fill.
"""

import argparse
import sys
from pathlib import Path

import yaml


def generate_claude_md(config: dict, output_dir: str = "docs") -> str:
    """Generate a filled CLAUDE_MD.md from project.yaml."""
    project = config.get("project", {})
    authority = config.get("authority", {})
    publication = config.get("publication", {})
    skill_clusters = config.get("skill_clusters", {})
    experiments = config.get("experiments", {})
    phases = config.get("phases", [])
    ai_gov = config.get("ai_governance", {})
    infra = config.get("infrastructure", {})

    name = project.get("name", "{{PROJECT_NAME}}")
    profile = project.get("profile", "{{PROFILE}}")
    python_ver = project.get("python_version", "3.11")
    conda_env = project.get("conda_env", "{{ENV_NAME}}")

    # Build phase table
    phase_rows = []
    for i, phase in enumerate(phases):
        status = "**CURRENT**" if i == 0 else "Not started"
        phase_rows.append(f"| {i} | {phase.get('name', f'Phase {i}')} | {status} |")
    phase_table = "\n".join(phase_rows) if phase_rows else "| 0 | Phase 0 | **CURRENT** |"

    # Build experiment parts summary
    parts_summary = []
    for part in experiments.get("parts", []):
        methods = ", ".join(part.get("methods", []))
        parts_summary.append(f"- **{part.get('name', '?')}:** {methods}")
    parts_text = "\n".join(parts_summary) if parts_summary else "*(fill from project.yaml)*"

    # Build AI division of labor
    ai_tools = []
    for tool in ai_gov.get("tools", []):
        permitted = tool.get("role", "General assistance")
        prohibited = tool.get("prohibited", "None specified")
        ai_tools.append(f"- **{tool.get('name', 'AI Tool')}:** {permitted}\n  - Prohibited: {prohibited}")
    ai_text = "\n".join(ai_tools) if ai_tools else "*(fill from project.yaml)*"

    # Build output
    content = f"""# {name} — Claude Code Context

> **govML v2.5** | Profile: {profile} (blog-track)

## Project Purpose

{publication.get('title', name)}

- **Context:** Self-directed research ({name})
- **Profile:** {profile}
- **Python:** {python_ver} | **Env:** {conda_env}
- **Brand pillar:** {publication.get('pillar', '{{CONTENT_PILLAR}}')}
- **Workload type:** {infra.get('workload_type', '{{WORKLOAD_TYPE}}')}

## Authority Hierarchy

| Tier | Source | Path |
|------|--------|------|
| 1 (highest) | Project Brief | `{authority.get('tier1', 'docs/PROJECT_BRIEF.md')}` |
| 2 | {authority.get('tier2') or '—'} | {authority.get('tier2') or 'No external FAQ'} |
| 3 | Advisory methodology | `{authority.get('tier3', 'docs/ADVERSARIAL_EVALUATION.md')}` |
| Contracts | Governance docs | `docs/*.md` |

## Current Phase

**Phase:** 0 — Environment & Setup

### Phase Progression

| Phase | Name | Status |
|-------|------|--------|
{phase_table}

## Experiment Summary

Seeds: {experiments.get('seeds', [42, 123, 456])}

{parts_text}

## Key Files

| File | Purpose |
|------|---------|
| `docs/PROJECT_BRIEF.md` | **READ FIRST** — thesis, RQs, scope |
| `docs/PUBLICATION_PIPELINE.md` | Blog post governance + distribution |
| `docs/DECISION_LOG.md` | All tradeoff decisions (mandatory at every phase gate) |
| `config/base.yaml` | Experiment configuration |

## AI Division of Labor

### Permitted
{ai_text}

### Prohibited (all projects)
- Modifying PROJECT_BRIEF thesis or research questions
- Writing interpretation/analysis prose (human insight)

## Conventions

- **Seeds:** {experiments.get('seeds', [42, 123, 456])}
- **Smoke test first:** `--sample-frac 0.01` or `--dry-run` before full runs
- **Decisions:** Log in DECISION_LOG at every phase gate (mandatory per v2.5)
- **Commit early:** Phase 0a scaffold → commit → Phase 0b research → commit
"""

    output_path = Path(output_dir) / "CLAUDE_MD.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="G17: Generate CLAUDE_MD.md from project.yaml")
    parser.add_argument("config", help="Path to project.yaml")
    parser.add_argument("--output-dir", default="docs", help="Output directory")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    path = generate_claude_md(config, args.output_dir)
    print(f"Generated: {path}")
    print(f"  Project: {config.get('project', {}).get('name', '?')}")
    print(f"  Profile: {config.get('project', {}).get('profile', '?')}")
    print(f"  Phases: {len(config.get('phases', []))}")


if __name__ == "__main__":
    main()
