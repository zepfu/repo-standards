# Contributing to repo-standards

Thank you for your interest in contributing to repo-standards. This document covers everything you need to get started.

## Quick Start

```bash
# 1. Clone and enter the repository
git clone https://github.com/zepfu/repo-standards.git
cd repo-standards

# 2. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Verify setup
pre-commit run --all-files
```

## What This Repo Provides

- **Configuration files** synced to consumer repos via `sync-configs.sh`
- **Pre-commit hooks** for Python, Shell, YAML, Markdown, Dockerfile, GitHub Actions, and Makefile
- **Reusable GitHub Actions workflows** (10 workflows for CI checks)
- **Automation scripts** for changelog, repo map, architecture diagrams, and workflow registry

## What NOT to Contribute

- Runtime libraries or importable packages
- Language-specific linters (use existing tools: Black, ShellCheck, hadolint, etc.)
- Custom CI runners or self-hosted infrastructure
- GUI or web dashboards
- Automatic enforcement that modifies consumer repos without opt-in

## Development Workflow

### Branching

```
main       <- Protected. Latest stable.
  develop  <- Integration. Feature branches merge here.
    feature/  fix/  chore/  <- Off develop
```

- Feature branches: `feature/<short-name>`
- Bug fixes: `fix/<short-name>`
- Chores: `chore/<short-name>`

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`, `security`

**Scopes:** `workflows`, `scripts`, `configs`, `docs`, `pre-commit`, `ci`, `makefile`

**Examples:**

```
feat(workflows): add Terraform CI workflow
fix(scripts): handle spaces in repo paths for sync-configs
docs(configs): document .markdownlint.json settings
chore(pre-commit): update Black to 26.x
```

### Pull Requests

- Target branch: `develop` (not `main`)
- Description: what changed, why, test plan
- CI must pass
- 2 approvals minimum
- Squash merge

## Code Standards

### Python (3.11+)

- **Formatter:** Black (line-length: 100)
- **Import sorting:** isort (profile: black)
- **Linter:** Flake8 (max-line: 120, max-complexity: 20)
- **Security:** Bandit
- **Types:** mypy (required on function signatures)
- **Docstrings:** Google style via pydocstyle (enforced when present)
- **Exit codes:** 0 = success, 1 = error, 2 = usage error

### Shell (Bash)

- **Shebang:** `#!/usr/bin/env bash`
- **Safety:** `set -euo pipefail`
- **Variables:** Always quote: `"${var}"`, not `$var`
- **Conditionals:** Use `[[ ]]`, not `[ ]`
- **Linter:** ShellCheck (severity: error)

### YAML

- **Linter:** yamllint (relaxed, line-length: 150)
- **GitHub Actions:** actionlint validation

### Markdown

- **Formatter:** mdformat (wrap: 120, GFM + tables + frontmatter)
- **Line length:** 120 characters (tables exempt)

### Makefile

- **Linter:** checkmake (max body: 15 lines)
- **Indentation:** Tabs only for recipes (enforced)
- **Required:** `.PHONY` declarations

### Output Formatting

All scripts and workflows must follow `MESSAGING_STANDARDS.md`:

- Status prefixes: `[PASS]`, `[FAIL]`, `[WARN]`, `[SKIP]`, `[INFO]`
- No emoji or ANSI color in persisted output
- One line per status item
- Name the tool that produced the result
- Include fix commands when available

## Pre-commit Hooks

All of these run automatically on every commit after `pre-commit install`:

| Category       | Tools                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------- |
| General        | trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-json, detect-private-key, check-merge-conflict |
| Python         | Black, isort, Flake8, autoflake, eradicate, pydocstyle, Bandit, mypy                                                 |
| Shell          | ShellCheck                                                                                                           |
| YAML           | yamllint                                                                                                             |
| Markdown       | mdformat                                                                                                             |
| Dockerfile     | hadolint                                                                                                             |
| GitHub Actions | actionlint                                                                                                           |
| Makefile       | checkmake                                                                                                            |

Run all hooks manually:

```bash
pre-commit run --all-files
```

## Available Make Targets

```bash
make help           # Display all available targets
make docs           # Generate auto-documentation
make sphinx         # Build and serve Sphinx docs locally
make test           # Run tests
make sync-configs   # Sync config files from upstream
make mermaid        # Render Mermaid diagrams to SVG
make mermaid-check  # Validate mermaid-cli installation
make archive        # Create tar.gz archive
make clean          # Remove backup files and caches
```

## Important Considerations

### Breaking Changes

Reusable workflows are referenced by consumer repos via `@main`:

```yaml
uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
```

Changes to workflows or synced config files **affect all downstream repos immediately**. Test thoroughly and consider
backwards compatibility.

### Config Change Process

When modifying a synced config file:

1. Make the change in this repo
1. Test with at least one consumer repo (`sync-configs.sh`)
1. Document in the PR what downstream impact to expect
1. Update `docs/reference/configs.rst` if settings change

### Adding a New Workflow

1. Create `.github/workflows/reusable-<name>.yml`
1. Include `workflow_call` trigger with typed inputs and defaults
1. Write GitHub Step Summary output following `MESSAGING_STANDARDS.md`
1. Add documentation to `docs/reference/workflows.rst`
1. Update `docs/guides/workflow-standards.rst` with usage example

### Adding a New Config File

1. Add the file to the repository root
1. Add to `CONFIG_FILES` array in `scripts/sync-configs.sh`
1. Add to `git sparse-checkout set` in `scripts/sync-configs.sh`
1. Document in `docs/reference/configs.rst`
1. Update config list in `docs/guides/getting-started.rst`

## Reporting Issues

- Use [GitHub Issues](https://github.com/zepfu/repo-standards/issues)
- Include: what you expected, what happened, steps to reproduce
- For consumer repo issues: include the workflow/config version and repo setup

## Further Reading

- [Getting Started Guide](https://zepfu.github.io/repo-standards/guides/getting-started.html)
- [CODE_STANDARDS.md](CODE_STANDARDS.md) -- Complete standards reference
- [MESSAGING_STANDARDS.md](MESSAGING_STANDARDS.md) -- Output formatting conventions
- [Workflows Reference](https://zepfu.github.io/repo-standards/reference/workflows.html)
- [Scripts Reference](https://zepfu.github.io/repo-standards/reference/scripts.html)
- [Configs Reference](https://zepfu.github.io/repo-standards/reference/configs.html)
