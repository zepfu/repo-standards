repo-standards Documentation
=============================

**Organization-wide code quality standards and configuration templates.**

This repository provides reusable workflows, configuration files, and automation scripts
to maintain consistent code quality across all projects.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   guides/getting-started
   guides/adopter-guide
   guides/workflow-examples
   guides/troubleshooting
   guides/quick-setup

.. toctree::
   :maxdepth: 2
   :caption: Standards

   guides/python-standards
   guides/shell-standards
   guides/workflow-standards
   guides/docker-standards

.. toctree::
   :maxdepth: 2
   :caption: Scripts & Tools

   reference/scripts
   reference/workflows
   reference/configs

.. toctree::
   :maxdepth: 1
   :caption: Auto-Generated Documentation

   auto/CHANGELOG
   auto/REPO_MAP
   auto/ARCHITECTURE_AUTO
   auto/WORKFLOW_REGISTRY

Features
--------

✅ **Reusable GitHub Actions Workflows**
   - Python standards (Black, isort, Flake8)
   - Shell standards (ShellCheck)
   - Docker build standards
   - Pre-commit enforcement
   - Configuration validation

✅ **Configuration Files**
   - `.gitattributes` - Line ending rules
   - `.gitignore` - Standard ignore patterns
   - `.editorconfig` - Editor consistency
   - `.flake8` - Python linting
   - `.shellcheckrc` - Shell linting
   - `.pre-commit-config.yaml` - Pre-commit hooks

✅ **Automation Scripts**
   - `changelog.py` - Generate changelogs from git history
   - `repo_map.py` - Generate repository structure docs
   - `generate_architecture.py` - Generate architecture diagrams
   - `generate_workflow_registry.py` - Generate workflow registry & tool coverage
   - `sync-configs.sh` - Sync config files from repo-standards

Quick Links
-----------

- `GitHub Repository <https://github.com/zepfu/repo-standards>`_
- `Issue Tracker <https://github.com/zepfu/repo-standards/issues>`_
- `Pull Requests <https://github.com/zepfu/repo-standards/pulls>`_

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
