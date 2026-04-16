# D365 Project Template — Setup & Usage Guide

A project template for D365 Finance & Operations customization work driven from Claude Code (or Codex / VS Code / Gemini using the same skill names). It encodes a **baseline-first, per-task-SNAPSHOT, MCP-only** workflow so a development team can customize a D365 F&O model across many tasks without losing context between sessions and without corrupting the production source line.

Use this file to:

1. Understand what the template gives you.
2. Clone it into a new customer project.
3. Run your first task end-to-end.
4. Keep sessions coherent across days and compactions.

---

## 1. What this template is

A prebuilt `.claude/` configuration plus a `Models/` layout that enforces four rules:

- **MCP is the only authoritative source of X++ code.** All discovery and all baseline fetches go through the local D365 MCP server (`mcp__xppatlas__*`). No local `Source/` folder is read. No sibling repo is read.
- **One task = one folder = one model.** Each task lives under `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/` and never spills into another model.
- **Baseline before edit.** For any task that modifies existing artifacts, the untouched current version is fetched from MCP and committed to Git *before* any edit is made. The task's real change set is then the Git diff from that baseline commit.
- **Per-task SNAPSHOT.md is the cross-session memory.** Every task owns a `SNAPSHOT.md` that survives compactions and hand-offs between Claude sessions. There is no global snapshot file.

The template ships:

- A `CLAUDE.md` project passport with a 7-step session protocol.
- 5 rule files in `.claude/rules/` covering autonomy, context discipline, X++ change safety, commit/checkpoint discipline, and production caution.
- 5 session skills in `.claude/skills/` (`session-start`, `session-finish`, `testing`, `housekeeping`, `fetch-baseline`) and the existing task skills (`new-task`, `review-code`, `prep-comment`, etc.).
- Specialist agent definitions (`d365-developer`, `d365-architect`) aligned across Claude Code, Codex, and Gemini.
- `SessionStart`, `PreCompact`, and `Stop` hooks in `.claude/settings.json` with a curated permissions allow/deny list.
- A per-task `SNAPSHOT.md` template under `Models/_Model_Template/Tasks/_Task_Template/`.
- A `.claude/CLEANUP_CANDIDATES.md` that `/housekeeping` appends to, never auto-executes.

---

## 2. Prerequisites

Before cloning the template into a customer project you need:

