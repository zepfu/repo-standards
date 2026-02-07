# repo-standards

[![Code Quality](https://github.com/zepfu/llama-gguf-inference/workflows/Code%20Quality/badge.svg)](https://github.com/zepfu/llama-gguf-inference/actions)

**Organization-wide code quality standards and configuration templates.**

This repository provides:
- **Reusable GitHub Actions workflows** - Python, Shell, Docker, Pre-commit standards
- **Configuration files** - `.gitattributes`, `.gitignore`, `.editorconfig`, etc. (in repo root)
- **Automated sync** - Keep all repos up to date with latest standards

---

## 🎯 Key Concept

**This repository IS the standard.**

All config files are in the **root** of this repo. Other repos sync directly from here.

```
repo-standards/              ← Other repos sync from here
├── .gitattributes          ← The standard
├── .gitignore              ← The standard
├── .editorconfig           ← The standard
├── .flake8                 ← The standard
├── .shellcheckrc           ← The standard
├── .pre-commit-config.yaml ← The standard
├── .markdownlint.json      ← The standard
├── pyproject.toml          ← The standard
├── .github/workflows/      ← Reusable workflows
└── scripts/
    └── sync-configs.sh     ← Downloads files from root
```

**No templates/ directory needed** - the repo itself is the template!

---

## Usage

### For New Repositories

**Quick setup:**
```bash
# Run sync script
curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

# Review and commit
git add .
git commit -m "chore: add repo standards"
```

### For Existing Repositories

```bash
# Sync config files
curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

# Add CI workflows that reference @main
# Create .github/workflows/ci.yml (see examples below)

# Commit
git add .
git commit -m "chore: adopt repo standards"
```

---

## Reusable Workflows

All projects should use these workflows via `@main`:

```yaml
# In your .github/workflows/ci.yml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
    with:
      python-version: '3.11'

  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

**Available workflows:**
- `reusable-python-ci.yml` - Python formatting, linting, syntax
- `reusable-shell-ci.yml` - ShellCheck, bash syntax
- `reusable-docker-build.yml` - Docker build testing
- `reusable-pre-commit.yml` - Pre-commit hook enforcement
- `reusable-config-validation.yml` - Config file validation

---

## Configuration Files

**What gets synced:**
- `.gitattributes` - Git line ending rules
- `.gitignore` - Python/IDE/OS ignore patterns
- `.editorconfig` - Editor consistency
- `.flake8` - Python linting config
- `.shellcheckrc` - Shell linting config
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.markdownlint.json` - Markdown linting
- `pyproject.toml` - Python project config


---

## Automated Sync

### Manual Sync

```bash
# Anytime you want to sync
bash scripts/sync-configs.sh
```

### Automated Sync (Optional)

Add this workflow to your repo:

```yaml
# .github/workflows/sync-configs.yml
name: Sync Config Files

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch: {}

permissions:
  contents: write
  pull-requests: write

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run sync script
        run: |
          curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: sync config files from repo-standards'
          title: 'Update config files from repo-standards'
          branch: sync-configs
          delete-branch: true
```

This creates weekly PRs to sync config files.

---

## Standards Enforced

**Python:**
- Version: 3.11+
- Formatter: Black (line-length 100)
- Import sorter: isort (Black-compatible)
- Linter: Flake8 (max-line 120, complexity 20)

**Shell:**
- Linter: ShellCheck (error-level)
- Style: Bash with proper quoting

**Git:**
- Line endings: LF (enforced via .gitattributes)
- Ignored: `__pycache__`, `.venv`, IDE files, OS files

**Editor:**
- Charset: UTF-8
- Line endings: LF
- Indentation: 4 spaces (Python), 2 spaces (YAML/Shell)

---

## Updating Standards

When you update standards in this repo:

1. Update config files in root (e.g., edit `.flake8`)
2. Commit and push to main
3. All repos using `@main` workflows get updates immediately
4. Config files sync via weekly PR (or manual trigger)
5. CI fails if repos don't meet new standards

This forces compliance across all repos.

---

## Example: Full CI Setup

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: ["main", "master"]
  pull_request:

jobs:
  # Validate configs match standards
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

  # Enforce Python standards
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
    with:
      python-version: '3.11'

  # Enforce Shell standards
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

  # Project-specific tests
  project-tests:
    runs-on: ubuntu-latest
    needs: [python-standards, shell-standards]
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/tests/run_tests.sh
```

---

## Local Development

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run checks
pre-commit run --all-files

# Sync latest configs
bash scripts/sync-configs.sh
```

---

## Why This Approach?

**✅ Single source of truth** - Config files in one place (repo root)
**✅ Self-validating** - repo-standards follows its own rules
**✅ Simple** - No templates/ directory, just sync from root
**✅ Transparent** - Anyone can see the actual configs in use
**✅ Versioned** - Git history shows how standards evolved

**Other repos simply mirror these files!**
