Workflow Standards
==================

Standards for GitHub Actions workflows.

Reusable Workflows
------------------

All projects should use centralized reusable workflows from ``repo-standards``.

**Benefits:**
- Update once, everyone benefits
- Consistent behavior
- Zero duplication
- Easy maintenance

Available Workflows
-------------------

Python CI
^^^^^^^^^

.. code-block:: yaml

   # .github/workflows/ci.yml
   jobs:
     python-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'

**What it does:**
- Black formatting check
- isort import sorting check
- Flake8 linting
- Syntax validation

Shell CI
^^^^^^^^

.. code-block:: yaml

   jobs:
     shell-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

**What it does:**
- ShellCheck linting
- Bash syntax validation

Docker Build
^^^^^^^^^^^^

.. code-block:: yaml

   jobs:
     docker-build:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
       with:
         platforms: 'linux/amd64,linux/arm64'

**What it does:**
- Multi-platform Docker builds
- Image inspection

Pre-commit
^^^^^^^^^^

.. code-block:: yaml

   jobs:
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

**What it does:**
- Runs all pre-commit hooks
- Enforces standards

Config Validation
^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   jobs:
     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

**What it does:**
- Validates required config files exist
- Checks content requirements

Architecture Update
^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   jobs:
     update-architecture:
       uses: zepfu/repo-standards/.github/workflows/reusable-update-architecture.yml@main
       with:
         output-path: 'docs/ARCHITECTURE_AUTO.md'
         diagrams: 'all'

**What it does:**
- Generates architecture diagrams
- Creates PR with updates

Complete Example
----------------

.. code-block:: yaml

   ---
   name: CI

   on:
     push:
       branches: [main]
     pull_request:

   permissions:
     contents: read

   jobs:
     # Validate configs
     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     # Python standards
     python-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'

     # Shell standards
     shell-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

     # Pre-commit checks
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main

     # Docker build
     docker-build:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
       needs: [python-standards, shell-standards]

Best Practices
--------------

Versioning
^^^^^^^^^^

Use ``@main`` for automatic updates:

.. code-block:: yaml

   uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

Or pin to specific version:

.. code-block:: yaml

   uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@v1.0.0

Dependencies
^^^^^^^^^^^^

Use ``needs:`` to control order:

.. code-block:: yaml

   jobs:
     test:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

     build:
       needs: test  # Run after test passes
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main

Permissions
^^^^^^^^^^^

Grant minimal permissions:

.. code-block:: yaml

   on: [push, pull_request]

   permissions:
     contents: read  # Minimal for CI

   jobs:
     test:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

Triggers
^^^^^^^^

Be specific with triggers:

.. code-block:: yaml

   on:
     push:
       branches: [main]
       paths:
         - 'src/**'
         - 'tests/**'
     pull_request:
       branches: [main]

Common Patterns
---------------

Multi-Language Project
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   jobs:
     python:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

     shell:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

     docker:
       needs: [python, shell]
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main

Monorepo
^^^^^^^^

.. code-block:: yaml

   jobs:
     service-a:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       # Add path filters in 'on:' section

     service-b:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main

See Also
--------

- :doc:`/reference/workflows` - Workflow reference
- :doc:`/guides/getting-started` - Setup guide
