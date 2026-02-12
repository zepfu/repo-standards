# Messaging Standards

Standards for consistent output messaging across all code in this repository: GitHub Actions workflows, shell scripts,
and Python scripts.

Every piece of automation that produces user-facing output should follow these conventions so that logs, summaries, and
terminal output are predictable and scannable regardless of which tool generated them.

______________________________________________________________________

## General Principles

These apply everywhere -- workflows, shell, and Python alike.

- No emoji. No unicode symbols. No ANSI colour codes in persisted output.
- Use plain ASCII status prefixes (see below).
- Keep messages terse. One line per status item.
- Name the tool or check that produced the result.
- When a fix command exists, include it.
- Separate concerns: structured summaries go to summary channels (step summary, report files); raw detail goes to
  stdout/stderr for debugging.

## Status Prefixes

Every status line uses one of four prefixes.

| Prefix   | Meaning            | When to use                                           |
| -------- | ------------------ | ----------------------------------------------------- |
| `[PASS]` | Check succeeded    | A tool ran and found no issues                        |
| `[FAIL]` | Check failed       | A tool ran and found blocking issues                  |
| `[WARN]` | Non-blocking issue | Something worth noting that should not fail the run   |
| `[SKIP]` | Check was not run  | Precondition not met (no files, missing config, etc.) |

These prefixes are used identically across all three contexts (workflows, shell, Python). The surrounding formatting
differs by context as described in the sections below.

______________________________________________________________________

## GitHub Actions Workflows

### Step Summary Structure

Every workflow writes to `$GITHUB_STEP_SUMMARY`. The structure is:

```markdown
## Workflow Title

- [PASS] Tool A: description
- [FAIL] Tool B: description
- [SKIP] Tool C: no files found -- skipping check

---
**Workflow title complete**
```

Rules:

- One H2 heading per workflow, matching the workflow's purpose (not its filename).
- H3 sub-headings are acceptable when a single workflow runs multiple distinct analysis categories (e.g. quality checks
  with Vulture, Autoflake, Eradicate).
- Each tool or check gets one status line prefixed with `[PASS]`, `[FAIL]`, `[WARN]`, or `[SKIP]`.
- A horizontal rule (`---`) followed by a bold closing line marks the end.
- If a tool produces detailed output (lint errors, diff, etc.), wrap it in a fenced code block above the status line.

### Message Templates

File detection (skip):

```bash
echo "- [SKIP] No Python files found -- skipping linting" >> $GITHUB_STEP_SUMMARY
```

Use a double dash (`--`) rather than an em dash or parenthetical to separate the skip reason. Name the file type and the
tool or check being skipped.

Tool passed:

```bash
echo "- [PASS] ShellCheck: all checks passed" >> $GITHUB_STEP_SUMMARY
```

Format: `[PASS] ToolName: brief description`.

Tool failed:

```bash
echo "- [FAIL] Flake8: linting issues found" >> $GITHUB_STEP_SUMMARY
```

When a fix command is available, add it on the next line:

```bash
echo "- [FAIL] Black: formatting issues found" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "Run \`black --line-length=100 .\` to fix" >> $GITHUB_STEP_SUMMARY
```

Non-blocking warning:

```bash
echo "- [WARN] .gitignore: recommended patterns missing (non-blocking):" >> $GITHUB_STEP_SUMMARY
printf '    - \`%s\`\n' "${MISSING[@]}" >> $GITHUB_STEP_SUMMARY
```

Always include `(non-blocking)` so it is clear the build will not fail.

Closing line:

```bash
echo "" >> $GITHUB_STEP_SUMMARY
echo "---" >> $GITHUB_STEP_SUMMARY
echo "**Python linting complete**" >> $GITHUB_STEP_SUMMARY
```

The closing line should be bold and state what finished. It does not repeat pass/fail status since that is already
visible above.

### Console Log Output

Console log output during step execution should be plain and terse:

```
Checking: scripts/sync-configs.sh
Checking: scripts/changelog.py
```

Do not duplicate the full summary format into stdout. The summary is for the GitHub UI; stdout is for debugging.

### Input Defaults

When a workflow supports both `workflow_call` and direct `push`/`pull_request` triggers, input values will be empty
strings on direct triggers (not the defaults defined under `workflow_call.inputs`). Every step that reads an input must
apply a fallback:

