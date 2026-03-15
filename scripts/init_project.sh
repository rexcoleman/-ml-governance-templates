#!/usr/bin/env bash
# init_project.sh — Copy governance templates to a new project
#
# Usage:
#   bash scripts/init_project.sh /path/to/project --profile <profile> [--fill]
#
# Profiles:
#   minimal          — 3 core contracts (Environment, Data, Metrics)
#   supervised       — 11 templates for classification/regression projects
#   optimization     — 11 templates for optimizer comparisons and ablation studies
#   unsupervised     — 23 templates for clustering and dimensionality reduction
#   rl-agent         — 24 templates for reinforcement learning projects
#   security-ml       — 21 templates: supervised + ADVERSARIAL_EVALUATION + TEST_ARCHITECTURE + publishing
#   blog-track        — 10 templates: lightweight governance for publication-track projects (ISS-035)
#   systems-benchmark — 12 templates for C/C++ systems projects with performance benchmarking
#   full             — All 32 templates + IEEE reference
#
# Templates are copied to <project>/docs/ with .tmpl.md renamed to .md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"

usage() {
    echo "Usage: bash $0 <project-dir> [--profile <profile>] [--generate] [--fill]"
    echo ""
    echo "Options:"
    echo "  --profile <profile>  Choose a template profile (default: supervised)"
    echo "  --generate           Copy project.yaml.example and run generators"
    echo "  --fill               Copy project.yaml, then bulk-replace common placeholders in all templates"
    echo ""
    echo "Profiles:"
    echo "  minimal          — 3 core contracts (Environment, Data, Metrics)"
    echo "  supervised       — 11 templates for classification/regression [default]"
    echo "  optimization     — 11 templates for optimizer comparisons, ablation studies"
    echo "  unsupervised     — 23 templates for clustering, dimensionality reduction"
    echo "  rl-agent         — 24 templates for reinforcement learning (full delivery)"
    echo "  security-ml       — 19 templates: supervised + adversarial eval + test architecture"
    echo "  systems-benchmark — 12 templates for C/C++ systems projects"
    echo "  full             — All 32 templates + IEEE reference"
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
FILL=false
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
        --fill)
            FILL=true
            shift
            ;;
        minimal|standard|supervised|optimization|unsupervised|rl-agent|security-ml|systems-benchmark|full)
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
VALID_PROFILES="minimal supervised optimization unsupervised rl-agent security-ml systems-benchmark blog-track full"
# Check for custom profile file first
CUSTOM_PROFILE_FILE="${SCRIPT_DIR}/profiles/${PROFILE}.txt"
if [[ -f "$CUSTOM_PROFILE_FILE" ]]; then
    USE_CUSTOM_PROFILE=true
elif ! echo "$VALID_PROFILES" | grep -qw "$PROFILE"; then
    echo "Error: Unknown profile '${PROFILE}'."
    echo "Available: ${VALID_PROFILES}"
    exit 1
else
    USE_CUSTOM_PROFILE=false
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

SECURITY_ML_FILES=(
    # Core — supervised baseline + adversarial + test architecture (11)
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/DATA_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    "${CORE}/HYPOTHESIS_CONTRACT.tmpl.md"
    "${CORE}/ADVERSARIAL_EVALUATION.tmpl.md"
    "${CORE}/TEST_ARCHITECTURE.tmpl.md"
    "${CORE}/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md"
    "${CORE}/ARTIFACT_MANIFEST_SPEC.tmpl.md"
    "${CORE}/CONFIGURATION_SPEC.tmpl.md"
    # Management (3)
    "${MGMT}/DECISION_LOG.tmpl.md"
    "${MGMT}/IMPLEMENTATION_PLAYBOOK.tmpl.md"
    "${MGMT}/RISK_REGISTER.tmpl.md"
    # Report (5)
    "${REPORT}/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${REPORT}/REPRODUCIBILITY_SPEC.tmpl.md"
    "${REPORT}/PRE_SUBMISSION_CHECKLIST.tmpl.md"
    "${REPORT}/REPORT_CONSISTENCY_SPEC.tmpl.md"
    "${REPORT}/RUBRIC_TRACEABILITY.tmpl.md"
    # Publishing (2)
    "${PUB}/PROJECT_BRIEF.tmpl.md"
    "${PUB}/PUBLICATION_PIPELINE.tmpl.md"
)

