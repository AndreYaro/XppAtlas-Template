---
task_id: "{TaskID}"
task_name: "{TaskName}"
task_type: bugfix
model: "{ModelName}"
owner: "{UserVISA}"
status: not-started
last_updated: "{Date}"
---

# Task SNAPSHOT — {TaskID} {TaskName}

Per-task cross-session state. Read this **first** at the start of any session on this task, and update it at every checkpoint (see `.claude/rules/task-lifecycle.md`). This is the single source of truth for "where we are" — not scratch notes in chat.

**Task type: bugfix** — understand first, smallest correct fix, record evidence, assess regression risk.

## 1. Purpose

What defect is being fixed? What is the user-visible symptom? What does "fixed" look like?

## 2. Scope

**In scope** — the specific defect and the minimal set of artifacts needed to fix it.

**Out of scope** — related cleanup, redesign, or feature work discovered during investigation.

**Model** — `{ModelName}`. One task edits one model only.

## 3. Constraints

- Urgency / SLA / production impact
- Environment where the bug was reported
- Data conditions required to reproduce
- Related hotfixes or pending releases

## 4. Source artifacts (read-only baseline)

| Artifact | Type | Model | Fetched via | Baseline commit |
|----------|------|-------|-------------|-----------------|
| | | | `mcp__xppatlas__get_artifact` | `<short sha>` |

## 5. Investigation and decisions log

Record evidence, suspected causes, and confirmed root cause here. Each entry: date, finding, source.

- `{Date}` — **Symptom:** (what the user sees)
- `{Date}` — **Root cause:** (what actually causes it — fill in after investigation)
- `{Date}` — **Fix approach:** (what will be changed and why this is the minimal correct fix)
- `{Date}` — **Regression risk:** (what else could be affected)

## 6. Extension strategy

If the fix requires a new artifact or CoC, record why no simpler approach works.

## 7. Changed files (since baseline)

| File | Status | Notes |
|------|--------|-------|
| | | |

## 8. Validation status

- `/review-code` — not run / passing / failing
- `/testing` — not run / passing / failing
- Bug reproduction — not attempted / reproduced / cannot reproduce
- Fix verification — not tested / verified / pending user confirmation

## 9. Next steps

1. …
2. …
3. …

## 10. Open questions for the user

Anything blocked on a user decision. For bugfixes, this often includes reproduction details or environment access.
