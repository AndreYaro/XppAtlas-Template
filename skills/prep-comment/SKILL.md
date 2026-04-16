---
name: prep-comment
description: Generate a formatted TFVC check-in comment for the current task's pending changes.
---

Generate a TFVC check-in comment for the current task.

## Steps

1. Read `context_setup.md` from the nearest task folder. Extract `TaskID`, `UserVISA`, `TaskName`.
2. List all files in the task `code/` folder using Glob to identify what was changed.
3. Read each changed file briefly to understand the nature of the changes.
4. Compose the check-in comment.

## Check-in Comment Format

```
{TaskID} {UserVISA} {Short description of changes}
```

Rules:
- `{TaskID}` is the numeric work item ID from `context_setup.md`
- `{UserVISA}` is the uppercase abbreviation from `context_setup.md`
- Description is a single sentence, max 80 characters, in plain English
- Start with a verb: "Add", "Fix", "Update", "Refactor", "Remove"
- Do not include file names — describe the logical change

## Examples

```
3641 OPT Add VAU prefix to DMS invoicing integration classes
3641 OPT Fix ttsbegin scope in VAUDMS_Invoicing_INT001F.process()
3641 OPT Refactor row-by-row loop to update_recordset in posting service
```

## After Output

Remind the user:
> Do NOT mark the work item as **Resolved** by default after check-in unless explicitly instructed. Set status to **In Progress** or leave as-is.
