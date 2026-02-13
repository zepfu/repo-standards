#!/usr/bin/env bash
# sync-configs.sh - Sync all config files from repo-standards (root directory)
# This script can update itself from the latest version in repo-standards
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash -s -- --yes

set -euo pipefail

REPO_URL="https://github.com/zepfu/repo-standards.git"
BRANCH="main"
SKIP_PROMPTS=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --yes|-y)
            SKIP_PROMPTS=true
            shift
            ;;
        --help|-h)
            echo "Usage: sync-configs.sh [options]"
            echo ""
            echo "Sync configuration files from repo-standards to current repository."
            echo ""
            echo "Options:"
            echo "  --yes, -y    Skip all confirmation prompts (for CI/automation)"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Files synced:"
            echo "  .gitattributes, .gitignore, .editorconfig, .flake8,"
            echo "  .shellcheckrc, .pre-commit-config.yaml, .readthedocs.yml,"
            echo "  pyproject.toml, Makefile, repo.mk.example, .checkmake,"
            echo "  .checkmake-mk, REUSABLE_WORKFLOW_REGISTRY.md"
            echo ""
            echo "Example:"
            echo "  curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash"
            echo "  curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash -s -- --yes"
            exit 0
            ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $*"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $*"; }
log_error() { echo -e "${RED}✗${NC} $*"; }

echo "=========================================="
echo "Syncing config files from repo-standards"
echo "=========================================="
echo ""

# Safety check: Are we in a git repository?
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository!"
    echo ""
    echo "This script must be run from the root of a git repository."
    echo "Current directory: $(pwd)"
    echo ""
    echo "Usage:"
    echo "  cd /path/to/your/project"
    echo "  curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash"
    exit 1
fi

# Safety check: Are we at the repository root?
GIT_ROOT=$(git rev-parse --show-toplevel)
CURRENT_DIR=$(pwd)

if [ "$GIT_ROOT" != "$CURRENT_DIR" ]; then
    log_warn "Not at repository root!"
    echo ""
    echo "Current directory: $CURRENT_DIR"
    echo "Repository root:   $GIT_ROOT"
    echo ""

    if [ "$SKIP_PROMPTS" = true ]; then
        cd "$GIT_ROOT"
        log_info "Changed to repository root: $GIT_ROOT"
    else
        read -p "Change to repository root and continue? (y/N) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd "$GIT_ROOT"
            log_info "Changed to repository root: $GIT_ROOT"
        else
            log_error "Aborted by user"
            exit 1
        fi
    fi
fi

# Safety check: Confirm before overwriting files
if [ -f ".pre-commit-config.yaml" ] || [ -f "pyproject.toml" ]; then
    if [ "$SKIP_PROMPTS" = false ]; then
        log_warn "Existing config files will be overwritten (backups will be created)"
        echo ""
        read -p "Continue? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Aborted by user"
            exit 1
        fi
    fi
fi

echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

log_info "Cloning repo-standards (root configs and scripts only)..."

# Clone with sparse checkout - just root config files and scripts
cd "$TEMP_DIR"
git clone \
  --depth 1 \
  --filter=blob:none \
  --sparse \
  --branch "$BRANCH" \
  "$REPO_URL" \
  repo-standards 2>&1 | grep -v "Cloning into" || true

cd repo-standards

# Set sparse-checkout to get root config files and scripts directory
git sparse-checkout set \
  .gitattributes \
  .gitignore \
  .editorconfig \
  .flake8 \
  .shellcheckrc \
  .pre-commit-config.yaml \
  .readthedocs.yml \
  pyproject.toml \
  Makefile \
  repo.mk.example \
  .checkmake \
  .checkmake-mk \
  .markdownlint.json \
  docs/auto/WORKFLOW_REGISTRY.md \
  2>&1 | grep -v "^$" || true

log_info "Sparse checkout complete"
echo ""

# Return to original directory (the git repository root)
cd "$GIT_ROOT"

# Copy config files from root of repo-standards
log_info "Copying config files..."
echo ""

SUCCESS_COUNT=0

# Config files to sync (from root of repo-standards)
CONFIG_FILES=(
  ".gitattributes"
  ".gitignore"
  ".editorconfig"
  ".flake8"
  ".shellcheckrc"
  ".pre-commit-config.yaml"
  ".readthedocs.yml"
  ".markdownlint.json"
  "pyproject.toml"
  "Makefile"
  "repo.mk.example"
  ".checkmake"
  ".checkmake-mk"
)

for file in "${CONFIG_FILES[@]}"; do
    SOURCE="$TEMP_DIR/repo-standards/$file"

    if [ ! -f "$SOURCE" ]; then
        log_warn "File not found in repo-standards: $file"
        continue
    fi

    # Backup existing file
    if [ -f "$file" ]; then
        cp "$file" "${file}.bak"
    fi

    # Copy file
    if cp "$SOURCE" "$file"; then
        log_info "Synced: $file"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        log_error "Failed to copy: $file"
        # Restore backup if copy failed
        if [ -f "${file}.bak" ]; then
            mv "${file}.bak" "$file"
        fi
    fi
done

echo ""

# Copy WORKFLOW_REGISTRY.md (reference copy from repo-standards)
REGISTRY_SOURCE="$TEMP_DIR/repo-standards/docs/auto/WORKFLOW_REGISTRY.md"
REGISTRY_DEST="REUSABLE_WORKFLOW_REGISTRY.md"

if [ -f "$REGISTRY_SOURCE" ]; then
    if [ -f "$REGISTRY_DEST" ]; then
        cp "$REGISTRY_DEST" "${REGISTRY_DEST}.bak"
    fi

    if cp "$REGISTRY_SOURCE" "$REGISTRY_DEST"; then
        log_info "Synced: $REGISTRY_DEST (from docs/auto/WORKFLOW_REGISTRY.md)"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        log_error "Failed to copy: $REGISTRY_DEST"
        if [ -f "${REGISTRY_DEST}.bak" ]; then
            mv "${REGISTRY_DEST}.bak" "$REGISTRY_DEST"
        fi
    fi
else
    log_warn "WORKFLOW_REGISTRY.md not found in repo-standards"
fi

echo ""
echo "=========================================="
echo "Sync complete!"
echo "  Synced:  $SUCCESS_COUNT files"
echo "=========================================="
echo ""
echo "Files synced:"
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
    fi
done
if [ -f "$REGISTRY_DEST" ]; then
    echo "  ✓ $REGISTRY_DEST"
else
    echo "  ✗ $REGISTRY_DEST (missing)"
fi
echo ""

# Exit successfully
exit 0
