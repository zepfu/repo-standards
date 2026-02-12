Quick Setup
===========

Ultra-fast setup for existing projects.

One-Command Setup
-----------------

.. code-block:: bash

   # 1. Sync configs
   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

   # 2. Install pre-commit
   pip install pre-commit && pre-commit install

   # 3. Create CI workflow
   mkdir -p .github/workflows
   cat > .github/workflows/ci.yml << 'EOF'
   ---
   name: CI
   on: [push, pull_request]
   jobs:
     standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'
   EOF

   # 4. Commit
   git add .
   git commit -m "feat: adopt repo standards"
   git push

Done! Standards are now enforced.

Python Project
--------------

.. code-block:: bash

   # Sync configs
   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

   # Install pre-commit
   pip install pre-commit
   pre-commit install

   # Add workflows
   cat > .github/workflows/ci.yml << 'EOF'
   ---
   name: CI
   on: [push, pull_request]
   jobs:
     python-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
     pre-commit:
       uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
   EOF

   # Test
   pre-commit run --all-files

   # Commit
   git add .
   git commit -m "feat: adopt repo standards"

Shell Project
-------------

.. code-block:: bash

   # Sync configs
   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

   # Add workflow
   cat > .github/workflows/ci.yml << 'EOF'
   ---
   name: CI
   on: [push, pull_request]
   jobs:
     shell-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
   EOF

   # Commit
   git add .
   git commit -m "feat: adopt shell standards"

Docker Project
--------------

.. code-block:: bash

   # Sync configs
   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

   # Add workflow
   cat > .github/workflows/ci.yml << 'EOF'
   ---
   name: CI
   on: [push, pull_request]
   jobs:
     docker-build:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
   EOF

   # Commit
   git add .
   git commit -m "feat: add docker build standards"

Multi-Language Project
----------------------

.. code-block:: bash

   # Sync configs
   curl -fsSL https://raw.githubusercontent.com/zepfu/repo-standards/main/scripts/sync-configs.sh | bash

   # Install pre-commit
   pip install pre-commit && pre-commit install

   # Add comprehensive workflow
   cat > .github/workflows/ci.yml << 'EOF'
   ---
   name: CI
   on: [push, pull_request]
   jobs:
     config-validation:
       uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main

     python-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'

     shell-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

     docker-build:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
       needs: [python-standards, shell-standards]
   EOF

   # Commit
   git add .
   git commit -m "feat: comprehensive standards enforcement"

Troubleshooting
---------------

**Pre-commit fails locally**

.. code-block:: bash

   # Update hooks
   pre-commit autoupdate
   pre-commit run --all-files

**CI fails but pre-commit passes**

Check that you're using the same Python version:

.. code-block:: yaml

   python-standards:
     uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
     with:
       python-version: '3.11'  # Match your local version

**Want to skip a check**

Add to ``.pre-commit-config.yaml``:

.. code-block:: yaml

   - repo: https://github.com/psf/black
     hooks:
       - id: black
         exclude: ^legacy/  # Skip legacy code
