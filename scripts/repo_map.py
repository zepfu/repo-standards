#!/usr/bin/env python3
"""
repo_map.py - Generate repository structure documentation

Automatically generates comprehensive repository structure documentation
including directory trees, file descriptions, and categorized overviews.

Usage:
    python3 repo_map.py                           # Generate REPO_MAP.md
    python3 repo_map.py --output docs/STRUCTURE.md
    python3 repo_map.py --format json
    python3 repo_map.py --format tree
    python3 repo_map.py --root /path/to/project

Output Formats:
    - markdown: Comprehensive documentation (default)
    - json: Machine-readable structure
    - tree: Simple text tree

Features:
    - Extracts descriptions from docstrings and comments
    - Categorizes files (entry points, configs, docs, scripts)
    - Marks important files
    - Generates tables and tree views
    - Respects .gitignore patterns
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Files that should be highlighted as important
IMPORTANT_FILES = {
    "start.sh",
    "gateway.py",
    "auth.py",
    "Dockerfile",
    "docker-compose.yml",
    "README.md",
    "Makefile",
}

# Directories and patterns to ignore
IGNORE_PATTERNS = {
    "__pycache__",
    ".git",
    ".github",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "dist",
    "build",
    "*.egg-info",
    ".venv",
    "venv",
    ".env",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.dylib",
    "*.dll",
    # Sphinx documentation build artifacts
    "_build",
    "_static",
    "_templates",
}


def should_ignore(path: Path, ignore_patterns: Set[str]) -> bool:
    """Check if path should be ignored."""
    parts = path.parts
    name = path.name

    # Check each part of the path
    for part in parts:
        if part in ignore_patterns or part.startswith("."):
            return True

    # Check filename patterns
    for pattern in ignore_patterns:
        if "*" in pattern:
            # Simple glob matching
            pattern_re = pattern.replace(".", r"\.").replace("*", ".*")
            if re.match(pattern_re, name):
                return True
        elif name == pattern:
            return True

    return False


def extract_description(file_path: Path) -> Optional[str]:
    """Extract description from file's docstring or comments."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(500)  # First 500 chars

        # Python docstring
        if file_path.suffix == ".py":
            match = re.search(r'"""(.+?)"""', content, re.DOTALL)
            if match:
                desc = match.group(1).strip().split("\n")[0]
                return desc[:100]

        # Shell/script comment
        if file_path.suffix in {".sh", ".bash"}:
            match = re.search(r"^#\s*(.+?)$", content, re.MULTILINE)
            if match:
                desc = match.group(1).strip()
                if not desc.startswith("!"):
                    return desc[:100]

        # Markdown first heading
        if file_path.suffix == ".md":
            match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
            if match:
                return match.group(1).strip()[:100]

        # YAML/Config comment
        if file_path.suffix in {".yml", ".yaml"}:
            match = re.search(r"^#\s*(.+?)$", content, re.MULTILINE)
            if match:
                desc = match.group(1).strip()
                return desc[:100]

    except Exception:  # nosec B110 - intentional: skip unreadable files
        pass

    return None


def get_file_category(file_path: Path) -> str:
    """Categorize file by type and purpose."""
    name = file_path.name.lower()
    suffix = file_path.suffix.lower()

    # Entry points
    if name in {"start.sh", "main.py", "__main__.py", "app.py", "server.py"}:
        return "entry_point"

    # Configuration
    if suffix in {".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf"}:
        return "config"
    if name in {".env.example", "dockerfile", ".dockerignore", "makefile"}:
        return "config"
    if name.startswith(".") and name not in {".gitignore", ".gitattributes"}:
        return "config"

    # Documentation
    if suffix == ".md" or name in {"license", "authors", "changelog"}:
        return "documentation"

    # Scripts
    if suffix in {".sh", ".bash", ".py"} and "script" in str(file_path):
        return "script"

    # Source code
    if suffix in {".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp"}:
        return "source"

    # Tests
    if "test" in name or "tests" in str(file_path):
        return "test"

    return "other"


def scan_directory(root: Path, ignore_patterns: Set[str]) -> Dict[str, Any]:
    """Recursively scan directory and build structure."""
    structure: Dict[str, Any] = {
        "name": root.name or str(root),
        "type": "directory",
        "path": str(root),
        "children": {},
        "files": [],
    }

    try:
        items = sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return structure

    for item in items:
        if should_ignore(item.relative_to(root), ignore_patterns):
            continue

        if item.is_dir():
            child_structure = scan_directory(item, ignore_patterns)
            structure["children"][item.name] = child_structure
        elif item.is_file():
            file_info = {
                "name": item.name,
                "type": "file",
                "path": str(item),
                "category": get_file_category(item),
                "description": extract_description(item),
                "important": item.name in IMPORTANT_FILES,
            }
            structure["files"].append(file_info)

    return structure