```bash
SEVERITY="${{ inputs.severity }}"
[ -z "$SEVERITY" ] && SEVERITY="error"
```

This pattern must be used for all inputs in all workflows. Never rely on `${{ inputs.x }}` producing the default value
on push/PR triggers.

### Avoiding Docker for Lint Tools

Prefer runner-native tool installation over Docker images for linting:

```bash
# Preferred
pip install black isort flake8

# Avoid
docker pull cytopia/black:latest
docker run --rm -v "$(pwd)":/src cytopia/black:latest ...
```

Reasons: eliminates registry authentication failures, avoids image pull latency, reduces workflow complexity, and
GitHub-hosted runners already include Python, Go, and common build tools.

Exceptions: Docker build/test workflows (`reusable-docker-build.yml`) and any workflow whose explicit purpose is to
validate Docker images.

### Naming Conventions

Step names use consistent verb patterns:

| Pattern                  | Example                  |
| ------------------------ | ------------------------ |
| `Check for [type] files` | Check for Python files   |
| `Run [tool]`             | Run ShellCheck           |
| `Validate [thing]`       | Validate Makefile syntax |
| `Install [tool]`         | Install linting tools    |
| `Summary`                | Summary                  |

Job names should be short and descriptive. Append `(Advisory)` when a job produces informational output that never fails
the build:

```yaml
detect-unused-shell:
  name: Detect Unused Shell Functions (Advisory)
```

______________________________________________________________________

## Shell Scripts

### Output Functions

Every shell script that produces user-facing output should define a standard set of logging functions. These print to
stderr so they do not interfere with stdout-based data pipelines.

```bash
log_pass() { echo "[PASS] $*" >&2; }
log_fail() { echo "[FAIL] $*" >&2; }
log_warn() { echo "[WARN] $*" >&2; }
log_skip() { echo "[SKIP] $*" >&2; }
log_info() { echo "[INFO] $*" >&2; }
```

