# XppAtlas-Template

Project template for D365 F&O customization with AI-assisted workflow. Part of the [XppAtlas](https://github.com/AndreYaro/XppAtlas) platform.

Clone this template for each new D365 customization project.

## Structure

```
.claude/
  settings.json         # MCP permissions, hooks
  rules/                # Project rules (X++ standards, tool usage, safety)
  agents/               # d365-developer, d365-architect
  skills/               # 30+ slash commands (/start, /finish, /new-task, etc.)
  hooks/                # SessionStart, PreCompact, Stop
  task-templates/       # analysis, development, bugfix templates
Models/
  _Model_Template/      # Template for new models
    Tasks/
      _Task_Template/   # Template for new tasks
        TASK.md         # Task metadata
        SNAPSHOT.md     # Cross-session state
        code/           # Working artifacts
        docs/           # Design docs
        refcode/        # Reference code
        samples/        # Example payloads
CLAUDE.md               # Project passport
GEMINI.md               # X++ naming and coding standards
context_setup.md        # Project-level configuration
```

## Setup

1. Clone this template into your project folder
2. Edit `context_setup.md`: set `ProjectPrefix`, `LabelFile`, `UserVISA`
3. Verify XppAtlas MCP server is reachable: `mcp__xppatlas__list_models`
4. Run `validate-ai-setup.ps1`
5. Commit: `git commit -m "chore: instantiate template for {ProjectName}"`

## Daily workflow

```
/start          -> Identify task, load SNAPSHOT, check rules
/new-task       -> Scaffold new task folder
/fetch-baseline -> Pull artifacts from MCP into code/ folder
  (edit)        -> Work on the task
/review-code    -> Code review against project rules
/finish         -> Update SNAPSHOT, session handoff
```

## MCP server

All X++ discovery uses `mcp__xppatlas__*` tools from the XppAtlas MCP server.

## Related

- [XppAtlas](https://github.com/AndreYaro/XppAtlas) — Knowledge platform (server + client)
