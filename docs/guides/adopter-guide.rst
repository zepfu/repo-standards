External Adopter Guide
======================

A comprehensive guide for teams outside the organization who want to adopt repo-standards
for their own projects. If you just need the basics, see :doc:`getting-started`.

.. contents:: On this page
   :local:
   :depth: 2

Choosing Your Adoption Path
----------------------------

**New repository (greenfield):**
Quickest path. Adopt everything at once. Follow :ref:`new-repo-setup` below.

**Existing repository with custom configs (brownfield):**
Needs careful merging to preserve your customizations. Follow :ref:`existing-repo-setup`.

**Monorepo:**
Sync configs once (repo-wide). Create separate workflow jobs per service.
Follow :ref:`new-repo-setup`, then see :ref:`monorepo-tips`.

.. _new-repo-setup:

Setup: New Repository
----------------------

**Phase 1: Sync configs (2 min)**

.. code-block:: bash

   cd /path/to/your/repo
   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

This adds 13 config files to your repo root. See :doc:`/reference/configs` for what each does.

**Phase 2: Install pre-commit (2 min)**

.. code-block:: bash

   pip install pre-commit
   pre-commit install
   pre-commit run --all-files

**Phase 3: Add CI workflows (3 min)**

Create ``.github/workflows/ci.yml``:

.. code-block:: yaml

   ---
   name: CI

   on: [push, pull_request]

   permissions:
     contents: read

   jobs:
     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'

     shell:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

**Phase 4: Commit and push**

.. code-block:: bash

   git add .
   git commit -m "feat: adopt repo-standards"
   git push

Pre-commit hooks run on commit. GitHub Actions runs the same checks on push.

.. _existing-repo-setup:

Setup: Existing Repository
---------------------------

**Step 1: Audit your current configs**

.. code-block:: bash

   ls -la .flake8 .pre-commit-config.yaml pyproject.toml Makefile .editorconfig 2>/dev/null

Note which files you have and what customizations matter to you.

**Step 2: Sync configs**

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

The script creates ``.bak`` backups of every file it overwrites. Your customizations are preserved
in ``<filename>.bak``.

**Step 3: Merge your customizations**

For each ``.bak`` file, compare and merge:

.. code-block:: bash

   # See what changed
   diff .flake8.bak .flake8

   # If you had custom ignores in .flake8, add them back:
   # extend-ignore = E203, W503, YOUR_CUSTOM_IGNORE
   # extend-exclude = your_custom_dir

For ``pyproject.toml``: repo-standards defines Black, isort, pytest, mypy, bandit, and pydocstyle
settings. Your package metadata and custom tool configs are safe to merge back in.

For ``.pre-commit-config.yaml``: append your custom hooks after the repo-standards hooks.

**Step 4: Test and commit**

.. code-block:: bash

   pip install pre-commit
   pre-commit install
   pre-commit run --all-files
   git add . && git commit -m "chore: adopt repo-standards, merge customizations"

Customization Patterns
-----------------------

repo-standards provides opinionated defaults. Customize locally without losing the ability to re-sync.

