# XppAtlas-Template — Getting Started

| | |
|---|---|
| **Document type** | Quick Start Guide |
| **Audience** | Any developer starting a new D365 customization project |
| **Time estimate** | 30-60 minutes (if XppAtlas server is already reachable) |
| **Prerequisites** | Git, Claude Code, Python 3.11+, an XppAtlas server you can reach |

---

## Prerequisites

Before cloning the template you need:

- **Windows + Git Bash** — the template assumes Unix shell syntax in hooks and skills.
- **Python 3.11+** on `PATH` — the hooks call `python tools/ensure_index.py` on session start.
- **Claude Code** installed and authenticated (or Codex / VS Code Copilot / Gemini using the same skill catalog).
- **XppAtlas server reachable** — either locally installed on your machine (stdio MCP) or on a shared LAN server (MCP over HTTP at `/mcp`). See the [XppAtlas Getting Started](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/02-getting-started.md) guide if you need to stand one up.
- **TFVC workspace** for the customer's production D365 codeline. Check-ins happen outside Claude — the template only prepares the check-in comment.

---

## Step 1 — Clone the template (2 minutes)

```bash
git clone https://github.com/AndreYaro/XppAtlas-Template.git C:/Work/GitHub/D365{CustomerName}
cd C:/Work/GitHub/D365{CustomerName}
rm -rf .git
git init
```

The `rm -rf .git && git init` step detaches the clone from the template's history so the customer project starts with its own clean Git timeline.

---

## Step 2 — Fill in project identity (5 minutes)

Edit these files and replace every `{Placeholder}`:

### `context_setup.md` (project root)

| Field | Meaning | Example |
|-------|---------|---------|
| `ProjectPrefix` | AOT prefix for every new object this project creates | `VAU`, `DYS`, `ACM` |
| `LabelFile` | Target label file for all new labels | `VaudoiseLabel` |
| `LabelLanguages` | Translation targets, comma-separated | `en-us, fr-ch, de-ch, it-ch` |
| `UserVISA` | Developer check-in initials — used in TODO markers and TFVC comments | `AYR` |
| `AutoTranslate` | Auto-generate translations for new labels | `true` or `false` |

### `CLAUDE.md`

Replace `{ProjectName}` and `{ModelName}` everywhere, and rewrite the short description paragraph to explain what the customer does and which models are in scope.

### `README.md`

Replace `{ProjectName}`, `{Organization}`, `{ProjectPrefix}`, `{LabelFile}`, `{LabelLanguages}`, `{UserVISA}` in the overview table.

### `.claude/settings.json`

In the `SessionStart` hook message, replace `{ProjectName}` and `{ModelName}` so the session-start reminder is specific to this project. Everything else (permissions, other hooks) you usually keep as-is.

---

## Step 3 — Configure the XppAtlas connection (3 minutes)

Copy the reference env file:

```bash
cp .env.example .env
```

Edit `.env`. The fields you actually need depend on which XppAtlas deployment mode you're connecting to.

### Client against a LAN server (recommended for teams)

```env
# Point at the XppAtlas server
XPPATLAS_STANDARD_SERVER_URL=http://10.0.0.50:8765

# Local source tree for VENDOR + CUSTOM models
XPPATLAS_SOURCE_ROOT=models-src

# Embeddings (for local VENDOR + CUSTOM indexing)
OPENAI_API_KEY=sk-...
XPPATLAS_EMBEDDING_MODEL=text-embedding-3-small
# Or local:
# XPPATLAS_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Dev mode gives the local client admin rights (safe — it's your own machine)
XPPATLAS_DEV_MODE=true
```

### Local-only (no server)

Leave `XPPATLAS_STANDARD_SERVER_URL` blank. You also need a full XppAtlas installation on your own machine with STANDARD models indexed — see the XppAtlas Getting Started guide.

---

## Step 4 — Wire MCP (2 minutes)

Edit `.vscode/mcp.json` so Claude Code can reach your XppAtlas server.

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

### HTTP mode (server/client split)

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

You can keep both entries in the file and comment out the one you're not using.

---

## Step 5 — Scaffold one folder per model (5 minutes)

For each D365 model this project will customize:

```bash
cp -r Models/_Model_Template Models/{ModelName}
```

