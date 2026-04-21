# Rule: Fallback & Evidence

Every assistant response that references X++ / D365 symbols, standard behaviour, or file paths **must** be grounded in retrievable evidence and must survive a partial MCP outage without aborting.

This rule is the consumer-side contract for the Phase 29 transparent-client changes: the XppAtlas MCP server now exposes remote failures as a structured `meta.standard_server_detail.reason ∈ {timeout, connect, http, unauthorized, empty, other, none}` envelope alongside the flat `meta.standard_server` status. Consumers branch on that signal instead of giving up.

## Evidence labels — use on every factual claim

When an answer rests on retrieved content, tag each load-bearing statement with one of:

| Label | Meaning | When to use |
|-------|---------|-------------|
| `[MCP-confirmed]` | Fetched this session via `search_artifacts` / `search_chunks` / `explore_artifact` / `get_artifact` / `semantic_search` / `check_symbol`, returned non-empty, `meta.standard_server.status == "ok"` where applicable | Anything newly looked up from the live index |
| `[standard-pack-cached]` | Answer derived from a pinned Standard Pack release (check with `list_standard_releases` / `explain_standard_source`); remote fetch not attempted or not needed because the cached pack covers the ask | Standard-model symbols present in the pinned Pack |
| `[inferred]` | Derived from D365 conventions (naming, framework patterns) or from the current task folder — **no MCP evidence fetched** | Truly conventional guidance where the user asked "in general, how does X work" |
| `[user-provided]` | Verbatim from the current conversation or files the user already pasted | Specs, FDDs, screenshots the user just dropped in |

**One claim, one label.** Do not chain labels. If a single claim has mixed provenance, split it into two sentences.

## Fallback cascade (ordered)

When the task needs information about a symbol or standard artifact, step through this cascade in order. Stop at the first tier that returns usable evidence.

1. **MCP live — `[MCP-confirmed]`.** Call the relevant tool (`search_artifacts`, `explore_artifact`, `check_symbol`, `semantic_search`). If `meta.standard_server.status == "ok"` and `data` is non-empty, the claim is sourced from here.

2. **Standard Pack cache — `[standard-pack-cached]`.** If tier 1 failed with `meta.standard_server.status in {"unreachable", "error"}`, fall through: call `list_standard_releases` to confirm a Pack is pinned, then use `explain_standard_source` / local search on the pinned release. Label every claim from this tier `[standard-pack-cached]`.

3. **Cached names — `[inferred]`.** If tiers 1 and 2 both come up empty, you may proceed using well-known D365 symbol names (e.g. `SalesTable`, `LedgerJournalTable`) only to *structure* the response (suggest where to look, what pattern likely applies), never to *assert facts* about fields, methods, or signatures. Label these statements `[inferred]` and suffix them with a follow-up: "Retry with `check_symbol(...)` once the Standard Server is reachable to confirm."

4. **Ask user — `[user-provided]`.** If the task requires a fact that tiers 1–3 cannot supply, ask the user for the source material (paste the class, link the Learn page, share the repository path). Do not invent.

## No-abort rule

A remote MCP failure is **never a reason to stop the task**. Specifically:

- `meta.standard_server.status == "unreachable"` → continue on tiers 2 → 3 → 4, explicitly surface the degradation.
- `meta.standard_server_detail.reason == "timeout"` → retry once with a narrower query or a different model filter; if still timing out, drop to tier 2.
- `meta.standard_server_detail.reason == "unauthorized"` → surface as a config error to the user (wrong admin token or server URL). Do not retry.
- `meta.standard_server_detail.reason == "http"` → log the status + reason, drop to tier 2.
- `meta.standard_server_detail.reason == "connect"` → likely server not running. Surface cleanly, drop to tier 2.
- `meta.standard_server_detail.reason == "empty"` → the query ran but returned nothing. This is a retrieval miss, not an infrastructure failure. Drop to tier 3.

At the end of any response produced with one or more remote failures, emit an **Incomplete evidence banner**:

```
⚠ INCOMPLETE STANDARD EVIDENCE
Remote Standard Server reported: <status / reason>
Standard-model claims marked [inferred] are not verified against the live index.
Retry with the Standard Server reachable to upgrade them to [MCP-confirmed].
```

This banner replaces "I cannot complete this task because the server is down." The task still completes; the provenance is just honestly reported.

## Evidence block at end of substantive responses

For any response that makes ≥ 3 factual claims about D365 symbols or behaviour, end with a short **Evidence** block listing the distinct sources consulted, e.g.:

```
Evidence:
- [MCP-confirmed] SalesTable.find() signature via explore_artifact (model=ApplicationSuite, chunks=3)
- [MCP-confirmed] SalesFormLetterPost.run() body via get_artifact (model=ApplicationSuite)
- [standard-pack-cached] LedgerJournalTable relations via explain_standard_source (release=10.0.1935)
- [inferred] VAUSalesTable extension naming convention (project prefix VAU)
```

Readers verify an answer by reading the Evidence block first and the prose second. Lack of an Evidence block on a substantive D365 answer is a code smell.

## When this rule applies

- Always, for any response that references X++ symbols, framework behaviour, or standard-model source.
- Skills that produce code (`/gen-coc`, `/gen-batch`, `/gen-entity`, `/gen-service`) must call at least one MCP tool before scaffolding, and the generated file must carry an `// Evidence:` comment block at the top of the class.
- Skills that explain or review (`/explain`, `/review-code`, `/fix-perf`, `/design-integration`) must include the Evidence block in their textual output.

## What this rule is *not*

- Not a license to pad every sentence with labels. Conversational chatter and project-local claims (task folder contents, user's stated goals) do not need labels.
- Not a replacement for `safety-boundaries.md`. Evidence discipline ≠ authorization. Even a `[MCP-confirmed]` fact does not authorize a destructive action.
