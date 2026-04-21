# Rule: Tool and MCP usage

## XppAtlas MCP server (`xppatlas`)

The XppAtlas server (`mcp__xppatlas__*`) is the **only authoritative source** for all X++ source. It holds CUSTOM, VENDOR, and STANDARD model artifacts, patterns, embeddings, and community/learn search.

**Phase 28 transparent-client topology.** In server/client split mode this project is the client; the client indexes VENDOR + CUSTOM locally and proxies STANDARD queries to a LAN XppAtlas server. Every fan-out-capable response carries a `meta.standard_server.status` + `meta.standard_server_detail.reason` envelope — always inspect it before acting. See [`split-mode.md`](split-mode.md) for the full read/write plane invariants and [`fallback-and-evidence.md`](fallback-and-evidence.md) for the no-abort cascade.

### Discovery workflow (use in this order)

| Step | Tool | When |
|------|------|------|
| 1 | `semantic_search` or `search_patterns` | Intent-style lookup ("how does posting work?", "staging pattern") |
| 2 | `search_artifacts` | Known object by name+type; always pass `model_name`; **scan top-5 for exact-name match, do not trust #1** |
| 3 | `search_chunks` | Search within method bodies and source code |
| 4 | `explore_artifact` | Deep object context: fields, relations, methods, delegates, callers |
| 5 | `get_artifact` or `build_edit_bundle` | Full source XML before editing |
| 6 | `check_symbol` | Cross-check a member/field/enum value exists on an artifact before emitting code that references it |
| 7 | `recommend_patterns` | Find reusable implementation patterns for the current problem |

### Additional tools

- `search_learn` / `search_community` — Microsoft Learn docs and community answers
- `list_models` / `get_index_metadata` — model registry and metadata; `list_models` inspects `meta.standard_server` to tell you the split-mode shape
- `list_impl_patterns` / `get_impl_pattern` — browse implementation patterns
- `build_edit_bundle` — assembled source context before making edits
- `list_standard_releases` / `explain_standard_source` — Standard Pack cache fallback when the standard server is unreachable

**Deprecated (do not call):** `search_standard_artifacts`, `explore_standard_artifact`, `get_standard_source`. These are shim-only for one release cycle; XppAtlas unifies STANDARD/VENDOR/CUSTOM via the `model_name` parameter on the generic tools above.

### Exact-match discipline (T29-006)

Ranking is tiered: **1.0 exact name** / **0.8 prefix match** / **0.5 substring** / **0.3 multi-term AND**. When you know the exact object name (`CustTable`, `SalesFormLetter`, etc.), scan the **top-5** results for an exact-name hit — do not blindly take result #1. If no exact match appears in top-5, the artifact may not exist in the indexed models; fall through to `check_symbol` (for a member) or the fallback cascade (for a whole artifact).

### SysOp pivot — known-object matrix

When `search_artifacts` returns a `*Contract` / `*UIBuilder` / `*Response` but the user wants the service logic, pivot by naming convention:

| You found | You want | How |
|-----------|----------|-----|
| `{Name}Contract` | `{Name}Service` | Search `search_artifacts("{Name}Service", model_name=...)` |
| `{Name}UIBuilder` | `{Name}Controller` | Search `search_artifacts("{Name}Controller", model_name=...)` |
| `{Name}Response` / `{Name}Request` | `{Name}Service` | Search `search_artifacts("{Name}Service", model_name=...)` |

Then `explore_artifact` on the service for the actual logic. `get_object_relations` on the contract also exposes the service wiring via `DataContractAttribute`.

### Always pass `model_name`

When calling MCP tools that accept `model_name`, always pass it explicitly. Do not let the server guess the model — cross-model noise wastes context and causes errors. Empty `model_name` intentionally triggers fan-out discovery; only use it for cross-model exploration.

## MCP is the source of truth

All X++ source discovery goes through the XppAtlas MCP server. Never read from local `Source/` folders. Never reach into sibling repos. The sole exception is the user-driven check-in step (see `safety-boundaries.md`).

## Evidence labels (mandatory on generated code)

Every factual claim about the D365 codebase — class name, field type, attribute signature, default value, method existence — must carry one of these labels:

| Label | Meaning | Source |
|-------|---------|--------|
| `[MCP-confirmed]` | Just retrieved live from MCP | `search_artifacts` / `explore_artifact` / `get_artifact` / `check_symbol` response in this session |
| `[standard-pack-cached]` | Standard server unreachable, served from Pack cache | `list_standard_releases` + `explain_standard_source` |
| `[inferred]` | Best-guess from naming convention or structural pattern; **requires user verification** | `INCOMPLETE STANDARD EVIDENCE` banner at top of output |
| `[user-provided]` | Fact came from the user's prompt or an attached FDD | Chat / doc reference |

Never emit code that mixes confirmed and inferred facts without labels per fact. See `fallback-and-evidence.md` for the full doctrine.

## No-abort rule on standard-server unreachable

When `meta.standard_server.status != "ok"`, the session does **not** stop. Branch per `reason`:

- `timeout` → retry once; on second timeout, drop to Standard Pack cache
- `unauthorized` → surface as config error, **stop** (admin token wrong/missing)
- `http` / `connect` / `empty` / `other` → drop tier, do not retry, fall through cascade
- `not_configured` (status, no reason) → split-mode not active; no action needed if local mode is intended

Cascade: MCP live → Standard Pack cache → cached names → ask user. Emit with the label matching the tier actually used, plus the `INCOMPLETE STANDARD EVIDENCE` banner if the tier is below `[MCP-confirmed]`.

## XML structure reference

**Before generating any AOT object XML**, load a real example of the same object type from MCP:
1. Use `search_artifacts` with `model_name="ApplicationSuite"` (or equivalent standard model) to find a reference example — scan top-5 for exact match
2. Use `get_artifact` or `explore_artifact` to read its full XML structure
3. If the standard server is unreachable, fall through to `list_standard_releases` + `explain_standard_source` and label with `[standard-pack-cached]`

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
