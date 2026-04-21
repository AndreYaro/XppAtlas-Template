# XppAtlas-Template — User Guide

| | |
|---|---|
| **Document type** | Daily Workflow Guide |
| **Audience** | D365 developers delivering customer tasks |
| **Version** | 1.0 |
| **Last updated** | 2026-04-16 |

---

## Table of Contents

1. [Daily session lifecycle](#1-daily-session-lifecycle)
2. [Starting a new task](#2-starting-a-new-task)
3. [Fetching the baseline](#3-fetching-the-baseline)
4. [Editing safely](#4-editing-safely)
5. [Extension-strategy decision order](#5-extension-strategy-decision-order)
6. [Validation and review](#6-validation-and-review)
7. [TFVC check-in preparation](#7-tfvc-check-in-preparation)
8. [Writing back to MCP source](#8-writing-back-to-mcp-source)
9. [Closing the session](#9-closing-the-session)
10. [Cross-session context discipline](#10-cross-session-context-discipline)

---

## 1. Daily session lifecycle

Every day, every task, every developer follows the same five-phase loop:

```
/session-start   →  load SNAPSHOT, check rules, find active task
                    ↓
/new-task or /fetch-baseline (only at task boundaries)
                    ↓
(edit)           →  Claude edits with extension-strategy awareness
                    ↓
/review-code / /audit-arch / /fix-perf / /testing
                    ↓
/session-finish  →  update SNAPSHOT, prep handoff, exit cleanly
```

The `SessionStart` hook in `.claude/settings.json` reminds Claude to run `/session-start` before anything else. If you skip it, the session will have no memory of the active task.

## 2. Starting a new task

```
/new-task {ModelName} {TaskID} {TaskName}
```

Example: `/new-task Vaudoise 3641 INT001_DMS_Invoicing`

Creates `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/` with:

| File | Purpose |
|------|---------|
| `SNAPSHOT.md` | Cross-session state (copied from `_Task_Template/SNAPSHOT.md`) |
| `README.md` | Human-facing task summary |
| `code_review_checklist.md` | Prefilled with project rules |
| `context_setup.md` | Task-level overrides (rarely needed) |
| `code/Ax*/` | Empty folders, one per AOT type |
| `docs/` | Design documents |
| `samples/` | Example payloads |
| `refcode/` | Reference code from standard or vendor models |

**Fill in `SNAPSHOT.md` §1 Purpose, §2 Scope, §3 Constraints before any edit.** Claude refuses to start editing if they are empty — this is enforced by `.claude/rules/10-context-and-snapshot.md`, not a convention.

Then commit the scaffold as its own Git commit:

```bash
git commit -am "{TaskID} scaffold: new task folder for {TaskName}"
```

## 3. Fetching the baseline

For any existing AOT artifact the task will modify:

```
/fetch-baseline AxClass:CustInvoiceJour AxTable:CustInvoiceJour AxForm:CustInvoiceJournal
```

Claude calls `mcp__xppatlas__get_artifact` with the active `model_name`, writes each artifact byte-for-byte into the task's `code/Ax{Type}/` folder, appends a row to `SNAPSHOT.md` §4 Source artifacts, and **stops**. It will not make any edits until you commit the baseline yourself:

```bash
git commit -am "{TaskID} baseline: fetched from MCP"
```

Reply to Claude with the short SHA. Claude records it in `SNAPSHOT.md` §4 and begins edit work.

**Why a separate baseline commit?** The task's real change set is the Git diff from this SHA to `HEAD`. Without a baseline commit, any accidental layering delta in the environment would be indistinguishable from the customer's changes. Baseline-first makes the diff reviewable.

If the task creates only new artifacts (no existing ones to baseline), skip this step and record "no baseline needed — all new artifacts" in `SNAPSHOT.md` §4.

## 4. Editing safely

Work in the normal Claude Code flow: describe the change, review the diff, iterate. Two disciplines run in parallel:

**Extension-strategy order** — Claude follows the priority order from `.claude/rules/20-xpp-change-safety.md` (see §5 below).

**Checkpoint discipline** — `.claude/rules/10-context-and-snapshot.md` requires `SNAPSHOT.md` updates at explicit moments:

| When | Claude updates |
|------|-----------------|
| Every 5+ file edits | §7 Changed files, §9 Next steps |
| Before running any validation skill | Full checkpoint |
| Before `PreCompact` fires | Full checkpoint (hook-driven) |
| Before `/session-finish` | Full checkpoint |

If a session feels degraded — Claude revisiting files, contradicting earlier decisions, asking for info already recorded — **stop, run `/session-finish`, restart, run `/session-start`**. The new session resumes from the snapshot instead of the corrupted running conversation.

## 5. Extension-strategy decision order

Claude picks the least-invasive extension mechanism that can express the change. The order is enforced by `.claude/rules/20-xpp-change-safety.md`:

| Rank | Mechanism | Use when |
|------|-----------|----------|
| 1 | Event handler on an existing delegate or post-event | The standard artifact exposes a hook at the right boundary |
| 2 | Chain of Command (`[ExtensionOf(...)]`) with mandatory `next` call | No hook exists but the method can be wrapped |
| 3 | Table / Form / Data Entity extension | New field / control / data-source on an existing artifact |
| 4 | New artifact with `{ProjectPrefix}` prefix | A net-new class/table/form is the right answer |
| 5 | Overlayering | **Only with explicit user authorization** — logged in `SNAPSHOT.md` §6 |

If Claude chooses rank 4 or 5, it records the reason in `SNAPSHOT.md` §6 so the audit trail survives into the TFVC check-in.

Optionally, for larger decisions, call the XppAtlas decision engine explicitly:

> "Use `mcp__xppatlas__propose_extension_strategy_v2` to rank extension mechanisms for adding an approval step to `VendInvoicePost`."

The engine returns an `ExtensionDecision` record with an 8-dimension scoring table, rejected alternatives, and anti-pattern gates — stored under the XppAtlas task workspace, auditable, and can be linked to a build log via `link_execution_to_decision` once you run a compile.

## 6. Validation and review

| Skill | Scope | Writes? |
|-------|-------|---------|
| `/review-code` | Full code review against project rules | Read-only report |
| `/audit-arch` | Separation-of-concerns audit across touched artifacts | Read-only report |
| `/fix-perf` | Flags row-by-row loops that should be set-based (report mode) | Read-only report |
| `/testing` | Static validation of the task folder | Read-only report |

All four are **read-only reports**. They never claim the build passed — Claude cannot run the X++ compiler. `/testing` explicitly lists what cannot be verified without a live build (compiler clean, BP clean, SysTest green).

For actual compile / BP / SysTest signals, produce the log file with Visual Studio or the Dev Tools build chain, then feed it to XppAtlas:

> "Ingest the build log at `C:/builds/run-123.log` for task `3641`, then summarise the failures."

XppAtlas writes an immutable `ExecutionRun`, ranks findings in compiler-first order, and (if you ran `propose_extension_strategy_v2` earlier) can link compiler errors against the active decision via `link_execution_to_decision` — surfacing the decision as `NOT_READY` when reality contradicts the recommendation.

## 7. TFVC check-in preparation

```
/prep-comment
```

Produces a TFVC check-in comment in the canonical form:

```
{TaskID} {UserVISA} <short description>
```

Example: `3641 AYR INT001 DMS invoicing — event handler on CustInvoiceJour.post + new VAU_DmsInvoiceRouter`

Claude does **not** run `tf`, `tf vc checkin`, or any TFVC command — those are denied in `.claude/settings.json`. The developer performs the check-in manually.

Optionally, at this point, freeze readiness:

> "Freeze readiness for task `3641` with label `checkin-gate`."

XppAtlas writes `readiness/latest.json` + `readiness/history/{TR-*}.json` capturing the current verdict (`READY` / `NOT_READY` / `BLOCKED`) across the 8 readiness gates. Attach the readiness snapshot to the check-in comment or PR description for the audit trail.

## 8. Writing back to MCP source

The task's code lives in `Models/{ModelName}/Tasks/{TaskID}_*/code/Ax{Type}/`. The XppAtlas source store lives somewhere like `C:/Work/GitHub/XppAtlas/models-src/custom/{ModelName}/Ax{Type}/`.

**The write-back is manual and user-driven.** Claude does not automate it — the template rules forbid it as the only cross-repo write the workflow allows:

```bash
# Outside Claude Code
cp Models/Vaudoise/Tasks/3641_*/code/AxClass/*.xml \
   C:/Work/GitHub/XppAtlas/models-src/custom/Vaudoise/AxClass/

# Re-index so the next session sees the update
cd C:/Work/GitHub/XppAtlas
python -m xppatlas.platform.admin index-model Vaudoise
python -m xppatlas enrich
python -m xppatlas.platform.admin migrate-chroma
```

(Or, in server/client split mode, these index commands run on your local client for VENDOR + CUSTOM — they never run on the LAN server, which is STANDARD-only. Phase 23 enforces this at the entrypoint.)

Then check in to TFVC using the comment from `/prep-comment`.

## 9. Closing the session

```
/session-finish
```

Claude updates:

- `SNAPSHOT.md §5 Decisions log` — what was decided and why
- `SNAPSHOT.md §7 Changed files` — final list with status
- `SNAPSHOT.md §8 Validation status` — what ran, what didn't, what's pending
- `SNAPSHOT.md §9 Next steps` — what the next session should pick up first
- `SNAPSHOT.md §10 Open questions` — anything blocked on a human decision

Then prints a handoff summary: one paragraph that a fresh Claude session can read cold. The `Stop` hook refreshes the local search index afterwards.

**Never fabricate validation status.** `.claude/rules/10-context-and-snapshot.md` forbids marking something as "passing" Claude did not actually run. If the snapshot says "Compile: passing" and no build log was ingested, treat it as a session bug and correct the snapshot manually.

## 10. Cross-session context discipline

Long D365 tasks stretch across days. Context compactions erase conversation history. The template's three-layer defence:

| Layer | Mechanism | What survives |
|-------|-----------|----------------|
| 1. Per-task `SNAPSHOT.md` | Claude reads it at every `/session-start` | Purpose, scope, decisions, changed files, validation state, next steps, open questions |
| 2. `PreCompact` hook | Fires before Claude would compact the conversation, forces a snapshot write | Everything that was in §7, §8, §9 at the moment of compaction |
| 3. Checkpoint triggers | Explicit moments enumerated in `.claude/rules/10-context-and-snapshot.md` | Updated SNAPSHOT before any lossy event |

If you suspect Claude has lost the thread (re-explores a class it already read two turns ago, asks about a field it just saw, contradicts a decision from `SNAPSHOT.md §5`), run `/session-finish` and restart. The new session picks up from the snapshot, not from the degraded conversation tail.

---

## See also

- [Getting Started](02-getting-started.md) — initial setup
- [Admin Guide](04-admin-guide.md) — multi-developer setup, housekeeping
- [Tool Reference](06-tool-reference.md) — every skill, hook, and rule
- [XppAtlas User Guide](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/03-user-guide.md) — server-side retrieval, pattern workflow, decision engine, readiness gates