SYSTEMS_BENCHMARK_FILES=(
    # Core (8)
    "${CORE}/ENVIRONMENT_CONTRACT.tmpl.md"
    "${CORE}/BUILD_SYSTEM_CONTRACT.tmpl.md"
    "${CORE}/PERFORMANCE_BENCHMARKING_SPEC.tmpl.md"
    "${CORE}/CONCURRENCY_TESTING_SPEC.tmpl.md"
    "${CORE}/EXPERIMENT_CONTRACT.tmpl.md"
    "${CORE}/METRICS_CONTRACT.tmpl.md"
    "${CORE}/TEST_ARCHITECTURE.tmpl.md"
    "${CORE}/FIGURES_TABLES_CONTRACT.tmpl.md"
    # Management (1)
    "${MGMT}/DECISION_LOG.tmpl.md"
    # Report (3)
    "${REPORT}/REPORT_ASSEMBLY_PLAN.tmpl.md"
    "${REPORT}/REPORT_CONSISTENCY_SPEC.tmpl.md"
    "${REPORT}/RUBRIC_TRACEABILITY.tmpl.md"
)

FULL_FILES=(
    # Core (16)
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
    "${CORE}/BUILD_SYSTEM_CONTRACT.tmpl.md"
    "${CORE}/PERFORMANCE_BENCHMARKING_SPEC.tmpl.md"
    "${CORE}/CONCURRENCY_TESTING_SPEC.tmpl.md"
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
    # Publishing (5)
    "${PUB}/PUBLICATION_BRIEF.tmpl.md"
    "${PUB}/ACADEMIC_INTEGRITY_FIREWALL.tmpl.md"
    "${PUB}/LEAN_HYPOTHESIS.tmpl.md"
    "${PUB}/PROJECT_BRIEF.tmpl.md"
    "${PUB}/PUBLICATION_PIPELINE.tmpl.md"
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
    security-ml)
        echo "Copying security ML templates (21 files):"
        for f in "${SECURITY_ML_FILES[@]}"; do copy_template "$f"; done
        ;;
    systems-benchmark)
        echo "Copying systems benchmark templates (12 files):"
        for f in "${SYSTEMS_BENCHMARK_FILES[@]}"; do copy_template "$f"; done
        ;;
    full)
        echo "Copying full template suite (32 files + IEEE reference):"
        for f in "${FULL_FILES[@]}"; do copy_template "$f"; done
        if [[ -f "${REPORT}/IEEE_Report_Template.tex" ]]; then
            copy_raw "${REPORT}/IEEE_Report_Template.tex"
        fi
        ;;
    blog-track)
        echo "Copying blog-track templates (10 files):"
        # Read from profile file, skip comments and empty lines
        while IFS= read -r line; do
            line="$(echo "$line" | sed 's/#.*//' | xargs)"
            [[ -z "$line" ]] && continue
            template_path="${TEMPLATES_DIR}/${line}"
            if [[ -f "$template_path" ]]; then
                copy_template "$template_path"
            else
                echo "  WARNING: Template not found: ${line}"
            fi
        done < "${SCRIPT_DIR}/profiles/blog-track.txt"
        ;;
    *)
        # Try loading from custom profile file
        if [[ "$USE_CUSTOM_PROFILE" == "true" ]] && [[ -f "$CUSTOM_PROFILE_FILE" ]]; then
            echo "Copying custom profile '${PROFILE}' templates:"
            while IFS= read -r line; do
                line="$(echo "$line" | sed 's/#.*//' | xargs)"
                [[ -z "$line" ]] && continue
                template_path="${TEMPLATES_DIR}/${line}"
                if [[ -f "$template_path" ]]; then
                    copy_template "$template_path"
                else
                    echo "  WARNING: Template not found: ${line}"
                fi
            done < "$CUSTOM_PROFILE_FILE"
        else
            echo "Error: Unknown profile '${PROFILE}'."
            echo "Available: ${VALID_PROFILES}"
            exit 1
        fi
        ;;
esac

