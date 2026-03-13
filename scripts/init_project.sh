#!/usr/bin/env bash
# init_project.sh — Copy governance templates to a new project
#
# Usage:
#   bash scripts/init_project.sh /path/to/project --profile <profile>
#
# Profiles:
#   minimal       — 3 core contracts (Environment, Data, Metrics)
#   supervised    — 11 templates for classification/regression projects
#   optimization  — 11 templates for optimizer comparisons and ablation studies
#   unsupervised  — 23 templates for clustering and dimensionality reduction
#   rl-agent      — 24 templates for reinforcement learning projects
#   full          — All 29 templates + IEEE reference
#
# Templates are copied to <project>/docs/ with .tmpl.md renamed to .md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"

usage() {
    echo "Usage: bash $0 <project-dir> [--profile <profile>] [--generate]"
    echo ""
    echo "Options:"
    echo "  --profile <profile>  Choose a template profile (default: supervised)"
    echo "  --generate           Copy project.yaml.example and run generators"
    echo ""
    echo "Profiles:"
    echo "  minimal       — 3 core contracts (Environment, Data, Metrics)"
    echo "  supervised    — 11 templates for classification/regression [default]"
    echo "  optimization  — 11 templates for optimizer comparisons, ablation studies"
    echo "  unsupervised  — 23 templates for clustering, dimensionality reduction"
    echo "  rl-agent      — 24 templates for reinforcement learning (full delivery)"
    echo "  full          — All 29 templates + IEEE reference"
    echo ""
    echo "Legacy tiers (backward-compatible):"
    echo "  minimal       — same as minimal profile"
    echo "  standard      — maps to supervised profile"
    echo "  full          — same as full profile"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

PROJECT_DIR="$1"
shift

# Parse flags
PROFILE="supervised"
GENERATE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)
            if [[ $# -ge 2 ]]; then
                PROFILE="$2"
                shift 2
            else
                echo "Error: --profile requires a value"
                usage
            fi
            ;;
        --generate)
            GENERATE=true
            shift
            ;;
        minimal|standard|supervised|optimization|unsupervised|rl-agent|full)
            PROFILE="$1"
            shift
            ;;
        *)
            echo "Error: Unknown argument '$1'"
            usage
            ;;
    esac
done

# Map legacy tier names
case "$PROFILE" in
    standard) PROFILE="supervised" ;;
esac

# Validate profile
VALID_PROFILES="minimal supervised optimization unsupervised rl-agent full"
if ! echo "$VALID_PROFILES" | grep -qw "$PROFILE"; then
    echo "Error: Unknown profile '${PROFILE}'."
    echo "Available: ${VALID_PROFILES}"
    exit 1
fi

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

# --- Define file lists per profile ---

CORE="${TEMPLATES_DIR}/core"
MGMT="${TEMPLATES_DIR}/management"
REPORT="${TEMPLATES_DIR}/report"
PUB="${TEMPLATES_DIR}/publishing"

MINIMAL_FILES=(
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
)

SUPERVISED_FILES=(
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${CORE}/HYPOTHESIS_CONTRACT.tmpl.md"
    "${REPORT}/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${REPORT}/REPRODUCIBILITY_SPEC.tmpl.md"
    "${REPORT}/PRE_SUBMISSION_CHECKLIST.tmpl.md"
    "${REPORT}/REPORT_CONSISTENCY_SPEC.tmpl.md"
    "${REPORT}/RUBRIC_TRACEABILITY.tmpl.md"
)

OPTIMIZATION_FILES=(
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/CONFIGURATION_SPEC.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${CORE}/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${CORE}/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${CORE}/HYPOTHESIS_CONTRACT.tmpl.md"
    "${MGMT}/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${MGMT}/RISK_REGISTER.tmpl.md"
)

