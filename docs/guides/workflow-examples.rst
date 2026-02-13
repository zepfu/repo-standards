Workflow Usage Examples
======================

This guide shows how to set up CI workflows for different project types using
the reusable workflows from ``repo-standards``.

All workflows are called via::

   uses: zepfu/repo-standards/.github/workflows/reusable-<name>@main

.. contents:: On This Page
   :local:
   :depth: 2

Starter Configuration
---------------------

For any new project, this minimal workflow file covers the essentials. Create
``.github/workflows/ci.yml``:

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     yaml:
       uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main

This gives you pre-commit enforcement, config file validation, and YAML linting
out of the box.

Python Application
------------------

A Python web application or CLI tool (Flask, FastAPI, Django, Click, etc.).

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.13'

     quality:
       uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
       with:
         python-version: '3.13'

     yaml:
       uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main

**What this checks:**

- Black formatting, isort import ordering, Flake8 linting
- Bandit security scanning, mypy type checking, pydocstyle docstrings
- Dead code detection (vulture, eradicate)
- YAML file validation
- Pre-commit hooks (all configured hooks)
- Config file presence and correctness

Python Library
--------------

A Python package or library published to PyPI. Same as a Python application
but typically with stricter quality checks.

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

     quality:
       uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
       with:
         fail-on-unused: true

     yaml:
       uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main
       with:
         strict: true

**Key differences from application:**

- ``fail-on-unused: true`` -- libraries should have zero dead code
- ``strict: true`` on YAML -- warnings become errors for release quality

Shell Scripts / DevOps Tooling
------------------------------

A repository primarily containing shell scripts, Makefiles, and CI tooling.

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     shell:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
       with:
         severity: warning

     makefile:
       uses: zepfu/repo-standards/.github/workflows/reusable-makefile-ci.yml@main

     yaml:
       uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main

**What this checks:**

- ShellCheck at warning level (stricter than default error-only)
- Bash syntax validation for all ``.sh`` files
- Makefile best practices via checkmake
- YAML validation for CI config files

Dockerized Service
------------------

A service that ships as a Docker container.

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

     docker:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
       with:
         platforms: 'linux/amd64,linux/arm64'
         push: false

     shell:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

     yaml:
       uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main

**What this checks:**

- Dockerfile linting via hadolint
- Multi-platform build verification (amd64 + arm64)
- Python code quality (if the service is Python)
- Shell script quality (for entrypoint scripts)

Full Suite (All Workflows)
--------------------------

For ``repo-standards`` itself or repos that want maximum coverage.

.. code-block:: yaml

   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

     quality:
       uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
       with:
         fail-on-unused: true

     shell:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
       with:
         severity: warning

     yaml:
       uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main
       with:
         strict: true

     docker:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main

     makefile:
       uses: zepfu/repo-standards/.github/workflows/reusable-makefile-ci.yml@main

Auto-Documentation Workflow
---------------------------

Add this as a separate workflow file to auto-generate and deploy documentation.
Create ``.github/workflows/docs.yml``:

.. code-block:: yaml

   name: Documentation

   on:
     push:
       branches: [main]
       paths:
         - '**.py'
         - '**.sh'
         - 'docs/**'
     workflow_dispatch: {}

   permissions:
     contents: write
     pages: write
     id-token: write

   jobs:
     docs:
       uses: zepfu/repo-standards/.github/workflows/reusable-update-docs.yml@main
       with:
         docs-directory: docs
         generate-architecture: true

This auto-generates CHANGELOG, REPO_MAP, ARCHITECTURE, and WORKFLOW_REGISTRY
docs, builds Sphinx, and deploys to GitHub Pages on every push to main.

.. note::

   The documentation workflow requires ``contents: write`` permission to commit
   auto-generated files and ``pages: write`` for GitHub Pages deployment.

Input Reference Quick Table
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 20 20

   * - Workflow
     - Input
     - Default
     - Notes
   * - python-ci
     - ``python-version``
     - ``3.13``
     - Must be 3.11+
   * - shell-ci
     - ``severity``
     - ``error``
     - error/warning/info/style
   * - shell-ci
     - ``shellcheck-version``
     - ``v0.10.0``
     -
   * - yaml-ci
     - ``config``
     - relaxed, 150 chars
     - yamllint config string
   * - yaml-ci
     - ``strict``
     - ``false``
     - Fail on warnings
   * - docker-build
     - ``platforms``
     - ``linux/amd64``
     - Comma-separated
   * - docker-build
     - ``push``
     - ``false``
     - Push after build
   * - quality-checks
     - ``python-version``
     - ``3.13``
     -
   * - quality-checks
     - ``fail-on-unused``
     - ``false``
     - Fail on dead code
   * - makefile-ci
     - ``fail-on-warnings``
     - ``false``
     - Fail on checkmake warnings
   * - pre-commit
     - ``python-version``
     - ``3.13``
     -
   * - update-docs
     - ``docs-directory``
     - ``docs``
     -
   * - update-docs
     - ``generate-architecture``
     - ``true``
     -
