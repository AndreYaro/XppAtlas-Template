# XppAtlas-Template — Tool Reference

| | |
|---|---|
| **Document type** | Skill + Hook + Rule Reference |
| **Audience** | Developers and project leads |
| **Version** | 1.0 |
| **Last updated** | 2026-04-16 |

---

## 1. Skills overview

Skills are slash-commands in Claude Code (and their Codex / Gemini equivalents). Every skill is a standalone `SKILL.md` file under `.claude/skills/{skill-name}/` that tells Claude the exact steps to take.

| Category | Count | Purpose |
|----------|-------|---------|
| Session lifecycle | 2 | Cold-open and close-out |
| Task lifecycle | 3 | Task-boundary workflows |
| Validation | 4 | Read-only reports |
| Generation | 4 | Scaffold mechanism-specific code |
| Design | 2 | Multi-artifact reasoning |
| Maintenance | 1 | Non-destructive audit |

---

## 2. Session lifecycle skills

### `/session-start`

**What it does.** Cold-opens a session. Runs `git status` and `git log` to find the active task, reads its `SNAPSHOT.md`, reads `context_setup.md` bottom-up, reads the five rule files in `.claude/rules/`, verifies every file under the active task's `code/` has a baseline commit, and prints a readiness report.

**When to use.** At the start of every conversation, always. The `SessionStart` hook reminds Claude to run it.

**What it reads.**

- `git status --short` and `git log --oneline -20`
- `Models/*/Tasks/*/SNAPSHOT.md` (active task only)
- `context_setup.md` at project root, then model level, then task level
- `.claude/rules/00-autonomy.md` through `.claude/rules/40-production-caution.md`

**What it writes.** Nothing. Read-only.

### `/session-finish`

**What it does.** Closes the session cleanly. Updates the active task's `SNAPSHOT.md` — specifically §5 Decisions log, §7 Changed files, §8 Validation status, §9 Next steps, §10 Open questions — and prints a one-paragraph handoff summary.

**When to use.** At the end of every session, always. Especially before restarting a degraded session.

**What it writes.** `Models/{ActiveModel}/Tasks/{ActiveTask}/SNAPSHOT.md`.

---

## 3. Task lifecycle skills

### `/new-task`

**Signature.** `/new-task {ModelName} {TaskID} {TaskName}`

**What it does.** Scaffolds `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/` from `Models/_Model_Template/Tasks/_Task_Template/`. Fills in the SNAPSHOT frontmatter with the task id, task name, and today's date. Does not commit — the developer commits the scaffold afterwards.

**Guardrails.**

- Refuses if `{ModelName}` doesn't exist under `Models/` (forces the user to scaffold the model folder first).
- Refuses if the task folder already exists.

### `/fetch-baseline`

**Signature.** `/fetch-baseline AxClass:CustInvoiceJour AxTable:CustInvoiceJour ...`

**What it does.** Calls `mcp__xppatlas__get_artifact` with the active model_name for each artifact. Writes the returned XML byte-for-byte into `code/Ax{Type}/{ObjectName}.xml`. Appends a row to `SNAPSHOT.md §4 Source artifacts`. **Stops and waits** — does not make any edits until the developer commits the baseline.

**Guardrails.**

- Refuses if any artifact is not found in MCP (forces the user to fix the MCP config or choose a different artifact).
- Refuses if the file already exists and has uncommitted edits (would overwrite work).

### `/prep-comment`

**What it does.** Produces a TFVC check-in comment in the canonical form `{TaskID} {UserVISA} <short description>`. Pulls `{TaskID}` from the active task folder name and `{UserVISA}` from `context_setup.md`. Does **not** run `tf` or any TFVC command.

---

## 4. Validation skills

All four are read-only reports. They never claim the build passed — Claude cannot run the X++ compiler.

### `/review-code`

Full code review against project rules. Checks:

- Extension-strategy order (picked the right mechanism for the change).
- `{ProjectPrefix}` on new artifacts.
- Naming conventions (from `GEMINI.md`).
- Transaction safety: tts balance, no try-in-tts, no nested tts.
- Performance: no select-in-loop, firstOnly where applicable.
- Security: no direct SQL concat, changeCompany in scoped block, queryValue guarded.
- Label discipline: new strings go to `{LabelFile}`, translations present per `{LabelLanguages}`.

### `/audit-arch`

Separation-of-concerns audit across touched artifacts. Flags:

- Business logic in form event handlers (should be on a controller / data contract).
- Posting logic outside the posting class (should be in `*Post` extensions).
- Cross-model references that violate the one-task-one-model rule.
- Framework-mixing (RunBase + SysOperation in the same batch).

### `/fix-perf`

Report mode for performance anti-patterns. Flags:

- Row-by-row loops that should be set-based (update_recordset, delete_from, insert_recordset).
- Multiple select statements that could be joined.
- Missing indexes implied by where clauses.

Does not auto-fix. Produces a report the developer reviews and acts on.

### `/testing`

Static validation of the task folder. Checks:

- `SNAPSHOT.md` §8 Validation status is plausible (no "passing" claims for things nothing ran).
- Every file under `code/` has a baseline or is marked new.
- Extension attributes match containing artifacts (`[ExtensionOf]` class names match the file name pattern).
- XML well-formedness.