UNSUPERVISED_FILES=(
    # Core (13)
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${CORE}/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${CORE}/HYPOTHESIS_CONTRACT.tmpl.md"
    "${CORE}/AI_DIVISION_OF_LABOR.tmpl.md"
    "${CORE}/CONFIGURATION_SPEC.tmpl.md"
    "${CORE}/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${CORE}/TEST_ARCHITECTURE.tmpl.md"
    # Management (6)
    "${MGMT}/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${MGMT}/PRIOR_WORK_REUSE.tmpl.md"
    "${MGMT}/DECISION_LOG.tmpl.md"
    "${MGMT}/CHANGELOG.tmpl.md"
    "${MGMT}/RISK_REGISTER.tmpl.md"
    "${MGMT}/TASK_BOARD.tmpl.md"
    # Report (6)
    "${REPORT}/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${REPORT}/REPRODUCIBILITY_SPEC.tmpl.md"
    "${REPORT}/PRE_SUBMISSION_CHECKLIST.tmpl.md"
    "${REPORT}/EXECUTION_MANIFEST.tmpl.md"
    "${REPORT}/REPORT_CONSISTENCY_SPEC.tmpl.md"
    "${REPORT}/RUBRIC_TRACEABILITY.tmpl.md"
)

RL_AGENT_FILES=(
    # Core (11)
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/ENVIRONMENT_SPEC.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${CORE}/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${CORE}/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${CORE}/HYPOTHESIS_CONTRACT.tmpl.md"
    "${CORE}/AI_DIVISION_OF_LABOR.tmpl.md"
    "${CORE}/CONFIGURATION_SPEC.tmpl.md"
    "${CORE}/TEST_ARCHITECTURE.tmpl.md"
    # Management (5)
    "${MGMT}/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${MGMT}/RISK_REGISTER.tmpl.md"
    "${MGMT}/DECISION_LOG.tmpl.md"
    "${MGMT}/CHANGELOG.tmpl.md"
    "${MGMT}/PRIOR_WORK_REUSE.tmpl.md"
    # Report (6)
    "${REPORT}/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${REPORT}/REPRODUCIBILITY_SPEC.tmpl.md"
    "${REPORT}/PRE_SUBMISSION_CHECKLIST.tmpl.md"
    "${REPORT}/EXECUTION_MANIFEST.tmpl.md"
    "${REPORT}/REPORT_CONSISTENCY_SPEC.tmpl.md"
    "${REPORT}/RUBRIC_TRACEABILITY.tmpl.md"
    # Publishing (1)
    "${PUB}/ACADEMIC_INTEGRITY_FIREWALL.tmpl.md"
)

FULL_FILES=(
    # Core (13)
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${CORE}/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${CORE}/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${CORE}/HYPOTHESIS_CONTRACT.tmpl.md"
    "${CORE}/AI_DIVISION_OF_LABOR.tmpl.md"
    "${CORE}/CONFIGURATION_SPEC.tmpl.md"
    "${CORE}/TEST_ARCHITECTURE.tmpl.md"
    "${CORE}/ADVERSARIAL_EVALUATION.tmpl.md"
    "${CORE}/ENVIRONMENT_SPEC.tmpl.md"
    # Management (6)
    "${MGMT}/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${MGMT}/TASK_BOARD.tmpl.md"
    "${MGMT}/RISK_REGISTER.tmpl.md"
    "${MGMT}/DECISION_LOG.tmpl.md"
    "${MGMT}/CHANGELOG.tmpl.md"
    "${MGMT}/PRIOR_WORK_REUSE.tmpl.md"
    # Report (6)
    "${REPORT}/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${REPORT}/REPRODUCIBILITY_SPEC.tmpl.md"
    "${REPORT}/PRE_SUBMISSION_CHECKLIST.tmpl.md"
    "${REPORT}/EXECUTION_MANIFEST.tmpl.md"
    "${REPORT}/REPORT_CONSISTENCY_SPEC.tmpl.md"
    "${REPORT}/RUBRIC_TRACEABILITY.tmpl.md"
    # Publishing (3)
    "${PUB}/PUBLICATION_BRIEF.tmpl.md"
    "${PUB}/ACADEMIC_INTEGRITY_FIREWALL.tmpl.md"
    "${PUB}/LEAN_HYPOTHESIS.tmpl.md"
)

