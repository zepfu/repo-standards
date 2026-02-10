#!/bin/bash

# When piped from curl, detect repo root as current directory
REPO_ROOT="$(pwd)"
REPO_NAME="$(basename "$REPO_ROOT")"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Archive directory
ARCHIVE_DIR="${REPO_ROOT}/archive"

# Output file
OUTPUT_FILE="${ARCHIVE_DIR}/${REPO_NAME}_${TIMESTAMP}.tar.gz"

echo "Cleaning up Zone.Identifier and backup files..."
# Clean Zone.Identifier files
find "$REPO_ROOT" -name "*:Zone.Identifier" -type f -delete 2>/dev/null
# Clean backup files
find "$REPO_ROOT" -name "*.bak" -type f -delete 2>/dev/null
find "$REPO_ROOT" -name "*.backup" -type f -delete 2>/dev/null
find "$REPO_ROOT" -name "*~" -type f -delete 2>/dev/null

echo "? Cleanup complete"
echo ""

# Create archive directory if it doesn't exist
if [ ! -d "$ARCHIVE_DIR" ]; then
  echo "Creating archive directory: $ARCHIVE_DIR"
  mkdir -p "$ARCHIVE_DIR"
fi

echo "Creating archive: $OUTPUT_FILE"
echo "From directory: $REPO_ROOT"

# Create tar.gz excluding unnecessary files
cd "$REPO_ROOT" || exit 1

tar -czf "$OUTPUT_FILE" \
  --exclude="*.pyc" \
  --exclude="__pycache__" \
  --exclude="*.egg-info" \
  --exclude=".pytest_cache" \
  --exclude="venv" \
  --exclude=".venv" \
  --exclude=".git" \
  --exclude="dist" \
  --exclude="build" \
  --exclude=".vscode" \
  --exclude=".idea" \
  --exclude="*.swp" \
  --exclude="*~" \
  --exclude="*.bak" \
  --exclude="*.backup" \
  --exclude="*:Zone.Identifier" \
  --exclude="docs/_build" \
  --exclude=".DS_Store" \
  --exclude="archive" \
  .

if [ $? -eq 0 ]; then
  echo ""
  echo "? Archive created successfully: $OUTPUT_FILE"
  # Show size
  ls -lh "$OUTPUT_FILE" | awk '{print "  Size:", $5}'
else
  echo "? Error creating archive"
  exit 1
fi
