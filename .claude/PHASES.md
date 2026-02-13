# PHASES.md — Build Phases & Execution Plan

## Current Status

### Phase 1 — COMPLETE

**Built:**

- EditorConfig, gitignore, gitattributes base configs
- Pre-commit hook configuration with Python, Shell, YAML, Markdown, Docker, Makefile hooks
- Black, isort, Flake8, ShellCheck, yamllint, hadolint, checkmake configs
- pyproject.toml with tool configurations (Black, isort, pytest, bandit, mypy, pydocstyle)
- `sync-configs.sh` for distributing configs to consumer repos
- Basic Makefile with help, sync, and clean targets

**Gaps:** None — foundation is complete.

### Phase 2 — COMPLETE

**Built:**

- 10 reusable GitHub Actions workflows covering Python CI, Shell CI, YAML CI, Docker build, Makefile CI, pre-commit,
  config validation, quality checks, architecture docs, and general docs
- All workflows support configurable inputs with sensible defaults
- GitHub Step Summaries for all workflows
- actionlint enforcement for workflow validation
- Quality checks workflow (bandit, mypy, pydocstyle, eradicate)

**Gaps:** None — workflow suite is complete.

### Phase 3 — COMPLETE

**Built:**

- `scripts/changelog.py` — changelog generation from Conventional Commits
- `scripts/repo_map.py` — repo structure documentation generation
- `scripts/generate_architecture.py` — Mermaid architecture diagram generation
- `scripts/generate_workflow_registry.py` — workflow registry and tool coverage docs
- `scripts/render-mermaid.sh` — Mermaid diagram rendering (SVG/PNG/PDF)
- `scripts/archive.sh` — tar.gz archive for AI context
- Sphinx documentation site (`docs/`) with guides and reference
- ReadTheDocs and GitHub Pages deployment configs
- Auto-generated docs (`docs/auto/`): changelog, repo map, architecture, workflow registry
- CODE_STANDARDS.md — complete standards reference
- MESSAGING_STANDARDS.md — output formatting conventions

**Gaps:** None — automation and docs are complete.

### Phase 4 — ACTIVE (Maintenance Mode)

**Built:**

- Claude orchestration framework (CLAUDE.md, .claude/ files, agent-logs/)
- All core functionality operational

**Focus:**

- Keep tool versions current (pre-commit hook versions, action versions)
- Address bug reports from consumer repos
- Improve documentation based on user feedback
- Expand language coverage when mature tooling exists
- Community readiness (documentation for external adopters)

______________________________________________________________________

## Build Phases

### Phase 1: Foundation (COMPLETE)

**Deliverable:** A developer can sync config files to their repo and have pre-commit hooks enforcing Python, Shell,
YAML, Markdown, Docker, and Makefile standards.

- [x] Base config files (`.editorconfig`, `.gitignore`, `.gitattributes`, `.flake8`, `.shellcheckrc`)
- [x] Pre-commit hook configuration
- [x] Python tool configs in `pyproject.toml`
- [x] `sync-configs.sh` distribution script
- [x] Makefile with core targets

### Phase 2: Reusable CI Workflows (COMPLETE)

**Deliverable:** A developer can add a single workflow file to their repo that calls reusable workflows from
repo-standards, getting full CI coverage.

- [x] Python CI workflow (Black, isort, Flake8)
- [x] Shell CI workflow (ShellCheck, syntax check)
- [x] YAML CI workflow (yamllint)
- [x] Docker build workflow (hadolint, build test)
- [x] Makefile CI workflow (checkmake)
- [x] Pre-commit workflow (all hooks)
- [x] Config validation workflow
- [x] Quality checks workflow (bandit, mypy, pydocstyle, eradicate, actionlint)
- [x] Architecture docs workflow
- [x] General docs workflow (changelog, repo map, architecture, workflow registry)

### Phase 3: Automation & Documentation (COMPLETE)

