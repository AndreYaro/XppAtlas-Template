# {ProjectName} — Claude Code Project Passport

D365 F&O customizations project. Replace `{ProjectName}`, `{ModelName}`, and `{ProjectPrefix}` when cloning into a new customer project. Model source of truth is the **D365 MCP server** (`mcp__xppatlas__*`). All new work lives under `Models/{ModelName}/Tasks/{TaskID}_{Name}/`.

## Session protocol

1. **Run `/start`.** Identify the active task and model from `git status`. Read the task's `rules.md` (task type) and `SNAPSHOT.md` (working memory) before any discovery.
2. **Read the project rules** in `.claude/rules/`:
   - `project-main.md` — rule hierarchy, X++ principles, coding standards
   - `tool-usage.md` — MCP discovery workflow, tool guidance
   - `safety-boundaries.md` — confirmation boundaries, hard limits
   - `task-lifecycle.md` — artifact lifecycle, snapshot discipline, checkpoint triggers
3. **Read model rules** at `Models/{ModelName}/rules.md` if they exist.
4. **MCP is the source of truth.** Use `mcp__xppatlas__*` for all X++ discovery. Never read from local `Source/` or sibling repos.
5. **Load `context_setup.md` bottom-up**: task → model → project.
6. **Work according to the task type** (analysis / development / bugfix). Task rules shape behavior.
7. **Checkpoint SNAPSHOT** after 5+ edits, before validation, before ending the session. Run `/finish` to close cleanly.
8. **Delegate** wide research to `d365-architect` or `Explore`, multi-artifact reviews to `d365-developer`.

## Rule hierarchy

Precedence: task rules > model rules > project rules.

| Level | Location | Scope |
|-------|----------|-------|
| Project | `.claude/rules/*.md` | Applies everywhere |
| Model | `Models/{ModelName}/rules.md` | Overrides project for that model |
| Task | `Models/{ModelName}/Tasks/{TaskID}/rules.md` | Overrides model+project for that task |

## Task types

| Type | Created via | Behavioral emphasis |
|------|-------------|-------------------|
| **analysis** | `/new-task analysis ...` | Explore, gather evidence, produce docs. No code changes. |
| **development** | `/new-task dev ...` | Extension-first implementation, baseline workflow, validate before done. |
| **bugfix** | `/new-task bugfix ...` | Investigate root cause first, smallest correct fix, assess regression. |

Task-type templates live in `.claude/task-templates/{type}/`. Task rules are copied into each task folder.

## X++ standards

@GEMINI.md

## Session bootstrap

Read the nearest `context_setup.md` (task level first, then model, then project):

| Variable | Purpose |
|----------|---------|
| `ProjectPrefix` | Prefix for all new AOT objects |
| `LabelFile` | Target label file for new labels |
| `LabelLanguages` | Translation targets |
| `UserVISA` | Used in TODO markers and check-in comments |

## D365 MCP workflow

1. Intent-style lookup → `semantic_search` or `search_patterns`
2. Known object → `search_artifacts` (always pass `model_name`)
3. Code search → `search_chunks`
4. Deep inspection → `explore_artifact`
5. Full source → `get_artifact` or `build_edit_bundle`
6. Pattern reuse → `recommend_patterns`

**Before generating any AOT XML**, load a reference example from MCP first.

## Project layout

```text
{Project}/
├── Models/
│   └── {ModelName}/
│       ├── rules.md                    ← model-specific rules (optional)
│       ├── context_setup.md            ← model-level config
│       └── Tasks/
│           └── {TaskID}_{TaskName}/
│               ├── TASK.md             ← task identity and metadata
│               ├── rules.md            ← task-type rules
│               ├── SNAPSHOT.md         ← working memory
│               ├── context_setup.md    ← task-level config
│               ├── code/Ax{Type}/      ← working artifacts
│               ├── docs/               ← designs, specs, investigation notes
│               ├── refcode/            ← reference code
│               └── samples/            ← payload examples
├── context_setup.md                    ← project-level config
└── .claude/
    ├── rules/                          ← project rules
    ├── task-templates/                 ← analysis, development, bugfix templates
    ├── skills/                         ← slash commands
    └── agents/                         ← specialist agent definitions
```

## Specialist agents

| Agent | When to use |
|-------|-------------|
| `d365-developer` | X++ coding, bug fixes, code generation, code review, check-in prep |
| `d365-architect` | Integration design, architecture decisions, system-level analysis |

## Skills

| Command | Purpose |
|---------|---------|
| `/start` | Session cold-open — identify task, load context, report readiness |
| `/finish` | Session close — update SNAPSHOT, produce handoff summary |
| `/new-task [type] [Model] [ID] [Name]` | Scaffold a new task (analysis / dev / bugfix) |
| `/task-resume [Model] [ID]` | Resume a known task in a new session |
| `/fetch-baseline` | Pull baseline artifacts from MCP |
| `/review-code` | Full code review against project rules |
| `/testing` | Static validation of task code |
| `/audit-arch` | Separation-of-concerns audit |
| `/xpp-analysis [topic]` | Deep X++ investigation with MCP |
| `/extension-design [artifact]` | Design extension strategy for a standard artifact |
| `/bug-investigation [symptom]` | Structured root cause analysis |
| `/gen-coc [Class] [Method]` | CoC extension scaffold |
| `/gen-batch [Name]` | SysOperation batch job scaffold |
| `/gen-entity [Name]` | Data Entity + staging table |
| `/gen-service [Name]` | Custom Service class |
| `/design-integration [Name]` | Integration architecture proposal |
| `/fix-perf` | Convert row-by-row loops to set-based |
| `/explain [Topic]` | D365 pattern explanation with code example |
| `/prep-comment` | Generate TFVC check-in comment |
| `/housekeeping` | Repository hygiene audit |
