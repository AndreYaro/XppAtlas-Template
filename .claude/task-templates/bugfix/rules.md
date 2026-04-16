# Task rules — bugfix

This task is a **bugfix** task. These rules override project defaults where specified.

## Behavioral emphasis

- **Understand or reproduce the issue first.** Do not jump to a fix. Read error messages, trace execution, inspect data state.
- **Distinguish symptom from root cause.** The first thing that looks wrong is often a symptom. Dig deeper before patching.
- **Prefer the smallest correct fix.** The ideal bugfix changes one method in one artifact. Broader changes need stronger justification.
- **Avoid unrelated cleanup or refactor.** A bugfix is not an opportunity to redesign. If cleanup is needed, record it as a separate follow-up task.
- **Record evidence and suspected cause.** Write what you found (error messages, data states, execution paths) into SNAPSHOT §5 and TASK.md before proposing a fix.
- **Consider regression risk explicitly.** Every fix can break something else. List what could be affected and how to verify.
- **Test the fix path, not just the happy path.** Consider edge cases: null values, empty collections, cross-company, different legal entities, concurrent users.

## Investigation workflow

1. Read the bug description and reproduction steps
2. Use MCP tools to inspect the affected artifacts:
   - `explore_artifact` — understand the full object structure
   - `search_chunks` — find the specific code path
   - `find_references` — understand who calls the affected code
   - `trace_posting_flow` / `trace_form_to_table_flow` — trace execution flow
3. Identify the root cause (not just the symptom)
4. Determine the minimal fix
5. Check for existing CoC or event handlers on the same target — extend if present, don't create duplicates
6. Implement the fix in `code/`
7. Run `/review-code` and `/testing`

## Baseline-first workflow

Even for bugfixes, follow the full artifact lifecycle:
1. `/fetch-baseline` for the artifact(s) being fixed
2. User commits baseline
3. Apply the minimal fix
4. Validate

The baseline commit proves exactly what changed for the fix.

## What to record in SNAPSHOT

- Symptoms observed and error details (§5)
- Root cause identified (§5)
- Evidence gathered and how (§5)
- Artifacts inspected during investigation (§4)
- Regression risk assessment (§5)
- Fix applied and rationale (§5, §7)

## What this task does NOT do

- Refactor unrelated code alongside the fix
- Redesign the feature that contains the bug
- Add new functionality beyond what's needed to fix the defect
- Skip the baseline commit because "it's just a small fix"

If the bug reveals a deeper design problem, record it in `docs/` and recommend a development task.