# --- Copy CLAUDE.md template if it exists ---
if [[ -f "${MGMT}/CLAUDE_MD.tmpl.md" ]]; then
    copy_template "${MGMT}/CLAUDE_MD.tmpl.md"
fi

# --- Scaffold repo hygiene files (ISS-048) ---
echo ""
echo "Scaffolding repo hygiene files:"

# .gitignore
if [[ ! -f "${PROJECT_DIR}/.gitignore" ]]; then
    cat > "${PROJECT_DIR}/.gitignore" << 'GITIGNORE'
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.pytest_cache/
.env
data/raw/
data/processed/
outputs/*.json
GITIGNORE
    echo "  + .gitignore"
fi

# LICENSE (MIT)
if [[ ! -f "${PROJECT_DIR}/LICENSE" ]]; then
    cat > "${PROJECT_DIR}/LICENSE" << 'LICENSE_TEXT'
MIT License

Copyright (c) 2026 Rex Coleman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
LICENSE_TEXT
    echo "  + LICENSE (MIT)"
fi

# tests/ directory
mkdir -p "${PROJECT_DIR}/tests"
if [[ ! -f "${PROJECT_DIR}/tests/__init__.py" ]]; then
    touch "${PROJECT_DIR}/tests/__init__.py"
    echo "  + tests/__init__.py"
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

# --- Bulk placeholder fill if --fill flag is set ---
if [[ "$FILL" == true ]]; then
    echo ""
    echo "--- Bulk Placeholder Fill ---"

    # Copy project.yaml if it doesn't exist
    if [[ ! -f "${PROJECT_DIR}/project.yaml" ]]; then
        # Use research example for security-ml and blog-track, academic example for others
        if [[ "$PROFILE" == "security-ml" || "$PROFILE" == "blog-track" ]] && [[ -f "${SCRIPT_DIR}/project.yaml.research-example" ]]; then
            cp "${SCRIPT_DIR}/project.yaml.research-example" "${PROJECT_DIR}/project.yaml"
            echo "  + project.yaml (from research example — edit before running generators)"
        else
            cp "${SCRIPT_DIR}/project.yaml.example" "${PROJECT_DIR}/project.yaml"
            echo "  + project.yaml (from example — edit before running generators)"
        fi
    fi

    # Read common values from project.yaml using grep/sed (no python dependency)
    YAML_FILE="${PROJECT_DIR}/project.yaml"
    if [[ -f "$YAML_FILE" ]]; then
        # Extract values (simple grep — works for flat YAML keys)
        PROJ_NAME=$(grep -m1 '^\s*name:' "$YAML_FILE" | sed 's/.*name:\s*"\?\([^"]*\)"\?.*/\1/' | xargs)
        PY_VERSION=$(grep -m1 '^\s*python_version:' "$YAML_FILE" | sed 's/.*python_version:\s*"\?\([^"]*\)"\?.*/\1/' | xargs)
        ENV_NAME=$(grep -m1 '^\s*conda_env:' "$YAML_FILE" | sed 's/.*conda_env:\s*"\?\([^"]*\)"\?.*/\1/' | xargs)
        TIER1=$(grep -m1 '^\s*tier1:' "$YAML_FILE" | sed 's/.*tier1:\s*"\?\([^"]*\)"\?.*/\1/' | xargs)
        TIER2=$(grep -m1 '^\s*tier2:' "$YAML_FILE" | sed 's/.*tier2:\s*"\?\([^"]*\)"\?.*/\1/' | xargs)
        TIER3=$(grep -m1 '^\s*tier3:' "$YAML_FILE" | sed 's/.*tier3:\s*"\?\([^"]*\)"\?.*/\1/' | xargs)

        # Default env file
        ENV_FILE="environment.yml"

        FILL_COUNT=0

        # Perform substitutions across all docs/*.md files
        for doc in "${DOCS_DIR}"/*.md; do
            [[ -f "$doc" ]] || continue
            changed=false

            if [[ -n "$PROJ_NAME" ]] && grep -q '{{PROJECT_NAME}}' "$doc" 2>/dev/null; then
                sed -i "s|{{PROJECT_NAME}}|${PROJ_NAME}|g" "$doc"
                changed=true
            fi
            if [[ -n "$PY_VERSION" ]] && grep -q '{{PYTHON_VERSION}}' "$doc" 2>/dev/null; then
                sed -i "s|{{PYTHON_VERSION}}|${PY_VERSION}|g" "$doc"
                changed=true
            fi
            if [[ -n "$ENV_NAME" ]] && grep -q '{{ENV_NAME}}' "$doc" 2>/dev/null; then
                sed -i "s|{{ENV_NAME}}|${ENV_NAME}|g" "$doc"
                changed=true
            fi
            if [[ -n "$ENV_FILE" ]] && grep -q '{{ENV_FILE}}' "$doc" 2>/dev/null; then
                sed -i "s|{{ENV_FILE}}|${ENV_FILE}|g" "$doc"
                changed=true
            fi
            if [[ -n "$TIER1" ]] && [[ "$TIER1" != "null" ]] && grep -q '{{TIER1_DOC}}' "$doc" 2>/dev/null; then
                sed -i "s|{{TIER1_DOC}}|${TIER1}|g" "$doc"
                changed=true
            fi
            if [[ -n "$TIER2" ]] && [[ "$TIER2" != "null" ]] && grep -q '{{TIER2_DOC}}' "$doc" 2>/dev/null; then
                sed -i "s|{{TIER2_DOC}}|${TIER2}|g" "$doc"
                changed=true
            fi
            if [[ -n "$TIER3" ]] && [[ "$TIER3" != "null" ]] && grep -q '{{TIER3_DOC}}' "$doc" 2>/dev/null; then
                sed -i "s|{{TIER3_DOC}}|${TIER3}|g" "$doc"
                changed=true
            fi
            # Default ENV_MANAGER to conda
            if grep -q '{{ENV_MANAGER}}' "$doc" 2>/dev/null; then
                sed -i "s|{{ENV_MANAGER}}|conda|g" "$doc"
                changed=true
            fi

            if [[ "$changed" == true ]]; then
                FILL_COUNT=$((FILL_COUNT + 1))
            fi
        done

        # Count remaining placeholders
        REMAINING=$(grep -roh '{{[A-Z_]*}}' "${DOCS_DIR}"/*.md 2>/dev/null | sort -u | wc -l)

        echo "  Filled placeholders in ${FILL_COUNT} files."
        echo "  ${REMAINING} unique content placeholders remain (fill these during project phases)."
    else
        echo "  WARNING: No project.yaml found. Skipping bulk fill."
    fi
fi

echo ""
echo "Done. Next steps:"
if [[ "$FILL" == true ]]; then
    echo "  1. Edit project.yaml with your specific experiment matrix and datasets"
    echo "  2. Fill PROJECT_BRIEF.md first (thesis, research questions, scope)"
    echo "  3. Fill PUBLICATION_PIPELINE.md (blog title, pillar, structure)"
    echo "  4. Fill remaining {{PLACEHOLDER}} values in docs/"
    echo "  5. Start with ENVIRONMENT_CONTRACT.md and DATA_CONTRACT.md"
    echo "  6. (Optional) Run generators: python scripts/generators/generate_all.py project.yaml"
else
    echo "  1. Open each file in docs/ and fill in {{PLACEHOLDER}} values"
    echo "  2. Start with ENVIRONMENT_CONTRACT.md and DATA_CONTRACT.md"
fi
if [[ "$GENERATE" == true ]]; then
    echo "  3. Edit project.yaml with your experiment matrix, phases, and artifacts"
    echo "  4. Re-run generators: python scripts/generators/generate_all.py project.yaml"
    echo "  5. Fill in {{PLACEHOLDER}} values in docs/CLAUDE_MD.md"
elif [[ "$FILL" != true ]]; then
    echo "  3. Use the Prompt Playbook for AI-assisted customization:"
    echo "     https://github.com/<your-org>/ml-governance-templates/blob/main/PROMPT_PLAYBOOK.md"
    echo "  4. (Optional) Add --fill flag for bulk placeholder substitution from project.yaml"
    echo "  5. (Optional) Add --generate flag to also set up project.yaml + generators"
fi
echo "  Delete the Customization Guide section from each file when done"
echo "  Commit: git add docs/ && git commit -m 'Initialize project governance'"
