Workflows Reference
===================

Reusable GitHub Actions workflows.

See :doc:`/guides/workflow-standards` for usage examples.

Available Workflows
-------------------

reusable-python-ci.yml
^^^^^^^^^^^^^^^^^^^^^^

Python code quality checks.

**Inputs:**

- ``python-version`` - Python version (default: '3.11')

reusable-shell-ci.yml
^^^^^^^^^^^^^^^^^^^^^

Shell script quality checks.

**Inputs:**

- ``severity`` - ShellCheck severity (default: 'error')
- ``shellcheck-version`` - ShellCheck version (default: 'v0.9.0')

reusable-docker-build.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^

Docker build testing.

**Inputs:**

- ``platforms`` - Build platforms (default: 'linux/amd64')
- ``push`` - Push image after build (default: false)

reusable-pre-commit.yml
^^^^^^^^^^^^^^^^^^^^^^^

Pre-commit hook enforcement.

**Inputs:**

- ``python-version`` - Python version (default: '3.11')

reusable-config-validation.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration file validation.

**No inputs.**

reusable-yaml-ci.yml
^^^^^^^^^^^^^^^^^^^^^

YAML file validation and linting.

**Inputs:**

- ``config`` - yamllint configuration string (default: ``{extends: relaxed, rules: {line-length: {max: 150}}}``)
- ``strict`` - Fail on warnings, not just errors (default: false)

**Checks performed:**

- yamllint linting (uses project ``.yamllint`` if present, otherwise workflow default config)
- YAML syntax validation (``yaml.safe_load``)
- GitHub Actions workflow structure validation (``name``, ``on``, ``jobs`` fields)

reusable-makefile-ci.yml
^^^^^^^^^^^^^^^^^^^^^^^^^

Makefile syntax and standards validation.

**Inputs:**

- ``fail-on-warnings`` - Fail build on checkmake warnings (default: false)

**Checks performed:**

- Makefile syntax validation (``make -n``)
- checkmake linting (Makefile and all ``.mk`` files)
- ``.PHONY`` declaration check (advisory)
- Tab indentation check (recipes must use tabs, not spaces)

reusable-quality-checks.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Advanced code quality analysis beyond standard linting.

**Inputs:**

- ``python-version`` - Python version (default: '3.13')
- ``fail-on-unused`` - Fail build if unused code is detected (default: false)

**Jobs (run in parallel):**

- **Detect Unused Python** - Vulture (dead code), Autoflake (unused imports), Eradicate (commented-out code), PyLint (unreachable code)
- **Detect Unused Shell** - Static analysis for unused shell functions (advisory)
- **Markdown Formatting** - mdformat check (wrap 120)
- **Python Security** - Bandit security scan
- **Python Types** - mypy type checking
- **Python Docstyle** - pydocstyle Google convention
- **GitHub Actions Lint** - actionlint validation

reusable-update-docs.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^

Auto-generate documentation and deploy to GitHub Pages.

**Inputs:**

- ``python-version`` - Python version (default: '3.13')
- ``docs-directory`` - Documentation directory path (default: 'docs')
- ``auto-docs-directory`` - Auto-generated docs directory (default: 'docs/auto')
- ``generate-architecture`` - Generate architecture diagrams (default: true)
- ``architecture-diagrams`` - Comma-separated diagram types or 'all' (default: 'all')

**What it generates:**

- ``CHANGELOG.md`` from git history
- ``REPO_MAP.md`` repository structure
- ``ARCHITECTURE_AUTO.md`` Mermaid architecture diagrams
- ``WORKFLOW_REGISTRY.md`` workflow registry and tool coverage

Auto-commits generated docs and deploys Sphinx site to GitHub Pages (on main branch only).

reusable-update-architecture.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Architecture documentation generation.

**Inputs:**

- ``output-path`` - Output file (default: 'docs/ARCHITECTURE_AUTO.md')
- ``diagrams`` - Diagram types (default: 'all')
- ``python-version`` - Python version (default: '3.11')
- ``create-pr`` - Create PR (default: true)
