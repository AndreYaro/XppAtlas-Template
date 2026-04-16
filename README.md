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
.vscode/
  mcp.json              # XppAtlas MCP server connection (stdio or HTTP)
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
.env.example            # Client-side XppAtlas config template
```

## Setup

1. Clone this template into your project folder
2. Edit `context_setup.md`: set `ProjectPrefix`, `LabelFile`, `UserVISA`
3. Copy `.env.example` to `.env` and set `XPPATLAS_STANDARD_SERVER_URL` (only in server/client split mode) plus embedding options
4. Verify `.vscode/mcp.json` points at your XppAtlas checkout (stdio) or your LAN server (HTTP)
5. Verify XppAtlas MCP server is reachable: `mcp__xppatlas__list_models`
6. Run `validate-ai-setup.ps1`
7. Commit: `git commit -m "chore: instantiate template for {ProjectName}"`

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

All X++ discovery uses `mcp__xppatlas__*` tools from the XppAtlas MCP server. Two deployment shapes are supported:

- **Local mode** — XppAtlas runs on your workstation; the local server serves every model. Configured via `.vscode/mcp.json` (stdio).
- **Server/client split** — a shared LAN server hosts standard models behind an HTTP API; your local client proxies standard-model queries to it. Configured via `XPPATLAS_STANDARD_SERVER_URL` in `.env` (plus optional HTTP entry in `.vscode/mcp.json`).

## Related

- [XppAtlas](https://github.com/AndreYaro/XppAtlas) — Knowledge platform (server + client)
