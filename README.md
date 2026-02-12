# repo-standards

[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://zepfu.github.io/repo-standards/)
[![ReadTheDocs](https://readthedocs.org/projects/repo-standards/badge/?version=latest)](https://repo-standards.readthedocs.io/en/latest/)

Organization-wide code quality standards and configuration templates.

______________________________________________________________________

## What This Provides

**Config files** synced to every repo: `.editorconfig`, `.gitattributes`, `.gitignore`, `.flake8`, `.shellcheckrc`,
`.pre-commit-config.yaml`, `pyproject.toml`, `.markdownlint.json`.

**Pre-commit hooks** covering Python (Black, isort, Flake8, Bandit, mypy, pydocstyle, autoflake, eradicate), shell
(ShellCheck), YAML (yamllint), Markdown (mdformat), Dockerfile (hadolint), GitHub Actions (actionlint), and Makefile
(checkmake).

**Reusable CI workflows** that run the same checks in GitHub Actions:

| Workflow                           | Purpose                                          |
| ---------------------------------- | ------------------------------------------------ |
| `reusable-python-ci.yml`           | Black, isort, Flake8, syntax validation          |
| `reusable-shell-ci.yml`            | ShellCheck, bash syntax validation               |
| `reusable-pre-commit.yml`          | All pre-commit hooks                             |
| `reusable-config-validation.yml`   | Required config files exist and are valid        |
| `reusable-yaml-ci.yml`             | YAML linting                                     |
| `reusable-docker-build.yml`        | Docker build test                                |
| `reusable-makefile-ci.yml`         | Makefile linting                                 |
| `reusable-quality-checks.yml`      | Security, types, docstyle, dead code, actionlint |
| `reusable-update-docs.yml`         | Auto-generate changelog, repo map, architecture  |
| `reusable-update-architecture.yml` | Architecture diagram generation                  |

**Automation scripts** for documentation generation: `changelog.py`, `repo_map.py`, `generate_architecture.py`,
`sync-configs.sh`.

______________________________________________________________________

## Quick Start

```bash
# 1. Sync config files
curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

# 2. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Add CI workflow
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
---
name: CI
on: [push, pull_request]
jobs:
  python:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  shell:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
EOF

# 4. Verify and commit
pre-commit run --all-files
git add . && git commit -m "feat: adopt repo standards"
```

______________________________________________________________________

## Updating

```bash
bash scripts/sync-configs.sh
pre-commit autoupdate
pre-commit run --all-files
git add . && git commit -m "chore: sync config files"
```

The sync script updates itself from the latest version in this repo.

______________________________________________________________________

## Documentation

Full documentation is available at **[zepfu.github.io/repo-standards](https://zepfu.github.io/repo-standards/)**.

Key pages:

- [Getting Started](https://zepfu.github.io/repo-standards/guides/getting-started.html) — first-time setup
- [Code Standards](CODE_STANDARDS.md) — all enforced rules and tool configurations
- [Messaging Standards](MESSAGING_STANDARDS.md) — output formatting conventions
- [Python Standards](https://zepfu.github.io/repo-standards/guides/python-standards.html) — Python-specific guidelines
- [Shell Standards](https://zepfu.github.io/repo-standards/guides/shell-standards.html) — shell scripting guidelines
- [Workflow Standards](https://zepfu.github.io/repo-standards/guides/workflow-standards.html) — GitHub Actions patterns

### Building Docs Locally

```bash
pip install -r docs/requirements.txt pyyaml
make docs        # generates auto-docs, builds Sphinx
make docs-serve  # serves at http://localhost:8000
```

______________________________________________________________________

## Repository Structure

```
repo-standards/
├── .github/workflows/       # CI and reusable workflows
├── docs/                    # Sphinx documentation source
│   ├── guides/              # User guides (rst)
│   ├── reference/           # Reference docs (rst)
│   └── auto/                # Auto-generated (changelog, repo map, architecture)
├── scripts/                 # Automation scripts
│   ├── changelog.py         # Generate changelog from git history
│   ├── repo_map.py          # Generate repository structure docs
│   ├── generate_architecture.py  # Generate Mermaid architecture diagrams
│   └── sync-configs.sh      # Sync config files to consumer repos
├── CODE_STANDARDS.md        # Complete standards reference
├── MESSAGING_STANDARDS.md   # Output formatting conventions
├── Makefile                 # Development commands
└── pyproject.toml           # Python tool configuration
```
