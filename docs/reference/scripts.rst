Scripts Reference
=================

Automation scripts in ``scripts/``.

changelog.py
------------

Generate changelog from git history using conventional commits.

Usage:

.. code-block:: bash

   python3 scripts/changelog.py --output CHANGELOG.md

Options:

- ``--from-git`` - Generate from git history (default)
- ``--since TAG`` - Generate since specific tag
- ``--with-commits`` - Include commit links
- ``--output FILE`` - Output file (default: CHANGELOG.md)

repo_map.py
-----------

Generate repository structure documentation.

Usage:

.. code-block:: bash

   python3 scripts/repo_map.py --output REPO_MAP.md

Options:

- ``--output FILE`` - Output file (default: REPO_MAP.md)
- ``--format FORMAT`` - Output format (markdown, json, tree)
- ``--root PATH`` - Repository root (default: current directory)

generate_architecture.py
-------------------------

Generate architecture diagrams from codebase.

Usage:

.. code-block:: bash

   python3 scripts/generate_architecture.py --all-diagrams

Options:

- ``--output FILE`` - Output file (default: docs/ARCHITECTURE_AUTO.md)
- ``--diagrams TYPES`` - Comma-separated diagram types
- ``--all-diagrams`` - Generate all diagram types
- ``--root PATH`` - Project root (default: current directory)

Diagram types:

- ``flowchart`` - Execution flow
- ``state`` - State machines
- ``sequence`` - API interactions
- ``architecture`` - System overview
- ``er`` - Data models
- ``class`` - OOP structure
- ``journey`` - User flows
- ``mindmap`` - Organization
- ``workflow_pipeline`` - CI/CD pipeline
- ``workflow_triggers`` - Workflow triggers
- ``workflow_jobs`` - Job dependencies

sync-configs.sh
---------------

Sync configuration files from repo-standards.

Usage:

.. code-block:: bash

   bash scripts/sync-configs.sh

What it syncs:

- ``.gitattributes``
- ``.gitignore``
- ``.editorconfig``
- ``.flake8``
- ``.shellcheckrc``
- ``.pre-commit-config.yaml``
- ``.markdownlint.json``
- ``pyproject.toml``
