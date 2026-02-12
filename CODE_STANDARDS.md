# Code Standards

Enforced standards for all repositories using repo-standards. This document is the single source of truth for what is
checked, how it is configured, and where each rule is enforced.

______________________________________________________________________

## Quick Reference

| Language / Area | Formatter    | Linter               | Additional                        |
| --------------- | ------------ | -------------------- | --------------------------------- |
| Python          | Black, isort | Flake8, Bandit, mypy | pydocstyle, autoflake, eradicate  |
| Shell           | —            | ShellCheck           | bash -n syntax check              |
| YAML            | —            | yamllint             | actionlint (for workflows)        |
| Markdown        | mdformat     | —                    | —                                 |
| Dockerfile      | —            | hadolint             | —                                 |
| Makefile        | —            | checkmake            | —                                 |
| General         | EditorConfig | pre-commit-hooks     | detect-private-key, case-conflict |

______________________________________________________________________

## Python

**Required version:** 3.11+

### Formatting (auto-fixed)

**Black** formats all `.py` files on commit.

| Setting        | Value | Config                          |
| -------------- | ----- | ------------------------------- |
| Line length    | 100   | `pyproject.toml` `[tool.black]` |
| Target version | py311 | `pyproject.toml` `[tool.black]` |

**isort** sorts imports on commit.

| Setting     | Value | Config                          |
| ----------- | ----- | ------------------------------- |
| Profile     | black | `pyproject.toml` `[tool.isort]` |
| Line length | 100   | `pyproject.toml` `[tool.isort]` |

Import order: standard library, third-party, local. Blank line between each group.

### Linting (blocks commit)

**Flake8** enforces style rules.

| Setting          | Value               | Config                          |
| ---------------- | ------------------- | ------------------------------- |
| Max line length  | 120                 | `.flake8`                       |
| Max complexity   | 20                  | `.flake8`                       |
| Ignored rules    | E203, W503          | `.flake8` (Black compatibility) |
| Per-file ignores | `__init__.py: F401` | `.flake8`                       |

Note: Black formats to 100 chars, Flake8 allows up to 120. This gives breathing room for cases where Black cannot break
a line (long strings, URLs).

**Autoflake** removes unused imports and variables on commit.

- Removes all unused imports
- Removes unused variables
- Removes duplicate dict keys
- Preserves `__init__.py` imports

**Eradicate** removes commented-out code on commit.

### Docstrings (blocks commit)

**pydocstyle** enforces Google-style docstrings.

| Setting             | Value        | Config                               |
| ------------------- | ------------ | ------------------------------------ |
| Convention          | Google       | `pyproject.toml` `[tool.pydocstyle]` |
| Missing docstrings  | Not required | D100-D107 ignored                    |
| Conflict resolution | D212 ignored | Google uses D213                     |
| Punctuation         | Not enforced | D415 ignored                         |

Docstrings are not mandatory, but when present they must follow Google format:

```python
def process_data(input_path: str, output_path: str) -> bool:
    """Process data from input file and write to output.

    Reads the input file line by line, applies transformations,
    and writes results to the output path.

    Args:
        input_path: Path to the source data file.
        output_path: Path where processed data will be written.

    Returns:
        True if processing succeeded, False otherwise.

    Raises:
        FileNotFoundError: If input_path does not exist.
    """
```

Key rules:

- Summary on the line after the opening `"""`, not on the same line
- Blank line between summary and description
- `Args:`, `Returns:`, `Raises:` sections use Google format (indented descriptions)
- One blank line before closing `"""` for multi-line docstrings

### Security (blocks commit and CI)

**Bandit** scans for common security issues.

| Setting       | Value                                 | Config           |
| ------------- | ------------------------------------- | ---------------- |
| Config file   | `pyproject.toml`                      | `[tool.bandit]`  |
| Excluded dirs | tests, .venv, venv, build, dist       | `pyproject.toml` |
| Skipped rules | B101 (assert), B404/B603 (subprocess) | `pyproject.toml` |

Subprocess rules are skipped because automation scripts legitimately shell out. Use `# nosec B110` inline comments for
intentional exceptions (e.g., bare except in non-critical code paths).

### Type Checking (warns in CI, blocks commit)

**mypy** checks type annotations.

| Setting             | Value                           | Config                         |
| ------------------- | ------------------------------- | ------------------------------ |
| Python version      | 3.11                            | `pyproject.toml` `[tool.mypy]` |
| Missing imports     | Ignored                         | `--ignore-missing-imports`     |
| Warn on Any returns | Yes                             | `pyproject.toml`               |
| Excluded dirs       | build, dist, .venv, venv, tests | `pyproject.toml`               |

