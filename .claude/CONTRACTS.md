# CONTRACTS.md — Cross-Agent Interface Contracts

> **Shared source of truth for boundaries between agents.** When two or more agents must produce/consume the same
> interface (API response shape, webhook payload, event format, shared type, config schema), the contract is defined
> here BEFORE either agent begins implementation.
>
> PRODUCT-OWNER approves contracts. TECH-LEAD enforces them during dispatch and review. Changes require PRODUCT-OWNER
> approval and are logged in the changelog at the bottom.

______________________________________________________________________

## How Contracts Work

### Lifecycle

1. **PRODUCT-OWNER identifies a coordination boundary** during planning (typically from PHASES.md execution streams or
   when multiple agents touch the same interface). TECH-LEAD may also escalate the need for a contract during dispatch.
1. **PRODUCT-OWNER drafts the contract** with the producing agent's input (or the coordinator dispatches to
   API-ARCHITECT for complex contracts via TECH-LEAD).
1. **Contract is written here** with status `DRAFT`.
1. **Both sides confirm** — producer and consumer agents acknowledge the contract in their dispatch response. Status
   moves to `ACTIVE`.
1. **Agents implement against the contract**, not against assumptions or each other's code.
1. **Changes go through PRODUCT-OWNER** — if an agent discovers the contract needs to change during implementation, they
   propose the change (not apply it). PRODUCT-OWNER evaluates impact on the other side, updates the contract, and the
   coordinator notifies affected agents. Logged in the changelog.
1. **Contract is marked `VERIFIED`** once both sides have integration tests passing against it.
1. **Contract moves to `ARCHIVED`** when the feature is stable and the interface is unlikely to change.

### When to Create a Contract

- An API endpoint's response shape is consumed by a frontend component, plugin, or external integration
- A webhook/event payload is produced by one agent and handled by another
- A shared type or interface is used across packages/modules owned by different agents
- A database query result is shaped by one agent and consumed by another's service layer
- A configuration format is written by one agent and read by another

### When NOT Needed

- Work entirely within one agent's ownership boundary
- Internal implementation details that don't cross agent boundaries
- Standard patterns already fully defined in GUIDELINES.md (e.g., error response envelope, pagination format)

______________________________________________________________________

## Active Contracts

### C-001: Distributed Config File Set

**Status:** ACTIVE **Producer:** DEVOPS-ENGINEER — maintains config files in repo root **Consumer(s):** Consumer
repositories (via `sync-configs.sh`) **Phase:** Phase 1 (Foundation), ongoing **Related files:**
`scripts/sync-configs.sh`, all root-level config files

**Interface:** The following files are distributed to consumer repos and must remain valid, parseable, and compatible:

```
.editorconfig
.flake8
.gitattributes
.gitignore
.shellcheckrc
.pre-commit-config.yaml
pyproject.toml
```

**Rules/Invariants:**

- All config files must parse without errors by their respective tools
- `sync-configs.sh` creates `.bak` backups before overwriting
- Config values must be consistent across files (e.g., Black line-length in `pyproject.toml` must align with references
  in `.flake8`)
- Adding a new file to the distributed set requires updating `sync-configs.sh` and `CODE_STANDARDS.md`

**Notes:**

- `.markdownlint.json` is referenced in README but may not be present in all synced repos

______________________________________________________________________

### C-002: Reusable Workflow Interface

**Status:** ACTIVE **Producer:** DEVOPS-ENGINEER — maintains workflow files **Consumer(s):** Consumer repositories (via
`uses: zepfu/repo-standards/.github/workflows/<name>@main`) **Phase:** Phase 2 (Reusable CI Workflows), ongoing
**Related files:** `.github/workflows/reusable-*.yml`

**Interface:** Each reusable workflow exposes inputs via `on.workflow_call.inputs` and optionally
`on.workflow_call.secrets`. All inputs must have defaults so workflows work with zero configuration.

**Rules/Invariants:**

- Removing or renaming an input is a breaking change — requires deprecation period
- Adding a new required input without a default is a breaking change
- All workflows must work with their default input values (zero-config)
- Workflow names follow the pattern `reusable-<domain>-<purpose>.yml`

**Notes:**

- Consumer repos pin to `@main` — any push to main is immediately live for all consumers

______________________________________________________________________

## Draft Contracts

<!-- Contracts being defined but not yet confirmed by both sides -->

______________________________________________________________________

## Deprecated / Archived Contracts

<!-- Contracts that are no longer active. Keep for historical reference.
Move here with a note on what replaced them and when. -->

______________________________________________________________________

## Changelog

<!--
Append-only log of contract changes. Every creation, modification, and status change gets an entry.

Format:
### YYYY-MM-DD HH:MM — [Action]
**Contract:** C-[NNN]
**Change:** [What changed]
**Reason:** [Why]
**Impact:** [Which agents/code affected]
**Notified:** [Agents who were informed]
-->
