Getting Started
===============

Welcome to repo-standards! This guide will help you adopt organization-wide code quality standards.

Overview
--------

``repo-standards`` provides:

- **Reusable workflows** for CI/CD
- **Configuration files** for tools
- **Automation scripts** for documentation
- **Centralized maintenance** of all standards

Quick Setup
-----------

1. **Sync Configuration Files**

   .. code-block:: bash

      curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

   This adds:
   - ``.gitattributes``
   - ``.gitignore``
   - ``.editorconfig``
   - ``.flake8``
   - ``.shellcheckrc``
   - ``.pre-commit-config.yaml``
   - ``pyproject.toml``

2. **Install Pre-commit**

   .. code-block:: bash

      pip install pre-commit
      pre-commit install

3. **Add Reusable Workflows**

   Create ``.github/workflows/ci.yml``:

   .. code-block:: yaml

      ---
      name: CI

      on: [push, pull_request]

      jobs:
        python-standards:
          uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
          with:
            python-version: '3.11'

        shell-standards:
          uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

        config-validation:
          uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

4. **Test Locally**

   .. code-block:: bash

      pre-commit run --all-files

5. **Push and Watch**

   .. code-block:: bash

      git add .
      git commit -m "feat: adopt repo standards"
      git push

   GitHub Actions will now enforce standards on every push!

What Gets Enforced
------------------

Python Code
^^^^^^^^^^^

- **Black** formatting (100 char lines)
- **isort** import sorting
- **Flake8** linting (max complexity 20)
- Syntax validation

Shell Scripts
^^^^^^^^^^^^^

- **ShellCheck** linting (error level)
- Bash syntax validation
- Executable shebangs

YAML Files
^^^^^^^^^^

- Syntax validation
- Reasonable line length (150 chars)

General
^^^^^^^

- Trailing whitespace removal
- End-of-file newlines
- LF line endings (enforced via .gitattributes)
- No large files (>1MB)
- No merge conflicts

Next Steps
----------

- Read :doc:`python-standards` for Python guidelines
- Read :doc:`shell-standards` for shell scripting guidelines
- Read :doc:`workflow-standards` for GitHub Actions patterns
- See :doc:`/reference/scripts` for automation tools