All function signatures should use type hints. Use `Dict[str, Any]` for loosely-typed dicts rather than bare `Dict` or
`dict`. The `typing` module provides `Any`, `Dict`, `List`, `Optional`, `Set`, `Tuple` for annotations targeting Python
3.11.

### Dead Code Detection (advisory in CI)

**Vulture** detects unused code with 80% confidence threshold. **PyLint** checks for unreachable code and pointless
statements.

These are advisory — they warn but do not block merges.

______________________________________________________________________

## Shell

### Shebang and Safety

All shell scripts must:

- Use `#!/usr/bin/env bash` shebang
- Set `set -euo pipefail`
- Be executable (`chmod +x`)

Pre-commit enforces `check-executables-have-shebangs` and `check-shebang-scripts-are-executable` automatically.

### Linting (blocks commit and CI)

**ShellCheck** enforces shell best practices.

| Setting          | Value                | Config                                     |
| ---------------- | -------------------- | ------------------------------------------ |
| Severity         | error                | Pre-commit and CI                          |
| Follow sources   | Yes                  | `-x` flag                                  |
| Shell dialect    | bash                 | `.shellcheckrc`                            |
| Disabled rules   | SC2250               | `.shellcheckrc` (`${var}` vs `$var` style) |
| Optional checks  | quote-safe-variables | `.shellcheckrc`                            |
| External sources | Allowed              | `.shellcheckrc`                            |

### Syntax Validation (blocks CI)

`bash -n` runs against all `.sh` files in `scripts/` to catch syntax errors before they reach production.

### Style Guidelines

- Always quote variables: `"$variable"`, not `$variable`
- Use `[[ ]]` for conditionals, not `[ ]`
- Use `$()` for command substitution, not backticks
- Declare local variables in functions: `local my_var="value"`
- Use `readonly` for constants

______________________________________________________________________

## YAML

### Linting (blocks commit)

**yamllint** enforces YAML formatting.

| Setting         | Value   | Config                    |
| --------------- | ------- | ------------------------- |
| Base config     | relaxed | Inline in pre-commit args |
| Max line length | 150     | Inline in pre-commit args |

### GitHub Actions Workflows (blocks commit and CI)

**actionlint** validates workflow files.

Catches:

- Invalid `${{ }}` expressions
- Unknown action inputs
- Bad `needs` references
- Deprecated runner versions
- Type mismatches in workflow inputs/outputs

______________________________________________________________________

## Markdown

### Formatting (auto-fixed)

**mdformat** formats all `.md` files on commit.

| Setting             | Value     | Config                        |
| ------------------- | --------- | ----------------------------- |
| Wrap                | 120 chars | Pre-commit args               |
| GFM support         | Yes       | `mdformat-gfm` plugin         |
| Table formatting    | Yes       | `mdformat-tables` plugin      |
| Frontmatter support | Yes       | `mdformat-frontmatter` plugin |

### CI Enforcement

The `markdown-lint` job in `reusable-quality-checks.yml` runs `mdformat --check` and fails the build on unformatted
files.

______________________________________________________________________

## Dockerfile

### Linting (blocks commit)

**hadolint** lints Dockerfiles against best practices.

Installed via `AleksaC/hadolint-py` (no Docker dependency required). Uses default hadolint rules. Add a `.hadolint.yaml`
to customize if needed.

______________________________________________________________________

## Makefile

### Linting (blocks commit)

**checkmake** validates Makefile structure.

| Setting         | Value    | Config       |
| --------------- | -------- | ------------ |
| Max body length | 15 lines | `.checkmake` |
| Min phony       | Enabled  | `.checkmake` |

Required targets: `all` and `test` must exist (minphony rule). Recipe bodies should stay under 15 lines — extract to
scripts if longer.

______________________________________________________________________

## General File Checks

These run on every commit via `pre-commit-hooks`:

| Check                     | What it does                                               |
| ------------------------- | ---------------------------------------------------------- |
| `trailing-whitespace`     | Strips trailing spaces (preserves markdown line breaks)    |
| `end-of-file-fixer`       | Ensures files end with a newline                           |
| `check-yaml`              | Validates YAML syntax                                      |
| `check-toml`              | Validates TOML syntax                                      |
| `check-json`              | Validates JSON syntax                                      |
| `check-added-large-files` | Blocks files over 1MB                                      |
| `check-merge-conflict`    | Catches unresolved merge markers                           |
| `check-symlinks`          | Validates symlink targets exist                            |
| `destroyed-symlinks`      | Catches symlinks broken by git                             |
| `check-case-conflict`     | Catches files that collide on case-insensitive filesystems |
| `fix-byte-order-marker`   | Strips BOM from files                                      |
| `detect-private-key`      | Catches accidentally committed SSH/PGP keys                |
| `mixed-line-ending`       | Forces LF line endings                                     |

