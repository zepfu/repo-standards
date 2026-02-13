# GUIDELINES.md — Development Conventions & Standards

## Python Conventions

All Python code in this repo follows the standards defined in `CODE_STANDARDS.md`. Summary:

- **Formatter:** Black (line-length=100, target=py311) — auto-fixes on commit
- **Import sorting:** isort (profile=black, line_length=100) — auto-fixes on commit
- **Linting:** Flake8 (max-line=120, max-complexity=20, ignore E203/W503)
- **Dead code:** autoflake (remove unused imports/variables), eradicate (remove commented-out code)
- **Docstrings:** pydocstyle (Google convention, D100-D107 ignored — format enforced, not existence)
- **Security:** Bandit (skips B101/B404/B603 for scripts)
- **Type checking:** mypy (Python 3.11, ignore_missing_imports)
- **Required version:** Python 3.11+

### Python Script Conventions

Scripts in `scripts/` follow additional conventions:

- Use `argparse` for CLI arguments with clear `--help` text
- Use `if __name__ == "__main__":` guard
- Exit codes: 0 = success, 1 = error, 2 = usage error
- Follow MESSAGING_STANDARDS.md for output formatting (status prefixes, no emoji, terse messages)
- Log to stderr, structured output to stdout
- Handle file-not-found and permission errors gracefully

## Shell Conventions

- **Linter:** ShellCheck (severity=error, enable=all, shell=bash)
- All scripts start with `#!/usr/bin/env bash`
- Use `set -euo pipefail` at the top of every script
- Quote all variable expansions: `"${var}"` not `$var`
- Use `[[ ]]` for conditionals, not `[ ]`
- Follow MESSAGING_STANDARDS.md for output formatting

## YAML Conventions

- **Linter:** yamllint (relaxed preset, line-length=150)
- Indent with 2 spaces
- No trailing spaces
- Use `---` document start marker

## Markdown Conventions

- **Formatter:** mdformat (wrap=120, GFM + tables + frontmatter)
- One sentence per line in source (for clean diffs)
- Use ATX headers (`#` style, not underline)
- Fenced code blocks with language tags

## Dockerfile Conventions

- **Linter:** hadolint (v2.12.0)
- Follow hadolint recommendations for best practices

## Makefile Conventions

- **Linter:** checkmake (via `.checkmake` config)
- Every target must have a `## Help text` comment for `make help`
- Use `.PHONY` for non-file targets
- Use `$(MAKE)` for recursive make calls

## GitHub Actions Workflow Conventions

- **Linter:** actionlint
- All reusable workflows use `workflow_call` trigger
- Provide configurable inputs with sensible defaults
- Generate GitHub Step Summaries for visibility
- Pin action versions to specific SHAs or tags (not `@main`)
- Include path filters to avoid unnecessary runs

## Messaging & Output Standards

All automation output (workflows, scripts, Makefile targets) follows `MESSAGING_STANDARDS.md`:

- Status prefixes: `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`
- No emoji, no Unicode symbols, no ANSI color in persisted output
- One line per status item
- Name the tool or check that produced the result
- Include fix commands when a fix exists

## Config File Change Process

When modifying any distributed config file (`.editorconfig`, `.flake8`, `.pre-commit-config.yaml`, `pyproject.toml`,
etc.):

1. Make the change in this repo first
1. Update `CODE_STANDARDS.md` if the change affects documented standards
1. Test with pre-commit locally: `pre-commit run --all-files`
1. Document the change in the commit message (Conventional Commits)
1. After merge, consumer repos pull the update via `sync-configs.sh`

## Testing Strategy

- **Pre-commit validation:** All hooks must pass locally before commit
- **CI validation:** All reusable workflows must be syntactically valid (actionlint)
- **Config validation:** `reusable-config-validation.yml` checks that required config files exist and parse correctly
- **Script testing:** Python scripts must handle edge cases (empty repos, missing files) without crashing
- **Consumer repo testing:** Verify workflows work correctly when called from a consumer repo

### Critical Test Scenarios

1. `sync-configs.sh` preserves consumer customizations (creates `.bak` backups)
1. Pre-commit hooks catch all intended violations (Black, isort, Flake8, ShellCheck, etc.)
1. Reusable workflows work with default inputs (no required inputs that lack defaults)
1. Documentation generation scripts handle empty/new repos gracefully
1. Config files don't conflict with each other (e.g., Black line-length vs Flake8 max-line-length)

## Environment Variables

```env
# No runtime environment variables — this is a static config/tooling repo.
# Python scripts use CLI arguments, not environment variables.
# GitHub Actions workflows use inputs, not environment variables.
```
