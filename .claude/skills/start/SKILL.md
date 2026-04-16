---
name: start
description: Cold-open procedure for a new Claude Code session. Identifies active task and model, reads task rules and SNAPSHOT, loads context, reports readiness.
---

# /start

Run this at the start of every session **before** any discovery, search, or edit.

## Steps

1. **Identify the active task and model.**
   - Run `git status` and `git log --oneline -n 10`.
   - Look for modified paths under `Models/{ModelName}/Tasks/{TaskID}_*`.
   - If exactly one task folder has uncommitted or recent changes, treat that as active.
   - If several, or none, **ask the user**. Do not guess.
   - One session = one task. One task = one model.

2. **Read the task's rules and SNAPSHOT.**
   - Open `Models/{ModelName}/Tasks/{TaskID}_{Name}/rules.md` — this tells you the task type and behavioral emphasis.
   - Open `Models/{ModelName}/Tasks/{TaskID}_{Name}/SNAPSHOT.md` — this is the working memory.
   - If missing, fall back to `Models/_Model_Template/Tasks/_Task_Template/SNAPSHOT.md` and tell the user.
   - Pay particular attention to §5 Decisions, §6 Extension strategy, §7 Changed files, §9 Next steps, §10 Open questions.

3. **Load `context_setup.md` bottom-up.**
   - Task folder → model folder → project root.
   - Capture `ProjectPrefix`, `LabelFile`, `LabelLanguages`, `UserVISA`.
   - Task values override model values override project defaults.

4. **Read the project rules.**
   - `.claude/rules/project-main.md`
   - `.claude/rules/tool-usage.md`
   - `.claude/rules/safety-boundaries.md`
   - `.claude/rules/task-lifecycle.md`

5. **Read model rules** if they exist at `Models/{ModelName}/rules.md`.

6. **Verify baseline state** (for development/bugfix tasks).
   - For every file under `code/**`, confirm it appears in a baseline commit.
   - If any file has no baseline commit, **stop** and ask the user.

7. **Report readiness.** One short paragraph:
   - Active task ID, name, model, task type.
   - Snapshot last-updated date.
   - Next step (from §9).
   - Open questions (§10) the user needs to answer.
   - Baseline gaps found in step 6.

## Anti-patterns

- Do not start searching MCP before reading the snapshot.
- Do not silently assume the most recently modified task is active when ambiguous — ask.
- Do not cross model boundaries.
