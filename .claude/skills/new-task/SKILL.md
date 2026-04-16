---
name: new-task
description: Scaffold a new task folder from a task-type template. Supports analysis, development, and bugfix tasks. Usage: /new-task [type] [ModelName] [TaskID] [TaskName]
---

# /new-task

Scaffold a new task folder with the appropriate task-type template.

## Arguments

Parse `$ARGUMENTS` as: `{type} {ModelName} {TaskID} {TaskName}`

- `{type}` — one of `analysis`, `development`, `bugfix` (aliases: `dev`, `fix`, `bug`)
- `{ModelName}` — the model this task lives in
- `{TaskID}` — DevOps work item ID
- `{TaskName}` — short descriptive name

Examples:
- `/new-task dev Vaudoise 3641 INT001F_DMS_Invoicing`
- `/new-task analysis DYSNepi 5001 PostingFlowInvestigation`
- `/new-task bugfix DYSGEPIntegration 4200 VendorImportDuplicate`

If arguments are missing:
- If model is inferrable from the current working folder, use it
- If task type is not specified, **ask** — do not default to development
- If TaskID or TaskName are missing, ask

## Steps

1. **Determine the task type.** Map aliases: `dev` → `development`, `fix`/`bug` → `bugfix`.

2. **Read `context_setup.md`** from the model folder first, then project root, to get `ProjectPrefix`, `LabelFile`, `LabelLanguages`, `UserVISA`.

3. **Determine the task folder path:** `Models/{ModelName}/Tasks/{TaskID}_{TaskName}/`

4. **Copy the task-type template** from `.claude/task-templates/{type}/`:
   - `TASK.md` → fill in frontmatter and placeholders
   - `rules.md` → copy as-is (task-type rules)
   - `SNAPSHOT.md` → fill in frontmatter (`task_id`, `task_name`, `task_type`, `model`, `owner`, `last_updated`)

5. **Create the folder structure:**

   ```
   Models/{ModelName}/Tasks/{TaskID}_{TaskName}/
     TASK.md
     rules.md
     SNAPSHOT.md
     context_setup.md      ← generated with inherited values
     code/
       AxClass/
       AxTable/
       AxForm/
       AxEnum/
       AxEdt/
       AxLabel/
       AxMenuItemAction/
       AxMenuItemDisplay/
       AxMenuItemOutput/
     docs/
     samples/
     refcode/
   ```

   For **analysis** tasks, `code/` subfolders are created but expected to remain empty.

6. **Generate `context_setup.md`** with inherited values from model and project.

7. **Leave §1 Purpose, §2 Scope, §3 Constraints empty** in SNAPSHOT — prompt the user to fill them in.

## Output

1. Confirm the folder path and task type.
2. Create all directories and files.
3. Report each file created.
4. Remind the user to:
   - Fill in `SNAPSHOT.md` §1 Purpose, §2 Scope, §3 Constraints
   - Update `UserVISA` in `context_setup.md` if still placeholder
   - For development/bugfix tasks: run `/fetch-baseline` for existing artifacts before editing

## What NOT to do

- Do not create files under `code/Ax*/` — those are populated by `/fetch-baseline` or during edit sessions
- Do not fetch or read X++ source from local `Source/` or sibling repos
- Do not assume `ProjectPrefix` or `UserVISA` — read or ask
- Do not pre-fill SNAPSHOT Purpose/Scope/Constraints from guesses
- Do not default the task type — always ask if not specified
