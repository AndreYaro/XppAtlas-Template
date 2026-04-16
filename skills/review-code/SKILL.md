---
name: review-code
description: Perform a full architect-level code review of X++ files in the current task folder against project rules and coding standards.
---

Perform a full code review of the X++ files in the current task `code/` folder.

## Steps

1. Read `context_setup.md` from the nearest task or project folder. Extract `ProjectPrefix`, `UserVISA`, `LabelFile`.
2. Read `rules.md` from the project folder for project-specific overrides.
3. Read `_Global_Resources/_Task_Template/code_review_checklist.md` for the checklist.
4. Locate all `.xml` files under the task `code/` folder using Glob.
5. Read each file and review against every rule below.

## Review Checklist

| # | Check | Severity if failed |
|---|-------|--------------------|
| 1 | Every new AOT object name starts with `{ProjectPrefix}` | Major |
| 2 | Extension classes follow `{Prefix}[Original]_Cls_Extension` pattern | Major |
| 3 | No `select *` — field list always specified | Major |
| 4 | No hardcoded user-facing strings — Label IDs used | Major |
| 5 | `ttsbegin` and `ttscommit` open and close in the same method | Critical |
| 6 | `next` call present in every CoC extension method | Critical |
| 7 | No overlayering of standard objects | Critical |
| 8 | No business logic in form methods or data source events | Major |
| 9 | Null check (`if (!record)`) before field access on buffer variables | Critical |
| 10 | Row-by-row insert/update/delete loops replaced with set-based ops | Major |
| 11 | Variable names are `camelCase`; parameters prefixed with `_` | Minor |
| 12 | Methods are < 50 lines | Minor |
| 13 | No commented-out dead code | Minor |
| 14 | TODO comments follow `// TODO: [{UserVISA}] <text>` format | Info |
| 15 | Files are in correct `code/Ax{ObjectType}/` sub-folder | Major |

## Output Format

For each finding:
```
[SEVERITY] {FileName} | ~Line {N}
Issue   : <what is wrong>
Rule    : <which check above failed>
Fix     : <exact corrective action>
```

End with a summary table:
```
| Severity | Count |
|----------|-------|
| Critical | N     |
| Major    | N     |
| Minor    | N     |
| Info     | N     |
```

State clearly: **PASS** (zero Critical/Major) or **FAIL** (one or more Critical/Major found).
