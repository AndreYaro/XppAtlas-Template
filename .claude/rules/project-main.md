# Project rules — main source of truth

This is the central rule file for the project. All other rules, skills, agents, and CLAUDE.md reference this hierarchy. Read this file at the start of every session.

## Rule hierarchy and precedence

Rules are layered. A narrower scope always overrides a broader one.

1. **Project rules** — `.claude/rules/*.md` — apply everywhere
2. **Model rules** — `Models/{ModelName}/rules.md` — override project rules for work inside that model
3. **Task rules** — `Models/{ModelName}/Tasks/{TaskID}/rules.md` — override model and project rules for the active task

If a task rule contradicts a project rule, the task rule wins. If a model rule is silent on a topic, the project rule applies. All three layers share the same safety boundaries (see `safety-boundaries.md`).

### Always-on rules (read every session)

The following project rules apply to every session and every task type. Read them at `/start`:

- [`project-main.md`](project-main.md) — this file
- [`safety-boundaries.md`](safety-boundaries.md) — confirmation boundaries, hard limits
- [`tool-usage.md`](tool-usage.md) — MCP tool discipline, exact-match ranking, SysOp pivot
- [`split-mode.md`](split-mode.md) — Phase 28 transparent-client read/write plane invariants
- [`fallback-and-evidence.md`](fallback-and-evidence.md) — **no-abort on remote MCP failure**, evidence-label vocabulary, cascade
- [`task-lifecycle.md`](task-lifecycle.md) — task state machine, handoff discipline

## Task-centric operating model

All work lives inside a task. A task lives inside exactly one model.

```
Models/{ModelName}/Tasks/{TaskID}_{TaskName}/
  TASK.md          ← task identity and metadata
  rules.md         ← task-type rules (generated from template)
  SNAPSHOT.md      ← working memory (the session-to-session state carrier)
  code/            ← working artifacts (NOT auto-pushed to model source)
  docs/            ← FDDs, designs, specs, investigation notes
  refcode/         ← reference code not in MCP
  samples/         ← payload examples, test data
```

### Task types

Every task has a type that shapes agent behavior:

| Type | Purpose | Behavioral emphasis |
|------|---------|-------------------|
| **analysis** | Investigation, estimation, planning, architecture exploration, impact analysis | Explore before editing; gather evidence; compare options; produce structured findings |
| **development** | Feature implementation, code/metadata changes, extension-based work | Safe incremental implementation; extension-first; checkpoint; validate before completion |
| **bugfix** | Bug investigation, root cause analysis, targeted fixes | Understand/reproduce first; distinguish symptom from root cause; smallest correct fix |

Task type is set when creating a task via `/new-task` and recorded in `TASK.md`. The corresponding `rules.md` is copied from `.claude/task-templates/{type}/rules.md`.

### Task folder semantics

| Folder | Contents | Push-back rule |
|--------|----------|----------------|
| `code/` | Working copies of X++ artifacts fetched from MCP or newly created | **Never auto-pushed.** User-driven copy back to MCP source at check-in time. |
| `docs/` | Task-related documents: FDDs, designs, specs, meeting notes, investigation writeups | Stays in repo |
| `refcode/` | Reference code not in MCP or not conveniently indexed; comparison material; legacy snippets | Read-only by default |
| `samples/` | Sample payloads: JSON, XML, CSV, interface examples, test data | Reference assets, not implementation |

## X++ / D365FO core principles

These principles apply to all task types. They are non-negotiable unless a task rule explicitly overrides one with a recorded justification.

### Extension strategy (priority order)

1. **Event handler** on an existing delegate or post-event — lowest risk, fully upgrade-safe
2. **Chain of Command** (`[ExtensionOf(...)]` + mandatory `next`) — proven, widely supported
3. **Table / Form / Data Entity extension** — for adding fields, field groups, controls, mappings
4. **New artifact with `{ProjectPrefix}` prefix** — only when no extension point fits; record reason in SNAPSHOT §6
5. **Overlayering** — forbidden unless the user explicitly authorizes it for this specific task

### Coding standards

| Area | Rule |
|------|------|
| **Prefix** | Every new AOT object starts with `{ProjectPrefix}` from `context_setup.md` |
| **Extensions** | `{Prefix}[Original]_Cls_Extension`, `_Tab_Extension`, `_Form_Extension`, `_Entity_Extension` |
| **Variables** | `camelCase`; no Hungarian notation; parameters prefixed with `_` |
| **Labels** | No hardcoded user-facing strings; use Label IDs from `{LabelFile}` |
| **Queries** | Never `select *`; always enumerate required fields |
| **Transactions** | `ttsBegin`/`ttsCommit` open and close in the **same method**; `throw error(...)` never `ttsAbort` |
| **Null checks** | Validate record existence before field access |
| **Set-based** | Row-by-row insert/update/delete over >1 record must use `insert_recordset`/`update_recordset`/`delete_from` |
| **Method length** | Prefer < 50 lines; extract helpers when exceeded |
| **Dead code** | Delete unused code; never comment it out |
| **TODO format** | `// TODO: [{UserVISA}] <description>` |
| **File location** | Generated XML goes in `code/AxClass/`, `code/AxTable/`, etc. within the task folder |

### Model and package boundaries

- Respect model ownership. One task edits one model only.
- If work spills into another model, stop and create a separate task in that model.
- Record secondary/impacted models in TASK.md but do not edit their artifacts from the primary task.
- Understand package references before adding cross-model dependencies.

### High-risk areas

Extra care required around:
- Posting logic (`*Post`, `*Journal*`, `*Voucher*`, tax, ledger, inventory valuation)
- Transaction boundaries (`ttsbegin`/`ttscommit`)
- Cross-company behavior
- Number sequences, aging, settlement, period-end
- Workflow approval paths
- Integration classes with live external counterparts
- Security roles, duties, privileges

For edits in these areas: state the impact radius, get user confirmation, and consider spawning `d365-architect` for impact review.

## Context recovery behavior

At the start of every session:

1. Read this file and the other project rules
2. Read the active model's `rules.md` if it exists
3. Read the active task's `rules.md` and `SNAPSHOT.md`
4. Load `context_setup.md` bottom-up: task → model → project
5. Work according to the task type
6. Checkpoint after meaningful milestones
7. Summarize before switching subproblems
8. Recover deliberately when context gets noisy
