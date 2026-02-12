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
