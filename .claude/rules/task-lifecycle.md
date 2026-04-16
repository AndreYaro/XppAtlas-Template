# Rule: Task lifecycle

## The artifact lifecycle — MCP is the source of truth

Every development or bugfix task that modifies existing artifacts follows this lifecycle:

1. **Scaffold.** `/new-task` creates `Models/{ModelName}/Tasks/{TaskID}/` with the appropriate task-type template. No XML is generated from memory.
2. **Fetch baseline.** `/fetch-baseline AxClass:Foo AxTable:Bar …` pulls the **untouched** current version from MCP into the task's `code/Ax{Type}/` folder. Byte-for-byte, no reformatting.
3. **User commits baseline.** The user creates a Git commit — this becomes the "before" state. Claude does **not** make any edits until the user confirms this commit.
4. **Edit.** Claude modifies the files in the task folder. The Git diff from this point is the task's actual change set.
5. **Validate.** `/review-code`, `/audit-arch`, `/fix-perf`, `/testing` — all scoped to the task folder.
6. **Prep check-in.** `/prep-comment` produces the TFVC check-in comment.
7. **Write back to MCP source.** At check-in time (outside Claude Code), the user copies final files into the MCP source store and re-indexes. This is **always user-driven, never automatic**.

**Never skip steps 2–3.** Edits without a baseline commit produce an unreviewable diff and destroy the pre-change state.

Analysis tasks may skip steps 2–7 since they don't produce code artifacts.

## Snapshot is per-task, not per-project

There is **no** global snapshot file. Every task keeps its own snapshot at:

```
Models/{ModelName}/Tasks/{TaskID}_{TaskName}/SNAPSHOT.md
```

The snapshot is the stable carrier of context across sessions. Scratch memory is not.

## Every session must

1. **Identify the active task** from `git status`, the last commit, or by asking the user. One session = one task. One task = one model.
2. **Read the active task's `SNAPSHOT.md`** before any discovery or source reading.
3. **Read the active task's `rules.md`** to understand the task type and behavioral emphasis.
4. **Read `context_setup.md` bottom-up**: task folder → model folder → project root. Task values always win.
5. **Refuse to continue if the SNAPSHOT is missing or stale by more than a day without changes** — ask the user to confirm the task state.

## Anti-degradation protocol

Claude's context degrades over long sessions: conflating tasks, forgetting decisions, re-exploring the same file, drifting scope. Defend explicitly.

### Checkpoint triggers

Update the active task's `SNAPSHOT.md` whenever:

- You have made **5+ file edits** since the last checkpoint
- You are about to run a validation skill (`/review-code`, `/audit-arch`, `/fix-perf`, `/testing`)
- The user has made a new decision that changes scope or approach
- You are about to switch tasks (stop, save, then switch)
- The session is about to hit a compaction (the `PreCompact` hook will remind you)
- You are about to end the session

### What a checkpoint writes

- §5 Decisions log — append new decisions with date + rationale
- §7 Changed files — refresh from `git status` against the baseline commit
- §8 Validation status — update with whatever has actually been run
- §9 Next steps — rewrite so the first bullet is the next concrete action

Never rewrite §1 Purpose or §2 Scope without the user's explicit approval — those define the task identity.

### Do not fabricate context

If the snapshot says "not yet decided" for something, and the user has not decided it in this session, do **not** silently replace it with an assumption. Re-ask.

### Do not skip the snapshot

Skipping the snapshot because "the task is small" is how the next session has to re-derive everything. Even a 30-minute task needs a one-paragraph snapshot update at the end.

## Git and TFVC discipline

### Two separate change-control systems

- **Git** is the development notebook: frequent small commits, per-task branches. Claude suggests messages but never commits without authorization.
- **TFVC** is the ship line: the user checks in once per task with a formal comment. Claude never drives TFVC directly.

### What Claude may do (git)

- `git status`, `git status -s`, `git log`, `git diff`, `git show`, `git branch` — read-only, safe
- Suggest commit messages in chat or via `/prep-comment`

### What Claude must not do without explicit user authorization, every time

- `git commit` / `git commit --amend`
- `git push` / `git push --force`
- `git reset --hard`, `git checkout -- <path>`, `git clean -fd`, `git branch -D`

One-time approval for a specific commit does not generalize. The next commit needs its own approval.

### Baseline commit

Before editing any artifact, the user must have committed the `/fetch-baseline` output. If Claude sees uncommitted files in `code/Ax*/` with no matching baseline commit, it must stop and ask.

## Task creation

When creating a new task:
1. Determine the model (from context or ask the user)
2. Determine the task type (analysis, development, or bugfix)
3. Create the task folder from `.claude/task-templates/{type}/`
4. Place it at `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/`
5. Fill in TASK.md metadata
6. Prompt the user to fill in SNAPSHOT §1 Purpose, §2 Scope, §3 Constraints

## Impact radius guard

Before making a change that touches ≥ 3 AOT artifacts **or** any artifact referenced by another model:
1. Use `search_chunks` or reference lookups to list callers
2. Write the impact list into SNAPSHOT §7
3. Ask the user to confirm scope

If callers exist in a different model, stop. Cross-model work requires a new task in the target model.
