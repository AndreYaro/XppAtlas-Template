# Rule: Tool and MCP usage

## D365 MCP server (`xppatlas`)

The XppAtlas server (`mcp__xppatlas__*`) is the **only authoritative source** for all X++ source. It holds custom and standard model artifacts, patterns, embeddings, and community/learn search.

### Discovery workflow (use in this order)

| Step | Tool | When |
|------|------|------|
| 1 | `semantic_search` or `search_patterns` | Intent-style lookup ("how does posting work?", "staging pattern") |
| 2 | `search_artifacts` | Known object by name+type; always pass `model_name` |
| 3 | `search_chunks` | Search within method bodies and source code |
| 4 | `explore_artifact` | Deep object context: fields, relations, methods, delegates, callers |
| 5 | `get_artifact` or `build_edit_bundle` | Full source XML before editing |
| 6 | `recommend_patterns` | Find reusable implementation patterns for the current problem |

### Additional tools

- `search_standard_artifacts` / `explore_standard_artifact` / `get_standard_source` — for standard D365 objects
- `search_learn` / `search_community` — Microsoft Learn docs and community answers
- `list_models` / `get_index_metadata` — model registry and metadata
- `list_impl_patterns` / `get_impl_pattern` — browse implementation patterns
- `build_edit_bundle` — assembled source context before making edits

### Always pass `model_name`

When calling MCP tools that accept `model_name`, always pass it explicitly. Do not let the server guess the model — cross-model noise wastes context and causes errors.

## MCP is the source of truth

All X++ source discovery goes through the D365 MCP server. Never read from local `Source/` folders. Never reach into sibling repos. The sole exception is the user-driven check-in step (see `safety-boundaries.md`).

## XML structure reference

**Before generating any AOT object XML**, load a real example of the same object type from MCP:
1. Use `search_artifacts` or `search_standard_artifacts` to find a reference example
2. Use `get_artifact` or `explore_artifact` to read its full XML structure

Never generate XML structure from memory alone.

## Local tools

### Git (read-only)

Safe to run without confirmation:
- `git status`, `git status -s`, `git log`, `git diff`, `git show`, `git branch`

All write operations (`commit`, `push`, `reset`, `checkout`) require explicit user authorization every time.

### Python helper scripts

Safe to run:
- `python tools/ensure_index.py` — refresh X++ model index
- `python tools/search_index.py` — search pre-built indexes
- `python tools/bootstrap_context.py` — load context
- `python tools/index_all.py --incremental` — incremental index rebuild

### File operations

- Use Read for precise file reads
- Use Grep for code search within the repo
- Use Glob for file pattern matching
- Use the Agent tool with `Explore` for broad codebase exploration

### Terminal

- Use Bash for git commands, Python scripts, and system inspection
- Prefer MCP over terminal-based file exploration for X++ source

## Cost and risk awareness

| Operation | Cost | Risk |
|-----------|------|------|
| MCP read tools (search, explore, get) | Low | None |
| Git read-only (status, log, diff) | Low | None |
| File read/grep/glob | Low | None |
| MCP semantic_search (embedding-based) | Medium | None |
| Agent delegation (subagent spawn) | Medium | Context overhead |
| File write/edit in task folder | Low | Reversible |
| File write/edit outside task folder | Medium | Confirm first |
| Git write (commit, push) | High | User must authorize |

## What makes long sessions productive

- Read task SNAPSHOT first (avoids re-deriving context)
- Use MCP search before browsing folders manually
- Checkpoint SNAPSHOT after milestones (survives compaction)
- Use task `docs/` for investigation notes (survives across sessions)
- Delegate wide research to subagents (keeps main context clean)
- Stop and summarize instead of repeatedly rediscovering context
