.DEFAULT_GOAL := help
.PHONY: help sphinx archive clean sync-configs mermaid mermaid-pnf mermaid-pdf docs
# Configuration
SHELL := /bin/bash
PYTHON := python3
REPO_STANDARDS_URL := https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts

##@ Help

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# Include optional repo-specific Makefile
# Users can create repo.mk to add custom targets with ## comments
-include repo.mk

##@ Documentation

sphinx: ## Build and serve Sphinx documentation locally
	@echo "Building Sphinx documentation..."
	@cd docs && sphinx-build -b html . _build/html
	@echo "✓ Documentation built at docs/_build/html/index.html"
	@echo ""
	@echo "Serving documentation at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	@cd docs/_build/html && python3 -m http.server 8000

docs: ## Auto generated documents
	@curl -fsSL $(REPO_STANDARDS_URL)/repo_map.py | $(PYTHON) - --output docs/auto/REPO_MAP.md
	@curl -fsSL $(REPO_STANDARDS_URL)/changelog.py | $(PYTHON) - --from-git --with-commits --output docs/auto/CHANGELOG.md
	@curl -fsSL $(REPO_STANDARDS_URL)/generate_architecture.py | $(PYTHON) - --output docs/auto/ARCHITECTURE_AUTO.md


mermaid: ## Render all Mermaid diagrams to SVG images
	@echo "Downloading render-mermaid.sh..."
	@curl -fsSL $(REPO_STANDARDS_URL)/render-mermaid.sh -o /tmp/render-mermaid.sh
	@chmod +x /tmp/render-mermaid.sh
	@bash /tmp/render-mermaid.sh --format svg
	@rm /tmp/render-mermaid.sh

mermaid-png: ## Render all Mermaid diagrams to PNG images
	@echo "Downloading render-mermaid.sh..."
	@curl -fsSL $(REPO_STANDARDS_URL)/render-mermaid.sh -o /tmp/render-mermaid.sh
	@chmod +x /tmp/render-mermaid.sh
	@bash /tmp/render-mermaid.sh --format png
	@rm /tmp/render-mermaid.sh

mermaid-pdf: ## Render all Mermaid diagrams to PDF files
	@echo "Downloading render-mermaid.sh..."
	@curl -fsSL $(REPO_STANDARDS_URL)/render-mermaid.sh -o /tmp/render-mermaid.sh
	@chmod +x /tmp/render-mermaid.sh
	@bash /tmp/render-mermaid.sh --format pdf
	@rm /tmp/render-mermaid.sh

mermaid-check: ## Validate Mermaid diagrams (check if mmdc is installed)
	@if command -v mmdc &> /dev/null; then \
		echo "✓ mermaid-cli is installed: $$(mmdc --version 2>&1 | head -1)"; \
	else \
		echo "✗ mermaid-cli (mmdc) not found"; \
		echo ""; \
		echo "Install with:"; \
		echo "  npm install -g @mermaid-js/mermaid-cli"; \
		echo ""; \
		echo "Or use npx without installing:"; \
		echo "  npx -p @mermaid-js/mermaid-cli mmdc --help"; \
		exit 1; \
	fi

##@ Maintenance

sync-configs:  ## Sync config files from repo-standards
	@echo "Creating repository archive..."
	@curl -fsSL $(REPO_STANDARDS_URL)/sync-configs.sh$(date +%s) | bash -s -- --yes

archive:  ## Create tar.gz archive for AI context
	@curl -fsSL $(REPO_STANDARDS_URL)/archive.sh | sh

clean: ## Remove backup files, logs, and Zone.Identifier files
	@echo "Cleaning repository..."
	@echo "Removing backup files..."
	@find . -name "*.bak" -type f -delete 2>/dev/null || true
	@find . -name "*.backup" -type f -delete 2>/dev/null || true
	@find . -name "*.old" -type f -delete 2>/dev/null || true
	@find . -name "*.orig" -type f -delete 2>/dev/null || true
	@find . -name "*~" -type f -delete 2>/dev/null || true
	@echo "Removing Zone.Identifier files..."
	@find . -name "*:Zone.Identifier" -type f -delete 2>/dev/null || true
	@echo "Removing tar.gz archives..."
	@find . -name "*.tar.gz" \
		-not -path "./archive/*" \
		-type f -delete 2>/dev/null || true
	@echo "Removing log files..."
	@find . -name "*.log" -type f -delete 2>/dev/null || true
	@find . -name "*.log.*" -type f -delete 2>/dev/null || true
	@echo "Removing compiled files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"
