# Task rules — development

This task is a **development** task. These rules override project defaults where specified.

## Behavioral emphasis

- **Safe incremental implementation.** Make changes one artifact at a time. Commit checkpoints.
- **Extension-first patterns.** Follow the extension strategy priority order from `project-main.md`. Prefer event handlers and CoC over new artifacts.
- **Explicit touched artifacts.** Maintain a clear list of every artifact created or modified in SNAPSHOT §7.
- **Localized impact.** Keep changes within the active model. If cross-model impact is discovered, stop and discuss.
- **Checkpointing.** Update SNAPSHOT after every 5 edits, before validation, before session end.
- **Validation before completion.** Run `/review-code` and `/testing` before declaring work done. Never claim "tests pass" without evidence.
- **No unnecessary redesign.** Implement what was planned. If a better design is discovered during implementation, record it as a finding and discuss before changing course.

## Baseline-first workflow

This task follows the full artifact lifecycle:
1. `/fetch-baseline` to pull existing artifacts from MCP
2. User commits baseline
3. Edit files in `code/`
4. Validate with review skills
5. `/prep-comment` for check-in

**Never edit a file that has no baseline commit.** If code files exist in `code/Ax*/` without a corresponding baseline commit in `git log`, stop and ask.

## What to record in SNAPSHOT

- Extension strategy chosen and why (§6)
- Every file created/modified with one-line purpose (§7)
- Validation results — only what was actually run (§8)
- Decisions made during implementation with rationale (§5)

## MCP usage in development

- `get_artifact` / `build_edit_bundle` — before editing, always fetch current source
- `explore_artifact` — understand object structure before extending
- `search_chunks` — find existing CoC/handlers to avoid duplicates
- `recommend_patterns` — check for established patterns before inventing new ones
- `search_artifacts` + `get_artifact` — load XML reference examples before generating new XML

## Code review checklist

Before completion, verify:
- [ ] Every new AOT object starts with `{ProjectPrefix}`
- [ ] Extension classes follow `{Prefix}[Original]_Cls_Extension` pattern
- [ ] No `select *` — field list always specified
- [ ] No hardcoded strings — Label IDs from `{LabelFile}` used
- [ ] `ttsbegin`/`ttscommit` open and close in the same method
- [ ] `next` call present in every CoC extension method
- [ ] No overlayering of standard objects
- [ ] No business logic in form methods
- [ ] Null checks before buffer field access
- [ ] Row-by-row DML loops replaced with set-based operations
- [ ] All files in correct `code/Ax*/` sub-folder
