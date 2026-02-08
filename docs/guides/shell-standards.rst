Shell Standards
===============

Code quality standards for shell scripts.

Overview
--------

All shell scripts must:

- Use ``#!/usr/bin/env bash`` shebang
- Pass ShellCheck (error level)
- Use ``set -euo pipefail``
- Have proper quoting

ShellCheck
----------

Configuration
^^^^^^^^^^^^^

``.shellcheckrc``:

.. code-block:: bash

   # ShellCheck configuration
   disable=SC2250  # Prefer ${var} over $var (style preference)
   enable=quote-safe-variables
   shell=bash
   external-sources=true

Usage
^^^^^

.. code-block:: bash

   # Check script
   shellcheck scripts/automation.sh

   # Check all scripts
   find . -name "*.sh" -exec shellcheck {} \;

Common Rules
^^^^^^^^^^^^

- **SC2086**: Quote variables to prevent word splitting
- **SC2046**: Quote command substitutions
- **SC2004**: Don't use $ on arithmetic variables
- **SC2250**: Prefer ${var} over $var (can be disabled)

Script Template
---------------

Standard Template
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   #!/usr/bin/env bash
   # script-name.sh - Brief description
   #
   # Longer description if needed.
   #
   # Usage:
   #   bash script-name.sh [options]
   #
   # Options:
   #   -h, --help     Show this help message
   #   -v, --verbose  Enable verbose output

   set -euo pipefail

   # Script directory
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

   # Constants
   readonly SCRIPT_NAME="$(basename "$0")"
   readonly DEFAULT_CONFIG="config.yml"

   # Functions
   log() {
       echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
   }

   die() {
       log "ERROR: $*"
       exit 1
   }

   usage() {
       cat << EOF
   Usage: $SCRIPT_NAME [options]

   Description of script.

   Options:
       -h, --help      Show this help
       -v, --verbose   Verbose output
   EOF
   }

   # Main function
   main() {
       local verbose=false

       # Parse arguments
       while [[ $# -gt 0 ]]; do
           case $1 in
               -h|--help)
                   usage
                   exit 0
                   ;;
               -v|--verbose)
                   verbose=true
                   shift
                   ;;
               *)
                   die "Unknown option: $1"
                   ;;
           esac
       done

       # Script logic here
       log "Starting..."
   }

   # Run main
   main "$@"

Style Guidelines
----------------

Quoting
^^^^^^^

Always quote variables:

.. code-block:: bash

   # Good
   echo "$variable"
   cp "$source" "$destination"

   # Bad - word splitting
   echo $variable
   cp $source $destination

Arrays
^^^^^^

.. code-block:: bash

   # Define array
   files=("file1.txt" "file2.txt" "file3.txt")

   # Iterate
   for file in "${files[@]}"; do
       echo "$file"
   done

   # Check length
   if [[ ${#files[@]} -gt 0 ]]; then
       echo "Has files"
   fi

Conditionals
^^^^^^^^^^^^

Use ``[[ ]]`` for tests:

.. code-block:: bash

   # Good
   if [[ -f "$file" ]]; then
       echo "File exists"
   fi

   if [[ "$var" == "value" ]]; then
       echo "Match"
   fi

   # Bad - use [[ ]] instead
   if [ -f $file ]; then
       echo "File exists"
   fi

Functions
^^^^^^^^^

.. code-block:: bash

   # Define function
   process_file() {
       local input_file="$1"
       local output_file="$2"

       if [[ ! -f "$input_file" ]]; then
           echo "Input file not found" >&2
           return 1
       fi

       # Process file
       cp "$input_file" "$output_file"
   }

   # Call function
   process_file "input.txt" "output.txt"

Error Handling
^^^^^^^^^^^^^^

.. code-block:: bash

   # Exit on error
   set -e

   # Exit on undefined variable
   set -u

   # Exit on pipe failure
   set -o pipefail

   # Combined
   set -euo pipefail

   # Trap errors
   trap 'echo "Error on line $LINENO"' ERR

Common Patterns
---------------

Check if command exists
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   if command -v python3 >/dev/null 2>&1; then
       echo "Python 3 found"
   else
       echo "Python 3 not found" >&2
       exit 1
   fi

Read file line by line
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   while IFS= read -r line; do
       echo "Line: $line"
   done < "$file"

Iterate over files
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Using find
   find . -name "*.txt" -print0 | while IFS= read -r -d '' file; do
       echo "Processing: $file"
   done

   # Using glob
   shopt -s nullglob
   for file in *.txt; do
       echo "Processing: $file"
   done

Enforcement
-----------

Pre-commit
^^^^^^^^^^

.. code-block:: yaml

   # .pre-commit-config.yaml
   - repo: https://github.com/shellcheck-py/shellcheck-py
     hooks:
       - id: shellcheck
         args: ['-x', '--severity=error']

GitHub Actions
^^^^^^^^^^^^^^

.. code-block:: yaml

   # .github/workflows/ci.yml
   jobs:
     shell-standards:
       uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main

Best Practices
--------------

Portability
^^^^^^^^^^^

- Use ``#!/usr/bin/env bash`` not ``#!/bin/bash``
- Avoid bashisms if targeting sh
- Test on multiple systems

Security
^^^^^^^^

- Quote all variables
- Validate input
- Use ``readonly`` for constants
- Avoid eval

Performance
^^^^^^^^^^^

- Use built-ins over external commands
- Avoid subshells when possible
- Use ``[[`` over ``[``

Documentation
^^^^^^^^^^^^^

- Add header with description
- Document all functions
- Show usage examples
- List dependencies

Common Issues
-------------

**Word splitting**

.. code-block:: bash

   # Wrong
   files=$( ls *.txt )
   rm $files  # Word splitting!

   # Right
   files=( *.txt )
   rm "${files[@]}"

**Useless use of cat**

.. code-block:: bash

   # Wrong
   cat file.txt | grep pattern

   # Right
   grep pattern file.txt

**Command substitution**

.. code-block:: bash

   # Prefer $() over backticks
   result=$(command)  # Good
   result=`command`   # Old style

See Also
--------

- `ShellCheck Wiki <https://www.shellcheck.net/wiki/>`_
- :doc:`/reference/configs`
