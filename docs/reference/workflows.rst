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

reusable-update-architecture.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Architecture documentation generation.

**Inputs:**

- ``output-path`` - Output file (default: 'docs/ARCHITECTURE_AUTO.md')
- ``diagrams`` - Diagram types (default: 'all')
- ``python-version`` - Python version (default: '3.11')
- ``create-pr`` - Create PR (default: true)
