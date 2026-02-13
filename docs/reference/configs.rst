Configuration Files
===================

Standard configuration files synced via ``sync-configs.sh``.

.gitattributes
--------------

Line ending rules.

Key settings:

- ``* text=auto`` - Auto-detect text files
- ``*.sh text eol=lf`` - Force LF for shell scripts
- ``*.py text eol=lf`` - Force LF for Python files

.gitignore
----------

Ignore patterns for Python, IDE, OS files.

.editorconfig
-------------

Editor consistency settings.

- UTF-8 encoding
- LF line endings
- 4 spaces for Python
- 2 spaces for YAML

.flake8
-------

Python linting configuration.

- Max line length: 120
- Max complexity: 20
- Ignores: E203, W503 (Black compatibility)

.shellcheckrc
-------------

Shell linting configuration.

- Shell: bash
- Disabled: SC2250 (${var} vs $var style)

.pre-commit-config.yaml
-----------------------

Pre-commit hooks configuration.

Includes:

- trailing-whitespace
- end-of-file-fixer
- check-yaml
- shellcheck
- black
- isort
- flake8
- yamllint

pyproject.toml
--------------

Python project configuration.

Includes settings for:

- Black (line-length: 100)
- isort (profile: black)
- pytest (testpaths, addopts)
- mypy (python_version: 3.11, strict optional)
- pydocstyle (Google convention)
- bandit (skips: B101, B404, B603)

.readthedocs.yml
-----------------

Read the Docs build configuration.

Key settings:

- Sphinx configuration: ``docs/conf.py``
- Python version: 3.11
- Build OS: ubuntu-22.04
- Dependencies: ``docs/requirements.txt``

.markdownlint.json
-------------------

Markdown linting configuration for markdownlint.

Key settings:

- Line length: 120 characters (headings and code blocks)
- Tables: unlimited line length
- MD024 (duplicate headings): allowed within siblings
- MD033 (inline HTML): disabled
- MD041 (first line heading): disabled

Makefile
--------

Standard Makefile with common development targets.

Available targets:

- ``make help`` - Display all available targets
- ``make all`` - Build all generated assets
- ``make test`` - Run tests
- ``make docs`` - Generate auto-documentation (changelog, repo map, architecture, workflow registry)
- ``make sphinx`` - Build and serve Sphinx documentation locally
- ``make mermaid`` / ``mermaid-png`` / ``mermaid-pdf`` - Render Mermaid diagrams
- ``make mermaid-check`` - Validate mermaid-cli installation
- ``make sync-configs`` - Sync config files from repo-standards
- ``make archive`` - Create tar.gz archive for AI context
- ``make clean`` - Remove backup files, logs, and cache directories

Uses ``-include repo.mk`` to load optional repository-specific targets.

repo.mk.example
-----------------

Example template for ``repo.mk``, an optional gitignored file for repository-specific Makefile extensions.

- Allows adding custom targets without modifying the main Makefile
- Convention: define ``help-repo`` target to extend help output
- Pattern: ``.PHONY`` declarations, custom targets with ``##`` help comments

Copy to ``repo.mk`` and customize:

.. code-block:: bash

   cp repo.mk.example repo.mk

.checkmake
----------

Configuration for checkmake (Makefile linting tool).

Key settings:

- Max body length: 15 lines (default 5 is too strict for multi-step targets)
- Minimum phony: enabled (requires ``all`` and ``test`` targets)

.checkmake-mk
--------------

Alternative checkmake configuration for ``.mk`` include fragments.

Key differences from ``.checkmake``:

- Same max body length (15 lines)
- Minimum phony: disabled (``.mk`` fragments don't need ``all``/``clean``/``test`` targets)
