# XppAtlas-Template — Configuration Reference

| | |
|---|---|
| **Document type** | Configuration Reference |
| **Audience** | Project leads, template maintainers, developers tuning their setup |
| **Version** | 1.0 |
| **Last updated** | 2026-04-16 |

---

## Table of Contents

1. [`context_setup.md` (project / model / task)](#1-context_setupmd)
2. [`.env` client configuration](#2-env-client-configuration)
3. [`.vscode/mcp.json`](#3-vscodemcpjson)
4. [`.claude/settings.json`](#4-claudesettingsjson)
5. [`SNAPSHOT.md` structure](#5-snapshotmd-structure)
6. [`validate-ai-setup.ps1` checks](#6-validate-ai-setupps1-checks)

---

## 1. `context_setup.md`

`context_setup.md` is the project identity file. It lives in three places and is read bottom-up (task → model → project) — the deepest override wins.

### Project-level fields (always required)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `ProjectPrefix` | string (3-5 chars) | Yes | AOT prefix for every new object this project creates | `VAU`, `DYS`, `ACM` |
| `LabelFile` | string | Yes | Target label file for every new label this project adds | `VaudoiseLabel` |
| `LabelLanguages` | comma-separated list | Yes | Translation targets for new labels | `en-us, fr-ch, de-ch, it-ch` |
| `UserVISA` | string (3 chars typical) | Yes | Developer check-in initials; used in TODO markers and TFVC comments | `AYR` |
| `AutoTranslate` | bool | No | Auto-generate translations for new labels when adding them | `true` or `false` (default `false`) |
| `ProjectName` | string | Yes | Human-facing project name | `Vaudoise D365 Core` |
| `Organization` | string | No | Customer organization name | `Vaudoise Assurances` |

### Model-level overrides (optional)

Per-model `Models/{ModelName}/context_setup.md` can override any project-level field. Typical use: a vendor model needs a different `ProjectPrefix`, or an integration model uses a different `LabelFile`.

### Task-level overrides (rare)

Per-task `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/context_setup.md` exists for the unusual case where a specific task needs a different prefix (e.g. a co-branded module). Almost always left empty — inheriting from the model level is the default.

---

## 2. `.env` client configuration

`.env` lives at the project root, is gitignored, and contains secrets. Copy `.env.example` to `.env` on first setup.

### XppAtlas connection

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `XPPATLAS_STANDARD_SERVER_URL` | str | empty | URL of the LAN XppAtlas server (e.g. `http://10.0.0.50:8765`). Set only in server/client split mode; leave empty for local-only |
| `XPPATLAS_SOURCE_ROOT` | str | `models-src` | Root of the local VENDOR + CUSTOM X++ source tree (client-side) |
| `XPPATLAS_DEV_MODE` | bool | `false` | In server/client split, set to `true` on the client so the local client automatically has admin rights (safe — it's your own machine) |

### Embeddings (needed for local indexing of VENDOR + CUSTOM)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | str | | OpenAI API key for cloud embeddings |
| `XPPATLAS_EMBEDDING_MODEL` | str | | Embedding model name: `text-embedding-3-small` (cloud) or `sentence-transformers/all-MiniLM-L6-v2` (local) |

See [XppAtlas Configuration Reference §3](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/07-configuration.md#3-embedding-options) for the full embedding options matrix.

### What should not be here

Secrets other than `OPENAI_API_KEY`, API tokens for external systems, any TFVC credentials. `.env` is gitignored but that's a safety net, not a substitute for discipline. Production keys live in OS keystores, not text files.

---

## 3. `.vscode/mcp.json`

Wires Claude Code / VS Code Copilot to the XppAtlas MCP server. Two shapes supported:

### Stdio mode (local-only or local XppAtlas install)

```json
{
  "servers": {
    "xppatlas": {
      "type": "stdio",
      "command": "C:/Work/GitHub/XppAtlas/.venv/Scripts/python.exe",
      "args": ["-m", "xppatlas", "start"],
      "cwd": "C:/Work/GitHub/XppAtlas"
    }
  }
}
```

### HTTP mode (server/client split over LAN)

```json
{
  "servers": {
    "xppatlas-http": {
      "type": "http",
      "url": "http://10.0.0.50:8765/mcp"
    }
  }
}
```

### Notes

- The template ships with both entries present but the HTTP one commented out. Uncomment whichever matches your deployment mode.
- Do not put API tokens directly in `mcp.json` — if you need one, read it from an environment variable via the `env` field and document the variable in `.env.example`.
- If you switch from stdio to HTTP (or vice versa) mid-project, commit the `mcp.json` change as its own commit so the history is searchable.

---

## 4. `.claude/settings.json`

### Shape

```jsonc
{
  "permissions": {
    "allow": [ /* commands Claude runs without asking */ ],
    "deny":  [ /* commands Claude refuses outright */ ]
  },
  "hooks": {
    "SessionStart": { "command": "...", "message": "..." },
    "PreCompact":   { "command": "..." },
    "Stop":         { "command": "..." }
  }
}
```

### Permissions — shipped `allow`

| Category | Examples |
|----------|----------|
| Git read-only | `git status`, `git log`, `git diff`, `git show`, `git branch` (read-only forms) |
| MCP tools | All `mcp__xppatlas__*` read tools are auto-allowed; write tools like `create_task` are auto-allowed because they stay within the task workspace |
| Project-scoped file ops | Read/write under `Models/`, `docs/`, `.claude/` (except `settings.json`); Write to `SNAPSHOT.md` |
| Python helpers | `python tools/ensure_index.py`, `python tools/search_index.py`, `python tools/bootstrap_context.py`, `python tools/index_all.py --incremental` |

### Permissions — shipped `deny`

| Category | Examples | Why |
|----------|----------|-----|
| Destructive git | `git push`, `git reset --hard`, `git checkout -- <path>`, branch deletion, `git commit --amend` after push | Destructive; developer-driven only |
| `git commit` (bulk) | Commits via shell | Commits should be deliberate; the developer runs `git commit` manually after reviewing the diff |
| TFVC | `tf *` | Check-ins happen outside Claude by policy |
| Build scripts | `scripts/build-v4-model.bat` etc. | Claude can't run X++ compiler; false-green risk |
| Out-of-repo writes | Any write path outside the repo | Hard boundary; only exception is the user-driven MCP write-back |
| Secret-bearing writes | Write to `.env`, `.pfx`, `.mcp.json` | Secret-leak guard |

### Hooks

| Hook | Typical command |
|------|------------------|
| `SessionStart` | `{ "message": "You're in {ProjectName}. Active model is {ModelName}. Run /session-start first. Read 5 rule files in .claude/rules/ before any edit." }` |
| `PreCompact` | `{ "message": "Before compacting, update the active task's SNAPSHOT.md §5, §7, §9 so the post-compact session can resume cleanly." }` |
| `Stop` | `{ "command": "python tools/ensure_index.py --incremental" }` |

### Editing the permission list

Widening `allow` is a permanent loosening of the sandbox. Narrowing `deny` is worse. Both should come with a commit message explaining why. The project lead owns this file — developers don't edit it ad hoc.

---

## 5. `SNAPSHOT.md` structure

Every task has exactly one `SNAPSHOT.md` file. Copied from `Models/_Model_Template/Tasks/_Task_Template/SNAPSHOT.md` by `/new-task` and filled in by the developer + by Claude at checkpoint moments.

### Sections

| § | Title | Filled by | When |
|---|-------|-----------|------|
| 1 | Purpose | Developer | Before first edit |
| 2 | Scope | Developer | Before first edit |
| 3 | Constraints | Developer | Before first edit |
| 4 | Source artifacts | Claude (via `/fetch-baseline`) + baseline SHA | At `/fetch-baseline`, at baseline commit |
| 5 | Decisions log | Claude + developer | At every significant decision |
| 6 | Extension strategy | Claude | When extension mechanism is chosen; always includes rank (1-5) and reason |
| 7 | Changed files | Claude | Every 5 edits; at `/session-finish` |
| 8 | Validation status | Claude | After every `/review-code`, `/audit-arch`, `/fix-perf`, `/testing`; at `/session-finish` |
| 9 | Next steps | Claude | Every 5 edits; at `/session-finish` |
| 10 | Open questions | Claude | When Claude encounters a decision that needs the developer |

### Validation status language

`.claude/rules/10-context-and-snapshot.md` forbids fabricating validation status. Acceptable values:

| Value | Meaning |
|-------|---------|
| `not run` | The check hasn't been executed; this is the default for a new task |
| `reviewed — <findings summary>` | `/review-code` or similar has run and produced a report |
| `pending human` | Claude flagged something that needs the developer to decide |
| `N/A` | The check doesn't apply to this task |

**Never** `passing` for anything Claude did not actually run. If Claude writes `Compile: passing` without an ingested build log, that's a session bug — edit the snapshot manually to correct it.

---

## 6. `validate-ai-setup.ps1` checks

Run `pwsh -File ./validate-ai-setup.ps1` after any config change. It verifies cross-tool consistency.

| Check | What passes |
|-------|-------------|
| Rule files exist | All five numbered files under `.claude/rules/` |
| Skills exist | Every skill named in `CLAUDE.md` has `.claude/skills/{name}/SKILL.md` and `skills/{name}/SKILL.md` (Codex mirror) |
| Agent catalogues aligned | `.claude/agents/` and agent-references in `GEMINI.md` / `AGENTS.md` name the same set |
| Hook messages reference the right project | `SessionStart` hook mentions `{ProjectName}` that matches `context_setup.md` |
| Placeholder scan | No `{ProjectName}`, `{ModelName}`, `{ProjectPrefix}`, `{LabelFile}`, `{UserVISA}` literal remains anywhere (except in the `_Model_Template` / `_Task_Template` skeletons) |
| `SNAPSHOT.md` validity | Every task has a `SNAPSHOT.md`; every `SNAPSHOT.md` has §1 through §10 present |
| Baseline coverage | Every file under any task's `code/` has a baseline commit in `git log` |

Failed checks print the specific mismatch and exit non-zero. CI pipelines (Azure DevOps build validation, GitHub Actions, whatever the customer uses) should run this as a gate.

---

## See also

- [Getting Started](02-getting-started.md) — initial fill-in procedure
- [Admin Guide](04-admin-guide.md) — widening / narrowing permissions, rule maintenance
- [XppAtlas Configuration Reference](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/07-configuration.md) — server + client env vars, deployment modes, Phase 22 GC
