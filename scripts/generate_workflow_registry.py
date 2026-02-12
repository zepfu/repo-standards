#!/usr/bin/env python3
"""
generate_workflow_registry.py - Generate workflow registry and tool coverage matrix

Parses all reusable GitHub Actions workflow YAML files and the pre-commit config
to produce a comprehensive reference document covering:

1. Workflow Registry - structured details for each reusable workflow including
   description, inputs, tools executed, scope, severity (blocking vs advisory),
   and config files used.

2. Tool Coverage Matrix - a table showing every linting/quality tool, which
   workflow(s) run it, whether pre-commit also runs it, and what is unique
   to each execution context.

3. Recommended Adoption Profiles - suggested workflow combinations for common
   project types with overlap notes.

4. Workflow Version Notes - tracks default versions for key inputs across
   workflows so downstream consumers know when defaults change.

Usage:
    python3 generate_workflow_registry.py
    python3 generate_workflow_registry.py --output docs/auto/WORKFLOW_REGISTRY.md
    python3 generate_workflow_registry.py --root /path/to/repo-standards

Output:
    Markdown document suitable for inclusion in Sphinx docs (via MyST).
"""

import argparse
import datetime
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

# ---------------------------------------------------------------------------
# Data model helpers
# ---------------------------------------------------------------------------


def _safe_str(val: Any) -> str:
    """Convert YAML value to display string."""
    if isinstance(val, bool):
        return str(val).lower()
    if val is None:
        return ""
    return str(val)


# ---------------------------------------------------------------------------
# Workflow parser
# ---------------------------------------------------------------------------


