#!/usr/bin/env python3
"""
changelog.py - Generate changelog from git history

Automatically generates and maintains a CHANGELOG.md file following the
Keep a Changelog format using conventional commits.

Usage:
    python3 changelog.py                        # Generate from all history
    python3 changelog.py --from-git            # Explicit: from git history
    python3 changelog.py --since v1.0.0        # Since specific tag
    python3 changelog.py --with-commits        # Include commit links
    python3 changelog.py --output RELEASE.md   # Custom output file

Conventional Commit Types:
    feat:     → Added
    fix:      → Fixed
    docs:     → Changed
    style:    → Changed
    refactor: → Changed
    perf:     → Changed
    test:     → Changed
    build:    → Changed
    ci:       → Changed
    chore:    → Changed

Features:
    - Parses conventional commits
    - Groups by change type (Added, Fixed, Changed, etc.)
    - Skips documentation-only commits (prevents recursion)
    - Includes commit links (optional)
    - Supports semantic versioning
    - Handles breaking changes
"""

import argparse
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Changelog header
CHANGELOG_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""

# Change type sections (order matters)
CHANGE_TYPES = {
    "added": "### Added",
    "changed": "### Changed",
    "deprecated": "### Deprecated",
    "removed": "### Removed",
    "fixed": "### Fixed",
    "security": "### Security",
}

# Conventional commit type mapping
COMMIT_TYPE_MAPPING = {
    "feat": "added",
    "fix": "fixed",
    "docs": "changed",
    "style": "changed",
    "refactor": "changed",
    "perf": "changed",
    "test": "changed",
    "build": "changed",
    "ci": "changed",
    "chore": "changed",
    "revert": "changed",
}


def run_git_command(args: List[str]) -> Optional[str]:
    """Run a git command and return output."""
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, check=True, cwd=".")
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_git_repo_url() -> Optional[str]:
    """Get the repository URL for linking commits."""
    url = run_git_command(["config", "--get", "remote.origin.url"])
    if not url:
        return None

    # Convert to HTTPS URL for GitHub/GitLab
    if url.startswith("git@"):
        # git@github.com:user/repo.git → https://github.com/user/repo
        url = url.replace(":", "/").replace("git@", "https://")

    # Remove .git suffix
    url = url.rstrip(".git")

    return url


def should_include_commit(message: str, files_changed: List[str]) -> bool:
    """
    Determine if commit should appear in changelog.

    Skips commits that only update documentation to prevent recursion.
    """
    # Skip if only doc files changed
    doc_files = {"CHANGELOG.md", "REPO_MAP.md"}
    if files_changed and all(f in doc_files for f in files_changed):
        return False

    # Skip automated doc updates
    skip_patterns = [
        r"^docs:.*update.*changelog",
        r"^docs:.*update.*repo",
        r"^chore:.*update documentation",
        r"^\[automated\]",
        r"^docs:.*regenerate",
    ]

    message_lower = message.lower()
    for pattern in skip_patterns:
        if re.search(pattern, message_lower):
            return False

    return True


def parse_commit_message(message: str) -> Tuple[str, str, bool]:
    """
    Parse commit message to extract type, description, and breaking change flag.

    Returns:
        (change_type, description, is_breaking)

    Examples:
        "feat: add streaming" → ('added', 'Add streaming', False)
        "fix!: memory leak" → ('fixed', 'Memory leak', True)
        "feat(auth)!: change API" → ('added', 'Change API', True)
    """
    # Check for breaking change indicator
    is_breaking = "!" in message or "BREAKING CHANGE" in message

    # Try conventional format: type(scope): description
    # Also handles: type!: description or type(scope)!: description
    match = re.match(r"^(\w+)(?:\([^)]+\))?!?:\s*(.+)$", message)
    if match:
        commit_type = match.group(1).lower()
        description = match.group(2).strip()

        # Capitalize first letter
        if description:
            description = description[0].upper() + description[1:]

        change_type = COMMIT_TYPE_MAPPING.get(commit_type, "changed")
        return change_type, description, is_breaking

    # Fallback: Infer from keywords
    message_lower = message.lower()

    if any(word in message_lower for word in ["add", "added", "new", "implement"]):
        return "added", message, is_breaking

    if any(word in message_lower for word in ["fix", "fixed", "resolve", "patch"]):
        return "fixed", message, is_breaking

    if any(word in message_lower for word in ["remove", "removed", "delete"]):
        return "removed", message, is_breaking

    if "deprecat" in message_lower:
        return "deprecated", message, is_breaking

    if any(word in message_lower for word in ["security", "cve", "vulnerab"]):
        return "security", message, is_breaking

    # Default to changed
    return "changed", message, is_breaking