**Pattern 1: Extend config files (don't replace)**

Use ``extend-`` prefixes where tools support them:

.. code-block:: ini

   # .flake8 — add project-specific ignores
   [flake8]
   max-line-length = 120
   extend-ignore = E203, W503, YOUR_RULE
   extend-exclude = venv,build,your_dir
   max-complexity = 20

**Pattern 2: Use repo.mk for custom Make targets**

Instead of editing the synced ``Makefile``, create ``repo.mk`` (gitignored):

.. code-block:: bash

   cp repo.mk.example repo.mk
   # Edit repo.mk with your custom targets

The synced Makefile includes ``repo.mk`` automatically via ``-include repo.mk``.

**Pattern 3: Append custom pre-commit hooks**

Add your org-specific hooks at the end of ``.pre-commit-config.yaml``:

.. code-block:: yaml

   # ... repo-standards hooks above ...

   # Your custom hooks:
   - repo: https://github.com/your-org/your-linter
     rev: v1.0.0
     hooks:
       - id: your-custom-check

**Pattern 4: Override workflow inputs**

Reusable workflows accept inputs for customization:

.. code-block:: yaml

   jobs:
     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.12'  # Override the default

**What NOT to customize:**

- Don't remove hooks from ``.pre-commit-config.yaml`` — disable individual rules via config instead
- Don't edit synced ``Makefile`` targets — use ``repo.mk``
- Don't rename or move synced files — ``sync-configs.sh`` expects them at the repo root

Choosing Workflows
-------------------

**Starter workflows** — use these first:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Workflow
     - What it checks
     - When to use
   * - ``reusable-python-ci.yml``
     - Black, isort, Flake8, syntax
     - You have Python code
   * - ``reusable-shell-ci.yml``
     - ShellCheck, syntax
     - You have shell scripts
   * - ``reusable-pre-commit.yml``
     - All pre-commit hooks
     - After installing pre-commit
   * - ``reusable-config-validation.yml``
     - Config files exist and parse
     - After syncing configs

**Advanced workflows** — add after the first week:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Workflow
     - What it checks
     - Key input
   * - ``reusable-quality-checks.yml``
     - Bandit, mypy, pydocstyle, Vulture, mdformat, actionlint
     - ``fail-on-unused``
   * - ``reusable-yaml-ci.yml``
     - yamllint, YAML syntax, workflow validation
     - ``strict``
   * - ``reusable-makefile-ci.yml``
     - checkmake, syntax, tab indentation
     - ``fail-on-warnings``
   * - ``reusable-docker-build.yml``
     - hadolint, multi-platform build test
     - ``platforms``
   * - ``reusable-update-docs.yml``
     - Auto-generates changelog, repo map, architecture, registry
     - ``generate-architecture``

See :doc:`/reference/workflows` for full input documentation.

.. _monorepo-tips:

Monorepo Tips
--------------

- Sync configs once at the repo root (applies to all services)
- Create separate workflow jobs per service with different inputs:

.. code-block:: yaml

   jobs:
     service-a:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'
     service-b:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.12'

Keeping Up to Date
-------------------

Re-sync quarterly or when repo-standards announces updates:

.. code-block:: bash

   # 1. Sync latest configs
   bash scripts/sync-configs.sh

   # 2. Update pre-commit hooks
   pre-commit autoupdate

   # 3. Test locally
   pre-commit run --all-files

   # 4. Fix any new violations and commit
   git add . && git commit -m "chore: sync repo-standards updates"

After syncing, check ``.bak`` files to re-apply any customizations that were overwritten.

Breaking Changes
^^^^^^^^^^^^^^^^^

Reusable workflows are referenced via ``@main``, so workflow changes take effect immediately.
If a workflow change breaks your CI:

1. Pin to a known-good tag: ``@v1.0.0`` instead of ``@main``
2. Open an issue on the repo-standards repository

Troubleshooting
----------------

**"Black would reformat file X" — CI fails**

Run ``black .`` locally, commit the reformatted files. Once done, Black auto-runs on every commit.

**Pre-commit hooks fail on first run**

This is expected for existing codebases. Fix violations reported by each tool:

.. code-block:: bash

   black .                    # Auto-fix Python formatting
   isort .                    # Auto-fix import sorting
   pre-commit run --all-files # Re-check

**sync-configs.sh prompts for confirmation in CI**

Pass ``--yes`` to skip prompts:

.. code-block:: bash

   curl -fsSL .../sync-configs.sh | bash -s -- --yes

**Workflow fails with permission denied**

Add permissions to your workflow:

.. code-block:: yaml

   permissions:
     contents: write     # For auto-commit workflows
     pull-requests: write # For PR-creating workflows

**ShellCheck reports false positives**

Suppress specific rules inline:

.. code-block:: bash

   # shellcheck disable=SC2086
   command $var  # Intentionally unquoted

**Different team members have different config versions**

Have everyone run ``bash scripts/sync-configs.sh`` and commit together.

FAQ
----

**Q: Does repo-standards support languages other than Python?**

It enforces standards for Python, Shell, YAML, Markdown, Dockerfile, GitHub Actions, and Makefile.
For other languages, add your own linters to ``.pre-commit-config.yaml`` and workflow files.

**Q: Can I customize without forking?**

Yes. See the Customization Patterns section above. Fork only if your needs diverge significantly.

**Q: What Python version is required?**

Python 3.11+. All tooling targets this baseline.

**Q: How do I know which version of repo-standards I'm using?**

Check the modification date on synced files, or the ``@main`` / ``@vX.Y.Z`` ref in your workflows.

Next Steps
-----------

- :doc:`/reference/configs` — What each config file does
- :doc:`/reference/workflows` — Full workflow input documentation
- :doc:`/reference/scripts` — Automation script reference
- `CONTRIBUTING.md <https://github.com/zepfu/repo-standards/blob/main/CONTRIBUTING.md>`_ — How to contribute back
