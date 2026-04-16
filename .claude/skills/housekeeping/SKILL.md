---
name: housekeeping
description: Safe repository maintenance — reports stale files, duplicate task folders, snapshot gaps, and baseline mismatches. Never deletes anything automatically.
---

# /housekeeping

Report-before-act maintenance pass. This skill writes findings to `.claude/CLEANUP_CANDIDATES.md` and tells the user what to do. It does not delete, move, or rename anything.

## Steps

1. **Task folder audit.** For every `Models/*/Tasks/*/` folder:
   - Missing `SNAPSHOT.md` → flag.
   - `SNAPSHOT.md` `last_updated` older than 30 days and status != `done` → flag as stale.
   - Folder name has leading/trailing whitespace, non-ASCII surprises, or duplicates another folder with the same `TaskID` → flag as duplicate-suspect.
   - `code/Ax*/` contains files with no matching baseline commit in `git log` → flag as un-baselined.

2. **Snapshot audit.** For every `SNAPSHOT.md`:
   - §1 Purpose empty → flag.
   - §2 Scope says both "in scope: everything" → flag.
   - §6 Extension strategy is "overlayering" without justification → flag.
   - Frontmatter `model` does not match the folder path → flag.

3. **Cross-task contamination audit.** For every task folder, check that file edits stay inside that folder's `code/**`. A task that has also modified another task's files is suspect. Flag.

4. **Shared-config drift audit.** Check whether `CLAUDE.md`, `GEMINI.md`, `.claude/settings.json`, `.claude/rules/**` have been modified on a branch whose active task would not justify that edit. Flag.

5. **Write findings to `.claude/CLEANUP_CANDIDATES.md`.** Append to `## Active candidates`, never rewrite `## Resolved`. Use the entry format at the top of that file.

6. **Report in chat.** One short summary: N candidates found, top 3 by severity, file link to `CLEANUP_CANDIDATES.md`.

## What /housekeeping NEVER does

- Delete any file.
- Rename any folder (even obvious typos).
- `git reset`, `git clean`, `git branch -D`, `git checkout --` — all denied in `.claude/settings.json`.
- Rewrite a SNAPSHOT to "fix" issues.
- Touch `.mcp.json` — if secrets are found, report and ask the user to rotate.

The purpose is to give the user a trustworthy punch list they can then execute themselves.
