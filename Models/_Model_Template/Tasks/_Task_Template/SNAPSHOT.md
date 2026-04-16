---
task_id: {TaskID}
task_name: {TaskName}
model: {ModelName}
owner: {UserVISA}
status: not-started
last_updated: YYYY-MM-DD
---

# Task SNAPSHOT — {TaskID} {TaskName}

Per-task cross-session state. Read this **first** at the start of any session on this task, and update it at every checkpoint (see `.claude/rules/10-context-and-snapshot.md`). This is the single source of truth for "where we are" on this task — not scratch notes in chat.

## 1. Purpose

Why this task exists in business terms. One short paragraph. What is the user/business problem? What outcome does "done" look like? No implementation detail here.

## 2. Scope

**In scope** — bullet list of the functional areas, modules, and artifact categories that this task may touch.

**Out of scope** — explicit list of things this task must **not** touch. Anything not listed is presumed out of scope.

**Model** — `{ModelName}`. One task edits one model only. If work spills into another model, stop and open a second task in that model.

## 3. Constraints

- Deadlines / release windows / freeze windows that affect scheduling.
- Regulatory / audit / security constraints.
- Integration cutover dates or counterparty dependencies.
- Data-volume, performance, or concurrency constraints known up front.

## 4. Source artifacts (read-only baseline)

Every artifact this task will read or modify, with the MCP call used to fetch the baseline. Baseline files live in `code/Ax{Type}/` **before** any edit and are committed to Git by the user as the "before" state.

| Artifact | Type | Model | Fetched via | Baseline commit |
|----------|------|-------|-------------|-----------------|
| e.g. `CustInvoiceJour` | AxTable | {ModelName} | `mcp__xppatlas__get_artifact` | `<short sha>` |

If a row has no baseline commit, **do not edit that artifact** — run `/fetch-baseline` and wait for the user to commit.

## 5. Decisions log

Running list of decisions actually taken, not options considered. Each entry: date, decision, one-line rationale, who decided. Example:

- `2026-04-15` — chose CoC over event handler on `CustInvoiceJour.insert` because we need to short-circuit the base behavior under a specific flag. Decided with user.

## 6. Extension strategy

Chosen extension mechanism(s) from `.claude/rules/20-xpp-change-safety.md` priority order (event handler → CoC → extension → new artifact with `{ProjectPrefix}` → overlayering). State the choice and the reason. If the choice is "new artifact" or "overlayering", justify why no lower-risk option fits.

## 7. Changed files (since baseline)

Running list of files modified **after** the baseline commit. Refresh at every checkpoint. This is what will eventually be copied back into the MCP source store at check-in time.

| File | Status | Notes |
|------|--------|-------|
| `code/AxClass/{ProjectPrefix}Foo.xml` | new / modified | one-line purpose |

## 8. Validation status

- `/review-code` — not run / passing / failing
- `/audit-arch` — not run / passing / failing
- `/fix-perf` — not run / N/A
- Manual testing — N/A until the user confirms a deployable build exists.

Never claim "tests pass" unless the user has actually run them and reported the result.

## 9. Next steps

Ordered short list of the next concrete actions. Keep it tight — this is the hand-off note for the next session.

1. …
2. …
3. …

## 10. Open questions for the user

Anything blocked on a user decision. If the list is non-empty, the session should open by surfacing these, not by continuing to code.