`[INFO]` is available for shell scripts as a neutral progress indicator (e.g. "Cloning repository...", "Installing
dependencies..."). It is not a status prefix and should not appear in final pass/fail result lines.

### Progress vs Results

Separate progress messages from result messages. Progress uses `[INFO]`; results use `[PASS]`, `[FAIL]`, `[WARN]`, or
`[SKIP]`.

```bash
log_info "Syncing config files from repo-standards..."

# ... work happens ...

log_pass "Synced: .editorconfig"
log_pass "Synced: .flake8"
log_warn "File not found in repo-standards: .shellcheckrc"
```

### Summary Blocks

For scripts that perform multiple operations, print a summary block at the end:

```bash
echo ""
echo "=========================================="
echo "Sync complete"
echo "  Passed:  $PASS_COUNT"
echo "  Failed:  $FAIL_COUNT"
echo "  Skipped: $SKIP_COUNT"
echo "=========================================="
```

Use a simple box made of `=` characters. No emoji or unicode box-drawing characters. Keep the content aligned and
machine-parseable.

### Error Handling

Fatal errors should use `log_fail` and exit non-zero:

```bash
log_fail "Required file not found: $FILE"
exit 1
```

Non-fatal issues use `log_warn` and continue execution.

### Colour

ANSI colour codes are acceptable for interactive terminal output only. They must be gated behind a TTY check or a
`--color` flag so that piped or captured output remains clean:

```bash
if [ -t 2 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  NC='\033[0m'
else
  RED=''
  GREEN=''
  YELLOW=''
  NC=''
fi

log_pass() { echo -e "${GREEN}[PASS]${NC} $*" >&2; }
log_fail() { echo -e "${RED}[FAIL]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_skip() { echo "[SKIP] $*" >&2; }
log_info() { echo "[INFO] $*" >&2; }
```

When running in CI (GitHub Actions), colour is typically not needed since output is rendered in the Actions log viewer.
The TTY check handles this automatically.

______________________________________________________________________

## Python Scripts

### Logging Setup

Python scripts should use the standard `logging` module configured to match the same prefix convention:

```python
import logging
import sys

LOG_FORMAT = "[%(levelname)s] %(message)s"

LEVEL_NAMES = {
    logging.DEBUG: "INFO",
    logging.INFO: "INFO",
    logging.WARNING: "WARN",
    logging.ERROR: "FAIL",
    logging.CRITICAL: "FAIL",
}


class PrefixFormatter(logging.Formatter):
    """Format log records using standard status prefixes."""

    def format(self, record):
        record.levelname = LEVEL_NAMES.get(record.levelno, record.levelname)
        return super().format(record)


def setup_logging(verbose=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(PrefixFormatter(LOG_FORMAT))
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, handlers=[handler])
```

Usage:

```python
import logging

log = logging.getLogger(__name__)

log.info("Scanning %d Python files...", file_count)
log.warning("Could not parse %s", filepath)
log.error("No commits found")
```

Output:

```
[INFO] Scanning 14 Python files...
[WARN] Could not parse scripts/broken.py
[FAIL] No commits found
```

### Result Reporting

For scripts that produce structured results (changelogs, repo maps, architecture docs), use dedicated result functions
rather than logging:

```python
def report_pass(msg: str) -> None:
    print(f"[PASS] {msg}", file=sys.stderr)

def report_fail(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)

def report_warn(msg: str) -> None:
    print(f"[WARN] {msg}", file=sys.stderr)

def report_skip(msg: str) -> None:
    print(f"[SKIP] {msg}", file=sys.stderr)
```

This keeps result lines visually identical to shell output and workflow summaries.

### Summary Output

Python scripts that perform multiple checks should print a summary block that mirrors the shell convention:

```python
print("", file=sys.stderr)
print("==========================================", file=sys.stderr)
print("Generation complete", file=sys.stderr)
print(f"  Generated: {output_path}", file=sys.stderr)
print(f"  Modules:   {module_count}", file=sys.stderr)
print(f"  Diagrams:  {diagram_count}", file=sys.stderr)
print("==========================================", file=sys.stderr)
```

### Exit Codes

| Code | Meaning                                                          |
| ---- | ---------------------------------------------------------------- |
| `0`  | All checks passed or generation succeeded                        |
| `1`  | Blocking failure (missing input, generation error, check failed) |
| `2`  | Usage error (bad arguments, missing required flags)              |

______________________________________________________________________

## Quick Reference

Summary of how the same status looks in each context:

| Context          | Pass                                      | Fail                                      |
| ---------------- | ----------------------------------------- | ----------------------------------------- |
| Workflow summary | `- [PASS] Black: formatting check passed` | `- [FAIL] Black: formatting issues found` |
| Shell script     | `[PASS] Synced: .editorconfig`            | `[FAIL] Required file not found: .flake8` |
| Python script    | `[PASS] Generated: CHANGELOG.md`          | `[FAIL] No commits found`                 |

The prefix is always the same. The surrounding formatting adapts to the context.

______________________________________________________________________

## Checklists

### New Workflow Checklist

1. Add input defaults fallback for every input (`[ -z "$VAR" ] && VAR="default"`).
1. Write `$GITHUB_STEP_SUMMARY` with H2 title, per-tool status lines, and a bold closing line separated by `---`.
1. Use `[PASS]` / `[FAIL]` / `[WARN]` / `[SKIP]` prefixes on every status line.
1. Handle the "no files found" case with a `[SKIP]` message.
1. Install tools via pip or the runner's package manager, not Docker (unless Docker is the subject of the workflow).
1. Include a fix command in `[FAIL]` messages when one exists.
1. Keep console log output plain and terse.
1. No emoji anywhere.

### New Shell Script Checklist

1. Define `log_pass`, `log_fail`, `log_warn`, `log_skip`, `log_info` functions.
1. Gate ANSI colour behind a TTY check.
1. Log to stderr; reserve stdout for data output.
1. Print a summary block at the end for multi-step operations.
1. Use `[INFO]` for progress, status prefixes for results.
1. Exit `1` on failure, `0` on success.
1. No emoji anywhere.

### New Python Script Checklist

1. Use the `PrefixFormatter` logging setup or equivalent.
1. Log to stderr; reserve stdout for data output.
1. Use `report_pass` / `report_fail` / `report_warn` / `report_skip` for result lines.
1. Print a summary block at the end for multi-step operations.
1. Return exit code `0` on success, `1` on failure, `2` on usage error.
1. No emoji anywhere.
