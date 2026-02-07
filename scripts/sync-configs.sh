#!/usr/bin/env bash
# sync-configs.sh - Sync all config files from repo-standards (root directory)
# This script can update itself from the latest version in repo-standards

set -euo pipefail

REPO_URL="https://github.com/zepfu/repo-standards.git"
BRANCH="main"

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
  .markdownlint.json \
  pyproject.toml \
  scripts \
  2>&1 | grep -v "^$" || true

log_info "Sparse checkout complete"
echo ""

# Return to original directory
cd "$OLDPWD"

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
  ".markdownlint.json"
  "pyproject.toml"
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
        ((SUCCESS_COUNT++))
    else
        log_error "Failed to copy: $file"
        # Restore backup if copy failed
        if [ -f "${file}.bak" ]; then
            mv "${file}.bak" "$file"
        fi
    fi
done

echo ""

# Self-update: Copy the latest version of this script
SCRIPT_PATH="scripts/sync-configs.sh"
log_info "Checking for script updates..."

if [ -f "$SCRIPT_PATH" ]; then
    LATEST_SCRIPT="$TEMP_DIR/repo-standards/scripts/sync-configs.sh"

    if [ -f "$LATEST_SCRIPT" ]; then
        # Check if script has changed
        if ! cmp -s "$SCRIPT_PATH" "$LATEST_SCRIPT"; then
            log_warn "Script has updates available"

            # Backup current script
            cp "$SCRIPT_PATH" "${SCRIPT_PATH}.bak"

            # Copy latest version
            if cp "$LATEST_SCRIPT" "$SCRIPT_PATH"; then
                chmod +x "$SCRIPT_PATH"
                log_info "Updated: $SCRIPT_PATH"
                ((SUCCESS_COUNT++))
            else
                log_error "Failed to update script"
                mv "${SCRIPT_PATH}.bak" "$SCRIPT_PATH"
            fi
        else
            log_info "Script is up to date"
        fi
    fi
elif [ ! -d "scripts" ]; then
    # First time setup - create scripts directory
    log_info "Creating scripts/ directory..."
    mkdir -p scripts

    LATEST_SCRIPT="$TEMP_DIR/repo-standards/scripts/sync-configs.sh"
    if cp "$LATEST_SCRIPT" "$SCRIPT_PATH"; then
        chmod +x "$SCRIPT_PATH"
        log_info "Installed: $SCRIPT_PATH"
        ((SUCCESS_COUNT++))
    fi
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
echo ""
echo "Note: .gitmodules is NOT synced (each repo manages its own submodules)"
echo "Note: .env.example is NOT synced (each repo documents its own environment)"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test pre-commit: pre-commit run --all-files"
echo "  3. Commit changes: git add . && git commit -m 'chore: sync config files'"
