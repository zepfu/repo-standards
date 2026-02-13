# CLAUDE_SUGGESTIONS.md — Spec Improvement Suggestions

> **Pending inbox.** TECH-LEAD and PRODUCT-OWNER write suggestions here. Operator reviews and marks each item.
>
> **Format:** `- [ ] [CRITICALITY] Description — PROPOSER (via UNDERLYING-AGENT)`
>
> **Operator actions** (change the brackets):
>
> - `[Y]` — Yes, approve. Coordinator applies the edit, logs to PROJECT_LOG.md, removes from this file.
> - `[N]` — No, reject. Coordinator logs to PROJECT_LOG.md, archives to `logs/REJECTED_SUGGESTIONS.md`, removes from
>   this file.
> - `[E]` — Explain more. Coordinator routes back to the proposer for additional detail, then resets to `[ ]`.
> - `[ ]` — Pending operator review (default).
>
> **Checked continuously** — same cadence as TASKS.md. Operator can mark items at any time during a session.
>
> **Before adding a new suggestion**, check `logs/REJECTED_SUGGESTIONS.md` to avoid re-proposing previously rejected
> items.

______________________________________________________________________

## Suggestions

<!-- New suggestions go here. Always include criticality and attribution.

Examples:

- [ ] [HIGH] Add Retry-After header convention — TECH-LEAD (via INTEGRATIONS-LEAD)
  **File:** .claude/GUIDELINES.md → "API Design Conventions" section
  **Add after:** "Error codes are meaningful and consistent"
  **Change:** `All 429 responses must include a Retry-After header with seconds until retry.`
  **Reason:** Rate-limited webhook retries have no backoff signal. Discovered during EasyPost integration.

- [ ] [MEDIUM] Standardize pagination cursor format — PRODUCT-OWNER (via API-ARCHITECT)
  **File:** .claude/SPEC.md → "Pagination" section
  **Change:** Define cursor-based pagination spec for all list endpoints.
  **Reason:** Three different pagination approaches emerging across endpoints.

- [ ] [CRITICAL] Fix ShippingProfile partial type mismatch — TECH-LEAD (via QA-ENGINEER)
  **File:** .claude/GUIDELINES.md → "Test Fixtures" section
  **Change:** Add rule: "Full Product fixtures require complete ShippingProfile (all 9 fields)"
  **Reason:** Unit tests failing due to incomplete shipping profiles in test data.
-->
