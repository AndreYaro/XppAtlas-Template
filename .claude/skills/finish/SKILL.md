---
name: finish
description: End-of-session procedure. Updates the active task SNAPSHOT, writes a handoff summary, leaves the repo in a clean resumable state.
---

# /finish

Run this before ending any non-trivial session.

## Steps

1. **Confirm the active task.** If genuinely nothing to save (read-only session with no edits and no new decisions), say so and stop.

2. **Update the per-task SNAPSHOT.**
   - §5 Decisions log — append any new decisions made this session, each with date + rationale.
   - §7 Changed files — refresh from `git status` against the baseline commit.
   - §8 Validation status — update with anything actually run. Do not mark "passing" what was not run.
   - §9 Next steps — rewrite so the first bullet is the literal next action for the next session.
   - §10 Open questions — add anything blocked, remove anything answered.
   - Update frontmatter `last_updated` date.
   - **Never** rewrite §1 Purpose or §2 Scope without explicit user approval.

3. **Produce a handoff summary in chat.** One short paragraph:
   - What was done this session (1–3 bullets).
   - What is queued next.
   - Open questions the user needs to answer.
   - Baseline gaps the user should resolve.

4. **Suggest, do not run, a Git checkpoint commit.** Wait for the user.

5. Do not run `/prep-comment` automatically — that is a separate step at check-in time.

## Anti-patterns

- Do not stamp "session finished" in §1/§2/§3.
- Do not claim "all tests pass" unless actually confirmed.
- Do not commit on the user's behalf.
