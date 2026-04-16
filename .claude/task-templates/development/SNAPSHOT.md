---
task_id: "{TaskID}"
task_name: "{TaskName}"
task_type: development
model: "{ModelName}"
owner: "{UserVISA}"
status: not-started
last_updated: "{Date}"
---

# Task SNAPSHOT — {TaskID} {TaskName}

Per-task cross-session state. Read this **first** at the start of any session on this task, and update it at every checkpoint (see `.claude/rules/task-lifecycle.md`). This is the single source of truth for "where we are" — not scratch notes in chat.

**Task type: development** — safe incremental implementation, extension-first, checkpoint, validate before completion.

## 1. Purpose

Why this task exists in business terms. What is the user/business problem? What outcome does "done" look like? No implementation detail here.

## 2. Scope

**In scope** — bullet list of the functional areas, modules, and artifact categories that this task may touch.

**Out of scope** — explicit list of things this task must **not** touch. Anything not listed is presumed out of scope.

**Model** — `{ModelName}`. One task edits one model only. If work spills into another model, stop and open a second task.

## 3. Constraints

- Deadlines / release windows / freeze windows
- Regulatory / audit / security constraints
- Integration cutover dates or counterparty dependencies
- Data-volume, performance, or concurrency constraints known up front

## 4. Source artifacts (read-only baseline)

Every artifact this task will read or modify, with the MCP call used to fetch the baseline. Baseline files live in `code/Ax{Type}/` **before** any edit.

| Artifact | Type | Model | Fetched via | Baseline commit |
|----------|------|-------|-------------|-----------------|
| | | | `mcp__xppatlas__get_artifact` | `<short sha>` |

If a row has no baseline commit, **do not edit that artifact** — run `/fetch-baseline` and wait for the user to commit.

## 5. Decisions log

Running list of decisions taken. Each entry: date, decision, one-line rationale, who decided.

## 6. Extension strategy

Chosen extension mechanism(s) from the priority order (event handler → CoC → extension → new artifact → overlayering). State the choice and the reason.

## 7. Changed files (since baseline)

| File | Status | Notes |
|------|--------|-------|
| `code/AxClass/{ProjectPrefix}Foo.xml` | new / modified | one-line purpose |

## 8. Validation status

- `/review-code` — not run / passing / failing
- `/audit-arch` — not run / passing / failing
- `/fix-perf` — not run / N/A
- Manual testing — N/A until user confirms a deployable build exists

Never claim "tests pass" unless the user has actually run them and reported the result.

## 9. Next steps

1. …
2. …
3. …

## 10. Open questions for the user

Anything blocked on a user decision. If non-empty, the session should open by surfacing these.