def format_tree(structure: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
    """Format structure as text tree."""
    lines = []

    # Current item
    connector = "└── " if is_last else "├── "
    name = structure["name"]
    if structure["type"] == "directory":
        name += "/"

    lines.append(prefix + connector + name)

    # Extension for children
    extension = "    " if is_last else "│   "

    # Files first
    files = structure.get("files", [])
    for i, file_info in enumerate(files):
        is_last_file = (i == len(files) - 1) and not structure.get("children")
        file_connector = "└── " if is_last_file else "├── "
        file_name = file_info["name"]
        if file_info.get("important"):
            file_name = f"⭐ {file_name}"
        lines.append(prefix + extension + file_connector + file_name)

    # Then directories
    children = structure.get("children", {})
    child_items = list(children.items())
    for i, (name, child) in enumerate(child_items):
        is_last_child = i == len(child_items) - 1
        child_lines = format_tree(child, prefix + extension, is_last_child)
        lines.append(child_lines)

    return "\n".join(lines)


def _build_directory_tree(struct: Dict[str, Any], lines: List[str], prefix: str = ""):
    """Helper to build directory tree recursively."""
    # Files first
    files = struct.get("files", [])
    for i, file_info in enumerate(files):
        is_last_file = (i == len(files) - 1) and not struct.get("children")
        connector = "└── " if is_last_file else "├── "
        file_name = file_info["name"]
        if file_info.get("important"):
            file_name = f"⭐ {file_name}"
        lines.append(prefix + connector + file_name)

    # Then directories
    children = struct.get("children", {})
    child_items = list(children.items())
    for i, (name, child) in enumerate(child_items):
        is_last_child = i == len(child_items) - 1
        connector = "└── " if is_last_child else "├── "
        lines.append(prefix + connector + name + "/")

        extension = "    " if is_last_child else "│   "
        _build_directory_tree(child, lines, prefix + extension)


def _collect_files_by_category(
    struct: Dict[str, Any], category: str, collected: List[Dict[str, Any]]
):
    """Helper to collect files of a specific category."""
    for file_info in struct.get("files", []):
        if file_info["category"] == category:
            collected.append(file_info)

    for child in struct.get("children", {}).values():
        _collect_files_by_category(child, category, collected)


def _collect_important_files(struct: Dict[str, Any], collected: List[Dict[str, Any]]):
    """Helper to collect important files."""
    for file_info in struct.get("files", []):
        if file_info.get("important") and file_info["category"] != "entry_point":
            collected.append(file_info)
    for child in struct.get("children", {}).values():
        _collect_important_files(child, collected)


def _add_key_files_section(lines: List[str], structure: Dict[str, Any]):
    """Add key files section to documentation."""
    entry_points: List[Dict[str, Any]] = []
    _collect_files_by_category(structure, "entry_point", entry_points)

    important_files: List[Dict[str, Any]] = []
    _collect_important_files(structure, important_files)

    if not entry_points and not important_files:
        return

    lines.extend(["## Key Files", ""])

    if entry_points:
        lines.extend(["### Entry Points", ""])
        for file_info in entry_points:
            lines.append(f"**`{file_info['name']}`**")
            if file_info["description"]:
                lines.append(f"  - {file_info['description']}")
            lines.append("")

    if important_files:
        lines.extend(["### Important Files", ""])
        for file_info in important_files:
            lines.append(f"**`{file_info['name']}`**")
            if file_info["description"]:
                lines.append(f"  - {file_info['description']}")
            lines.append("")


def _add_category_section(
    lines: List[str], structure: Dict[str, Any], category: str, title: str, as_table: bool = False
):
    """Add a category section (config, docs, or scripts)."""
    files: List[Dict[str, Any]] = []
    _collect_files_by_category(structure, category, files)

    if not files:
        return

    lines.extend([f"## {title}", ""])

    if as_table:
        lines.append(
            "| File | Description |" if category == "config" else "| Script | Description |"
        )
        lines.append(
            "|------|-------------|" if category == "config" else "|--------|-------------|"
        )
        for file_info in files:
            desc = file_info["description"] or "*No description*"
            name = file_info["name"]
            lines.append(f"| `{name}` | {desc} |")
    else:
        for file_info in files:
            lines.append(f"- **`{file_info['name']}`**")
            if file_info["description"]:
                lines.append(f"  - {file_info['description']}")

    lines.append("")


def format_markdown(structure: Dict[str, Any], root_path: Path) -> str:
    """Format structure as comprehensive markdown documentation."""
    lines = ["# Repository Structure", "", "> Auto-generated repository map", ""]

    # Table of contents
    lines.extend(
        [
            "## Table of Contents",
            "",
            "- [Directory Tree](#directory-tree)",
            "- [Key Files](#key-files)",
            "- [Configuration Files](#configuration-files)",
            "- [Documentation](#documentation)",
            "- [Scripts](#scripts)",
            "",
        ]
    )

    # Directory tree
    lines.extend(
        [
            "## Directory Tree",
            "",
            "```",
            structure["name"] + "/",
        ]
    )

    _build_directory_tree(structure, lines)
    lines.extend(["```", ""])

    # Key files section
    _add_key_files_section(lines, structure)

    # Configuration files
    _add_category_section(lines, structure, "config", "Configuration Files", as_table=True)

    # Documentation
    _add_category_section(lines, structure, "documentation", "Documentation", as_table=False)

    # Scripts
    _add_category_section(lines, structure, "script", "Scripts", as_table=True)

    # Footer
    lines.extend(
        [
            "---",
            "",
            "*This file is auto-generated. Do not edit manually.*",
            "",
            f"*Last updated: {Path(root_path).absolute()}*",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate repository structure map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--output", "-o", default="REPO_MAP.md", help="Output file path (default: REPO_MAP.md)"
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json", "tree"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--root", default=".", help="Root directory to scan (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.root).resolve()

    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        return 1

    print(f"Scanning {root_path}...")
    structure = scan_directory(root_path, IGNORE_PATTERNS)

    # Generate output
    if args.format == "json":
        output = json.dumps(structure, indent=2)
    elif args.format == "tree":
        output = format_tree(structure)
    else:  # markdown
        output = format_markdown(structure, root_path)

    # Write to file or stdout
    if args.output == "-":
        print(output)
    else:
        output_path = Path(args.output)
        output_path.write_text(output, encoding="utf-8")
        print(f"Generated: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
