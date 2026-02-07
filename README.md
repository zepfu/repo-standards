# repo-standards

**Organization-wide code quality standards and configuration templates.**

This repository provides:
- **Reusable GitHub Actions workflows** - Python, Shell, Docker, Pre-commit standards
- **Configuration templates** - `.gitattributes`, `.gitignore`, `.editorconfig`, etc.
- **Automated sync** - Keep all repos up to date with latest standards

## Usage

### For New Repositories

**Option 1: Use as Template (Recommended)**
1. Click "Use this template" on GitHub
2. All config files and workflows are copied automatically
3. Push and CI enforces standards

**Option 2: Manual Setup**
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
# See: templates/.github/workflows/ for examples

# Commit
git add .
git commit -m "chore: adopt repo standards"
```

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

## Configuration Files

Templates in `templates/`:
- `.gitattributes` - Git line ending rules
- `.gitignore` - Python/IDE/OS ignore patterns
- `.editorconfig` - Editor consistency
- `.flake8` - Python linting config
- `.shellcheckrc` - Shell linting config
- `.pre-commit-config.yaml` - Pre-commit hooks
- `pyproject.toml` - Python project config

## Automated Sync

Enable automatic updates in your repo:

```bash
# Copy the sync workflow
curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/templates/.github/workflows/sync-configs.yml \
  -o .github/workflows/sync-configs.yml

# Commit
git add .github/workflows/sync-configs.yml
git commit -m "chore: enable automated config sync"
```

**This workflow:**
- Runs weekly on Sunday
- Downloads latest configs from repo-standards
- Creates PR with updates
- Updates itself automatically

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

## Updating Standards

When you update standards in this repo:
1. All repos using `@main` workflows get updates immediately
2. Config files sync via weekly PR (or manual trigger)
3. CI fails if repos don't meet new standards

This forces compliance across all repos.

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

## See Also

- [CODE_STYLE.md](CODE_STYLE.md) - Detailed code standards
- [CONFIGURATION.md](CONFIGURATION.md) - Config file documentation