**Deliverable:** Documentation is auto-generated, comprehensive, and publicly accessible. Scripts handle repo-map,
changelog, architecture diagrams, and workflow registry.

- [x] Changelog generation script
- [x] Repo map generation script
- [x] Architecture diagram generation script
- [x] Workflow registry generation script
- [x] Mermaid rendering script
- [x] Archive script for AI context
- [x] Sphinx documentation site with guides and reference
- [x] ReadTheDocs and GitHub Pages deployment
- [x] CODE_STANDARDS.md and MESSAGING_STANDARDS.md

### Phase 4: Maintenance & Community (ACTIVE)

**Deliverable:** The project stays current, well-documented, and easy for external adopters to use.

- [ ] Keep all tool versions up to date (pre-commit hooks, GitHub Actions, Python tools)
- [ ] Monitor and fix issues reported by consumer repos
- [ ] Improve onboarding documentation for external adopters
- [ ] Add language support as mature tooling becomes available (Go, Rust, JS/TS)
- [ ] Community contribution guidelines (CONTRIBUTING.md)

______________________________________________________________________

## Execution Streams

### Stream A: Maintenance

| Task                                     | Agent           | Status    |
| ---------------------------------------- | --------------- | --------- |
| A1. Pre-commit hook version updates      | DEVOPS-ENGINEER | Ongoing   |
| A2. GitHub Actions version updates       | DEVOPS-ENGINEER | Ongoing   |
| A3. Python tool version updates          | DEVOPS-ENGINEER | Ongoing   |
| A4. Bug fixes from consumer repo reports | TECH-LEAD       | As needed |

### Stream B: Documentation Improvements

| Task                                               | Agent       | Status  |
| -------------------------------------------------- | ----------- | ------- |
| B1. External adopter onboarding guide              | TECH-WRITER | Pending |
| B2. Workflow usage examples per consumer repo type | TECH-WRITER | Pending |
| B3. Troubleshooting guide                          | TECH-WRITER | Pending |

### Stream C: Expansion (Future)

| Task                                 | Agent           | Branch                   | Depends On |
| ------------------------------------ | --------------- | ------------------------ | ---------- |
| C1. Evaluate Go linting standards    | DEVOPS-ENGINEER | `feature/go-standards`   | —          |
| C2. Evaluate JS/TS linting standards | DEVOPS-ENGINEER | `feature/js-standards`   | —          |
| C3. Evaluate Rust linting standards  | DEVOPS-ENGINEER | `feature/rust-standards` | —          |

______________________________________________________________________

## Phase Gate Checks

### Phase 1 → Phase 2 (PASSED)

All true:

- [x] Config files sync correctly to consumer repos
- [x] Pre-commit hooks catch formatting and linting violations
- [x] All config files parse correctly
- [x] Documentation covers setup process

### Phase 2 → Phase 3 (PASSED)

All true:

- [x] All 10 reusable workflows functional
- [x] Workflows work with default inputs
- [x] actionlint passes on all workflow files
- [x] Consumer repos can call workflows successfully

### Phase 3 → Phase 4 (PASSED)

All true:

- [x] All automation scripts generate correct output
- [x] Sphinx docs build without errors
- [x] Documentation deployed to GitHub Pages and ReadTheDocs
- [x] CODE_STANDARDS.md and MESSAGING_STANDARDS.md complete

### Phase 4 → v1 Release

- [ ] All tool versions current
- [ ] No open critical/high issues
- [ ] External adopter documentation complete
- [ ] CONTRIBUTING.md in place
- [ ] Changelog generated for release
- [ ] Operator approval

______________________________________________________________________

## Pentest Timing

Not applicable — this project has no attack surface (no API, no auth, no user data). Security concerns are limited to:

- Ensuring `sync-configs.sh` doesn't introduce vulnerabilities in consumer repos
- Ensuring workflow configs don't expose secrets
- Bandit/mypy scanning of Python scripts for code quality
