#!/usr/bin/env bash
# render-mermaid.sh - Extract and render Mermaid diagrams from markdown files
#
# Finds all mermaid code blocks in markdown files and generates images (SVG/PNG/PDF)
#
# Usage:
#   bash scripts/render-mermaid.sh [--format svg|png|pdf] [--output-dir DIR]
#
# Options:
#   --format      Output format: svg, png, or pdf (default: svg)
#   --output-dir  Output directory (default: auto-detected)
#   --help        Show this help message

set -uo pipefail  # Note: no -e, to handle mmdc failures gracefully

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $*"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $*"; }
log_error() { echo -e "${RED}✗${NC} $*"; }
log_step() { echo -e "${BLUE}▶${NC} $*"; }

# Default options
OUTPUT_FORMAT="svg"
OUTPUT_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --format)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --help|-h)
      cat << 'HELP'
render-mermaid.sh - Extract and render Mermaid diagrams from markdown files

Usage:
  bash render-mermaid.sh [--format svg|png|pdf] [--output-dir DIR]

Options:
  --format      Output format: svg, png, or pdf (default: svg)
  --output-dir  Output directory (default: auto-detected)
  --help        Show this help message

Auto-detects output directory:
  1. docs/diagrams/     (if docs/ exists)
  2. diagrams/          (fallback)
HELP
      exit 0
      ;;
    *)
      log_error "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Auto-detect output directory
if [ -z "$OUTPUT_DIR" ]; then
  if [ -d "docs" ]; then
    OUTPUT_DIR="docs/diagrams"
  else
    OUTPUT_DIR="diagrams"
  fi
fi

# Validate format
if [[ "$OUTPUT_FORMAT" != "svg" ]] && [[ "$OUTPUT_FORMAT" != "png" ]] && [[ "$OUTPUT_FORMAT" != "pdf" ]]; then
  log_error "Invalid format: $OUTPUT_FORMAT (must be svg, png, or pdf)"
  exit 1
fi

echo "=========================================="
echo "Mermaid Diagram Renderer"
echo "=========================================="
echo ""

# Check for markdown files
if ! find . -maxdepth 3 -name "*.md" -type f 2>/dev/null | grep -q .; then
  log_warn "No markdown files found"
  exit 0
fi

# Check mmdc
if ! command -v mmdc &> /dev/null; then
  log_error "mermaid-cli (mmdc) not found"
  echo ""
  echo "Install with:"
  echo "  npm install -g @mermaid-js/mermaid-cli"
  exit 1
fi

log_info "Running in local mode"
log_info "mermaid-cli found: $(mmdc --version 2>&1 | head -1)"
echo ""

mkdir -p "$OUTPUT_DIR"
log_info "Output directory: $OUTPUT_DIR"
log_info "Output format: $OUTPUT_FORMAT"
echo ""

# Find markdown files
log_step "Searching for markdown files..."
MARKDOWN_FILES=($(find . -name "*.md" -type f \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/venv/*" \
  -not -path "*/.venv/*" \
  -not -path "*/archive/*" \
  -not -path "*/_build/*" | sort))

if [ ${#MARKDOWN_FILES[@]} -eq 0 ]; then
  log_warn "No markdown files found"
  exit 0
fi

log_info "Found ${#MARKDOWN_FILES[@]} markdown files"
echo ""

# Extract and render
TOTAL_DIAGRAMS=0
RENDERED_COUNT=0
FAILED_COUNT=0

for md_file in "${MARKDOWN_FILES[@]}"; do
  DIAGRAM_COUNT=0
  IN_MERMAID=false
  CURRENT_DIAGRAM=""
  LINE_NUM=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    ((LINE_NUM++))

    # Check for mermaid block start
    if [[ "$line" =~ ^\`\`\`mermaid ]]; then
      IN_MERMAID=true
      CURRENT_DIAGRAM=""
      continue
    fi

    # Check for code block end
    if [[ "$line" =~ ^\`\`\`$ ]] && [ "$IN_MERMAID" = true ]; then
      IN_MERMAID=false
      ((DIAGRAM_COUNT++))
      ((TOTAL_DIAGRAMS++))

      FILE_BASE=$(basename "$md_file" .md)
      DIAGRAM_NAME="${FILE_BASE}_diagram_${DIAGRAM_COUNT}"
      TEMP_FILE="/tmp/${DIAGRAM_NAME}.mmd"
      OUTPUT_FILE="${OUTPUT_DIR}/${DIAGRAM_NAME}.${OUTPUT_FORMAT}"

      echo "$CURRENT_DIAGRAM" > "$TEMP_FILE"

      log_step "Rendering: ${FILE_BASE} (diagram ${DIAGRAM_COUNT})"

      if mmdc -i "$TEMP_FILE" -o "$OUTPUT_FILE" -b transparent 2>/dev/null; then
        log_info "Created: $OUTPUT_FILE"
        ((RENDERED_COUNT++))

        DIAGRAM_TYPE=$(echo "$CURRENT_DIAGRAM" | head -1 | awk '{print $1}')
        echo "         Type: $DIAGRAM_TYPE"
      else
        log_error "Failed to render diagram ${DIAGRAM_COUNT} in $md_file"
        ((FAILED_COUNT++))

        FIRST_LINE=$(echo "$CURRENT_DIAGRAM" | head -1)
        echo "         First line: $FIRST_LINE"
      fi

      rm -f "$TEMP_FILE"
      echo ""
      continue
    fi

    # Accumulate diagram content
    if [ "$IN_MERMAID" = true ]; then
      CURRENT_DIAGRAM="${CURRENT_DIAGRAM}${line}"$'\n'
    fi
  done < "$md_file"
done

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
log_info "Total diagrams found: $TOTAL_DIAGRAMS"
log_info "Successfully rendered: $RENDERED_COUNT"

if [ $FAILED_COUNT -gt 0 ]; then
  log_error "Failed to render: $FAILED_COUNT"
fi

echo ""
log_info "Output directory: $OUTPUT_DIR"
echo ""

# List files
if [ $RENDERED_COUNT -gt 0 ]; then
  echo "Generated files:"
  find "$OUTPUT_DIR" -name "*.${OUTPUT_FORMAT}" -type f | sort | while read -r file; do
    SIZE=$(du -h "$file" | cut -f1)
    echo "  • $(basename "$file") ($SIZE)"
  done
  echo ""
fi

# Create index
INDEX_FILE="${OUTPUT_DIR}/INDEX.md"
log_step "Creating index file: $INDEX_FILE"

cat > "$INDEX_FILE" << 'EOF'
# Mermaid Diagrams Index

Auto-generated from markdown files.

## Diagrams

EOF

find "$OUTPUT_DIR" -name "*.${OUTPUT_FORMAT}" -type f | sort | while read -r file; do
  BASENAME=$(basename "$file" .${OUTPUT_FORMAT})
  echo "### $BASENAME" >> "$INDEX_FILE"
  echo "" >> "$INDEX_FILE"
  echo "![${BASENAME}](./${BASENAME}.${OUTPUT_FORMAT})" >> "$INDEX_FILE"
  echo "" >> "$INDEX_FILE"
done

log_info "Created index: $INDEX_FILE"
echo ""

if [ $RENDERED_COUNT -gt 0 ]; then
  echo "✓ Success! View diagrams:"
  echo "  • Open: $INDEX_FILE"
  echo "  • Or browse: $OUTPUT_DIR"
else
  log_warn "No diagrams were rendered"
fi

exit 0
