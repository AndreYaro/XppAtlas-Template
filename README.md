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

## Transparent client read/write plane (Phase 28, ADR-018)

In split mode this template is **always the client side**. The platform transparently merges the local catalog (VENDOR + CUSTOM) with the remote catalog (STANDARD) so you work against **one unified tool surface**, not two:

- **Read plane — local ∪ remote, auto-routed.** `list_models`, `semantic_search` (empty `model_name`), `search_artifacts` / `search_chunks` / `get_artifact` / `explore_artifact` / `check_symbol`, and the curated list/search tools all fan out. Results carry `source: "local" \| "remote"` and remote entries carry `writable: false`.
- **Write plane — local-only, explicitly guarded.** `propose_extension_strategy`, `propose_extension_strategy_v2`, and `reevaluate_decision` reject STANDARD targets with `"Standard model is read-only from this client. Target a local custom artifact instead."` The fix is re-anchoring the extension onto a `{ProjectPrefix}` artifact, never bypassing the guard.
- **Deprecated tools.** `search_standard_artifacts`, `explore_standard_artifact`, `get_standard_source` are shim-only (one release cycle); the unified tools with `model_name` scoping replace them.

Every fan-out-capable response carries a `meta.standard_server` envelope so the client knows whether the STANDARD side was consulted:

```json
"meta": {
  "standard_server": { "status": "ok" | "unreachable" | "not_configured" },
  "standard_server_detail": { "reason": "timeout" | "connect" | "http" | "unauthorized" | "empty" | "other" | "none" }
}
```

A successful-looking response with `status != "ok"` means **the standard plane was not reached** — the list may be incomplete. The client never treats this as authoritative absence. Skills must fall through the cascade defined in [`.claude/rules/fallback-and-evidence.md`](.claude/rules/fallback-and-evidence.md) (MCP live → Standard Pack cache → cached names → ask user), and the split-mode invariants in [`.claude/rules/split-mode.md`](.claude/rules/split-mode.md).

Tuning knobs for unreachable behaviour live in `.env.example` (timeout, retry-on-timeout, soft-unreachable). See ADR-018 in the XppAtlas repo for the full design.

## Related

- [XppAtlas](https://github.com/AndreYaro/XppAtlas) — Knowledge platform (server + client)
