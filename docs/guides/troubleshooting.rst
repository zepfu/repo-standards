Troubleshooting
===============

Common issues and solutions when using ``repo-standards`` workflows, configs,
and pre-commit hooks.

.. contents:: On This Page
   :local:
   :depth: 2

Pre-commit Hook Failures
------------------------

Hook fails with "files were modified by this hook"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** A pre-commit hook (usually Black, isort, or mdformat) modifies
files during commit, causing the hook to fail.

**Solution:** Re-stage the modified files and commit again::

   git add -u
   git commit -m "your message"

This is expected behavior -- formatters fix files on the first run, then pass
on the second run.

"Your pre-commit configuration is unstaged"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** You modified ``.pre-commit-config.yaml`` but are trying to commit
other files without staging it.

**Solution:** Either stage the config change or stash it::

   # Option 1: Stage everything
   git add .pre-commit-config.yaml
   git commit

   # Option 2: Stash the config change
   git stash push .pre-commit-config.yaml
   git commit
   git stash pop

actionlint fails in CI but passes locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** The actionlint pre-commit hook passes locally but fails in CI with
shellcheck errors like SC2129 or SC2016.

**Cause:** Locally, ``shellcheck`` is not in your system PATH (it's installed
in pre-commit's virtual environment). actionlint silently skips shellcheck
integration when it can't find the binary. In CI, GitHub Actions runners have
shellcheck pre-installed, so actionlint runs shellcheck checks on workflow
``run:`` blocks.

Additionally, actionlint passes ``--norc`` to shellcheck, so ``.shellcheckrc``
is never read by actionlint's shellcheck.

**Solution:** Use ``-ignore`` args in ``.pre-commit-config.yaml``::

   - repo: https://github.com/rhysd/actionlint
     rev: v1.7.10
     hooks:
       - id: actionlint
         args:
           - -ignore
           - 'SC2129:'
           - -ignore
           - 'SC2016:'

Or create ``.github/actionlint.yaml``::

   ignore:
     - 'SC2129:'
     - 'SC2016:'

mdformat reformats files unexpectedly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** mdformat changes markdown files during pre-commit, breaking
your intended formatting.

**Solution:** mdformat enforces consistent markdown formatting. If specific
files should be excluded, add them to ``.mdformatignore`` in your repo root::

   # Skip auto-generated files
   docs/auto/*.md
   CHANGELOG.md

sync-configs.sh Issues
----------------------

"Permission denied" when running sync-configs.sh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution:** Make the script executable::

   chmod +x scripts/sync-configs.sh
   # Or run with bash directly:
   bash scripts/sync-configs.sh

Configs overwrite my customizations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** Running ``sync-configs.sh`` replaces your project-specific
config customizations.

**Solution:** ``sync-configs.sh`` intentionally overwrites configs to keep
repos in sync. To preserve customizations:

1. **For pyproject.toml:** Add project-specific settings in a separate section.
   The synced file provides tool defaults; your additions won't be overwritten
   if they're in different sections.

2. **For .flake8, .shellcheckrc:** Add project-specific overrides after the
   synced content. Re-run sync and re-add your overrides.

3. **For .pre-commit-config.yaml:** Add custom hooks after the synced hooks.

Sparse-checkout fails or times out
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** ``sync-configs.sh`` hangs or fails during the git clone step.

**Solution:** Check your network connection and GitHub access::

   # Test access
   git ls-remote https://github.com/zepfu/repo-standards.git

   # Use a specific branch
   bash scripts/sync-configs.sh --branch main

CI Workflow Issues
------------------

Workflow not triggering
^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** Push or PR doesn't trigger the expected workflow.

**Causes:**

1. **Path filters:** Most workflows only trigger on specific file types.
   Check the ``paths:`` filter in the workflow definition.
2. **Branch filters:** Workflows trigger on ``main`` and ``master`` branches
   for push events. PRs trigger on all branches.
3. **[skip ci]:** Commits with ``[skip ci]`` in the message skip all workflows.

**Solution:** Use ``workflow_dispatch`` to trigger manually::

   gh workflow run "reusable-pre-commit.yml" --ref main

"Permission denied" errors in workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** Workflow fails with permission errors when trying to push commits
or deploy to GitHub Pages.

**Solution:** Ensure your workflow has the required permissions::

   permissions:
     contents: write   # For committing auto-docs
     pages: write      # For GitHub Pages deployment
     id-token: write   # For OIDC token

Also check that your repository settings allow GitHub Actions to create commits:
Settings > Actions > General > Workflow permissions > "Read and write permissions."

Reusable workflow version pinning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** Workflows break after an update to ``repo-standards``.

**Cause:** Using ``@main`` means you always get the latest version. Breaking
changes to workflows affect all consumer repos immediately.

**Solution:** Pin to a specific tag for stability::

   # Pinned to a release (recommended for production)
   uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@v1.0.1

   # Always latest (recommended for active development)
   uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

Python CI Issues
----------------

"Python version must be 3.11 or higher"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** Python CI workflow fails immediately with a version check error.

**Solution:** Set the correct Python version::

   python:
     uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
     with:
       python-version: '3.13'

The minimum supported version is 3.11.

Black/isort formatting conflicts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** Black and isort produce conflicting changes.

**Solution:** This shouldn't happen with the synced ``pyproject.toml`` config,
which sets compatible options for both tools. If you see conflicts, ensure
your ``pyproject.toml`` includes::

   [tool.isort]
   profile = "black"

Docker Build Issues
-------------------

hadolint warnings on Dockerfile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** hadolint reports warnings or errors on your Dockerfile.

**Solution:** Review the `hadolint rules <https://github.com/hadolint/hadolint#rules>`_
and either fix the issue or add an inline ignore::

   # hadolint ignore=DL3008
   RUN apt-get update && apt-get install -y --no-install-recommends curl

Plugin Compatibility
--------------------

mdformat 1.0.0 and mdformat-gfm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom:** ``pip install mdformat mdformat-gfm`` fails with a dependency
resolution error.

**Cause:** ``mdformat-gfm`` requires ``mdformat<0.8.0``, which is incompatible
with mdformat 1.0.0.

**Solution:** Keep mdformat at 0.7.x until mdformat-gfm releases a compatible
version::

   pip install 'mdformat<0.8.0' mdformat-gfm

The ``.pre-commit-config.yaml`` from ``repo-standards`` already pins to a
compatible version.

Getting Help
------------

If your issue isn't covered here:

1. Check the `GitHub Issues <https://github.com/zepfu/repo-standards/issues>`_
   for known problems
2. Open a new issue with:

   - Which workflow/config/script is failing
   - The full error output
   - Your OS and tool versions
3. See :doc:`../reference/workflows` for detailed workflow documentation