______________________________________________________________________

## Line Endings

Enforced at two levels:

1. **`.gitattributes`** — normalizes on checkout/commit. LF enforced for all source code, scripts, config files,
   documentation, and Docker files. Binary files are excluded from normalization.

1. **`mixed-line-ending`** pre-commit hook — auto-fixes to LF on commit.

______________________________________________________________________

## Editor Configuration

**`.editorconfig`** ensures consistent settings across editors:

| File type              | Indent                                                     | Size |
| ---------------------- | ---------------------------------------------------------- | ---- |
| Python (`.py`)         | spaces                                                     | 4    |
| YAML (`.yml`, `.yaml`) | spaces                                                     | 2    |
| Shell (`.sh`)          | spaces                                                     | 2    |
| Makefile               | tabs                                                       | —    |
| All files              | UTF-8, LF endings, final newline, trim trailing whitespace | —    |

______________________________________________________________________

## Enforcement Layers

Standards are enforced at three levels. A rule must pass all applicable layers.

### Layer 1: Pre-commit (local, on every commit)

Runs automatically when `pre-commit install` has been executed. Auto-fixes where possible (Black, isort, autoflake,
eradicate, mdformat, mixed-line-ending). Blocks commit on lint failures (Flake8, ShellCheck, Bandit, mypy, pydocstyle,
yamllint, hadolint, actionlint, checkmake).

### Layer 2: CI Workflows (remote, on every push/PR)

Reusable workflows run the same checks in GitHub Actions:

| Workflow                         | What it checks                                                     |
| -------------------------------- | ------------------------------------------------------------------ |
| `reusable-python-ci.yml`         | Black, isort, Flake8, syntax validation                            |
| `reusable-shell-ci.yml`          | ShellCheck, bash syntax validation                                 |
| `reusable-pre-commit.yml`        | Runs all pre-commit hooks                                          |
| `reusable-config-validation.yml` | Required config files exist and are valid                          |
| `reusable-yaml-ci.yml`           | YAML linting                                                       |
| `reusable-docker-build.yml`      | Docker build test                                                  |
| `reusable-makefile-ci.yml`       | Makefile linting                                                   |
| `reusable-quality-checks.yml`    | Bandit, mypy, pydocstyle, actionlint, mdformat, Vulture, dead code |

### Layer 3: Config Files (passive, always present)

`.editorconfig`, `.gitattributes`, `.flake8`, `.shellcheckrc`, `pyproject.toml`, and `.checkmake` apply rules passively
through editor integration and tool defaults.

______________________________________________________________________

## Adopting These Standards

### New Repository

```bash
# Sync all config files
curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

# Install pre-commit
pip install pre-commit
pre-commit install

# Add CI workflow
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
---
name: CI
on: [push, pull_request]
jobs:
  standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  python:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  shell:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
EOF

# Verify
pre-commit run --all-files
git add . && git commit -m "feat: adopt repo standards"
```

### Updating Standards

```bash
bash scripts/sync-configs.sh
pre-commit autoupdate
pre-commit run --all-files
git add . && git commit -m "chore: sync config files"
```

______________________________________________________________________

## Suppressing Rules

When a rule must be bypassed, always use inline suppression with a comment explaining why. Never disable rules globally
unless the rationale applies project-wide.

| Tool       | Inline suppression             |
| ---------- | ------------------------------ |
| Flake8     | `# noqa: E501`                 |
| Bandit     | `# nosec B110`                 |
| mypy       | `# type: ignore[attr-defined]` |
| ShellCheck | `# shellcheck disable=SC2086`  |
| pydocstyle | `# noqa: D100`                 |
| hadolint   | `# hadolint ignore=DL3008`     |

______________________________________________________________________

## Messaging Standards

All automation output (CI logs, script output, step summaries) follows the conventions documented in
`MESSAGING_STANDARDS.md`:

- `[PASS]` — check succeeded
- `[FAIL]` — check failed, blocks merge
- `[WARN]` — issue detected, advisory only
- `[SKIP]` — check not applicable
- `[INFO]` — informational context

No emoji. No ANSI color codes in persisted output. One line per status item.

______________________________________________________________________

*This file documents the standards as configured. The authoritative configs are `.pre-commit-config.yaml`,
`pyproject.toml`, and the `reusable-*.yml` workflows.*
