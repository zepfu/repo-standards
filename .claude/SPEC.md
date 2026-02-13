# SPEC.md — Technical Specification

## Architecture Overview

repo-standards is a **meta-repository** — it does not run as a service. Instead, it distributes static assets (configs,
workflows, scripts) that consumer repositories pull in. The architecture has three layers:

```
┌─────────────────────────────────────────────────┐
│              Consumer Repositories               │
│  (call reusable workflows, sync config files)    │
└───────────────┬─────────────────┬───────────────┘
                │ workflow_call   │ sync-configs.sh
┌───────────────▼─────────────────▼───────────────┐
│             repo-standards (this repo)           │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────┐ │
│  │  Reusable     │  │  Config      │  │ Scripts│ │
│  │  Workflows    │  │  Templates   │  │        │ │
│  │  (.github/)   │  │  (root)      │  │        │ │
│  └──────────────┘  └──────────────┘  └────────┘ │
└───────────────┬─────────────────────────────────┘
                │ generates
┌───────────────▼─────────────────────────────────┐
│             Documentation                        │
│  GitHub Pages / ReadTheDocs (Sphinx)             │
└─────────────────────────────────────────────────┘
```

**Distribution model:**

- **Workflows** — Consumer repos reference them via `uses: zepfu/repo-standards/.github/workflows/<name>@main`
- **Config files** — Consumer repos pull them via `bash scripts/sync-configs.sh` (manual, explicit opt-in)
- **Pre-commit hooks** — Installed locally via `.pre-commit-config.yaml` (synced as a config file)
- **Documentation** — Sphinx-built HTML served via GitHub Pages and ReadTheDocs

## Tech Stack

| Layer                  | Technology                       | Notes                                          |
| ---------------------- | -------------------------------- | ---------------------------------------------- |
| Scripting              | Python 3.11+                     | Automation scripts (`scripts/*.py`)            |
| Shell                  | Bash                             | Utility scripts (`scripts/*.sh`), sync tooling |
| CI/CD                  | GitHub Actions                   | 10 reusable workflows in `.github/workflows/`  |
| Documentation          | Sphinx (RST)                     | `docs/` with guides and reference              |
| Diagrams               | Mermaid                          | Architecture diagrams, rendered via `mmdc`     |
| Python Formatting      | Black, isort                     | Enforced via pre-commit and CI                 |
| Python Linting         | Flake8, Bandit, mypy, pydocstyle | Enforced via pre-commit and CI                 |
| Shell Linting          | ShellCheck                       | Enforced via pre-commit and CI                 |
| YAML Linting           | yamllint                         | Enforced via pre-commit and CI                 |
| Markdown Formatting    | mdformat                         | Enforced via pre-commit                        |
| Docker Linting         | hadolint                         | Enforced via pre-commit and CI                 |
| Makefile Linting       | checkmake                        | Enforced via pre-commit and CI                 |
| GitHub Actions Linting | actionlint                       | Enforced via CI                                |

______________________________________________________________________

## Core Concepts

### Standards Distribution

The central concept — repo-standards is a single source of truth for quality configs. Consumer repos sync from here
rather than maintaining their own copies.

- **Rule:** All config changes happen here first, then propagate to consumers via `sync-configs.sh`
- **Rule:** Config files are opinionated defaults. Consumer repos can override locally, but overrides are their
  responsibility to maintain.
- **Invariant:** `sync-configs.sh` never silently overwrites consumer customizations — it creates `.bak` backups.

### Reusable Workflows

GitHub Actions workflows designed to be called from any repository via `workflow_call`.

- **Rule:** Each workflow is self-contained — it installs its own dependencies and doesn't assume consumer repo
  structure beyond standard conventions.
- **Rule:** All workflows support configurable inputs (Python version, paths, etc.) with sensible defaults.
- **Invariant:** Breaking changes to workflow inputs/outputs require a version bump and migration guide.

### Automation Scripts

Python and Bash scripts that generate documentation artifacts (changelog, repo map, architecture diagrams, workflow
registry).

