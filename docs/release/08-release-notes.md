# XppAtlas-Template — Release Notes

| | |
|---|---|
| **Version** | 1.0 (aligned with XppAtlas 5.4 / Phase 23) |
| **Release date** | 2026-04-16 |
| **Track** | Client project template |

---

## Highlights — V1.0

First public release. XppAtlas-Template ships as the opinionated starting point for any D365 F&O customization project that uses XppAtlas as its knowledge backend.

- **Four structural invariants** — MCP-only source, one-task-one-model, baseline-before-edit, per-task `SNAPSHOT.md`. All four are enforced by rules + skills + hooks, not by prompting discipline.
- **30+ slash-command skills** — session lifecycle (`/session-start`, `/session-finish`), task lifecycle (`/new-task`, `/fetch-baseline`, `/prep-comment`), validation (`/review-code`, `/audit-arch`, `/fix-perf`, `/testing`), generation (`/gen-coc`, `/gen-batch`, `/gen-entity`, `/gen-service`), design (`/design-integration`, `/explain`), maintenance (`/housekeeping`).
- **Three hooks** — `SessionStart` (reminds Claude to run `/session-start` first), `PreCompact` (forces a `SNAPSHOT.md` update before context compaction), `Stop` (refreshes the local search index).
- **Five numbered rule files** — autonomy, context-and-snapshot, xpp-change-safety, commit-and-checkpoint, production-caution. One page each by policy.
- **Two specialist agents** — `d365-developer` (default), `d365-architect` (design-heavy work).
- **Cross-tool alignment** — Claude Code (`CLAUDE.md` + `.claude/`), Codex (`AGENTS.md` + `skills/`), Gemini (`GEMINI.md` + shared `skills/`). `validate-ai-setup.ps1` enforces consistency.
- **Server/client split aware** — works identically against a local XppAtlas install (stdio MCP) or a shared LAN XppAtlas server (MCP over HTTP at `/mcp`). `.env` and `.vscode/mcp.json` carry the mode-specific wiring.
- **Multi-model support** — single-model projects and multi-model projects use the same layout. One `Models/{ModelName}/` folder per model; tasks never cross model boundaries.

---

## Compatibility matrix

| XppAtlas version | Template V1.0 support | Notes |
|-------------------|-----------------------|-------|
| 5.4 (Phase 23) | ✅ Recommended | Full server/client split with Phase 23 enforcement; `/session-start` knows to expect `build-core STANDARD` failures on clients and `build-core VENDOR/CUSTOM` failures on servers |
| 5.4 (Phases 21-22) | ✅ Supported | Pre-Phase 23 server/client split works; `build-core` rejections rely on manual operator discipline |
| 5.3 (Phase 20) | ✅ Supported | Standard Pack / Decision Engine / Log Reader are opt-in; template skills degrade gracefully when absent |
| 5.2 | ⚠️ Degraded | Metadata generator present; decision engine + log reader absent → `/review-code` cannot cite decision / readiness context |
| ≤ 5.1 | ❌ Not supported | MCP surface has too many gaps; template skills will fail |

The template's `validate-ai-setup.ps1` does not detect XppAtlas version — it's the project lead's responsibility to align. If the XppAtlas server is upgraded, re-run `validate-ai-setup.ps1` and check the [XppAtlas Release Notes](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/08-release-notes.md) for behaviour changes.

---

## Server/client split alignment (Phase 23)

With XppAtlas 5.4 Phase 23, indexing is split-mode-enforced:

- On an **XppAtlas server** (Ubuntu LAN, `XPPATLAS_SERVER_MODE=true`): `build-core` accepts STANDARD, refuses VENDOR and CUSTOM.
- On an **XppAtlas client** (developer PC with `XPPATLAS_STANDARD_SERVER_URL` set): `build-core` accepts VENDOR and CUSTOM, refuses STANDARD.
- On a **local-only install** (neither env var set): all kinds accepted.

The template does not index anything itself, but developers sometimes run `build-core` manually to refresh their local VENDOR + CUSTOM indices after the user-driven write-back at check-in time. If the refresh fails with a Phase 23 `ToolError(ErrorCode.CONFIG)`:

- On a client, ensure `XPPATLAS_STANDARD_SERVER_URL` is set (you're trying to index the wrong kind for your mode).
- On a server, developers should not be running `build-core` there at all; refresh happens on the server admin's schedule.
- On a local-only install, the error is spurious — check that neither env var is set in `.env`.

---

## Known limitations

- **No auto-compile.** The template cannot run the X++ compiler. Build / BP / SysTest signals come from Visual Studio or the Dev Tools build chain, then get fed into XppAtlas via `ingest_build_log`. This is by design — letting Claude shell out to the X++ toolchain would create false-green signals. See [XppAtlas ADR-017](https://github.com/AndreYaro/XppAtlas/blob/main/docs/adr/ADR-017-decision-lifecycle.md) for the level-A / level-B distinction.
- **TFVC check-in is manual.** `/prep-comment` produces the comment string; the developer runs `tf vc checkin` outside Claude. `.claude/settings.json` deny list refuses `tf` commands.
- **MCP source write-back is manual.** Copying `Models/{ModelName}/Tasks/{TaskID}_*/code/` into `models-src/custom/{ModelName}/` and re-indexing is user-driven. Claude never automates it — the template rules forbid it.
- **Skill mirrors are duplicated, not symlinked.** `.claude/skills/` (Claude Code) and `skills/` (Codex / Gemini) are separate copies kept in sync by `validate-ai-setup.ps1`. Windows symlinks don't work reliably across git clients; duplication is the pragmatic answer.
- **Single language for `SNAPSHOT.md`.** The template assumes English SNAPSHOT content. Localizing the SNAPSHOT file would require translating the rule references inside it — not done in V1.0.

---

## Upgrade path

### From no template (greenfield)

Follow [Getting Started](02-getting-started.md) steps 1-10.

### From an earlier iteration of the template (pre-V1.0 internal drafts)

- Back up the project's existing `Models/` and `docs/` — these are customer work.
- Replace everything else (`.claude/`, `skills/`, `tools/`, `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `SETUP_AND_USAGE.md`, `validate-ai-setup.ps1`, `.vscode/mcp.json`, `.env.example`) with V1.0.
- Restore `Models/` and `docs/` into the updated layout.
- Re-fill placeholders in the replaced files using your `context_setup.md` values.
- Run `validate-ai-setup.ps1` — fix any drift it flags.
- Commit: `chore: upgrade template to V1.0`.

### From XppAtlas 5.3 → 5.4 on the server

No template change required. The template works identically across XppAtlas 5.3 and 5.4 — the new Phase 21 / 22 / 23 capabilities are opt-in. Developers can start using `propose_extension_strategy_v2`, `ingest_build_log`, `assess_task_readiness`, `freeze_task_readiness` against their tasks without any template wiring.

---

## Version history

| Template version | Aligned with | Date | Notes |
|-------------------|--------------|------|-------|
| V1.0 | XppAtlas 5.4 (Phase 23) | 2026-04-16 | First public release |

---

## Breaking changes

None. V1.0 is the first release.

---

## See also

- [Product Overview](01-product-overview.md) — what this template is and who it's for
- [Getting Started](02-getting-started.md) — clone and configure
- [XppAtlas Release Notes](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/08-release-notes.md) — backend release history (V5.4, Phase 21 / 22 / 23)