Edit `Models/{ModelName}/context_setup.md` if the model needs different values from the project default (e.g. a different `ProjectPrefix` or `LabelFile`).

**Keep `Models/_Model_Template/` in place** — do not delete it. The `/new-task` skill uses its `_Task_Template/SNAPSHOT.md` as the snapshot source every time you scaffold a new task.

---

## Step 6 — Verify MCP connectivity (1 minute)

Open Claude Code in the project root and ask:

> "Use `mcp__xppatlas__list_models` to list every model the MCP server knows about."

The response should include:

- STANDARD models (ApplicationSuite, ApplicationFoundation, etc.) — served by the LAN server, or by your local install in local-only mode.
- Your VENDOR + CUSTOM models — served locally by your own client.

If the list is missing your target model, stop and fix the MCP configuration before anything else. The template will refuse to read from local `Source/` folders, so there is no workaround.

---

## Step 7 — Run the validator (1 minute)

```bash
pwsh -File ./validate-ai-setup.ps1
```

This checks that the rules, agent definitions, and skill catalogs are consistent across Claude Code, Codex, and Gemini. It should print `OK` for every check. Fix any mismatches before committing.

---

## Step 8 — First Git commit (1 minute)

```bash
git add .
git commit -m "chore: instantiate template for {ProjectName}"
```

This is the project's origin commit. Everything after it is task work.

---

## Step 9 — Run your first task end-to-end (15-45 minutes)

In Claude Code, at the start of a fresh conversation:

```
/session-start
```

Claude will run `git status`, find no active task, and ask. Reply:

```
/new-task {ModelName} {TaskID} {TaskName}
```

Example: `/new-task Vaudoise 3641 INT001_DMS_Invoicing`

Claude scaffolds `Models/Vaudoise/Tasks/3641_INT001_DMS_Invoicing/` with `SNAPSHOT.md`, `README.md`, `code_review_checklist.md`, `context_setup.md`, and empty `code/` / `docs/` folders. **Fill in `SNAPSHOT.md` §1 Purpose, §2 Scope, §3 Constraints before any edit** — the rules refuse to proceed otherwise.

Commit the scaffold:

```bash
git commit -am "3641 scaffold: new task folder for INT001_DMS_Invoicing"
```

Then in Claude Code:

```
/fetch-baseline AxClass:CustInvoiceJour AxTable:CustInvoiceJour
```

Claude pulls those artifacts from MCP into the task's `code/` folder byte-for-byte and stops. You commit the baseline yourself:

```bash
git commit -am "3641 baseline: fetched from MCP"
```

Reply to Claude with the baseline SHA. It records it in `SNAPSHOT.md` §4 and begins edit work.

---

## Step 10 — Close the session properly

When you're done for the day:

```
/session-finish
```

Claude updates `SNAPSHOT.md` §5 (decisions log), §7 (changed files), §8 (validation status), §9 (next steps), §10 (open questions), and prints a handoff summary the next session can pick up cold.

Commit whatever you want to keep. The `Stop` hook refreshes the local search index afterwards.

---

## What's next?

- **[User Guide](03-user-guide.md)** — full daily workflow: fetch, edit, validate, prep-comment, write-back
- **[Admin Guide](04-admin-guide.md)** — multi-developer setup, housekeeping, rule maintenance
- **[Architecture Reference](05-architecture.md)** — folder layout, MCP boundary, skill layering
- **[Tool Reference](06-tool-reference.md)** — every skill, hook, and rule
- **[Configuration Reference](07-configuration.md)** — `context_setup.md`, `.env`, `.claude/settings.json`, `.vscode/mcp.json`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `list_models` does not show my model | MCP server isn't indexing it — fix the server config, don't try to work around it |
| Claude refuses to edit | `SNAPSHOT.md` §1-3 is probably empty — fill it in before asking again |
| Claude edits a file with no baseline commit | Stop the session, run `/fetch-baseline` retroactively (creates an honest baseline) or revert |
| Hook errors about `python tools/ensure_index.py` | Python isn't on `PATH`, or tools folder is missing — fix the env and restart |
| `validate-ai-setup.ps1` flags drift | Shared rules / agents / skills have diverged — align them, don't just silence the check |
| Claude reaches into a sibling repo | Rule violation — close the session, verify nothing outside the repo was modified, reopen |