# --- Copy templates based on profile ---

echo "Initializing project governance in: ${PROJECT_DIR}"
echo "Profile: ${PROFILE}"
echo ""

case "$PROFILE" in
    minimal)
        echo "Copying minimal templates (3 files):"
        for f in "${MINIMAL_FILES[@]}"; do copy_template "$f"; done
        ;;
    supervised)
        echo "Copying supervised ML templates (11 files):"
        for f in "${SUPERVISED_FILES[@]}"; do copy_template "$f"; done
        ;;
    optimization)
        echo "Copying optimization benchmark templates (11 files):"
        for f in "${OPTIMIZATION_FILES[@]}"; do copy_template "$f"; done
        ;;
    unsupervised)
        echo "Copying unsupervised analysis templates (23 files):"
        for f in "${UNSUPERVISED_FILES[@]}"; do copy_template "$f"; done
        ;;
    rl-agent)
        echo "Copying RL / agent study templates (24 files):"
        for f in "${RL_AGENT_FILES[@]}"; do copy_template "$f"; done
        ;;
    full)
        echo "Copying full template suite (29 files + IEEE reference):"
        for f in "${FULL_FILES[@]}"; do copy_template "$f"; done
        if [[ -f "${REPORT}/IEEE_Report_Template.tex" ]]; then
            copy_raw "${REPORT}/IEEE_Report_Template.tex"
        fi
        ;;
    *)
        echo "Error: Unknown profile '${PROFILE}'."
        echo "Available: minimal, supervised, optimization, unsupervised, rl-agent, full"
        exit 1
        ;;
esac

# --- Copy CLAUDE.md template if it exists ---
if [[ -f "${MGMT}/CLAUDE_MD.tmpl.md" ]]; then
    copy_template "${MGMT}/CLAUDE_MD.tmpl.md"
fi

# --- Generate scaffolding if --generate flag is set ---
if [[ "$GENERATE" == true ]]; then
    echo ""
    echo "--- Scaffolding Generator ---"

    # Copy project.yaml.example if no project.yaml exists
    if [[ ! -f "${PROJECT_DIR}/project.yaml" ]]; then
        cp "${SCRIPT_DIR}/project.yaml.example" "${PROJECT_DIR}/project.yaml"
        echo "  + project.yaml (from example — edit before running generators)"
    fi

    GENERATORS_DIR="${SCRIPT_DIR}/scripts/generators"
    if [[ -f "${GENERATORS_DIR}/generate_all.py" ]]; then
        echo ""
        echo "Running generators..."
        python3 "${GENERATORS_DIR}/generate_all.py" "${PROJECT_DIR}/project.yaml" \
            --output-dir "${PROJECT_DIR}"
    else
        echo "  WARNING: Generators not found at ${GENERATORS_DIR}"
        echo "  Run generators manually after editing project.yaml:"
        echo "    python scripts/generators/generate_all.py project.yaml"
    fi
fi

echo ""
echo "Done. Next steps:"
echo "  1. Open each file in docs/ and fill in {{PLACEHOLDER}} values"
echo "  2. Start with ENVIRONMENT_CONTRACT.md and DATA_CONTRACT.md"
if [[ "$GENERATE" == true ]]; then
    echo "  3. Edit project.yaml with your experiment matrix, phases, and artifacts"
    echo "  4. Re-run generators: python scripts/generators/generate_all.py project.yaml"
    echo "  5. Fill in {{PLACEHOLDER}} values in docs/CLAUDE_MD.md"
else
    echo "  3. Use the Prompt Playbook for AI-assisted customization:"
    echo "     https://github.com/<your-org>/ml-governance-templates/blob/main/PROMPT_PLAYBOOK.md"
    echo "  4. (Optional) Add --generate flag to also set up project.yaml + generators"
fi
echo "  Delete the Customization Guide section from each file when done"
echo "  Commit: git add docs/ && git commit -m 'Initialize project governance'"
