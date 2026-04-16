---
name: task-resume
description: Resume a known task in a new session. Lighter than /start when the task ID and model are already known. Usage: /task-resume [ModelName] [TaskID]
---

# /task-resume

Resume work on a specific task when you already know the task ID and model.

## Arguments

Parse `$ARGUMENTS` as: `{ModelName} {TaskID}` (e.g. `Vaudoise 3641`)
- If arguments provided, go directly to the task folder.
- If not provided, fall back to `/start` behavior (identify from git status).

## Steps

1. **Locate the task folder.** Find `Models/{ModelName}/Tasks/{TaskID}_*/`.

2. **Read the task's rules.md.** Understand the task type and behavioral emphasis.

3. **Read the task's SNAPSHOT.md.** This is your primary context source.
   - Check §9 Next steps — this is where you left off.
   - Check §10 Open questions — surface these to the user before continuing.
   - Check §7 Changed files — understand what has been touched.
   - Check §8 Validation status — know what has/hasn't been verified.

4. **Read `context_setup.md` bottom-up** (task → model → project).

5. **Quick baseline check.** For development/bugfix tasks, verify files in `code/**` have baseline commits.

6. **Report readiness and start working.** One short paragraph summarizing task state and next action.

## When to use /task-resume vs /start

- Use `/task-resume` when you know the exact task and want to skip the discovery step.
- Use `/start` at the beginning of a fresh session when the active task is unknown.
- Use `/task-resume` when switching between tasks within a session (after saving the current task via `/finish`).
