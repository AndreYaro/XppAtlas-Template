---
name: new-task
description: Scaffold a complete new task folder with all standard files (context_setup.md, README.md, code_review_checklist.md, folder structure). Usage: /new-task [ModelName] [TaskID] [TaskName]
---

Scaffold a new task folder with all standard files.

## Arguments
Parse `$ARGUMENTS` as: `{ModelName} {TaskID} {TaskName}` (e.g. `_Model_Template 3641 INT001F_DMS_Invoicing`)
- If the model name is omitted, infer it from the current working folder when possible.
- If no arguments are provided, ask for `ModelName`, `TaskID`, and `TaskName`.

## Steps

1. Read `context_setup.md` from the **model** folder first, then the project folder, to get `ProjectPrefix`, `LabelFile`, `LabelLanguages`, and `UserVISA`.
2. Determine the task folder path: `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/`
3. Create the folder structure and all files below.

## Folder Structure to Create

```
Models/{ModelName}/Tasks/{TaskID}_{TaskName}/
  code/
    AxClass/          ← X++ class XML files
    AxTable/          ← X++ table XML files
    AxForm/           ← X++ form XML files
    AxEnum/           ← Enum XML files
    AxEdt/            ← EDT XML files
    AxLabel/          ← Label file XML files
    AxMenuItemAction/ ← Action menu item XML files
  docs/               ← FDDs, mappings, technical designs
  samples/            ← JSON/XML sample payloads
  refcode/            ← .axpp reference projects
```

## Files to Generate

### `context_setup.md`
```markdown
# Task Context - {TaskID}_{TaskName}

## Project Settings (Inherited from {ProjectName} / {ModelName})
ProjectPrefix: "{ProjectPrefix}"
LabelFile: "{LabelFile}"
LabelLanguages: "{LabelLanguages}"
AutoTranslate: true

## Task-Specific Settings
TaskID: "{TaskID}"
TaskName: "{TaskName}"
UserVISA: "YOUR_VISA"
Description: "TODO: Add task description"

## Reference Paths
reference_paths:
  - path: "MCP_MODEL_SOURCE:{ModelName}"
    description: "Primary model source via D365 MCP (`resolve_object`, `get_chunk`, `get_file`). Do not use local Source folders."
  - path: "./refcode"
    description: "Task-specific reference code or .axpp projects"

## Ignore Patterns
ignore_patterns:
  - "*.dll"
  - "*.pdb"
  - "bin/"
  - "obj/"
  - ".git/"
```

### `README.md`
```markdown
# {TaskID} — {TaskName}

## Summary
TODO: Brief description of what this task implements.

## Work Item
- DevOps Task ID: {TaskID}
- Developer: YOUR_VISA

## Objects Modified / Created
| Object Type | Object Name | Action |
|-------------|-------------|--------|
| Class | {ProjectPrefix}... | Created |

## Check-in Comment Format
`{TaskID} YOUR_VISA <Short description>`

## Notes
TODO: Any special instructions, dependencies, or known limitations.
```

### `code_review_checklist.md`
```markdown
# Code Review Checklist — {TaskID}_{TaskName}

- [ ] Every new AOT object starts with `{ProjectPrefix}`
- [ ] Extension classes follow `{ProjectPrefix}[Original]_Cls_Extension` pattern
- [ ] No `select *` — field list always specified
- [ ] No hardcoded strings — Label IDs from `{LabelFile}` used
- [ ] `ttsbegin`/`ttscommit` open and close in the same method
- [ ] `next` call present in every CoC extension method
- [ ] No overlayering of standard objects
- [ ] No business logic in form methods
- [ ] Null checks before buffer field access
- [ ] Row-by-row DML loops replaced with set-based operations
- [ ] All files are in correct `code/Ax*/` sub-folder
- [ ] TODO comments follow `// TODO: [YOUR_VISA] <text>` format
```

## Output
1. Confirm the folder path that will be created.
2. Create all directories and files.
3. Report each file created.
4. Remind the user to update `UserVISA` in `context_setup.md`.
