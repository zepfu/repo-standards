.DEFAULT_GOAL := help
.PHONY: help sphinx archive clean sync-configs
# Configuration
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
