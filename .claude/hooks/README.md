# .claude/hooks — active hooks

Hooks live in `.claude/settings.json` under `hooks`. This file documents what each hook does and why.

## Active

### `SessionStart`

Reminds Claude to run `/start` before any discovery, identify the active task and model from `git status`, and read the task's `rules.md` and `SNAPSHOT.md` first.

**Why:** Without this reminder, Claude starts searching MCP or reading files before loading the snapshot. Every session that skips the snapshot costs the next session context.

### `PreCompact`

Reminds Claude to update the active task's `SNAPSHOT.md` (changed files, validation status, next steps) before context compaction.

**Why:** Compaction discards the running conversation; the snapshot is the only thing that survives.

### `Stop`

Runs `python tools/ensure_index.py --quiet` and prints a confirmation that the X++ model index is fresh. Timeout 60s.

**Why:** Keeps the local search index in sync with edits the user made outside Claude. Fail-silent by design.

## Adding a new hook

1. Edit `.claude/settings.json`
2. Document the new hook here
3. Prefer hooks that print `systemMessage` JSON — avoid hooks that silently mutate files
4. Never add a hook that runs destructive Git commands or writes into a sibling repo
