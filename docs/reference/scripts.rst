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

generate_workflow_registry.py
------------------------------

Generate workflow registry and tool coverage matrix from reusable workflows and pre-commit config.

Usage:

.. code-block:: bash

   python3 scripts/generate_workflow_registry.py
   python3 scripts/generate_workflow_registry.py --output docs/auto/WORKFLOW_REGISTRY.md
   python3 scripts/generate_workflow_registry.py --root /path/to/repo-standards

Options:

- ``--output FILE`` - Output file (default: docs/auto/WORKFLOW_REGISTRY.md)
- ``--root PATH`` - Repository root (default: current directory)

Output sections:

- **Workflow Registry** - Structured details for each reusable workflow (description, inputs, tools, scope, severity, config files)
- **Tool Coverage Matrix** - Table showing every linting/quality tool and which workflows/pre-commit runs it
- **Recommended Adoption Profiles** - Suggested workflow combinations for common project types
- **Workflow Version Notes** - Tracks default versions for key inputs across workflows

render-mermaid.sh
-----------------

Extract and render Mermaid diagrams from markdown files to image files.

Usage:

.. code-block:: bash

   bash scripts/render-mermaid.sh
   bash scripts/render-mermaid.sh --format png --output-dir images/

Options:

- ``--format FORMAT`` - Output format: ``svg``, ``png``, or ``pdf`` (default: ``svg``)
- ``--output-dir DIR`` - Output directory (default: ``{markdown-dir}/mermaid-images/``)
- ``--help`` - Show help message

Requires ``mmdc`` (mermaid-cli). Install with:

.. code-block:: bash

   npm install -g @mermaid-js/mermaid-cli

archive.sh
-----------

Create a compressed archive of the repository for AI context or backup.

Usage:

.. code-block:: bash

   bash scripts/archive.sh

Behavior:

- Cleans temporary files (``.bak``, ``.backup``, ``~``, ``Zone.Identifier``)
- Creates ``archive/`` directory if missing
- Produces ``{repo-name}_{timestamp}.tar.gz`` in ``archive/``
- Excludes: ``*.pyc``, ``__pycache__``, ``.pytest_cache``, ``venv``, ``.git``, ``dist``, ``build``, IDE directories

sync-configs.sh
---------------

Sync configuration files from repo-standards to a consumer repository.

Usage:

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

Options:

- ``--yes`` - Skip confirmation prompt
- ``--branch BRANCH`` - Use specific branch (default: ``main``)

What it syncs:

- ``.gitattributes``
- ``.gitignore``
- ``.editorconfig``
- ``.flake8``
- ``.shellcheckrc``
- ``.pre-commit-config.yaml``
- ``.readthedocs.yml``
- ``.markdownlint.json``
- ``pyproject.toml``
- ``Makefile``
- ``repo.mk.example``
- ``.checkmake``
- ``.checkmake-mk``

Existing files are backed up with ``.bak`` extension before overwriting.
