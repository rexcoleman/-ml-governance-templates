#!/usr/bin/env bash
# init_project.sh — Copy governance templates to a new project
#
# Usage:
#   bash ml-governance-templates/scripts/init_project.sh /path/to/project [tier]
#
# Tiers:
#   minimal  — Core contracts only (3 files: Environment, Data, Metrics)
#   standard — Core + key management + report (11 files, recommended)
#   full     — All 15 templates
#
# Templates are copied to <project>/docs/ with .tmpl.md renamed to .md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"

if [[ $# -lt 1 ]]; then
    echo "Usage: bash $0 <project-dir> [minimal|standard|full]"
    echo ""
    echo "Tiers:"
    echo "  minimal  — 3 core contracts (Environment, Data, Metrics)"
    echo "  standard — 11 templates (core + playbook + risk + report) [default]"
    echo "  full     — All 15 templates"
    exit 1
fi

PROJECT_DIR="$1"
TIER="${2:-standard}"

if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "Error: Project directory does not exist: $PROJECT_DIR"
    exit 1
fi

DOCS_DIR="${PROJECT_DIR}/docs"
mkdir -p "$DOCS_DIR"

copy_template() {
    local src="$1"
    local basename
    basename="$(basename "$src" .tmpl.md).md"
    cp "$src" "${DOCS_DIR}/${basename}"
    echo "  + docs/${basename}"
}

copy_raw() {
    local src="$1"
    local basename
    basename="$(basename "$src")"
    cp "$src" "${DOCS_DIR}/${basename}"
    echo "  + docs/${basename}"
}

echo "Initializing project governance in: ${PROJECT_DIR}"
echo "Tier: ${TIER}"
echo ""

# --- Minimal: 3 core contracts ---
MINIMAL_FILES=(
    "${TEMPLATES_DIR}/core/ENVIRONMENT_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/DATA_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/METRICS_CONTRACT.tmpl.md"
)

# --- Standard: 11 files ---
STANDARD_FILES=(
    "${TEMPLATES_DIR}/core/ENVIRONMENT_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/DATA_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/EXPERIMENT_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/METRICS_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${TEMPLATES_DIR}/core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${TEMPLATES_DIR}/management/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${TEMPLATES_DIR}/management/RISK_REGISTER.tmpl.md"
    "${TEMPLATES_DIR}/report/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${TEMPLATES_DIR}/report/PRE_SUBMISSION_CHECKLIST.tmpl.md"
)

# --- Full: all 15 templates ---
FULL_FILES=(
    "${TEMPLATES_DIR}/core/ENVIRONMENT_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/DATA_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/EXPERIMENT_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/METRICS_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${TEMPLATES_DIR}/core/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${TEMPLATES_DIR}/core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${TEMPLATES_DIR}/management/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${TEMPLATES_DIR}/management/TASK_BOARD.tmpl.md"
    "${TEMPLATES_DIR}/management/RISK_REGISTER.tmpl.md"
    "${TEMPLATES_DIR}/management/DECISION_LOG.tmpl.md"
    "${TEMPLATES_DIR}/management/CHANGELOG.tmpl.md"
    "${TEMPLATES_DIR}/management/PRIOR_WORK_REUSE.tmpl.md"
    "${TEMPLATES_DIR}/report/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${TEMPLATES_DIR}/report/PRE_SUBMISSION_CHECKLIST.tmpl.md"
)

case "$TIER" in
    minimal)
        echo "Copying minimal templates (3 files):"
        for f in "${MINIMAL_FILES[@]}"; do copy_template "$f"; done
        ;;
    standard)
        echo "Copying standard templates (11 files):"
        for f in "${STANDARD_FILES[@]}"; do copy_template "$f"; done
        ;;
    full)
        echo "Copying full template suite (15 files):"
        for f in "${FULL_FILES[@]}"; do copy_template "$f"; done
        # Also copy IEEE template
        if [[ -f "${TEMPLATES_DIR}/report/IEEE_Report_Template.tex" ]]; then
            copy_raw "${TEMPLATES_DIR}/report/IEEE_Report_Template.tex"
        fi
        ;;
    *)
        echo "Error: Unknown tier '${TIER}'. Use: minimal, standard, or full"
        exit 1
        ;;
esac

echo ""
echo "Done. Next steps:"
echo "  1. Open each file in docs/ and fill in {{PLACEHOLDER}} values"
echo "  2. Start with ENVIRONMENT_CONTRACT.md and DATA_CONTRACT.md"
echo "  3. Delete the Customization Guide section from each file when done"
echo "  4. Commit: git add docs/ && git commit -m 'Initialize project governance'"
