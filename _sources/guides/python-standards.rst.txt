Python Standards
================

Code quality standards for Python projects.

Overview
--------

All Python code must follow these standards:

- Python 3.11+ required (organization standard)
- Black formatting (100 char lines)
- isort import sorting (Black-compatible)
- Flake8 linting (max complexity 20)

Formatting with Black
---------------------

Configuration
^^^^^^^^^^^^^

``.pyproject.toml``:

.. code-block:: toml

   [tool.black]
   line-length = 100
   target-version = ['py311']

Usage
^^^^^

.. code-block:: bash

   # Format files
   black scripts/*.py

   # Check only
   black --check scripts/*.py

Import Sorting with isort
--------------------------

Configuration
^^^^^^^^^^^^^

``pyproject.toml``:

.. code-block:: toml

   [tool.isort]
   profile = "black"
   line_length = 100

Usage
^^^^^

.. code-block:: bash

   # Sort imports
   isort scripts/*.py

   # Check only
   isort --check scripts/*.py

Linting with Flake8
-------------------

Configuration
^^^^^^^^^^^^^

``.flake8``:

.. code-block:: ini

   [flake8]
   max-line-length = 120
   extend-ignore = E203, W503
   max-complexity = 20

Usage
^^^^^

.. code-block:: bash

   # Lint files
   flake8 scripts/*.py

Common Rules
^^^^^^^^^^^^

- **E203**: Whitespace before ':' (Black compatibility)
- **W503**: Line break before binary operator (Black compatibility)
- **Complexity**: Functions should be under 20 complexity

Style Guidelines
----------------

Docstrings
^^^^^^^^^^

Use triple quotes for all docstrings:

.. code-block:: python

   def process_data(input_path: str, output_path: str) -> None:
       """
       Process data from input file and write to output.

       Args:
           input_path: Path to input file
           output_path: Path to output file

       Raises:
           FileNotFoundError: If input file doesn't exist
       """
       pass

Type Hints
^^^^^^^^^^

Use type hints for function signatures:

.. code-block:: python

   from pathlib import Path
   from typing import List, Optional

   def read_files(paths: List[Path]) -> Optional[str]:
       """Read content from multiple files."""
       pass

Imports
^^^^^^^

Order imports by:

1. Standard library
2. Third-party packages
3. Local modules

.. code-block:: python

   # Standard library
   import os
   import sys
   from pathlib import Path

   # Third-party
   import numpy as np
   import yaml

   # Local
   from .utils import helper_function

Line Length
^^^^^^^^^^^

- Maximum 100 characters (Black default)
- Break long lines naturally
- Use parentheses for grouping

.. code-block:: python

   # Good
   result = some_function(
       first_argument,
       second_argument,
       third_argument,
   )

   # Bad - too long
   result = some_function(first_argument, second_argument, third_argument, fourth_argument)

Enforcement
-----------

Pre-commit Hooks
^^^^^^^^^^^^^^^^

Standards are enforced via pre-commit:

.. code-block:: yaml

   # .pre-commit-config.yaml
   - repo: https://github.com/psf/black
     rev: 24.1.1
     hooks:
       - id: black
         args: ['--line-length=100']

   - repo: https://github.com/pycqa/isort
     rev: 5.13.2
     hooks:
       - id: isort
         args: ['--profile=black']

   - repo: https://github.com/pycqa/flake8
     rev: 7.0.0
     hooks:
       - id: flake8

GitHub Actions
^^^^^^^^^^^^^^

CI enforces standards on every push:

.. code-block:: yaml

   # .github/workflows/ci.yml
   jobs:
     python-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
       with:
         python-version: '3.11'

Best Practices
--------------

Project Structure
^^^^^^^^^^^^^^^^^

.. code-block:: text

   project/
   ├── src/
   │   └── package/
   │       ├── __init__.py
   │       ├── module.py
   │       └── utils.py
   ├── scripts/
   │   └── automation.py
   ├── tests/
   │   └── test_module.py
   ├── pyproject.toml
   └── README.md

Testing
^^^^^^^

Use pytest for testing:

.. code-block:: python

   # tests/test_module.py
   import pytest
   from package.module import process_data

   def test_process_data():
       """Test data processing."""
       result = process_data("input.txt", "output.txt")
       assert result is not None

Virtual Environments
^^^^^^^^^^^^^^^^^^^^

Always use virtual environments:

.. code-block:: bash

   # Create
   python3 -m venv .venv

   # Activate
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows

   # Install
   pip install -r requirements.txt

Common Issues
-------------

**Black and Flake8 conflict**

Add to ``.flake8``:

.. code-block:: ini

   extend-ignore = E203, W503

**Import order wrong**

Run isort:

.. code-block:: bash

   isort --profile=black .

**Line too long**

Black will auto-format, but for strings:

.. code-block:: python

   # Use implicit string concatenation
   message = (
       "This is a very long message that "
       "needs to be split across multiple lines"
   )

See Also
--------

- :doc:`/reference/configs` - Configuration file reference
- :doc:`/guides/quick-setup` - Quick project setup
