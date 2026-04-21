# Rule: Split-mode — transparent client read/write plane (Phase 28)

XppAtlas ships in two deployment shapes. Customer projects cloned from this template are **always the client side**. The platform side (server) lives in the XppAtlas repo, not here. This rule defines the invariants that every consumer workflow must obey when the server/client split is in play.

Read this rule alongside `fallback-and-evidence.md`. The split-mode rule tells you **where** data comes from; the fallback rule tells you **what to do when it doesn't**.

Reference: [ADR-018 — Transparent client read/write plane](https://github.com/AndreYaro/XppAtlas/blob/main/docs/adr/ADR-018-transparent-client-read-write-plane.md).

## The two shapes

| Shape | When | Topology |
|-------|------|----------|
| **Local mode** | One developer, no LAN server available | Single `xppatlas` process indexes STANDARD + VENDOR + CUSTOM; every MCP call hits the local store |
| **Server/client split** | Team shares a LAN XppAtlas server | Server (`XPPATLAS_SERVER_MODE=true`) hosts STANDARD models; each client indexes VENDOR + CUSTOM locally and proxies STANDARD queries to the server |

Detect which shape you are in by inspecting `.env`:

- `XPPATLAS_STANDARD_SERVER_URL` empty → local mode
- `XPPATLAS_STANDARD_SERVER_URL` set → split mode; that URL is the read-side of the standard plane

**Rule:** do not guess. If neither `.env` nor the active `list_models` response tells you clearly, run `mcp__xppatlas__list_models` once and read `meta.standard_server.status` — the envelope reveals the shape unambiguously (`ok` / `unreachable` / `not_configured`).

## Read plane — local ∪ remote, auto-routed

When split mode is configured, the client transparently merges local and remote results. The MCP tool surface is **one catalog**, not two.

| Tool | Behaviour on the client |
|------|------------------------|
| `list_models` | Fans out to the server; merged list carries `source: "local" \| "remote"` and `writable: false` on remote entries |
| `semantic_search` (empty `model_name`) | Fans out local + remote; per-hit `source` label + score-sorted merge |
| `search_artifacts` / `search_chunks` | Routed per-model via `_resolve_route` → LOCAL direct / REMOTE proxy / REMOTE_UNREACHABLE structured error |
| `get_artifact` / `explore_artifact` | Proxied to the server for remote models; `check_symbol` same |
| Curated list/search (funcmap / intmap / patcat / patterns) | Fans out on empty `model_name`; per-model results merged |

**Consequence:** never call the legacy `*_standard_*` tools. They are deprecated — `search_standard_artifacts`, `explore_standard_artifact`, `get_standard_source` all unify into the generic tools with `model_name` scoping. If you see them referenced in older rules or skills, treat it as a stale instruction and use the generic variant instead.

### `meta.standard_server` envelope

Every fan-out-capable response carries:

```json
{
  "items": [...],
  "meta": {
    "standard_server": {
      "status": "ok" | "unreachable" | "not_configured"
    },
    "standard_server_detail": {
      "reason": "timeout" | "connect" | "http" | "unauthorized" | "empty" | "other" | "none"
    }
  }
}
```

Always inspect the envelope before acting on results. A successful-looking response with `status != "ok"` means **the STANDARD side was not reached** — the list may be incomplete. Escalate per `fallback-and-evidence.md`.

## Write plane — local-only, explicitly guarded

STANDARD models are **read-only from the client**. The platform enforces this at the strategy/decision layer:

| Tool | Guard |
|------|-------|
| `propose_extension_strategy` | Rejects STANDARD `anchor_artifact_id` with "Standard model is read-only from this client. Target a local custom artifact instead." |
| `propose_extension_strategy_v2` | Same guard after `evidence_snapshot_id` validation |
| `reevaluate_decision` | Guard runs on `prior.model_name` from the loaded decision |

If you hit this error, the fix is **never** to bypass it — it means the CoC / extension / override target is inside a standard model and must be re-anchored to a custom artifact (typically a `{ProjectPrefix}`-prefixed extension class, table extension, or data-entity extension).

Pattern tools (`create_pattern`, `submit_pattern_for_review`) are not model-scoped — they're local-only writes without a `model_name` parameter, so the STANDARD-target concept does not apply.

## Route classification — internal behaviour you can trust

Every per-model MCP call goes through `_resolve_route(model_name) → LOCAL | REMOTE | REMOTE_UNREACHABLE`:

- **LOCAL** — model is in the local registry; serve from local store
- **REMOTE** — model is only on the server; proxy via HTTP to the server's `/semantic`, `/artifacts`, `/symbols/check`, etc.
- **REMOTE_UNREACHABLE** — model is expected on the server but the server is not reachable; return a structured error, never a silent empty result

The client never silently falls back to an empty result set. If a call returns empty items with `standard_server.status = "unreachable"`, that is the platform telling you the standard plane was **not consulted** — not that the data doesn't exist.

## Invariants — do not violate

1. **Never write to a STANDARD model.** All customizations target a local CUSTOM artifact.
2. **Never treat an unreachable envelope as authoritative absence.** Missing hits on `unreachable` ≠ artifact doesn't exist. Apply the fallback cascade.
3. **Never call the deprecated `*_standard_*` tools.** Use the unified tools with `model_name`.
4. **Always pass `model_name` when you know the target model.** Empty `model_name` triggers fan-out — useful for discovery, wasteful for targeted lookups.
5. **Never abort on split failure.** If the server is unreachable, fall through the cascade in `fallback-and-evidence.md` (Standard Pack cache → cached names → ask user).
6. **Record the plane in evidence labels.** `[MCP-confirmed]` on a remote hit implies the read-plane fan-out worked; `[standard-pack-cached]` implies the Pack snapshot was consulted because the server was unreachable.

## Server identity — off-limits from this repo

This template is the **client side**. Do not try to run `admin register-model`, `admin build-core`, `admin rebuild-core`, or `admin index-delta` against STANDARD models from a customer project session — those commands belong on the server host, run by an operator, against the XppAtlas server repo. The Phase 23 write-plane guard (`_require_indexable_here`, `_split_mode_reject`) lives in the server and is out of scope for consumer sessions.

If a task pushes you toward server-side admin work, stop and ask the user to open a session on the server host.

## When something is off

- `meta.standard_server.status = "unauthorized"` — the admin token is wrong or missing. Surface as a config error, do not retry.
- `meta.standard_server.status = "unreachable"` with `reason = "timeout"` — retry once per `fallback-and-evidence.md`; if still unreachable, fall through the cascade.
- `meta.standard_server.status = "unreachable"` with `reason = "connect"` / `"http"` / `"empty"` — do not retry the single call; drop tier and degrade to cached evidence.
- `meta.standard_server.status = "not_configured"` with `XPPATLAS_STANDARD_SERVER_URL` set — the URL is not valid from this client; surface, do not silently continue.
- Unexpected `writable: true` on a remote entry — stop and flag; the server is misreporting its own plane.