- **Rule:** Scripts are designed to run in CI (headless) and locally (developer workstation).
- **Rule:** Output goes to `docs/auto/` — never overwrite hand-written documentation.
- **Invariant:** Scripts exit with meaningful error codes and follow MESSAGING_STANDARDS.md output conventions.

______________________________________________________________________

## Data Model

Not applicable — this project has no database or persistent data store. All state is in files (configs, docs,
workflows).

______________________________________________________________________

## API Design

Not applicable — this project exposes no API endpoints. The "interface" is:

1. **Reusable workflow inputs/outputs** — defined in each `.github/workflows/reusable-*.yml` file's `on.workflow_call`
   section.
1. **Config file schemas** — the format and options of each distributed config file (`.flake8`, `pyproject.toml`, etc.).
1. **Script CLI arguments** — the `argparse` interfaces of each Python script.

______________________________________________________________________

## Project Structure

```
repo-standards/
├── CLAUDE.md                         # Project coordinator instructions
├── TASKS.md                          # Operator task injection
├── PROJECT_LOG.md                    # Build log (append-only)
├── CLAUDE_SUGGESTIONS.md             # Spec improvement inbox
├── README.md                         # Public-facing overview
├── CODE_STANDARDS.md                 # Complete standards reference
├── MESSAGING_STANDARDS.md            # Output formatting conventions
├── Makefile                          # Development commands
├── repo.mk.example                   # Example repo-specific Makefile
│
├── .claude/                          # Project coordination framework
│   ├── SPEC.md                       # This file
│   ├── GUIDELINES.md                 # Development conventions
│   ├── PHASES.md                     # Build phases & status
│   ├── CONTRACTS.md                  # Cross-agent interface contracts
│   └── GITHUB_INTEGRATION.md         # GitHub sync rules
│
├── .github/workflows/                # Reusable CI workflows
│   ├── reusable-python-ci.yml
│   ├── reusable-shell-ci.yml
│   ├── reusable-pre-commit.yml
│   ├── reusable-config-validation.yml
│   ├── reusable-yaml-ci.yml
│   ├── reusable-docker-build.yml
│   ├── reusable-makefile-ci.yml
│   ├── reusable-quality-checks.yml
│   ├── reusable-update-architecture.yml
│   └── reusable-update-docs.yml
│
├── scripts/                          # Automation & utility scripts
│   ├── changelog.py                  # Generate changelog from git history
│   ├── repo_map.py                   # Generate repo structure docs
│   ├── generate_architecture.py      # Generate Mermaid architecture diagrams
│   ├── generate_workflow_registry.py # Workflow registry & tool coverage
│   ├── sync-configs.sh               # Sync configs to consumer repos
│   ├── render-mermaid.sh             # Render Mermaid diagrams
│   └── archive.sh                    # Create tar.gz for AI context
│
├── docs/                             # Sphinx documentation source
│   ├── conf.py                       # Sphinx config
│   ├── index.rst                     # Entry point
│   ├── requirements.txt              # Sphinx deps
│   ├── guides/                       # User guides (RST)
│   ├── reference/                    # Reference docs (RST)
│   ├── auto/                         # Auto-generated docs
│   │   ├── CHANGELOG.md
│   │   ├── REPO_MAP.md
│   │   ├── ARCHITECTURE_AUTO.md
│   │   ├── WORKFLOW_REGISTRY.md
│   │   └── diagrams/                 # Architecture diagrams (PNG)
│   ├── _build/                       # Built HTML output
│   ├── _static/                      # Static assets
│   └── _templates/                   # Sphinx templates
│
├── agent-logs/                       # Agent work logs
│   ├── _TEMPLATE.md
│   └── archive/
│
├── logs/                             # Rotated logs and archives
│
│ # Distributed config files (synced to consumer repos)
├── .editorconfig
├── .flake8
├── .gitattributes
├── .gitignore
├── .shellcheckrc
├── .pre-commit-config.yaml
├── .checkmake
├── .readthedocs.yml
└── pyproject.toml
```
