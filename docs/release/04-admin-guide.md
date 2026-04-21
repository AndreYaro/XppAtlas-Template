# XppAtlas-Template — Admin Guide

| | |
|---|---|
| **Document type** | Administration Guide |
| **Audience** | Project lead / tech lead / AI-setup owner on the customer project |
| **Version** | 1.0 |
| **Last updated** | 2026-04-16 |

---

## Table of Contents

1. [Instantiating the template for a new customer](#1-instantiating-the-template-for-a-new-customer)
2. [Choosing the XppAtlas deployment mode](#2-choosing-the-xppatlas-deployment-mode)
3. [Multi-developer workflow](#3-multi-developer-workflow)
4. [Multi-model repositories](#4-multi-model-repositories)
5. [Housekeeping](#5-housekeeping)
6. [Rule maintenance](#6-rule-maintenance)
7. [Skill and agent maintenance](#7-skill-and-agent-maintenance)
8. [Hook troubleshooting](#8-hook-troubleshooting)
9. [Cross-tool consistency (Claude / Codex / Gemini)](#9-cross-tool-consistency-claude--codex--gemini)
10. [Security and permissions](#10-security-and-permissions)

---

## 1. Instantiating the template for a new customer

The project lead sets up the template once; every developer on the team clones the customer repo afterwards. Setup checklist:

1. Clone the template, detach from template history, init a fresh Git timeline (see [Getting Started §1](02-getting-started.md)).
2. Fill every `{Placeholder}` across `context_setup.md`, `CLAUDE.md`, `README.md`, `.claude/settings.json`.
3. Decide the deployment mode — local-only vs server/client split (see §2 below).
4. Create one `Models/{ModelName}/` folder per D365 model in scope.
5. Commit the instantiation as a single `chore: instantiate template for {ProjectName}` commit.
6. Push to the customer's team repo (Azure DevOps / GitHub / GitLab — the template is repo-host-agnostic).
7. Document the XppAtlas server URL (if server/client split) in the customer repo's `README.md` so new developers can find it.

## 2. Choosing the XppAtlas deployment mode

| Mode | When to pick | Disk per developer | Setup cost |
|------|--------------|---------------------|-------------|
| **Local-only** | Solo developer, short-lived project, no shared LAN | ~20-40 GB (STANDARD + VENDOR + CUSTOM on each machine) | 30-90 min per machine |
| **Server/client split** | ≥ 2 developers, long-lived project, shared LAN available | ~2-5 GB per client (VENDOR + CUSTOM only); STANDARD lives on the server | 30-90 min for the server, 20-40 min per client |

For teams of 2+, server/client split is strictly better:

- STANDARD model indexing is expensive (ApplicationSuite alone is 30-120 minutes of embedding time). Do it once, reuse it across every developer.
- Standard Pack releases, pattern catalogue, decision engine history live in one canonical store.
- Each developer's client only manages their current customer + vendor models, which they already own as source anyway.

The template works identically in either mode — `mcp__xppatlas__*` tools behave the same way. The difference is purely where STANDARD models are indexed (server vs every client).

### Switching from local-only to server/client split

Once the team grows from one developer to two:

1. Stand up an Ubuntu LAN box with XppAtlas in server mode (see [XppAtlas Admin Guide §9](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/04-admin-guide.md#9-deployment-modes)).
2. Index STANDARD models there.
3. On each developer's client `.env`: set `XPPATLAS_STANDARD_SERVER_URL=http://<server>:8765`.
4. On each developer's client: **delete** the local STANDARD index to free disk. Phase 23 will now refuse attempts to re-index STANDARD on a client.

No changes to the customer project repo are needed — `.vscode/mcp.json` can keep its stdio entry, which points to the client; the client handles the split transparently.

## 3. Multi-developer workflow

The template is designed so every developer has an identical `.claude/` setup, an identical `.vscode/mcp.json`, and each developer picks up tasks independently. Conventions the project lead should establish early:

- **One task = one developer.** Avoid multiple developers editing the same task folder simultaneously — it's a merge-conflict factory. If work has to be split, open two coordinated tasks referencing each other in `SNAPSHOT.md §3 Constraints`.
- **Task IDs match the ticket tracker.** `{TaskID}` is the ticket number (Azure DevOps work item, ServiceNow CR, TFS task, whatever the customer uses). `/new-task 3641 INT001_DMS_Invoicing` means "ticket 3641 — integration 001 — DMS invoicing".
- **Baseline commits are pushed immediately.** The baseline commit is the anchor for review. Push it before starting edits so reviewers can rebase onto it.
- **Check-ins reference readiness snapshots.** If your process includes a readiness gate, `freeze_task_readiness` before `/prep-comment` and attach the TR-\* id to the TFVC check-in comment or PR description.

## 4. Multi-model repositories

A single customer project can customize multiple D365 models (e.g. a core customer model plus integration-only models). The template supports this natively:

```text
D365{CustomerName}/
├── context_setup.md                          ← project default
└── Models/
    ├── Vaudoise/
    │   ├── context_setup.md                  ← can override ProjectPrefix / LabelFile
    │   └── Tasks/
    │       ├── 3641_INT001_DMS_Invoicing/
    │       └── 3642_EXT002_NewReportBank/
    ├── VaudoiseIntegrations/
    │   ├── context_setup.md
    │   └── Tasks/
    │       └── 3650_INT005_SAPOutbound/
    └── VaudoisePayroll/
        ├── context_setup.md
        └── Tasks/
            └── ...
```

**One task = one model**, always. `.claude/rules/20-xpp-change-safety.md` enforces this. A change touching two models is always two tasks, one per model, coordinated via `SNAPSHOT.md §3 Constraints`.

## 5. Housekeeping

Run `/housekeeping` periodically (weekly is a good cadence for active projects). It audits:

| Check | What it flags |
|-------|----------------|
| Stale SNAPSHOTs | Tasks whose `SNAPSHOT.md` hasn't been touched in N days but has uncommitted changes |
| Missing baselines | Tasks with files under `code/` that have no corresponding baseline commit |
| Duplicate task folders | Leading-whitespace or case-collision collisions in `Models/*/Tasks/` |
| Shared-config drift | `.claude/settings.json`, `.claude/rules/*.md`, `.claude/skills/*/SKILL.md` out of sync with the template |
| Cross-task contamination | Files in one task folder referencing another task's artifacts |
| `{ProjectPrefix}` violations | New artifacts whose names don't start with the configured prefix |

Findings are **appended** to `.claude/CLEANUP_CANDIDATES.md`. `/housekeeping` never deletes or renames anything — the project lead reviews the file and acts manually.

Separately, on the XppAtlas server side, the server admin runs `gc_task_workspace` periodically to garbage-collect old Phase 21 decisions and readiness history (see [XppAtlas Admin Guide §14.5](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/04-admin-guide.md)). That is a server concern, not a client/template concern.

## 6. Rule maintenance

Rules live in `.claude/rules/` as five numbered files:

| File | Scope |
|------|-------|
| `00-autonomy.md` | Confirmation boundaries — what Claude does / asks / refuses |
| `10-context-and-snapshot.md` | Per-task SNAPSHOT discipline, anti-degradation, checkpoint triggers |
| `20-xpp-change-safety.md` | Artifact lifecycle, extension-strategy order, baseline-before-edit |
| `30-commit-and-checkpoint.md` | Git + TFVC hygiene, checkpoint triggers |
| `40-production-caution.md` | Posting, integration, number-sequence, tax, security hard limits |

When changing a rule:

- Commit with a message that explains the rule delta: `rules: loosen 00-autonomy to allow git show without confirmation`.
- Keep rules short. Anything longer than a page tends to be ignored by Claude and by humans.
- If a rule change affects what Claude should / shouldn't do autonomously, bump it in the `SessionStart` hook reminder too — Claude only reads rules if it knows they exist.
- Run `validate-ai-setup.ps1` after any rule change — it checks that the Claude / Codex / Gemini catalogues stay consistent.

## 7. Skill and agent maintenance

Skills live in `.claude/skills/{skill-name}/SKILL.md`. Each skill is a standalone `.md` file that Claude loads on invocation. Conventions:

- **One file, one purpose.** If a skill grows beyond a page of instructions, split it.
- **Skills are imperative, not decorative.** A skill file should describe *exactly* the steps Claude takes, in order, with explicit tool calls. Vague skills ("help the user with code review") produce vague behaviour.
- **Skills mirror across tools.** The `skills/` root folder (Codex) and `.claude/skills/` (Claude Code) must stay in sync. `validate-ai-setup.ps1` enforces this.

Agents live in `.claude/agents/`. Two ship by default:

- **`d365-developer`** — the default agent for task edits. Owns the extension-strategy decision, the SNAPSHOT updates, the `/fetch-baseline` and `/new-task` flows.
- **`d365-architect`** — invoked for design-heavy work: solution blueprints, cross-task integration design, `/audit-arch` reports.

`claude-code-guide/` and similar project-agnostic agents can be added if the team wants them, but keep the default catalogue short — too many specialized agents slow down routing decisions.

## 8. Hook troubleshooting

Three hooks ship in `.claude/settings.json`:

| Hook | Trigger | Action |
|------|---------|--------|
| `SessionStart` | At the start of every conversation | Prints project-specific reminder ("You're in {ProjectName}. Run /session-start first.") |
| `PreCompact` | Right before Claude compacts the conversation | Forces a `SNAPSHOT.md` update so the post-compact session can resume |
| `Stop` | When a conversation ends | Runs `python tools/ensure_index.py --incremental` to refresh the local search index |

Common failures:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `python tools/ensure_index.py` fails on session start | Python not on `PATH`, or `tools/` was deleted | Fix the env; restore `tools/` from the template |
| `SessionStart` hook message mentions `{ProjectName}` literally | Template wasn't instantiated | Edit `.claude/settings.json` and replace the placeholders |
| `PreCompact` doesn't fire | Using a Claude Code version without the hook | Upgrade Claude Code |
| `Stop` hook hangs | `tools/index_all.py` is scanning too much — source tree too large | Tighten the `.gitignore` or add an `--exclude` flag to the command |

## 9. Cross-tool consistency (Claude / Codex / Gemini)

The template is designed so the same skill catalogue works across three tools:

| Tool | Entry point | Skill folder | Rules |
|------|-------------|---------------|-------|
| Claude Code | `CLAUDE.md` | `.claude/skills/` | `.claude/rules/` |
| Codex | `AGENTS.md` | `skills/` | Shared with Claude via symlinks / duplicated files |
| Gemini | `GEMINI.md` | Same `skills/` as Codex | Shared |

`validate-ai-setup.ps1` checks that:

- Every skill named in `CLAUDE.md` exists under `.claude/skills/` and under `skills/`.
- Every rule named in `CLAUDE.md` exists under `.claude/rules/`.
- The `SessionStart` hook message in `.claude/settings.json` matches the 7-step protocol in `CLAUDE.md`.
- Agent definitions (`d365-developer`, `d365-architect`) are consistent across the three tools.

Run it after every significant config change.

## 10. Security and permissions

The template's `.claude/settings.json` ships with a curated `permissions.deny` list. The key refusals:

| Command | Why denied |
|---------|------------|
| `git push`, `git reset --hard`, `git checkout -- <path>`, branch deletion | Destructive — developer-driven only |
| `git commit` (with exceptions) | Commits are explicitly user-initiated — baseline commits and task commits must be deliberate |
| `tf` / TFVC commands | Check-ins happen outside Claude by policy |
| `scripts/build-v4-model.bat` and equivalent build scripts | Claude cannot run the X++ compiler; letting it try creates false-green signals |
| Any write outside this repository | Hard boundary — the only legitimate cross-repo write is the user-driven copy back to MCP source at check-in time |
| Writing `.env`, `.pfx`, `.mcp.json` with secrets | Secret-leak guard |

**If you need to widen the allowed set**, edit `permissions.deny` with full awareness of the risk and document the change in a commit message. Common legitimate additions:

- `gh pr create` / `gh pr view` — for teams using GitHub + `gh` CLI for PRs.
- `az devops work-item show` — for Azure DevOps integration.
- `tf vc history` — read-only TFVC queries (don't allow write commands).

Never widen:

- Deploy commands, environment-mutating commands, model-publish commands.
- Secret-bearing file writes.
- Cross-repo writes beyond the MCP source store.

---

## See also

- [Getting Started](02-getting-started.md) — initial setup
- [User Guide](03-user-guide.md) — daily workflow
- [Configuration Reference](07-configuration.md) — `context_setup.md`, `.env`, `.claude/settings.json`, `.vscode/mcp.json`
- [XppAtlas Admin Guide](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/04-admin-guide.md) — server maintenance, deployment modes, Phase 22 GC
