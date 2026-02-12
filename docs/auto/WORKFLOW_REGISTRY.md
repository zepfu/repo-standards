# Workflow Registry & Tool Coverage

**Auto-generated:** 2026-02-12 04:08:44

> Complete reference for all reusable workflows: what tools they run, their inputs, blocking vs. advisory behavior, and
> overlap with pre-commit.

## How to Use This Document

- **Adopting workflows?** Jump to [Recommended Adoption Profiles](#recommended-adoption-profiles) to see which
  combination fits your project.
- **Debugging a CI failure?** Find the failing workflow in the [Workflow Registry](#workflow-registry) to see exactly
  which tools run and whether failures are blocking.
- **Choosing between pre-commit and CI?** See the [Tool Coverage Matrix](#tool-coverage-matrix) for the full overlap
  picture.

## Pre-commit vs. CI: How They Work Together

Many tools appear in **both** pre-commit hooks and CI workflows. This is intentional — they serve different roles:

|             | Pre-commit (local)                  | CI Workflows (remote)                            |
| ----------- | ----------------------------------- | ------------------------------------------------ |
| **When**    | Before each commit                  | On push / PR                                     |
| **Mode**    | Fix-then-commit — auto-fix in place | Check-only — report violations without modifying |
| **Scope**   | Staged files only                   | Full repository                                  |
| **Purpose** | Fast feedback; prevent bad commits  | Enforcement gate; catches skipped hooks          |
| **Failure** | Blocks `git commit` locally         | Blocks PR merge                                  |

### Why the overlap matters

A downstream repo should run **both** pre-commit and CI workflows. Pre-commit gives developers instant feedback and
auto-fixes. CI is the safety net that guarantees standards are met regardless of local setup — someone who clones fresh,
skips `pre-commit install`, or uses `--no-verify` will still be caught.

### Tools unique to each context

Some tools only run in one context:

- **CI only:** Vulture (dead code), PyLint unreachable-code checks, py_compile syntax validation, Docker build, Sphinx
  docs build. These are too slow or too noisy for a pre-commit hook.
- **Pre-commit only:** hadolint (Dockerfile linting), file-hygiene hooks (trailing whitespace, EOF fixer, merge conflict
  detection, private key detection). These are fast fixers best run locally.

See the [Tool Coverage Matrix](#tool-coverage-matrix) below for the complete mapping.

## Workflow Registry

### `reusable-config-validation.yml`

**Config Standards Validation**

#### Tools Executed

| Tool                        | Job                | Severity | Scope            | Config |
| --------------------------- | ------------------ | -------- | ---------------- | ------ |
| **Required file existence** | `validate-configs` | blocking | `repo root`      | —      |
| **.gitattributes content**  | `validate-configs` | blocking | `.gitattributes` | —      |
| **.gitignore pattern**      | `validate-configs` | advisory | `.gitignore`     | —      |

______________________________________________________________________

### `reusable-docker-build.yml`

**Docker Build Standards**

#### Inputs

| Input       | Type    | Default       | Description            |
| ----------- | ------- | ------------- | ---------------------- |
| `platforms` | string  | `linux/amd64` | Platforms to build for |
| `push`      | boolean | `false`       | Push image after build |

#### Tools Executed

| Tool             | Job            | Severity | Scope | Config |
| ---------------- | -------------- | -------- | ----- | ------ |
| **Docker Build** | `docker-build` | blocking | `.`   | —      |

______________________________________________________________________

### `reusable-makefile-ci.yml`

**Makefile Standards Enforcement**

#### Inputs

| Input              | Type    | Default | Description                      |
| ------------------ | ------- | ------- | -------------------------------- |
| `fail-on-warnings` | boolean | `false` | Fail build on checkmake warnings |

#### Tools Executed

| Tool                                | Job                 | Severity | Scope            | Config     |
| ----------------------------------- | ------------------- | -------- | ---------------- | ---------- |
| **checkmake**                       | `validate-makefile` | blocking | `.`              | .checkmake |
| **Makefile hygiene (tabs, .PHONY)** | `validate-makefile` | advisory | `Makefile, *.mk` | —          |

______________________________________________________________________

### `reusable-pre-commit.yml`

**Pre-commit Standards Enforcement**

#### Inputs

| Input            | Type   | Default | Description                   |
| ---------------- | ------ | ------- | ----------------------------- |
| `python-version` | string | `3.13`  | Python version for pre-commit |

#### Tools Executed

| Tool           | Job          | Severity | Scope | Config |
| -------------- | ------------ | -------- | ----- | ------ |
| **pre-commit** | `pre-commit` | blocking | `.`   | —      |

______________________________________________________________________

### `reusable-python-ci.yml`

**Python Standards Enforcement**

#### Inputs

| Input            | Type   | Default | Description                    |
| ---------------- | ------ | ------- | ------------------------------ |
| `python-version` | string | `3.13`  | Python version (must be 3.11+) |

#### Tools Executed

| Tool           | Job             | Severity | Scope            | Config                            |
| -------------- | --------------- | -------- | ---------------- | --------------------------------- |
| **Black**      | `python-lint`   | blocking | `. (all Python)` | --line-length=100                 |
| **isort**      | `python-lint`   | blocking | `. (all Python)` | --profile=black --line-length=100 |
| **Flake8**     | `python-lint`   | blocking | `. (all Python)` | .flake8                           |
| **py_compile** | `python-syntax` | blocking | `**/*.py`        | —                                 |

#### Job Dependencies

- `python-lint` ← `validate-python-version`
- `python-syntax` ← `validate-python-version`

______________________________________________________________________

### `reusable-quality-checks.yml`

**Advanced Quality Checks**

#### Inputs

| Input            | Type    | Default | Description                           |
| ---------------- | ------- | ------- | ------------------------------------- |
| `python-version` | string  | `3.13`  | Python version to use                 |
| `fail-on-unused` | boolean | `false` | Fail build if unused code is detected |

#### Tools Executed

| Tool                                | Job                    | Severity | Scope          | Config                   |
| ----------------------------------- | ---------------------- | -------- | -------------- | ------------------------ |
| **Vulture**                         | `detect-unused-python` | advisory | `scripts/`     | —                        |
| **Autoflake**                       | `detect-unused-python` | advisory | `scripts/*.py` | —                        |
| **Eradicate**                       | `detect-unused-python` | advisory | `scripts/*.py` | —                        |
| **PyLint**                          | `detect-unused-python` | advisory | `scripts/*.py` | —                        |
| **Unused shell function detection** | `detect-unused-shell`  | advisory | `scripts/*.sh` | —                        |
| **mdformat**                        | `markdown-lint`        | blocking | `.`            | --wrap 120               |
| **Bandit**                          | `python-security`      | blocking | `scripts/*.py` | pyproject.toml           |
| **mypy**                            | `python-types`         | advisory | `scripts/*.py` | --ignore-missing-imports |
| **pydocstyle**                      | `python-docstyle`      | blocking | `scripts/*.py` | pyproject.toml           |
| **actionlint**                      | `actionlint`           | blocking | `.`            | —                        |

#### Job Dependencies

- `summary` ← `detect-unused-python`, `detect-unused-shell`, `markdown-lint`, `python-security`, `python-types`,
  `python-docstyle`, `actionlint`

______________________________________________________________________

### `reusable-shell-ci.yml`

**Shell Script Standards Enforcement**

#### Inputs

| Input                | Type   | Default   | Description                                             |
| -------------------- | ------ | --------- | ------------------------------------------------------- |
| `severity`           | string | `error`   | ShellCheck severity level (error, warning, info, style) |
| `shellcheck-version` | string | `v0.10.0` | ShellCheck version to use                               |

#### Tools Executed

| Tool           | Job           | Severity | Scope     | Config        |
| -------------- | ------------- | -------- | --------- | ------------- |
| **ShellCheck** | `shellcheck`  | blocking | `**/*.sh` | .shellcheckrc |
| **bash -n**    | `bash-syntax` | blocking | `**/*.sh` | —             |

______________________________________________________________________

### `reusable-update-architecture.yml`

**Update Architecture Documentation**

#### Inputs

| Input            | Type   | Default                          | Description                                                                   |
| ---------------- | ------ | -------------------------------- | ----------------------------------------------------------------------------- |
| `output-path`    | string | `docs/auto/ARCHITECTURE_AUTO.md` | Output file path for generated documentation                                  |
| `diagrams`       | string | `all`                            | Comma-separated list of diagram types to generate (or "all" for all diagrams) |
| `python-version` | string | `3.13`                           | Python version to use                                                         |

#### Tools Executed

| Tool                         | Job                     | Severity | Scope      | Config     |
| ---------------------------- | ----------------------- | -------- | ---------- | ---------- |
| **generate_architecture.py** | `generate-architecture` | blocking | `scripts/` | —          |
| **mdformat**                 | `generate-architecture` | blocking | `.`        | --wrap 120 |

______________________________________________________________________

### `reusable-update-docs.yml`

**Update Documentation (Reusable)**

#### Inputs

| Input                   | Type    | Default     | Description                                    |
| ----------------------- | ------- | ----------- | ---------------------------------------------- |
| `python-version`        | string  | `3.13`      | Python version to use                          |
| `docs-directory`        | string  | `docs`      | Documentation directory path                   |
| `auto-docs-directory`   | string  | `docs/auto` | Auto-generated docs directory path             |
| `generate-architecture` | boolean | `true`      | Generate architecture diagrams                 |
| `architecture-diagrams` | string  | `all`       | Comma-separated list of diagram types or "all" |

#### Tools Executed

| Tool                         | Job                     | Severity | Scope      | Config     |
| ---------------------------- | ----------------------- | -------- | ---------- | ---------- |
| **changelog.py**             | `update-and-build-docs` | blocking | `scripts/` | —          |
| **repo_map.py**              | `update-and-build-docs` | blocking | `scripts/` | —          |
| **generate_architecture.py** | `update-and-build-docs` | blocking | `scripts/` | —          |
| **mdformat**                 | `update-and-build-docs` | blocking | `.`        | --wrap 120 |
| **pre-commit**               | `update-and-build-docs` | blocking | `.`        | —          |
| **Sphinx**                   | `update-and-build-docs` | blocking | `.`        | —          |

______________________________________________________________________

### `reusable-yaml-ci.yml`

**YAML Standards Enforcement**

#### Inputs

| Input    | Type    | Default                                                | Description                             |
| -------- | ------- | ------------------------------------------------------ | --------------------------------------- |
| `config` | string  | `{extends: relaxed, rules: {line-length: {max: 150}}}` | yamllint configuration                  |
| `strict` | boolean | `false`                                                | Fail on warnings (default: errors only) |

#### Tools Executed

| Tool                        | Job             | Severity | Scope                     | Config                    |
| --------------------------- | --------------- | -------- | ------------------------- | ------------------------- |
| **yamllint**                | `validate-yaml` | blocking | `.`                       | relaxed + line-length 150 |
| **Workflow YAML structure** | `validate-yaml` | blocking | `.github/workflows/*.yml` | —                         |

______________________________________________________________________

## Tool Coverage Matrix

Which tools run where — at a glance.

| Tool                                 | Category          | CI Workflow(s)                                                                                | Pre-commit | Unique to       |
| ------------------------------------ | ----------------- | --------------------------------------------------------------------------------------------- | ---------- | --------------- |
| actionlint                           | ci-linting        | `reusable-quality-checks.yml`                                                                 | ✅         | both            |
| Autoflake                            | dead-code         | `reusable-quality-checks.yml`                                                                 | ✅         | both            |
| Bandit                               | security          | `reusable-quality-checks.yml`                                                                 | ✅         | both            |
| Black                                | python-formatting | `reusable-python-ci.yml`                                                                      | ✅         | both            |
| checkmake                            | makefile-linting  | `reusable-makefile-ci.yml`                                                                    | ✅         | both            |
| Eradicate                            | dead-code         | `reusable-quality-checks.yml`                                                                 | ✅         | both            |
| Flake8                               | python-linting    | `reusable-python-ci.yml`                                                                      | ✅         | both            |
| isort                                | python-formatting | `reusable-python-ci.yml`                                                                      | ✅         | both            |
| mdformat                             | markdown          | `reusable-quality-checks.yml`, `reusable-update-architecture.yml`, `reusable-update-docs.yml` | ✅         | both            |
| mypy                                 | type-checking     | `reusable-quality-checks.yml`                                                                 | ✅         | both            |
| pydocstyle                           | docstyle          | `reusable-quality-checks.yml`                                                                 | ✅         | both            |
| ShellCheck                           | shell-linting     | `reusable-shell-ci.yml`                                                                       | ✅         | both            |
| yamllint                             | yaml-linting      | `reusable-yaml-ci.yml`                                                                        | ✅         | both            |
| check-added-large-files              | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| check-case-conflict                  | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| check-executables-have-shebangs      | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| check-json                           | json-syntax       | —                                                                                             | ✅         | pre-commit only |
| check-merge-conflict                 | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| check-shebang-scripts-are-executable | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| check-symlinks                       | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| check-toml                           | toml-syntax       | —                                                                                             | ✅         | pre-commit only |
| check-yaml                           | yaml-syntax       | —                                                                                             | ✅         | pre-commit only |
| destroyed-symlinks                   | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| detect-private-key                   | security          | —                                                                                             | ✅         | pre-commit only |
| end-of-file-fixer                    | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| fix-byte-order-marker                | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| hadolint                             | docker-linting    | —                                                                                             | ✅         | pre-commit only |
| mixed-line-ending                    | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| trailing-whitespace                  | file-hygiene      | —                                                                                             | ✅         | pre-commit only |
| .gitattributes content               | config-validation | `reusable-config-validation.yml`                                                              | —          | CI only         |
| .gitignore pattern                   | config-validation | `reusable-config-validation.yml`                                                              | —          | CI only         |
| Makefile hygiene (tabs, .PHONY)      | makefile-linting  | `reusable-makefile-ci.yml`                                                                    | —          | CI only         |
| Required file existence              | config-validation | `reusable-config-validation.yml`                                                              | —          | CI only         |
| Unused shell function detection      | dead-code         | `reusable-quality-checks.yml`                                                                 | —          | CI only         |
| Workflow YAML structure              | yaml-linting      | `reusable-yaml-ci.yml`                                                                        | —          | CI only         |
| bash -n                              | shell-syntax      | `reusable-shell-ci.yml`                                                                       | —          | CI only         |
| changelog.py                         | docs-gen          | `reusable-update-docs.yml`                                                                    | —          | CI only         |
| Docker Build                         | docker-build      | `reusable-docker-build.yml`                                                                   | —          | CI only         |
| generate_architecture.py             | docs-gen          | `reusable-update-architecture.yml`, `reusable-update-docs.yml`                                | —          | CI only         |
| pre-commit                           | meta-linting      | `reusable-pre-commit.yml`, `reusable-update-docs.yml`                                         | —          | CI only         |
| py_compile                           | python-syntax     | `reusable-python-ci.yml`                                                                      | —          | CI only         |
| PyLint                               | dead-code         | `reusable-quality-checks.yml`                                                                 | —          | CI only         |
| repo_map.py                          | docs-gen          | `reusable-update-docs.yml`                                                                    | —          | CI only         |
| Sphinx                               | docs-build        | `reusable-update-docs.yml`                                                                    | —          | CI only         |
| Vulture                              | dead-code         | `reusable-quality-checks.yml`                                                                 | —          | CI only         |

### Version Comparison (tools in both CI and pre-commit)

| Tool       | CI Version | Pre-commit Rev |
| ---------- | ---------- | -------------- |
| actionlint | `latest`   | `v1.7.10`      |
| Autoflake  | `latest`   | `v2.3.1`       |
| Bandit     | `latest`   | `1.9.3`        |
| Black      | `latest`   | `26.1.0`       |
| checkmake  | `latest`   | `v0.3.2`       |
| Eradicate  | `latest`   | `3.0.1`        |
| Flake8     | `latest`   | `7.3.0`        |
| isort      | `latest`   | `7.0.0`        |
| mdformat   | `latest`   | `0.7.22`       |
| mypy       | `latest`   | `v1.19.1`      |
| pydocstyle | `latest`   | `6.3.0`        |
| ShellCheck | `latest`   | `v0.11.0.1`    |
| yamllint   | `latest`   | `v1.38.0`      |

> **⚠️ Version drift risk:** CI workflows install tools via `pip install` without version pins, so they always get the
> latest release. Pre-commit pins specific revisions. A tool releasing a breaking change can cause CI to fail while
> pre-commit passes locally (or vice versa). If you hit this, check whether the versions in these two columns have
> diverged. Downstream repos that need stability should pin tool versions in their CI config or rely on pre-commit as
> the single source of truth for tool versions.

### Scope Differences Between CI and Pre-commit

Some tools scan different file sets in CI vs. pre-commit, which can produce different results:

| Tool                 | CI Scope                                  | Pre-commit Scope                                | Impact                                                                                                                                              |
| -------------------- | ----------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bandit               | `-r .` with `pyproject.toml` exclude_dirs | All staged `.py` files with `-c pyproject.toml` | CI scans the full tree (minus excludes); pre-commit only scans staged files. New `.py` files outside `scripts/` may be missed locally until staged. |
| Black, isort         | `. (all Python)`                          | Staged `.py` files only                         | CI catches unformatted files that weren't staged in the committing developer's working tree.                                                        |
| ShellCheck           | `**/*.sh` (full tree)                     | Staged `.sh` files only                         | Same pattern — CI is exhaustive, pre-commit is incremental.                                                                                         |
| Autoflake, Eradicate | `scripts/` (CI check-only)                | All staged `.py` (fix in-place)                 | CI only checks `scripts/`; pre-commit fixes across all staged Python files.                                                                         |

> For most repos this is fine — pre-commit catches issues incrementally and CI validates the full tree. But if CI fails
> on a file that pre-commit never saw, scope difference is the likely cause.

## Blocking vs. Advisory Behavior

Understanding which tools will block your PR and which are informational.

### Blocking (will fail your PR)

- **.gitattributes content** (`validate-configs` in `reusable-config-validation.yml`)
- **Bandit** (`python-security` in `reusable-quality-checks.yml`)
- **Black** (`python-lint` in `reusable-python-ci.yml`)
- **Docker Build** (`docker-build` in `reusable-docker-build.yml`)
- **Flake8** (`python-lint` in `reusable-python-ci.yml`)
- **Required file existence** (`validate-configs` in `reusable-config-validation.yml`)
- **ShellCheck** (`shellcheck` in `reusable-shell-ci.yml`)
- **Sphinx** (`update-and-build-docs` in `reusable-update-docs.yml`)
- **Workflow YAML structure** (`validate-yaml` in `reusable-yaml-ci.yml`)
- **actionlint** (`actionlint` in `reusable-quality-checks.yml`)
- **bash -n** (`bash-syntax` in `reusable-shell-ci.yml`)
- **changelog.py** (`update-and-build-docs` in `reusable-update-docs.yml`)
- **checkmake** (`validate-makefile` in `reusable-makefile-ci.yml`)
- **generate_architecture.py** (`generate-architecture` in `reusable-update-architecture.yml`)
- **generate_architecture.py** (`update-and-build-docs` in `reusable-update-docs.yml`)
- **isort** (`python-lint` in `reusable-python-ci.yml`)
- **mdformat** (`generate-architecture` in `reusable-update-architecture.yml`)
- **mdformat** (`markdown-lint` in `reusable-quality-checks.yml`)
- **mdformat** (`update-and-build-docs` in `reusable-update-docs.yml`)
- **pre-commit** (`pre-commit` in `reusable-pre-commit.yml`)
- **pre-commit** (`update-and-build-docs` in `reusable-update-docs.yml`)
- **py_compile** (`python-syntax` in `reusable-python-ci.yml`)
- **pydocstyle** (`python-docstyle` in `reusable-quality-checks.yml`)
- **repo_map.py** (`update-and-build-docs` in `reusable-update-docs.yml`)
- **yamllint** (`validate-yaml` in `reusable-yaml-ci.yml`)

### Advisory (warnings only, will not fail)

- **.gitignore pattern** (`validate-configs` in `reusable-config-validation.yml`)
- **Autoflake** (`detect-unused-python` in `reusable-quality-checks.yml`)
- **Eradicate** (`detect-unused-python` in `reusable-quality-checks.yml`)
- **Makefile hygiene (tabs, .PHONY)** (`validate-makefile` in `reusable-makefile-ci.yml`)
- **PyLint** (`detect-unused-python` in `reusable-quality-checks.yml`)
- **Unused shell function detection** (`detect-unused-shell` in `reusable-quality-checks.yml`)
- **Vulture** (`detect-unused-python` in `reusable-quality-checks.yml`)
- **mypy** (`python-types` in `reusable-quality-checks.yml`)

## Recommended Adoption Profiles

### Python Project (Minimal)

```yaml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
```

**What you get:** Black, isort, Flake8, syntax validation via CI; full hook suite locally via pre-commit.

**Overlap:** Black, isort, Flake8 run in both `reusable-python-ci.yml` and pre-commit. See
[Pre-commit vs. CI](#pre-commit-vs-ci-how-they-work-together) for why both are recommended.

______________________________________________________________________

### Python Project (Comprehensive)

```yaml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  quality-checks:
    uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

**What you get:** Everything from minimal, plus Bandit security scanning, mypy type checking, Vulture dead-code
detection, pydocstyle, actionlint, and mdformat.

**Overlap:** `reusable-quality-checks.yml` runs Bandit, mypy, pydocstyle, actionlint, Autoflake, Eradicate, and mdformat
— all of which also run via pre-commit hooks. The CI versions provide granular per-job visibility and add Vulture and
PyLint unreachable-code checks (not in pre-commit). See [Pre-commit vs. CI](#pre-commit-vs-ci-how-they-work-together)
for why both are recommended.

______________________________________________________________________

### Shell Project

```yaml
jobs:
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

______________________________________________________________________

### Python + Docker Project

```yaml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  quality-checks:
    uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  docker-build:
    uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
    needs: [python-standards, shell-standards]
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

**Note:** hadolint (Dockerfile linting) is in pre-commit only — there is no dedicated CI workflow for it yet. Docker
build validation happens via `reusable-docker-build.yml`.

______________________________________________________________________

### Full Stack (All Workflows)

```yaml
jobs:
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  yaml-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main
  makefile-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-makefile-ci.yml@main
  quality-checks:
    uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
  docker-build:
    uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
    needs: [python-standards, shell-standards]
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  update-docs:
    uses: zepfu/repo-standards/.github/workflows/reusable-update-docs.yml@main
    needs: [python-standards, shell-standards]
```

## Workflow Version Defaults

Key input defaults across workflows. Pin these in your CI config if you need stability — defaults may change when
repo-standards is updated.

| Workflow                           | Input                   | Current Default                                        |
| ---------------------------------- | ----------------------- | ------------------------------------------------------ |
| `reusable-docker-build.yml`        | `platforms`             | `linux/amd64`                                          |
| `reusable-docker-build.yml`        | `push`                  | `false`                                                |
| `reusable-makefile-ci.yml`         | `fail-on-warnings`      | `false`                                                |
| `reusable-pre-commit.yml`          | `python-version`        | `3.13`                                                 |
| `reusable-python-ci.yml`           | `python-version`        | `3.13`                                                 |
| `reusable-quality-checks.yml`      | `python-version`        | `3.13`                                                 |
| `reusable-quality-checks.yml`      | `fail-on-unused`        | `false`                                                |
| `reusable-shell-ci.yml`            | `severity`              | `error`                                                |
| `reusable-shell-ci.yml`            | `shellcheck-version`    | `v0.10.0`                                              |
| `reusable-update-architecture.yml` | `output-path`           | `docs/auto/ARCHITECTURE_AUTO.md`                       |
| `reusable-update-architecture.yml` | `diagrams`              | `all`                                                  |
| `reusable-update-architecture.yml` | `python-version`        | `3.13`                                                 |
| `reusable-update-docs.yml`         | `python-version`        | `3.13`                                                 |
| `reusable-update-docs.yml`         | `docs-directory`        | `docs`                                                 |
| `reusable-update-docs.yml`         | `auto-docs-directory`   | `docs/auto`                                            |
| `reusable-update-docs.yml`         | `generate-architecture` | `true`                                                 |
| `reusable-update-docs.yml`         | `architecture-diagrams` | `all`                                                  |
| `reusable-yaml-ci.yml`             | `config`                | `{extends: relaxed, rules: {line-length: {max: 150}}}` |
| `reusable-yaml-ci.yml`             | `strict`                | `false`                                                |

> **Tip:** If your project requires Python 3.11, pass `python-version: '3.11'` explicitly rather than relying on the
> default, which is currently `3.13`.

______________________________________________________________________

*This file is auto-generated by `generate_workflow_registry.py` from repo-standards.* *Manual edits will be
overwritten.*
