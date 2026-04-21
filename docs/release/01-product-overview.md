# XppAtlas-Template — Product Overview

| | |
|---|---|
| **Document type** | Product Overview |
| **Audience** | D365 F&O developers, project leads, architects |
| **Version** | 1.0 (aligned with XppAtlas 5.4 / Phase 23) |
| **Last updated** | 2026-04-16 |

---

## What XppAtlas-Template is

XppAtlas-Template is the **project template for a D365 Finance & Operations customization repository** that uses [XppAtlas](https://github.com/AndreYaro/XppAtlas) as its knowledge backend. Clone this template once per customer project to get a prebuilt, opinionated workspace that turns Claude Code (or Codex / VS Code Copilot / Gemini) into a disciplined D365 development partner.

The template is the **client-side half** of the XppAtlas platform. The server-side half — STANDARD-model indexing, semantic search, pattern catalogue, decision engine, log reader, readiness gates — lives in the XppAtlas server. The template connects to that server over MCP (stdio for local-only deployments, HTTP for server/client-split deployments) and layers a task-centric workflow on top.

## The problem it solves

D365 F&O work breaks AI agents in predictable ways:

- **AOT source is not files.** Claude wants to grep. ApplicationSuite is 100K+ artifacts in a database, not a source tree. Without MCP, Claude either hallucinates or re-explores the same artifacts every session.
- **Long tasks lose coherence.** A posting-flow extension spans days. Context compactions erase the decisions log. Re-reading the conversation replays the same mistakes.
- **Baseline drift corrupts Git history.** If the "before" state of an artifact was never committed, the task's diff includes both the customer's change and any layering delta the environment had — unreviewable.
- **MCP tool surface is large.** XppAtlas ships 143 tools. A fresh session does not know which one to reach for first, and reaching for the wrong one wastes context.

XppAtlas-Template addresses each of these with a concrete mechanism — the SNAPSHOT file, the baseline commit, the skill catalogue, the rule set — so the solution is structural, not dependent on prompting discipline.

## What ships

| Piece | Purpose |
|-------|---------|
| `.claude/` | Settings, rules, skills, hooks, agents — the full Claude Code configuration |
| `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` | Mirror project passports for Claude Code, Gemini, and Codex |
| `Models/_Model_Template/` | Skeleton copied for every new D365 model this project customizes |
| `Models/_Model_Template/Tasks/_Task_Template/` | Skeleton copied for every new task — includes the `SNAPSHOT.md` template |
| `context_setup.md` | Project-level identity — `ProjectPrefix`, `LabelFile`, `UserVISA`, `AutoTranslate` |
| `.vscode/mcp.json` | MCP server wiring — stdio (local) or HTTP (LAN server) |
| `.env.example` | Client-side XppAtlas config — server URL, source root, embedding options |
| `validate-ai-setup.ps1` | Consistency check across Claude Code / Codex / Gemini configs |
| `tools/` | Python helpers for local indexing (`ensure_index.py`, `search_index.py`, `index_all.py`) |

## How it fits with XppAtlas

```text
 ┌─────────────────────────────────────┐       ┌───────────────────────────────┐
 │  Customer project repo              │       │  XppAtlas Server (Ubuntu LAN) │
 │  (from this template)               │       │                               │
 │                                     │       │  · STANDARD models            │
 │  · Models/{ModelName}/Tasks/...     │       │  · Pattern catalogue          │
 │  · Per-task SNAPSHOT.md             │ MCP   │  · Semantic search            │
 │  · .claude/ skills + rules          ├──────▶│  · Decision engine            │
 │  · VENDOR + CUSTOM model source     │       │  · Log reader + readiness     │
 │  · Claude Code / Codex / Copilot    │       │                               │
 └─────────────────────────────────────┘       └───────────────────────────────┘
          client                                          server
```

The template assumes an XppAtlas server is reachable — either locally on the developer's machine (stdio MCP) or on a shared LAN server (MCP over HTTP at `/mcp` + HTTP REST). All X++ discovery, retrieval, pattern lookup, and decision-engine calls go through MCP. The template itself never reads raw `Source/` trees and never proxies around the MCP boundary.

## Core rules the template enforces

The template is opinionated because D365 projects that drift from these four rules become unreviewable:

1. **MCP is the only authoritative source.** No local `Source/` folder reads, no sibling repo reads. `mcp__xppatlas__get_artifact` is the single path for X++ code into the workspace.
2. **One task = one folder = one model.** Tasks never spill across models. A change touching two models is two coordinated tasks, not one.
3. **Baseline before edit.** Every existing artifact the task modifies is fetched byte-for-byte from MCP and committed to Git *before* any edit. The task's real change set is then the diff from that baseline commit.
4. **Per-task `SNAPSHOT.md` is the cross-session memory.** A dedicated file per task survives conversation compactions and hand-offs. No global snapshot file — that pattern always accumulates stale state.

The `.claude/rules/` directory encodes these as five numbered rule files (`00-autonomy`, `10-context-and-snapshot`, `20-xpp-change-safety`, `30-commit-and-checkpoint`, `40-production-caution`). The skills and hooks enforce them at runtime.

## Who should use this template

- **D365 F&O developers** delivering customer customizations in Visual Studio + TFVC.
- **Project architects** who need reviewable change sets and explicit extension-strategy trails.
- **Teams of 2+ developers** who want the XppAtlas server to handle shared STANDARD indexing while each developer owns their task folders locally.

Single-developer local-only projects work too, but the template shines when multiple developers cooperate on the same customer model — each developer runs their own client against a shared LAN server, and the template's discipline (baseline commits + SNAPSHOT + extension-strategy order) is what keeps their check-ins reviewable.

## Related documents

- [Getting Started](02-getting-started.md) — clone, configure, first task
- [User Guide](03-user-guide.md) — daily workflow end-to-end
- [Admin Guide](04-admin-guide.md) — multi-developer setup, housekeeping, rule maintenance
- [Architecture Reference](05-architecture.md) — folder layout, MCP boundary, skill layering
- [Tool Reference](06-tool-reference.md) — every skill, hook, and rule in the template
- [Configuration Reference](07-configuration.md) — `context_setup.md`, `.env`, `.claude/settings.json`
- [Release Notes](08-release-notes.md) — template version history
