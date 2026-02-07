#!/usr/bin/env bash
# sync-configs.sh - Sync all config files from repo-standards/templates
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

log_info "Cloning repo-standards (templates and scripts only)..."

# Clone with sparse checkout
cd "$TEMP_DIR"
git clone \
  --depth 1 \
  --filter=blob:none \
  --sparse \
  --branch "$BRANCH" \
  "$REPO_URL" \
  repo-standards 2>&1 | grep -v "Cloning into" || true

cd repo-standards
git sparse-checkout set templates scripts 2>&1 | grep -v "^$" || true

log_info "Sparse checkout complete"
echo ""

# Return to original directory
cd "$OLDPWD"

# Copy config files from templates/
log_info "Copying config files..."
echo ""

SUCCESS_COUNT=0
SKIP_COUNT=0

for file in "$TEMP_DIR"/repo-standards/templates/*; do
    filename=$(basename "$file")
    
    # Skip subdirectories (like .github/)
    if [ -d "$file" ]; then
        log_warn "Skipping directory: $filename"
        ((SKIP_COUNT++))
        continue
    fi
    
    # Backup existing file
    if [ -f "$filename" ]; then
        cp "$filename" "${filename}.bak"
    fi
    
    # Copy file
    if cp "$file" "$filename"; then
        log_info "Synced: $filename"
        ((SUCCESS_COUNT++))
    else
        log_error "Failed to copy: $filename"
        # Restore backup if copy failed
        if [ -f "${filename}.bak" ]; then
            mv "${filename}.bak" "$filename"
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

# Sync the sync-configs.yml workflow if .github/workflows exists
if [ -d ".github/workflows" ]; then
    SYNC_WORKFLOW=".github/workflows/sync-configs.yml"
    LATEST_WORKFLOW="$TEMP_DIR/repo-standards/templates/.github/workflows/sync-configs.yml"
    
    if [ -f "$LATEST_WORKFLOW" ]; then
        if [ -f "$SYNC_WORKFLOW" ]; then
            if ! cmp -s "$SYNC_WORKFLOW" "$LATEST_WORKFLOW"; then
                log_info "Updating sync workflow..."
                cp "$SYNC_WORKFLOW" "${SYNC_WORKFLOW}.bak"
                if cp "$LATEST_WORKFLOW" "$SYNC_WORKFLOW"; then
                    log_info "Updated: $SYNC_WORKFLOW"
                    ((SUCCESS_COUNT++))
                fi
            fi
        else
            log_info "Installing sync workflow..."
            if cp "$LATEST_WORKFLOW" "$SYNC_WORKFLOW"; then
                log_info "Installed: $SYNC_WORKFLOW"
                ((SUCCESS_COUNT++))
            fi
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Sync complete!"
echo "  Synced:  $SUCCESS_COUNT files"
echo "  Skipped: $SKIP_COUNT directories"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test pre-commit: pre-commit run --all-files"
echo "  3. Commit changes: git add . && git commit -m 'chore: sync config files'"