def get_commits_for_changelog(
    since: Optional[str] = None, include_commits: bool = False
) -> List[Dict]:
    """
    Get commits for changelog, excluding doc-only commits.

    Returns list of dicts with: hash, message, date, files, change_type, description
    """
    # Build git log command
    cmd = ["git", "log", "--pretty=format:%H|%s|%ai", "--name-only"]

    if since:
        cmd.extend([f"{since}..HEAD"])

    output = run_git_command(cmd[1:])  # Skip 'git' prefix
    if not output:
        return []

    commits = []
    current_commit = None

    for line in output.split("\n"):
        if "|" in line:
            # New commit header
            parts = line.split("|")
            if len(parts) >= 3:
                commit_hash, message, date = parts[0], parts[1], parts[2]
                current_commit = {
                    "hash": commit_hash,
                    "message": message,
                    "date": date,
                    "files": [],
                }
        elif line and current_commit:
            # File from this commit
            current_commit["files"].append(line.strip())
        elif not line and current_commit:
            # End of commit (blank line)
            if should_include_commit(current_commit["message"], current_commit["files"]):
                change_type, description, is_breaking = parse_commit_message(
                    current_commit["message"]
                )

                current_commit["change_type"] = change_type
                current_commit["description"] = description
                current_commit["is_breaking"] = is_breaking

                commits.append(current_commit)

            current_commit = None

    # Handle last commit (if file doesn't end with blank line)
    if current_commit:
        if should_include_commit(current_commit["message"], current_commit["files"]):
            change_type, description, is_breaking = parse_commit_message(current_commit["message"])
            current_commit["change_type"] = change_type
            current_commit["description"] = description
            current_commit["is_breaking"] = is_breaking
            commits.append(current_commit)

    return commits


def format_changelog_entry(
    commit: Dict, include_commit_link: bool = False, repo_url: Optional[str] = None
) -> str:
    """Format a single changelog entry."""
    description = commit["description"]

    # Add breaking change marker
    if commit.get("is_breaking"):
        description = f"{description} ⚠️ **BREAKING**"

    # Add commit link if requested
    if include_commit_link and repo_url:
        short_hash = commit["hash"][:7]
        commit_url = f"{repo_url}/commit/{commit['hash']}"
        description = f"{description} ([{short_hash}]({commit_url}))"

    return f"- {description}"


def generate_changelog(
    commits: List[Dict], include_commit_links: bool = False, repo_url: Optional[str] = None
) -> str:
    """Generate complete changelog content."""
    # Group commits by type
    changes_by_type = {key: [] for key in CHANGE_TYPES.keys()}

    for commit in commits:
        change_type = commit["change_type"]
        entry = format_changelog_entry(commit, include_commit_links, repo_url)
        changes_by_type[change_type].append(entry)

    # Build output
    lines = [CHANGELOG_HEADER.rstrip()]

    # Unreleased section
    has_changes = any(changes_by_type.values())

    if has_changes:
        lines.extend(["", "## [Unreleased]", ""])

        # Add each change type section
        for change_type, section_header in CHANGE_TYPES.items():
            entries = changes_by_type[change_type]
            if entries:
                lines.append(section_header)
                lines.append("")
                lines.extend(entries)
                lines.append("")
    else:
        lines.extend(["", "## [Unreleased]", "", "*No unreleased changes*", ""])

    # Footer
    lines.extend(
        [
            "---",
            "",
            "*This file is auto-generated from git history.*",
            "*Manual edits may be overwritten.*",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate changelog from git history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--output", "-o", default="CHANGELOG.md", help="Output file path (default: CHANGELOG.md)"
    )

    parser.add_argument(
        "--from-git", action="store_true", help="Generate from git history (default behavior)"
    )

    parser.add_argument("--since", help="Generate changes since tag/commit (e.g., v1.0.0)")

    parser.add_argument("--with-commits", action="store_true", help="Include commit hash links")

    args = parser.parse_args()

    # Check if we're in a git repository
    if not run_git_command(["rev-parse", "--git-dir"]):
        print("Error: Not a git repository")
        return 1

    print("Generating changelog from git history...")

    # Get commits
    commits = get_commits_for_changelog(since=args.since, include_commits=args.with_commits)

    if not commits:
        print("Warning: No commits found")
        # Still generate file with header
        changelog = CHANGELOG_HEADER + "\n## [Unreleased]\n\n*No changes yet*\n"
    else:
        print(f"Found {len(commits)} commits")

        # Get repo URL for commit links
        repo_url = None
        if args.with_commits:
            repo_url = get_git_repo_url()
            if not repo_url:
                print("Warning: Could not determine repository URL for commit links")

        # Generate changelog
        changelog = generate_changelog(commits, args.with_commits, repo_url)

    # Write to file
    output_path = Path(args.output)
    output_path.write_text(changelog, encoding="utf-8")
    print(f"Generated: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