class WorkflowParser:
    """Parse reusable workflow YAML files and extract tool/input metadata."""

    # Map of known tool identifiers to human-friendly names.
    # The key is a substring we look for in run: blocks or uses: actions.
    KNOWN_TOOLS: Dict[str, Dict[str, str]] = {
        "black": {"name": "Black", "category": "python-formatting"},
        "isort": {"name": "isort", "category": "python-formatting"},
        "flake8": {"name": "Flake8", "category": "python-linting"},
        "py_compile": {"name": "py_compile", "category": "python-syntax"},
        "shellcheck": {"name": "ShellCheck", "category": "shell-linting"},
        "bash -n": {"name": "bash -n", "category": "shell-syntax"},
        "vulture": {"name": "Vulture", "category": "dead-code"},
        "autoflake": {"name": "Autoflake", "category": "dead-code"},
        "eradicate": {"name": "Eradicate", "category": "dead-code"},
        "pylint": {"name": "PyLint", "category": "dead-code"},
        "bandit": {"name": "Bandit", "category": "security"},
        "mypy": {"name": "mypy", "category": "type-checking"},
        "pydocstyle": {"name": "pydocstyle", "category": "docstyle"},
        "actionlint": {"name": "actionlint", "category": "ci-linting"},
        "mdformat": {"name": "mdformat", "category": "markdown"},
        "yamllint": {"name": "yamllint", "category": "yaml-linting"},
        "checkmake": {"name": "checkmake", "category": "makefile-linting"},
        "hadolint": {"name": "hadolint", "category": "docker-linting"},
        "docker/build-push-action": {"name": "Docker Build", "category": "docker-build"},
        "sphinx-build": {"name": "Sphinx", "category": "docs-build"},
        "pre-commit": {"name": "pre-commit", "category": "meta-linting"},
        "changelog.py": {"name": "changelog.py", "category": "docs-gen"},
        "repo_map.py": {"name": "repo_map.py", "category": "docs-gen"},
        "generate_architecture.py": {"name": "generate_architecture.py", "category": "docs-gen"},
    }

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.workflows: Dict[str, Dict] = {}
        self.pre_commit_tools: Dict[str, Dict] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_all(self):
        """Parse all reusable workflows and pre-commit config."""
        self._parse_workflows()
        self._parse_pre_commit()
        return self

    # ------------------------------------------------------------------
    # Workflow parsing
    # ------------------------------------------------------------------

    def _parse_workflows(self):
        wf_dir = self.root_path / ".github" / "workflows"
        if not wf_dir.exists():
            return

        for yf in sorted(wf_dir.glob("reusable-*.yml")):
            try:
                data = yaml.safe_load(yf.read_text(encoding="utf-8"))
                if not data:
                    continue
                self.workflows[yf.name] = self._extract_workflow(yf.name, data)
            except Exception as exc:
                print(f"Warning: could not parse {yf.name}: {exc}")

    def _extract_workflow(self, filename: str, data: dict) -> dict:
        wf_name = data.get("name", filename)
        on_config = data.get("on", data.get(True, {}))  # YAML parses `on:` as True

        # Inputs
        inputs = {}
        if isinstance(on_config, dict):
            wc = on_config.get("workflow_call", {})
            if isinstance(wc, dict):
                raw_inputs = wc.get("inputs", {})
                if isinstance(raw_inputs, dict):
                    for inp_name, inp_def in raw_inputs.items():
                        if isinstance(inp_def, dict):
                            inputs[inp_name] = {
                                "type": inp_def.get("type", "string"),
                                "default": inp_def.get("default"),
                                "description": inp_def.get("description", ""),
                                "required": inp_def.get("required", False),
                            }

        # Jobs and tools
        jobs_info = {}
        tools_found: List[Dict] = []
        raw_jobs = data.get("jobs", {})

        for job_id, job_def in raw_jobs.items():
            if not isinstance(job_def, dict):
                continue
            job_name = job_def.get("name", job_id)
            needs = job_def.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]

            steps = job_def.get("steps", [])
            job_tools = self._detect_tools_in_steps(steps, job_id)
            tools_found.extend(job_tools)

            jobs_info[job_id] = {
                "name": job_name,
                "needs": needs,
                "tools": [t["tool_key"] for t in job_tools],
            }

        return {
            "filename": filename,
            "name": wf_name,
            "inputs": inputs,
            "jobs": jobs_info,
            "tools": tools_found,
        }

    def _detect_tools_in_steps(self, steps: list, job_id: str) -> List[Dict]:
        """Detect known tools executed in workflow steps.

        Two passes: first collect all matches, then prefer execution steps
        over install steps when the same tool appears in multiple steps.
        """
        # Pass 1: collect all candidate matches per tool
        candidates: Dict[str, List[Dict]] = defaultdict(list)

        for step in steps:
            if not isinstance(step, dict):
                continue

            run_block = step.get("run", "")
            uses_block = step.get("uses", "")
            step_name = step.get("name", "")
            is_install = any(kw in step_name.lower() for kw in ["install", "setup", "set up"])
            if not is_install:
                is_install = bool(re.search(r"pip install|npm install|go install", run_block))

            for tool_key, tool_meta in self.KNOWN_TOOLS.items():
                in_run = tool_key in run_block
                in_uses = tool_key in uses_block
                in_name = tool_key in step_name

                if not (in_run or in_uses or in_name):
                    continue

                # Avoid false positives: if the tool key only appears inside
                # quoted strings (config filenames like ".flake8"), skip.
                if in_run and not in_uses:
                    stripped = re.sub(r'"[^"]*"', "", run_block)
                    stripped = re.sub(r"'[^']*'", "", stripped)

                    filename_tools = {
                        "flake8",
                        "shellcheck",
                        "pre-commit",
                        "black",
                        "isort",
                        "yamllint",
                        "bandit",
                        "mypy",
                        "checkmake",
                    }
                    if tool_key in filename_tools:
                        invocation_patterns = [
                            rf"pip install\b.*\b{re.escape(tool_key)}\b",
                            rf"^\s*{re.escape(tool_key)}\b",
                            rf"\|\s*{re.escape(tool_key)}\b",
                            rf"if\s+{re.escape(tool_key)}\b",
                            rf"if\s+!\s+{re.escape(tool_key)}\b",
                            rf"run:\s*{re.escape(tool_key)}\b",
                        ]
                        is_invoked = any(
                            re.search(p, run_block, re.MULTILINE) for p in invocation_patterns
                        )
                        if not is_invoked and not in_uses:
                            continue

                severity = self._detect_severity(run_block, tool_key, step_name)
                scope = self._detect_scope(run_block, tool_key)
                version = self._detect_version(run_block, uses_block, tool_key)
                config_file = self._detect_config(run_block, tool_key)

                candidates[tool_key].append(
                    {
                        "tool_key": tool_key,
                        "name": tool_meta["name"],
                        "category": tool_meta["category"],
                        "job": job_id,
                        "severity": severity,
                        "scope": scope,
                        "version": version,
                        "config": config_file,
                        "_is_install": is_install,
                    }
                )

        # Pass 2: for each tool pick the best match (prefer non-install steps)
        found = []
        for tool_key, matches in candidates.items():
            non_install = [m for m in matches if not m["_is_install"]]
            best = non_install[0] if non_install else matches[0]
            del best["_is_install"]
            found.append(best)

        # Pass 3: detect bash validation checks (file existence, grep content
        # checks) that don't use named tools but still perform enforcement.
        found_keys = {t["tool_key"] for t in found}
        found.extend(self._detect_bash_checks(steps, job_id, found_keys))

        return found

    # Patterns that indicate bash-based validation checks in workflow steps.
    # Each entry: (step_name_pattern, run_block_pattern, check_info)
    BASH_CHECK_PATTERNS: List[Tuple[str, str, Dict[str, str]]] = [
        (
            r"required.*(config|file)",
            r'\[ [!-]+ -f "\$file" \]|MISSING_REQUIRED',
            {
                "tool_key": "_check_required_files",
                "name": "Required file existence",
                "category": "config-validation",
                "scope": "repo root",
                "config": "—",
            },
        ),
        (
            r"validate.*gitattributes",
            r"grep.*text=auto|grep.*eol=lf",
            {
                "tool_key": "_check_gitattributes",
                "name": ".gitattributes content",
                "category": "config-validation",
                "scope": ".gitattributes",
                "config": "—",
            },
        ),
        (
            r"validate.*gitignore",
            r"grep.*__pycache__|REQUIRED_PATTERNS",
            {
                "tool_key": "_check_gitignore",
                "name": ".gitignore pattern",
                "category": "config-validation",
                "scope": ".gitignore",
                "config": "—",
            },
        ),
        (
            r"check.*(phony|tab|indent)",
            r"\.PHONY|grep.*tab|indent",
            {
                "tool_key": "_check_makefile_hygiene",
                "name": "Makefile hygiene (tabs, .PHONY)",
                "category": "makefile-linting",
                "scope": "Makefile, *.mk",
                "config": "—",
            },
        ),
        (
            r"validate.*(workflow|yaml syntax)",
            r"yaml\.safe_load|grep.*name:|grep.*on:|grep.*jobs:",
            {
                "tool_key": "_check_workflow_yaml",
                "name": "Workflow YAML structure",
                "category": "yaml-linting",
                "scope": ".github/workflows/*.yml",
                "config": "—",
            },
        ),
        (
            r"unused.*shell|shell.*function",
            r"grep.*function|grep.*\(\)",
            {
                "tool_key": "_check_unused_shell",
                "name": "Unused shell function detection",
                "category": "dead-code",
                "scope": "scripts/*.sh",
                "config": "—",
            },
        ),
    ]

    def _detect_bash_checks(self, steps: list, job_id: str, already_found: set) -> List[Dict]:
        """Detect bash-based validation checks that aren't named tools."""
        found = []

        for step in steps:
            if not isinstance(step, dict):
                continue

            run_block = step.get("run", "")
            step_name = step.get("name", "")
            if not run_block or not step_name:
                continue

            for name_pat, run_pat, check_info in self.BASH_CHECK_PATTERNS:
                key = check_info["tool_key"]
                if key in already_found:
                    continue

                name_match = re.search(name_pat, step_name, re.IGNORECASE)
                run_match = re.search(run_pat, run_block, re.IGNORECASE)

                if name_match and run_match:
                    severity = self._detect_severity(run_block, key, step_name)
                    entry = dict(check_info)
                    entry["job"] = job_id
                    entry["severity"] = severity
                    entry["version"] = "bash"
                    found.append(entry)
                    already_found.add(key)

        return found

    def _detect_severity(self, run_block: str, tool_key: str, step_name: str) -> str:
        """Determine if a tool check is blocking or advisory."""
        # Check for WARN in the step output (summary writes) - this is a strong
        # advisory signal unless exit 1 follows directly
        has_warn = "WARN" in run_block
        has_exit1 = "exit 1" in run_block

        # Tools whose step writes WARN to summary and does NOT exit 1
        # within the same step are advisory.
        if has_warn and not has_exit1:
            return "advisory"

        # Vulture, autoflake, eradicate, pylint in quality-checks:
        # The tools themselves run in one step, but failure is gated by
        # a separate "Fail if requested" step that checks fail-on-unused.
        # The individual tool steps use "|| true" or WARN patterns.
        conditional_tools = {"vulture", "autoflake", "eradicate", "pylint"}
        if tool_key in conditional_tools:
            # These are advisory by default, blocking only if fail-on-unused=true
            if has_warn or "found=" in run_block:
                return "advisory (blocking if fail-on-unused=true)"

        # mypy in quality-checks writes WARN and does not exit 1
        if tool_key == "mypy" and has_warn:
            return "advisory"

        # If the run block contains exit 1, it's blocking
        if has_exit1:
            return "blocking"

        # Uses-based steps that don't have a continue-on-error are blocking
        return "blocking"

    def _detect_scope(self, run_block: str, tool_key: str) -> str:
        """Detect what files/directories a tool scans."""
        # Look for common scope patterns
        scope_patterns = [
            (r"scripts/\*\.py", "scripts/*.py"),
            (r"scripts/", "scripts/"),
            (r"\*\*/\*\.py", "**/*.py"),
            (r"\*\*/\*\.sh", "**/*.sh"),
            (r"\*\*/\*\.yml", "**/*.yml"),
            (r"\*\*/\*\.yaml", "**/*.yaml"),
            (r"\*\*/\*\.md", "**/*.md"),
            (r'"\."', "."),
            (r"'\.'", "."),
            (r"\b\.\s", ". (project root)"),
            (r"-r \.", ". (recursive)"),
        ]

        for pattern, label in scope_patterns:
            if re.search(pattern, run_block):
                return label

        if tool_key in ("shellcheck", "bash -n"):
            return "**/*.sh"
        if tool_key in ("black", "isort", "flake8"):
            return ". (all Python)"

        return "."

    def _detect_version(self, run_block: str, uses_block: str, tool_key: str) -> str:
        """Try to extract a tool version from pip install or uses action."""
        # Check uses: action version
        if uses_block and "@" in uses_block:
            return uses_block.split("@")[-1]

        # Check pip install with version pin
        match = re.search(rf"pip install\s+.*{re.escape(tool_key)}[=<>]+([^\s]+)", run_block)
        if match:
            return match.group(1)

        return "latest"

    def _detect_config(self, run_block: str, tool_key: str) -> str:
        """Detect config file used by a tool."""
        config_map = {
            "black": "--line-length=100",
            "isort": "--profile=black --line-length=100",
            "flake8": ".flake8",
            "bandit": "pyproject.toml",
            "mypy": "--ignore-missing-imports",
            "pydocstyle": "pyproject.toml",
            "shellcheck": ".shellcheckrc",
            "yamllint": "relaxed + line-length 150",
            "checkmake": ".checkmake",
            "mdformat": "--wrap 120",
        }
        return config_map.get(tool_key, "")

    # ------------------------------------------------------------------
    # Pre-commit parsing
    # ------------------------------------------------------------------

    def _parse_pre_commit(self):
        pc_path = self.root_path / ".pre-commit-config.yaml"
        if not pc_path.exists():
            return

        try:
            data = yaml.safe_load(pc_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Warning: could not parse pre-commit config: {exc}")
            return

        repos = data.get("repos", [])
        for repo in repos:
            if not isinstance(repo, dict):
                continue
            rev = repo.get("rev", "")
            hooks = repo.get("hooks", [])
            for hook in hooks:
                if not isinstance(hook, dict):
                    continue
                hook_id = hook.get("id", "")
                args = hook.get("args", [])
                self.pre_commit_tools[hook_id] = {
                    "rev": rev,
                    "args": args,
                    "repo": repo.get("repo", ""),
                }


# ---------------------------------------------------------------------------
# Document generator
# ---------------------------------------------------------------------------


class RegistryDocGenerator:
    """Generate the workflow registry markdown document."""

    def __init__(self, parser: WorkflowParser):
        self.parser = parser

    def generate(self) -> str:
        sections = [
            self._header(),
            self._precommit_vs_ci(),
            self._workflow_registry(),
            self._tool_coverage_matrix(),
            self._blocking_vs_advisory(),
            self._adoption_profiles(),
            self._version_defaults(),
            self._footer(),
        ]
        return "\n".join(sections)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _header(self) -> str:
        return f"""# Workflow Registry & Tool Coverage

**Auto-generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

> Complete reference for all reusable workflows: what tools they run,
> their inputs, blocking vs. advisory behavior, and overlap with pre-commit.

## How to Use This Document

- **Adopting workflows?** Jump to [Recommended Adoption Profiles](#recommended-adoption-profiles)
  to see which combination fits your project.
- **Debugging a CI failure?** Find the failing workflow in the
  [Workflow Registry](#workflow-registry) to see exactly which tools run and
  whether failures are blocking.
- **Choosing between pre-commit and CI?** See the
  [Tool Coverage Matrix](#tool-coverage-matrix) for the full overlap picture.
"""

    def _precommit_vs_ci(self) -> str:
        lines = [
            "## Pre-commit vs. CI: How They Work Together\n",
            "Many tools appear in **both** pre-commit hooks and CI workflows.",
            "This is intentional — they serve different roles:\n",
            "| | Pre-commit (local) | CI Workflows (remote) |",
            "|---|---|---|",
            "| **When** | Before each commit | On push / PR |",
            (
                "| **Mode** | Fix-then-commit — auto-fix in place |"
                " Check-only — report violations without modifying |"
            ),
            "| **Scope** | Staged files only | Full repository |",
            (
                "| **Purpose** | Fast feedback; prevent bad commits |"
                " Enforcement gate; catches skipped hooks |"
            ),
            ("| **Failure** | Blocks `git commit` locally |" " Blocks PR merge |"),
            "",
            "### Why the overlap matters\n",
            ("A downstream repo should run **both** pre-commit and" " CI workflows. Pre-commit"),
            ("gives developers instant feedback and auto-fixes. CI" " is the safety net that"),
            ("guarantees standards are met regardless of local" " setup — someone who clones"),
            ("fresh, skips `pre-commit install`, or uses" " `--no-verify` will still be caught."),
            "",
            "### Tools unique to each context\n",
            "Some tools only run in one context:\n",
            ("- **CI only:** Vulture (dead code), PyLint" " unreachable-code checks, py_compile"),
            ("  syntax validation, Docker build, Sphinx docs" " build. These are too slow or"),
            "  too noisy for a pre-commit hook.",
            ("- **Pre-commit only:** hadolint (Dockerfile" " linting), file-hygiene hooks"),
            ("  (trailing whitespace, EOF fixer, merge conflict" " detection, private key"),
            "  detection). These are fast fixers best run locally.",
            "",
            ("See the [Tool Coverage Matrix]" "(#tool-coverage-matrix) below for the complete"),
            "mapping.",
            "",
        ]
        return "\n".join(lines)

    def _workflow_registry(self) -> str:
        lines = ["## Workflow Registry\n"]

        for filename, wf in sorted(self.parser.workflows.items()):
            lines.append(f"### `{filename}`\n")
            lines.append(f"**{wf['name']}**\n")

            # Inputs table
            if wf["inputs"]:
                lines.append("#### Inputs\n")
                lines.append("| Input | Type | Default | Description |")
                lines.append("|-------|------|---------|-------------|")
                for inp_name, inp_def in wf["inputs"].items():
                    default = _safe_str(inp_def.get("default", ""))
                    if default:
                        default = f"`{default}`"
                    else:
                        default = "*(none)*"
                    lines.append(
                        f"| `{inp_name}` "
                        f"| {inp_def.get('type', 'string')} "
                        f"| {default} "
                        f"| {inp_def.get('description', '')} |"
                    )
                lines.append("")

            # Tools table
            if wf["tools"]:
                lines.append("#### Tools Executed\n")
                lines.append("| Tool | Job | Severity | Scope | Config |")
                lines.append("|------|-----|----------|-------|--------|")
                for t in wf["tools"]:
                    lines.append(
                        f"| **{t['name']}** "
                        f"| `{t['job']}` "
                        f"| {t['severity']} "
                        f"| `{t['scope']}` "
                        f"| {t['config'] if t['config'] else '—'} |"
                    )
                lines.append("")

            # Job dependency graph (text)
            jobs_with_deps = {jid: jinfo for jid, jinfo in wf["jobs"].items() if jinfo["needs"]}
            if jobs_with_deps:
                lines.append("#### Job Dependencies\n")
                for jid, jinfo in wf["jobs"].items():
                    if jinfo["needs"]:
                        deps = ", ".join(f"`{d}`" for d in jinfo["needs"])
                        lines.append(f"- `{jid}` ← {deps}")
                lines.append("")

            lines.append("---\n")

        return "\n".join(lines)

    def _tool_coverage_matrix(self) -> str:
        """Build tool coverage matrix with version and scope sub-tables."""
        lines = [
            "## Tool Coverage Matrix\n",
            "Which tools run where — at a glance.\n",
            "| Tool | Category | CI Workflow(s) | Pre-commit | Unique to |",
            "|------|----------|---------------|------------|-----------|",
        ]

        tool_workflows, tool_meta = self._collect_tool_workflows()
        pc_hook_to_key = self._pc_hook_key_map()
        pc_keys_mapped, all_tool_keys = self._merge_tool_keys(
            tool_workflows,
            pc_hook_to_key,
        )
        pc_only_categories = self._pc_only_categories()

        # Main matrix rows
        self._build_matrix_rows(
            lines,
            all_tool_keys,
            tool_workflows,
            pc_keys_mapped,
            tool_meta,
            pc_only_categories,
        )

        # Version comparison sub-table
        self._build_version_comparison(
            lines,
            all_tool_keys,
            tool_workflows,
            pc_keys_mapped,
            pc_hook_to_key,
            tool_meta,
        )

        # Scope mismatch notes
        self._build_scope_notes(lines)

        return "\n".join(lines)

    def _collect_tool_workflows(self):
        """Collect tool-to-workflow mapping and metadata."""
        tool_workflows: Dict[str, List[str]] = defaultdict(list)
        tool_meta: Dict[str, Dict] = {}

        for filename, wf in self.parser.workflows.items():
            for t in wf["tools"]:
                key = t["tool_key"]
                if filename not in tool_workflows[key]:
                    tool_workflows[key].append(filename)
                if key not in tool_meta:
                    tool_meta[key] = t

        return tool_workflows, tool_meta

    @staticmethod
    def _pc_hook_key_map() -> Dict[str, str]:
        """Map pre-commit hook IDs to normalized tool keys."""
        return {
            "trailing-whitespace": "trailing-whitespace",
            "end-of-file-fixer": "end-of-file-fixer",
            "check-yaml": "check-yaml",
            "check-toml": "check-toml",
            "check-json": "check-json",
            "check-added-large-files": "check-added-large-files",
            "check-merge-conflict": "check-merge-conflict",
            "check-executables-have-shebangs": ("check-executables-have-shebangs"),
            "check-shebang-scripts-are-executable": ("check-shebang-scripts-are-executable"),
            "check-symlinks": "check-symlinks",
            "destroyed-symlinks": "destroyed-symlinks",
            "check-case-conflict": "check-case-conflict",
            "fix-byte-order-marker": "fix-byte-order-marker",
            "detect-private-key": "detect-private-key",
            "mixed-line-ending": "mixed-line-ending",
            "shellcheck": "shellcheck",
            "black": "black",
            "isort": "isort",
            "flake8": "flake8",
            "autoflake": "autoflake",
            "eradicate": "eradicate",
            "pydocstyle": "pydocstyle",
            "bandit": "bandit",
            "mypy": "mypy",
            "yamllint": "yamllint",
            "mdformat": "mdformat",
            "hadolint": "hadolint",
            "actionlint": "actionlint",
            "checkmake": "checkmake",
        }

    def _merge_tool_keys(self, tool_workflows, pc_hook_to_key):
        """Merge CI and pre-commit tool keys into one set."""
        all_tool_keys = set(tool_workflows.keys())
        pc_keys_mapped = set()
        for hook_id in self.parser.pre_commit_tools:
            mapped = pc_hook_to_key.get(hook_id, hook_id)
            pc_keys_mapped.add(mapped)
            all_tool_keys.add(mapped)
        return pc_keys_mapped, all_tool_keys

    @staticmethod
    def _pc_only_categories() -> Dict[str, str]:
        """Category labels for pre-commit-only tools."""
        return {
            "trailing-whitespace": "file-hygiene",
            "end-of-file-fixer": "file-hygiene",
            "check-yaml": "yaml-syntax",
            "check-toml": "toml-syntax",
            "check-json": "json-syntax",
            "check-added-large-files": "file-hygiene",
            "check-merge-conflict": "file-hygiene",
            "check-executables-have-shebangs": "file-hygiene",
            "check-shebang-scripts-are-executable": "file-hygiene",
            "check-symlinks": "file-hygiene",
            "destroyed-symlinks": "file-hygiene",
            "check-case-conflict": "file-hygiene",
            "fix-byte-order-marker": "file-hygiene",
            "detect-private-key": "security",
            "mixed-line-ending": "file-hygiene",
            "hadolint": "docker-linting",
        }

    @staticmethod
    def _build_matrix_rows(
        lines,
        all_tool_keys,
        tool_workflows,
        pc_keys_mapped,
        tool_meta,
        pc_only_categories,
    ):
        """Populate the main coverage matrix rows."""

        def sort_key(k):
            in_ci = k in tool_workflows
            in_pc = k in pc_keys_mapped
            if in_ci and in_pc:
                return (0, k)
            if in_pc and not in_ci:
                return (1, k)
            return (2, k)

        for key in sorted(all_tool_keys, key=sort_key):
            in_ci = key in tool_workflows
            in_pc = key in pc_keys_mapped

            if key in tool_meta:
                name = tool_meta[key]["name"]
                cat = tool_meta[key]["category"]
            elif key in pc_only_categories:
                name = key
                cat = pc_only_categories[key]
            else:
                name = key
                cat = "other"

            ci_wfs = ", ".join(f"`{w}`" for w in tool_workflows.get(key, []))
            if not ci_wfs:
                ci_wfs = "—"

            pc_marker = "✅" if in_pc else "—"

            if in_ci and in_pc:
                unique = "both"
            elif in_ci:
                unique = "CI only"
            else:
                unique = "pre-commit only"

            lines.append(f"| {name} | {cat} | {ci_wfs}" f" | {pc_marker} | {unique} |")

        lines.append("")

    def _build_version_comparison(
        self,
        lines,
        all_tool_keys,
        tool_workflows,
        pc_keys_mapped,
        pc_hook_to_key,
        tool_meta,
    ):
        """Build version comparison sub-table and drift warning."""
        lines.append("### Version Comparison" " (tools in both CI and pre-commit)\n")
        lines.append("| Tool | CI Version | Pre-commit Rev |")
        lines.append("|------|-----------|---------------|")

        for key in sorted(all_tool_keys):
            if key not in tool_workflows or key not in pc_keys_mapped:
                continue
            ci_ver = "latest"
            for t in self._all_tools():
                if t["tool_key"] == key:
                    ci_ver = t.get("version", "latest")
                    break

            pc_rev = ""
            for hid, hinfo in self.parser.pre_commit_tools.items():
                if pc_hook_to_key.get(hid, hid) == key:
                    pc_rev = hinfo.get("rev", "")
                    break

            name = tool_meta[key]["name"] if key in tool_meta else key
            lines.append(f"| {name} | `{ci_ver}` | `{pc_rev}` |")

        lines.append("")
        lines.append("> **⚠️ Version drift risk:** CI workflows install" " tools via `pip install`")
        lines.append("> without version pins, so they always get the latest" " release. Pre-commit")
        lines.append(
            "> pins specific revisions. A tool releasing a breaking" " change can cause CI"
        )
        lines.append(
            "> to fail while pre-commit passes locally (or vice" " versa). If you hit this,"
        )
        lines.append(
            "> check whether the versions in these two columns have" " diverged. Downstream"
        )
        lines.append(
            "> repos that need stability should pin tool versions" " in their CI config or"
        )
        lines.append("> rely on pre-commit as the single source of truth" " for tool versions.")
        lines.append("")

    @staticmethod
    def _build_scope_notes(lines):
        """Add scope mismatch notes."""
        lines.append("### Scope Differences Between CI and Pre-commit\n")
        lines.append("Some tools scan different file sets in CI vs. pre-commit, which can")
        lines.append("produce different results:\n")
        lines.append("| Tool | CI Scope | Pre-commit Scope | Impact |")
        lines.append("|------|----------|-----------------|--------|")
        lines.append(
            "| Bandit | `-r .` with `pyproject.toml` exclude_dirs | "
            "All staged `.py` files with `-c pyproject.toml` | "
            "CI scans the full tree (minus excludes); pre-commit only scans staged files. "
            "New `.py` files outside `scripts/` may be missed locally until staged. |"
        )
        lines.append(
            "| Black, isort | `. (all Python)` | Staged `.py` files only | "
            "CI catches unformatted files that weren't staged in the committing developer's working tree. |"
        )
        lines.append(
            "| ShellCheck | `**/*.sh` (full tree) | Staged `.sh` files only | "
            "Same pattern — CI is exhaustive, pre-commit is incremental. |"
        )
        lines.append(
            "| Autoflake, Eradicate | `scripts/` (CI check-only) | "
            "All staged `.py` (fix in-place) | "
            "CI only checks `scripts/`; pre-commit fixes across all staged Python files. |"
        )
        lines.append("")
        lines.append(
            "> For most repos this is fine — pre-commit catches issues incrementally"
            " and CI validates the full tree. But if CI fails on a file that pre-commit"
            " never saw, scope difference is the likely cause."
        )
        lines.append("")

    def _blocking_vs_advisory(self) -> str:
        lines = [
            "## Blocking vs. Advisory Behavior\n",
            "Understanding which tools will block your PR and which are informational.\n",
        ]

        # Group tools by severity
        blocking = []
        advisory = []
        conditional = []

        for t in self._all_tools():
            sev = t["severity"]
            entry = f"**{t['name']}** (`{t['job']}` in `{t['_workflow']}`)"
            if "advisory" in sev and "blocking if" in sev:
                conditional.append((entry, sev))
            elif "advisory" in sev:
                advisory.append(entry)
            else:
                blocking.append(entry)

        lines.append("### Blocking (will fail your PR)\n")
        for b in sorted(set(blocking)):
            lines.append(f"- {b}")
        lines.append("")

        lines.append("### Advisory (warnings only, will not fail)\n")
        for a in sorted(set(advisory)):
            lines.append(f"- {a}")
        lines.append("")

        if conditional:
            lines.append("### Conditional (depends on input)\n")
            for entry, note in conditional:
                lines.append(f"- {entry} — {note}")
            lines.append("")

        return "\n".join(lines)

    def _adoption_profiles(self) -> str:
        return """## Recommended Adoption Profiles

### Python Project (Minimal)

```yaml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
```

**What you get:** Black, isort, Flake8, syntax validation via CI; full hook
suite locally via pre-commit.

**Overlap:** Black, isort, Flake8 run in both `reusable-python-ci.yml` and
pre-commit. See [Pre-commit vs. CI](#pre-commit-vs-ci-how-they-work-together)
for why both are recommended.

---

### Python Project (Comprehensive)

```yaml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  quality-checks:
    uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

**What you get:** Everything from minimal, plus Bandit security scanning,
mypy type checking, Vulture dead-code detection, pydocstyle, actionlint,
and mdformat.

**Overlap:** `reusable-quality-checks.yml` runs Bandit, mypy, pydocstyle,
actionlint, Autoflake, Eradicate, and mdformat — all of which also run via
pre-commit hooks. The CI versions provide granular per-job visibility and
add Vulture and PyLint unreachable-code checks (not in pre-commit).
See [Pre-commit vs. CI](#pre-commit-vs-ci-how-they-work-together) for why
both are recommended.

---

### Shell Project

```yaml
jobs:
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

---

### Python + Docker Project

```yaml
jobs:
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  quality-checks:
    uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  docker-build:
    uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
    needs: [python-standards, shell-standards]
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
```

**Note:** hadolint (Dockerfile linting) is in pre-commit only — there is no
dedicated CI workflow for it yet. Docker build validation happens via
`reusable-docker-build.yml`.

---

### Full Stack (All Workflows)

```yaml
jobs:
  config-validation:
    uses: zepfu/repo-standards/.github/workflows/reusable-config-validation.yml@main
  python-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-python-ci.yml@main
  shell-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-shell-ci.yml@main
  yaml-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-yaml-ci.yml@main
  makefile-standards:
    uses: zepfu/repo-standards/.github/workflows/reusable-makefile-ci.yml@main
  quality-checks:
    uses: zepfu/repo-standards/.github/workflows/reusable-quality-checks.yml@main
  docker-build:
    uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
    needs: [python-standards, shell-standards]
  pre-commit:
    uses: zepfu/repo-standards/.github/workflows/reusable-pre-commit.yml@main
  update-docs:
    uses: zepfu/repo-standards/.github/workflows/reusable-update-docs.yml@main
    needs: [python-standards, shell-standards]
```

"""

    def _version_defaults(self) -> str:
        lines = [
            "## Workflow Version Defaults\n",
            "Key input defaults across workflows. Pin these in your CI config if you",
            "need stability — defaults may change when repo-standards is updated.\n",
            "| Workflow | Input | Current Default |",
            "|----------|-------|-----------------|",
        ]

        for filename, wf in sorted(self.parser.workflows.items()):
            for inp_name, inp_def in wf["inputs"].items():
                default = _safe_str(inp_def.get("default", ""))
                if default:
                    lines.append(f"| `{filename}` | `{inp_name}` | `{default}` |")

        lines.append("")
        lines.append(
            "> **Tip:** If your project requires Python 3.11, pass "
            "`python-version: '3.11'` explicitly rather than relying on the "
            "default, which is currently `3.13`.\n"
        )
        return "\n".join(lines)

    def _footer(self) -> str:
        return """---

*This file is auto-generated by `generate_workflow_registry.py` from repo-standards.*
*Manual edits will be overwritten.*
"""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _all_tools(self) -> List[Dict]:
        """Flat list of all tools across all workflows, tagged with source."""
        tools = []
        for filename, wf in self.parser.workflows.items():
            for t in wf["tools"]:
                entry = dict(t)
                entry["_workflow"] = filename
                tools.append(entry)
        return tools


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate workflow registry and tool coverage matrix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--root",
        "-r",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="docs/auto/WORKFLOW_REGISTRY.md",
        help="Output file path (default: docs/auto/WORKFLOW_REGISTRY.md)",
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    print(f"Scanning workflows in {root}/.github/workflows/ ...")
    wp = WorkflowParser(root)
    wp.parse_all()

    print(f"  Found {len(wp.workflows)} reusable workflow(s)")
    print(f"  Found {len(wp.pre_commit_tools)} pre-commit hook(s)")

    doc = RegistryDocGenerator(wp).generate()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(doc, encoding="utf-8")

    print(f"✓ Generated: {output_path}")
    return 0


if __name__ == "__main__":
    exit(main())