**Explicitly lists what cannot be verified.** Compile clean, BP clean, SysTest green — these require a live build, which Claude cannot run. For those, ingest the build log via XppAtlas: `mcp__xppatlas__ingest_build_log`.

---

## 5. Generation skills

All four scaffold new code. They respect `{ProjectPrefix}` from `context_setup.md` and place files in the active task's `code/Ax{Type}/` folder.

### `/gen-coc`

Scaffolds a Chain of Command class. Produces `{ProjectPrefix}_{BaseClass}_Extension.xpp` with `[ExtensionOf(classStr(...))]`, mandatory `next` calls, and extension-attribute plumbing.

### `/gen-batch`

Scaffolds a SysOperation batch. Produces the data contract, controller, and service classes with correct attributes, plus the menu item wiring.

### `/gen-entity`

Scaffolds a Data Entity. Produces the entity XML with data source, field mapping, staging table reference, and public/privateKey fields set correctly.

### `/gen-service`

Scaffolds a service class (AIF / custom service). Produces the service class, service group registration, and operation signatures.

---

## 6. Design skills

### `/design-integration`

Multi-artifact reasoning for new integrations. Walks the integration landscape (inbound / outbound / bidirectional × REST / SOAP / OData / file / batch), picks a transport, designs the staging + posting flow, identifies error-handling patterns. Produces a design document under `docs/` — does not generate code directly.

### `/explain`

Walks the caller through an existing artifact or flow. Pulls the artifact from MCP via `mcp__xppatlas__explore_artifact`, traces references via `mcp__xppatlas__find_references`, and produces a narrative explanation with clickable references.

---

## 7. Maintenance skills

### `/housekeeping`

Non-destructive audit. Appends findings to `.claude/CLEANUP_CANDIDATES.md`. Never deletes or renames anything. See [Admin Guide §5](04-admin-guide.md#5-housekeeping) for the full list of checks.

---

## 8. Hooks

Three hooks in `.claude/settings.json`:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `SessionStart` | Every conversation start | Print project-specific reminder so Claude runs `/session-start` first |
| `PreCompact` | Right before conversation compaction | Force a `SNAPSHOT.md` update so post-compact session can resume cleanly |
| `Stop` | Conversation end | Run `python tools/ensure_index.py --incremental` to refresh local search index |

Hook payloads are short prompts; `SessionStart` prints a one-paragraph reminder naming the project, the active task discovery procedure, and the five rule files.

---

## 9. Rules

Five numbered rule files under `.claude/rules/`. Claude reads them at `/session-start`.

| File | Key invariants |
|------|-----------------|
| `00-autonomy.md` | Repo-scope hard limit; confirmation required for shared files; refuse `git push`, `git reset --hard`, destructive git |
| `10-context-and-snapshot.md` | Per-task SNAPSHOT mandatory; checkpoint at 5-edit boundaries, before validation, before session end; never fabricate validation status |
| `20-xpp-change-safety.md` | Extension-strategy order 1→5; baseline before edit; `{ProjectPrefix}` on new artifacts; labels via `{LabelFile}` only |
| `30-commit-and-checkpoint.md` | Commits are deliberate, user-initiated; baseline commits are separate from edit commits; no `--amend` after push |
| `40-production-caution.md` | Posting / integration / number-sequence / tax / security changes require explicit user confirmation, regardless of size |

Full rule text lives in the files themselves. They are one page each by policy — longer rules get ignored.

---

## 10. MCP tool surface used by the template

The template delegates all D365 knowledge work to the XppAtlas MCP server. The skills rely on this subset:

| Tool | Used by |
|------|---------|
| `mcp__xppatlas__list_models` | `/session-start`, `/new-task` (sanity check) |
| `mcp__xppatlas__get_artifact` | `/fetch-baseline` |
| `mcp__xppatlas__search_artifacts` | `/audit-arch`, `/explain` |
| `mcp__xppatlas__explore_artifact` | `/explain`, `/review-code` |
| `mcp__xppatlas__find_references` | `/audit-arch`, `/explain` |
| `mcp__xppatlas__build_edit_bundle` | `/review-code` |
| `mcp__xppatlas__recommend_patterns` | `/gen-coc`, `/gen-batch`, `/gen-entity`, `/gen-service` |
| `mcp__xppatlas__propose_extension_strategy_v2` | `/review-code` (when the extension-strategy choice is non-obvious) |
| `mcp__xppatlas__ingest_build_log` | User-driven, referenced by `/testing` as the path to real compile / BP / test signals |
| `mcp__xppatlas__assess_task_readiness` | User-driven, referenced by `/prep-comment` as the path to a frozen readiness snapshot |

The full XppAtlas tool surface (143 tools as of Phase 23) is documented in the [XppAtlas Tool Reference](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/06-tool-reference.md). The template's skills only directly invoke the subset above; the rest are available to the developer through direct MCP calls.

---

## See also

- [User Guide](03-user-guide.md) — daily workflow showing skills in action
- [Architecture Reference](05-architecture.md) — why the skill / rule / hook layering is shaped this way
- [Configuration Reference](07-configuration.md) — how to edit `.claude/settings.json` to tune the permissions and hooks