- **Windows + Git Bash** (the template assumes Unix shell syntax for Bash tool calls on Windows).
- **Python 3.x** on `PATH` (the hooks call `python tools/ensure_index.py`).
- **Claude Code** installed, with access to an Anthropic API key or equivalent credential.
- **XppAtlas MCP server** (`xppatlas`) running locally or reachable on a LAN server. This is the only path to X++ source — the template will not read from any local `Source/` folder. See [XppAtlas](https://github.com/AndreYaro/XppAtlas) for installation.
- **TFVC workspace** for the customer's production D365 codeline (the user performs check-ins outside Claude). This is *not* driven by Claude — the template only prepares check-in comments.

### 2.1. XppAtlas deployment modes

XppAtlas supports two deployment shapes that the template works with transparently:

- **Local mode** — the MCP server runs on the developer's own machine and serves every model (standard, vendor, custom) from local databases. Simplest setup; heaviest disk and RAM footprint.
- **Server/client split** — a shared Ubuntu LAN server hosts the large standard models (ApplicationSuite, ApplicationFoundation, …) behind an HTTP API; each developer's local client handles only the customer's custom + vendor models and proxies standard-model queries to the server. Recommended for teams larger than one or two developers.

The template does not care which mode you run — both expose the same `mcp__xppatlas__*` tool surface. The split is configured in `.env` (see §3.2 below) and in `.vscode/mcp.json`.

---

## 3. Clone and configure a new project from the template

### 3.1. Copy the template

Copy the whole `XppAtlas-Template` folder to your new project location, e.g.:

```
C:\Work\GitHub\D365<CustomerName>\
```

Initialize it as a Git repository if it is not already one.

### 3.2. Fill in the project identity

Edit these files and replace the `{Placeholders}`:

- **`context_setup.md`** (project root):
  - `ProjectPrefix` — AOT prefix for every new object this project creates (e.g. `VAU`, `DYS`, `ACM`). 3 letters is typical.
  - `LabelFile` — target label file for all new labels (e.g. `VaudoiseLabel`).
  - `LabelLanguages` — comma-separated translation targets (e.g. `en-us, fr-ch, de-ch, it-ch`).
  - `UserVISA` — the developer's check-in initials, used in TODO markers and TFVC comments.
  - `AutoTranslate` — `true` or `false`.
- **`CLAUDE.md`** — replace `{ProjectName}` and `{ModelName}` with the real names. Update the short description paragraph at the top to describe what the customer does and which models are in scope.
- **`README.md`** — replace `{ProjectName}`, `{Organization}`, `{ProjectPrefix}`, `{LabelFile}`, `{LabelLanguages}`, `{UserVISA}` in the overview table.
- **`.claude/settings.json`** — in the `SessionStart` hook message, replace `{ProjectName}` and `{ModelName}` so the session-start reminder is specific to this project.
- **`.env`** — copy `.env.example` to `.env` and fill in:
  - `XPPATLAS_STANDARD_SERVER_URL` — only if you are in server/client split mode; leave blank for local mode.
  - `XPPATLAS_SOURCE_ROOT` — path to this project's custom/vendor model source tree.
  - `OPENAI_API_KEY` or `XPPATLAS_EMBEDDING_MODEL` — pick an embedding option.
  The `.env` file is gitignored and must never be committed.
- **`.vscode/mcp.json`** — verify the `command` and `cwd` point at your local XppAtlas checkout (stdio mode). If you are using server/client split over HTTP, uncomment and edit the `xppatlas-http` entry to point at the LAN server's `/mcp` endpoint.

### 3.3. Create one folder per model

For each D365 model the project will customize, create:

```
Models/{ModelName}/
  context_setup.md      ← model-level overrides (ProjectPrefix, LabelFile, etc. if different from project)
  Tasks/                ← empty; tasks are scaffolded on demand
```

Copy `Models/_Model_Template/context_setup.md` as the starting point for each model. Keep `Models/_Model_Template/` in place — do not delete it, `/new-task` uses its `_Task_Template/SNAPSHOT.md` as the snapshot source.

Single-model projects have exactly one folder here; multi-model projects (e.g. a core model plus integration models) have one folder per model.

### 3.4. Verify the D365 MCP server is reachable

Inside Claude Code, ask:

```
Use mcp__xppatlas__list_models to list every model the MCP server knows about.
```

If the list does not include your target model(s), stop — the MCP server is not indexing the right source. Fix the MCP configuration before doing anything else. The template will refuse to read from local `Source/` folders, so if MCP is broken, nothing else will work.

### 3.5. Validate the setup

Run the bundled validator:

```
pwsh -File .\validate-ai-setup.ps1
```

It checks that shared rules, agents, and skill catalogs are consistent across Claude Code, Codex, and Gemini.

### 3.6. First Git commit

Make a single commit with all the renames and placeholder fills, message e.g.:

```
chore: instantiate template for {ProjectName}
```

This is the project's "origin" — everything after it is task work.

---

## 4. Daily workflow — running a task end to end

Every task, regardless of size, follows the same lifecycle. Skipping a step corrupts the baseline and makes the change set unreviewable.

### 4.1. Open a session

Start Claude Code in the project root. The `SessionStart` hook will remind Claude to run `/session-start` before anything else. At the start of the conversation, say:

```
/session-start
```

Claude will:

1. Run `git status` and `git log` to find the active task.
2. Read the active task's `SNAPSHOT.md`.
3. Read `context_setup.md` bottom-up.
4. Read the 5 rule files in `.claude/rules/`.
5. Verify every file under `code/**` has a baseline commit.
6. Report readiness.

If there is no active task yet, Claude will ask — skip to §4.2.

### 4.2. Scaffold a new task

```
/new-task {ModelName} {TaskID} {TaskName}
```

Example: `/new-task Vaudoise 3641 INT001_DMS_Invoicing`

This creates `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/` with:

- Empty `code/Ax*/` folders.
- `context_setup.md` for task-level overrides.
- `README.md` skeleton.
- `code_review_checklist.md` prefilled with project rules.
- **`SNAPSHOT.md`** copied from `Models/_Model_Template/Tasks/_Task_Template/SNAPSHOT.md` with frontmatter filled in.

**Before anything else**, fill in `SNAPSHOT.md` §1 Purpose, §2 Scope, §3 Constraints. Claude will refuse to start editing if these are empty.

Commit this scaffold as its own Git commit, e.g.:

```
{TaskID} scaffold: new task folder for {TaskName}
```

### 4.3. Fetch the baseline

For any existing AOT artifact this task will modify:

```
/fetch-baseline AxClass:CustInvoiceJour AxTable:CustInvoiceJour AxForm:CustInvoiceJournal
```

Claude will:

1. Call `mcp__xppatlas__get_artifact` with the active `model_name`.
2. Write each artifact byte-for-byte to `Models/{ModelName}/Tasks/{TaskID}_*/code/Ax{Type}/{ObjectName}.xml`.
3. Append a row to `SNAPSHOT.md` §4 Source artifacts.
4. **Stop and wait** — it will not make any edits until you commit the baseline.

**You commit the baseline yourself**, e.g.:

```
{TaskID} baseline: fetched from MCP
```

Reply to Claude with the short SHA. It records the SHA in `SNAPSHOT.md` §4 and begins edit work. This baseline commit is what turns the rest of the task into a reviewable Git diff.

If the task creates only new artifacts (no existing ones to baseline), skip this step and record "no baseline needed — all new artifacts" in `SNAPSHOT.md` §4.

### 4.4. Edit

Work in the normal Claude Code flow: describe the change, review the diff, iterate. Claude follows the extension-strategy priority order from `.claude/rules/20-xpp-change-safety.md`:

1. Event handler on an existing delegate or post-event.
2. Chain of Command (`[ExtensionOf(...)]` with mandatory `next` call).
3. Table / Form / Data Entity extension.
4. New artifact with `{ProjectPrefix}` prefix.
5. Overlayering — only with explicit user authorization.

If Claude chooses option 4 or 5, it records the reason in `SNAPSHOT.md` §6.

**Checkpoint discipline during edits:**

- Every 5+ file edits, Claude updates `SNAPSHOT.md` §7 Changed files and §9 Next steps.
- Before running any validation skill, Claude checkpoints the snapshot.
- Before ending the session, Claude checkpoints the snapshot.
- The `PreCompact` hook reinforces this right before Claude would compact the conversation.

### 4.5. Validate

```
/review-code        ← full code review against project rules
/audit-arch         ← separation-of-concerns audit
/fix-perf           ← convert row-by-row loops to set-based (report mode)
/testing            ← static validation of the task folder
```

These are all **read-only reports**. They never claim a build passed — Claude cannot run the X++ compiler. `/testing` explicitly lists what CANNOT be verified without a live build.

Fix any findings and checkpoint again.

### 4.6. Prepare the TFVC check-in

```
/prep-comment
```

This produces the TFVC check-in comment string in the form:

```
{TaskID} {UserVISA} <short description>
```

Claude does **not** run `tf` — those commands are denied in `.claude/settings.json`.

### 4.7. Write back to the MCP source store (manual, user-driven)

**Outside Claude Code**, copy the final files from:

```
Models/{ModelName}/Tasks/{TaskID}_*/code/Ax{Type}/*.xml
```

…into the MCP source store, typically:

```
C:/Work/GitHub/XppAtlas/models-src/custom/{ModelName}/Ax{Type}/
```

Then re-index the MCP server so the next session sees the updated source. This is the **only** legitimate write from the task folder into a sibling repo, and it is always user-driven — Claude never automates it.

Finally, check in to TFVC using the comment from `/prep-comment`.

### 4.8. Close the session

```
/session-finish
```

Claude updates `SNAPSHOT.md` §5, §7, §8, §9, §10 and prints a handoff summary for the next session. The `Stop` hook refreshes the local search index afterwards.

---

## 5. Cross-session context — how the template keeps Claude coherent

Long D365 sessions degrade predictably: Claude re-explores the same files, forgets earlier decisions, drifts scope. The template defends against this with three mechanisms:

- **Per-task SNAPSHOT.md** — Claude reads it at the start of every session. It carries purpose, scope, decisions log, extension strategy, changed files, validation status, next steps, and open questions. It is the *only* state guaranteed to survive a compaction.
- **`PreCompact` hook** — fires right before Claude would compact the conversation, forcing a snapshot update so the post-compact session can resume cleanly.
- **Checkpoint triggers** — `.claude/rules/10-context-and-snapshot.md` lists explicit moments when the snapshot must be updated (every 5 edits, before validation, before end-of-session).

If a session ever feels degraded (Claude revisits files, contradicts earlier decisions, asks for info already recorded), **stop, run `/session-finish`, restart, run `/session-start`**. The new session will resume from the snapshot instead of the corrupted running conversation.

---

## 6. Multi-model projects

The template supports both single-model and multi-model repos. For a multi-model project (e.g. a core customer model plus separate integration models):

- Create one `Models/{ModelName}/` folder per model.
- Each model has its own `context_setup.md` — it can override `ProjectPrefix` and `LabelFile` if that model uses different values from the project default.
- **One task = one model**, always. If a change has to touch two models, open two tasks, one per model, and coordinate them via `SNAPSHOT.md` §3 Constraints.
- Claude will refuse to cross a model boundary inside a single task. This is intentional.

---

## 7. What is safe vs what requires confirmation

### Claude will do without asking

- Read any file inside this repository.
- Run any `mcp__xppatlas__*` read-only tool.
- Run read-only Git: `status`, `log`, `diff`, `show`, `branch`.
- Run the bundled Python helpers (`tools/ensure_index.py`, `tools/search_index.py`, `tools/bootstrap_context.py`, `tools/index_all.py --incremental`).
- Update the active task's `SNAPSHOT.md` and `docs/`.

### Claude will ask first

- Create, rename, or delete files outside the active task folder.
- Touch shared project files (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `.claude/settings.json`, `.claude/rules/**`, `.mcp.json`, `.gitignore`).
- Edit a posting class, number sequence, tax, settlement, workflow approval, or live integration handler.
- Change security roles, duties, or privileges.
- Any refactor crossing ≥ 3 AOT artifacts.

### Claude will refuse, every time

- `git commit`, `git push`, `git reset --hard`, `git checkout -- <path>`, branch deletion — denied in `.claude/settings.json`.
- `tf` / TFVC commands — denied.
- `scripts/build-v4-model.bat` — denied.
- Deploy, model publish, package build, or any environment-mutating command.
- Read or write outside this repository — the only exception is the user-driven copy back to the MCP source store at check-in time, which is performed manually outside Claude Code.
- Commit a secret, `.env` file, `.pfx`, or build artifact.

To change these, edit the `permissions.deny` list in `.claude/settings.json` — with full awareness of the risk.

---

## 8. Maintenance

### Housekeeping

Run `/housekeeping` periodically. It audits:

- Tasks with missing or stale `SNAPSHOT.md`.
- Task folders with no baseline commit.
- Duplicate task folders (leading whitespace, case collisions).
- Shared-config drift.
- Cross-task contamination.

Findings are **appended** to `.claude/CLEANUP_CANDIDATES.md`. The skill never deletes or renames anything — the user does that manually after reviewing.

### Updating rules

Rules live in `.claude/rules/00-autonomy.md` through `40-production-caution.md`. Any change to them should be committed with a message that explains the rule delta, e.g.:

```
rules: loosen 00-autonomy to allow git show without confirmation
```

Keep them short. Rules longer than a page tend to be ignored.

### Secrets in `.mcp.json`

`.mcp.json` may contain API keys or PATs for the MCP server. **Never commit secrets**. If you find one in `.mcp.json`, rotate the key and move it to an environment variable or OS keystore. Claude will flag this on discovery.

---

## 9. Reference — file and folder map

```
D365{ProjectName}/
├── CLAUDE.md                        ← project passport + 7-step session protocol
├── GEMINI.md                        ← shared X++ standards (referenced by CLAUDE.md)
├── AGENTS.md                        ← Codex repo rules (mirror of CLAUDE.md)
├── README.md                        ← human-facing project overview
├── SETUP_AND_USAGE.md               ← this file
├── context_setup.md                 ← project-level ProjectPrefix, LabelFile, UserVISA
├── validate-ai-setup.ps1            ← consistency check across tools
│
├── .claude/
│   ├── settings.json                ← hooks + permissions allow/deny
│   ├── CLEANUP_CANDIDATES.md        ← /housekeeping findings (human-resolved)
│   ├── rules/
│   │   ├── 00-autonomy.md           ← confirmation boundaries + hard repo boundary
│   │   ├── 10-context-and-snapshot.md  ← per-task SNAPSHOT + anti-degradation
│   │   ├── 20-xpp-change-safety.md  ← artifact lifecycle + extension-strategy order
│   │   ├── 30-commit-and-checkpoint.md ← Git/TFVC + checkpoint triggers
│   │   └── 40-production-caution.md ← posting / integration / security hard limits
│   ├── skills/
│   │   ├── session-start/           ← cold-open procedure
│   │   ├── session-finish/          ← end-of-session handoff
│   │   ├── testing/                 ← scope-aware static validation
│   │   ├── housekeeping/            ← non-destructive audit
│   │   ├── fetch-baseline/          ← MCP → task folder, byte-for-byte
│   │   ├── new-task/                ← scaffold a new task
│   │   ├── review-code/
│   │   ├── audit-arch/
│   │   ├── fix-perf/
│   │   ├── gen-coc/
│   │   ├── gen-batch/
│   │   ├── gen-entity/
│   │   ├── gen-service/
│   │   ├── design-integration/
│   │   ├── prep-comment/
│   │   └── explain/
│   ├── agents/
│   │   ├── README.md                ← role map
│   │   ├── d365-developer.md
│   │   └── d365-architect.md
│   └── hooks/
│       └── README.md                ← SessionStart / PreCompact / Stop docs
│
├── skills/                          ← Codex / VS Code skill mirror
│
├── tools/                           ← Python helpers (indexer, search)
│
└── Models/
    ├── _Model_Template/             ← template — do not delete
    │   ├── context_setup.md
    │   └── Tasks/
    │       └── _Task_Template/
    │           ├── SNAPSHOT.md      ← copied into every new task
    │           ├── README.md
    │           ├── code_review_checklist.md
    │           ├── context_setup.md
    │           ├── code/
    │           ├── docs/
    │           ├── samples/
    │           └── refcode/
    │
    └── {ModelName}/                 ← one folder per real AX model
        ├── context_setup.md
        └── Tasks/
            └── {TaskID}_{TaskName}/
                ├── SNAPSHOT.md      ← per-task cross-session state
                ├── README.md
                ├── code_review_checklist.md
                ├── context_setup.md
                ├── code/Ax{Type}/   ← baseline + edits
                ├── docs/
                ├── samples/
                └── refcode/
```

---

## 10. Troubleshooting

**`list_models` does not show my model.**
The MCP server is not indexing that model. Fix the MCP configuration — do not try to work around it by pointing at a local `Source/` folder.

**Claude is editing files with no baseline commit.**
Stop the session. Run `/session-finish`, inspect `git log` for a baseline commit of those files, and if missing, either run `/fetch-baseline` retroactively (acceptable — creates an honest baseline) or revert the edits.

**`SNAPSHOT.md` says "passing" for something Claude did not run.**
Edit the snapshot manually to say "not run". The rule in `.claude/rules/10-context-and-snapshot.md` forbids fabricating validation status; if you see it, treat it as a bug in the session and correct it.

**Claude reaches into a sibling repo.**
Stop immediately. This violates `.claude/rules/00-autonomy.md`. Close the session without committing, verify nothing outside the repo was modified, and reopen with `/session-start` — the reminder from the `SessionStart` hook will reinforce the boundary.

**A task spans two models.**
Split it. One task = one model. Open a second task in the second model and reference both in each task's `SNAPSHOT.md` §3 Constraints.

**Context feels degraded mid-session.**
Run `/session-finish`, then restart Claude, then `/session-start`. The new session will resume from the snapshot, ignoring the degraded conversation tail.

---

## 11. Where to learn more

- `CLAUDE.md` — project passport, session protocol, skill catalog.
- `GEMINI.md` — X++ naming, syntax, XML structure rules.
- `.claude/rules/*.md` — authoritative rules. Read these before changing behavior.
- `.claude/skills/*/SKILL.md` — per-skill instructions.
- `.claude/agents/README.md` — when to delegate to `d365-developer` vs `d365-architect`.
- `.claude/hooks/README.md` — what each hook does and why.
