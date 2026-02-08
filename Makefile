.PHONY: help docs docs-auto docs-build docs-serve docs-clean

help:
	@echo "repo-standards Makefile"
	@echo ""
	@echo "Documentation targets:"
	@echo "  docs-auto   - Generate auto-documentation (changelog, map, architecture)"
	@echo "  docs-build  - Build Sphinx documentation"
	@echo "  docs-serve  - Serve documentation locally (http://localhost:8000)"
	@echo "  docs-clean  - Clean documentation build artifacts"
	@echo "  docs        - Full build (auto + build)"

# Generate auto-documentation
docs-auto:
	@echo "Generating auto-documentation..."
	@mkdir -p docs/auto
	@python3 scripts/changelog.py --output docs/auto/CHANGELOG.md
	@python3 scripts/repo_map.py --output docs/auto/REPO_MAP.md
	@python3 scripts/generate_architecture.py --output docs/auto/ARCHITECTURE_AUTO.md --all-diagrams
	@echo "✓ Auto-documentation generated in docs/auto/"

# Build Sphinx documentation
docs-build: docs-auto
	@echo "Building Sphinx documentation..."
	@cd docs && sphinx-build -b html . _build/html
	@echo "✓ Documentation built at docs/_build/html/index.html"

# Serve documentation locally
docs-serve: docs-build
	@echo "Serving documentation at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	@cd docs/_build/html && python3 -m http.server 8000

# Clean documentation
docs-clean:
	@echo "Cleaning documentation..."
	@rm -rf docs/_build docs/auto/*
	@echo "✓ Documentation cleaned"

# Full build
docs: docs-build
