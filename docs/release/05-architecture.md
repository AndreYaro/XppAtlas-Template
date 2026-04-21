# XppAtlas-Template — Architecture Reference

| | |
|---|---|
| **Document type** | Architecture Reference |
| **Audience** | Template maintainers, project leads, curious developers |
| **Version** | 1.0 |
| **Last updated** | 2026-04-16 |

---

## 1. What the template is architecturally

XppAtlas-Template is **configuration + conventions + skills**, not code. It is a prebuilt `.claude/` directory, a prebuilt `Models/` skeleton, and a small Python helper tree. When instantiated into a customer repo, it turns that repo into a disciplined AI-assisted D365 development workspace.

The template does not:

- Ship any X++ code.
- Ship any D365 source files.
- Index anything itself — it delegates all indexing to the XppAtlas MCP server.
- Execute X++ compilation, TFVC, or deployment — these are user-driven outside Claude.

The template does:

- Enforce four rules structurally (MCP-only, one task = one model, baseline before edit, per-task SNAPSHOT).
- Provide a skill catalogue so developers don't have to prompt Claude from scratch each session.
- Wire hooks that protect against context degradation.
- Align three AI tools (Claude Code / Codex / Gemini) on the same skill surface.

## 2. Folder layout

```text
{CustomerProjectRepo}/
│
├── CLAUDE.md                            ← Claude Code project passport + 7-step session protocol
├── GEMINI.md                            ← Shared X++ naming + coding standards
├── AGENTS.md                            ← Codex mirror of CLAUDE.md
├── README.md                            ← Human-facing project overview
├── SETUP_AND_USAGE.md                   ← Detailed setup guide
├── context_setup.md                     ← Project-level ProjectPrefix / LabelFile / UserVISA
├── validate-ai-setup.ps1                ← Cross-tool consistency check
│
├── docs/release/                        ← This documentation set (01-08)
│
├── .claude/
│   ├── settings.json                    ← MCP permissions, hooks, SessionStart reminder
│   ├── CLEANUP_CANDIDATES.md            ← /housekeeping findings (human-resolved, never auto-executed)
│   │
│   ├── rules/                           ← 5 numbered rule files (see §4)
│   │   ├── 00-autonomy.md
│   │   ├── 10-context-and-snapshot.md
│   │   ├── 20-xpp-change-safety.md
│   │   ├── 30-commit-and-checkpoint.md
│   │   └── 40-production-caution.md
│   │
│   ├── skills/                          ← 30+ slash commands (see §5)
│   │   ├── session-start/SKILL.md
│   │   ├── session-finish/SKILL.md
│   │   ├── new-task/SKILL.md
│   │   ├── fetch-baseline/SKILL.md
│   │   ├── review-code/SKILL.md
│   │   ├── audit-arch/SKILL.md
│   │   ├── prep-comment/SKILL.md
│   │   └── ... (see 06-tool-reference.md for the full list)
│   │
│   ├── agents/
│   │   ├── README.md                    ← When to delegate to which agent
│   │   ├── d365-developer.md            ← Default agent for task edits
│   │   └── d365-architect.md            ← Design-heavy work
│   │
│   └── hooks/
│       └── README.md                    ← SessionStart / PreCompact / Stop documentation
│
├── skills/                              ← Codex / VS Code skill mirror (synchronized by validate-ai-setup.ps1)
│
├── tools/                               ← Python helpers
│   ├── ensure_index.py                  ← Called by SessionStart hook
│   ├── search_index.py                  ← Local search fallback
│   ├── bootstrap_context.py             ← Initial context loader
│   └── index_all.py                     ← Full reindex (incremental by default)
│
├── .vscode/
│   └── mcp.json                         ← MCP server wiring (stdio or HTTP)
│
├── .env.example                         ← Client-side XppAtlas config template
│
└── Models/
    ├── _Model_Template/                 ← SKELETON — do not delete
    │   ├── context_setup.md
    │   └── Tasks/
    │       └── _Task_Template/
    │           ├── SNAPSHOT.md          ← Copied into every new task
    │           ├── README.md
    │           ├── code_review_checklist.md
    │           ├── context_setup.md
    │           ├── code/Ax{Type}/
    │           ├── docs/
    │           ├── samples/
    │           └── refcode/
    │
    └── {ModelName}/                     ← One folder per real D365 model
        ├── context_setup.md
        └── Tasks/
            └── {TaskID}_{TaskName}/
                ├── SNAPSHOT.md          ← Per-task cross-session state
                ├── README.md
                ├── code_review_checklist.md
                ├── context_setup.md
                ├── code/Ax{Type}/       ← Baseline + edits (XML / XPP)
                ├── docs/
                ├── samples/
                └── refcode/
```

## 3. The MCP boundary

The template maintains a hard boundary: **the XppAtlas MCP server is the only authoritative source of X++ code in scope of a task**. Everything else is local scratch.

```text
┌──────────────────────────────────────────────────────────┐
│  Customer project repo (from template)                   │
│                                                          │
│   ┌──────────────────┐                                   │
│   │  .claude/ rules  │◀──── enforced by                  │
│   │  + skills +      │      SessionStart hook            │
│   │  hooks           │                                   │
│   └────────┬─────────┘                                   │
│            │                                             │
│            ▼                                             │
│   ┌──────────────────────────────────────┐               │
│   │  Models/{ModelName}/Tasks/{TaskID}/  │               │
│   │    ├── SNAPSHOT.md  ◀── cross-session│               │
│   │    ├── code/AxClass/*.xml  ← baseline│ no local      │
│   │    │                         + edits │ Source/ reads │
│   │    └── docs/                         │               │
│   └──────────────┬───────────────────────┘               │
│                  │                                       │
│                  │ fetch-baseline,                       │
│                  │ get_artifact,                         │
│                  │ search_*, explore_*                   │
│                  │                                       │
└──────────────────┼───────────────────────────────────────┘
                   │  MCP (stdio or HTTP)
                   ▼
┌──────────────────────────────────────────────────────────┐
│  XppAtlas server (local or LAN)                          │
│  · STANDARD models (ApplicationSuite, etc.)              │
│  · VENDOR + CUSTOM models (local client only)            │
│  · Pattern catalogue, decision engine, readiness gates   │
└──────────────────────────────────────────────────────────┘
```

**What the template will not do:**

- Read X++ from any local `Source/` folder.
- Read from a sibling repo.
- Use `git`, `grep`, or `ripgrep` to search for X++ code (uses `mcp__xppatlas__search_*` instead).
- Write to the XppAtlas source store automatically. The write-back at check-in time is user-driven, outside Claude.

This boundary is what makes the workflow deterministic. Local source trees drift. MCP indexes are canonical by construction.

## 4. Rule architecture

Five numbered rule files under `.claude/rules/`. The numbering is load-bearing — lower numbers are read first, higher numbers assume earlier rules in context.

| File | Responsibility | Key invariant |
|------|----------------|---------------|
| `00-autonomy.md` | Confirmation boundaries, repo-scope hard limit | Claude never writes outside the repo except the user-driven MCP write-back |
| `10-context-and-snapshot.md` | Per-task SNAPSHOT, anti-degradation, checkpoint triggers | Every task has a SNAPSHOT; it's updated at explicit trigger moments |
| `20-xpp-change-safety.md` | Artifact lifecycle, extension-strategy order, baseline-before-edit | No edit without a baseline commit; extension-strategy order is 1→5 |
| `30-commit-and-checkpoint.md` | Git + TFVC hygiene | Commits are deliberate; `tf`/`git push`/`git reset --hard` denied |
| `40-production-caution.md` | Posting / integration / number-sequence / tax / security hard limits | Claude asks before touching these areas, even for "minor" changes |

The rule set is intentionally small. The default AI behaviour is to ignore walls of text — five files of one page each is roughly the ceiling at which Claude actually reads them.

## 5. Skill architecture

Skills are invoked as `/skill-name` in Claude Code. Categorization:

| Category | Skills | Purpose |
|----------|--------|---------|
| **Session lifecycle** | `/session-start`, `/session-finish` | Cold-open and close-out protocols |
| **Task lifecycle** | `/new-task`, `/fetch-baseline`, `/prep-comment` | Task-boundary workflows |
| **Validation** | `/review-code`, `/audit-arch`, `/fix-perf`, `/testing` | Read-only reports |
| **Generation** | `/gen-coc`, `/gen-batch`, `/gen-entity`, `/gen-service` | Scaffold mechanism-specific code |
| **Design** | `/design-integration`, `/explain` | Multi-artifact reasoning |
| **Maintenance** | `/housekeeping` | Non-destructive audit, appends to CLEANUP_CANDIDATES.md |

Each skill is a standalone `.md` file under `.claude/skills/{skill-name}/SKILL.md`. Skills are imperative — they describe *exactly* the steps Claude takes, in order, with explicit MCP tool calls. Vague skill descriptions produce vague behaviour.

## 6. Hook architecture

Three hooks in `.claude/settings.json`:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `SessionStart` | Every conversation start | Remind Claude to run `/session-start` first; print project-specific context |
| `PreCompact` | Right before Claude would compact the conversation | Force a `SNAPSHOT.md` update so the post-compact session can resume without losing decisions |
| `Stop` | Conversation ends | Run `python tools/ensure_index.py --incremental` to refresh the local search index |

The `PreCompact` hook is the anti-degradation safety net. It fires before Claude loses context, not after.

## 7. Deployment topology (where code lives and flows)

```text
                     ┌────────────────────────────────┐
                     │  XppAtlas Server (Ubuntu LAN)  │
                     │  STANDARD models only          │
                     │  HTTP /mcp + REST              │
                     │  Phase 23: rejects VENDOR+CUSTOM│
                     └────────────────┬───────────────┘
                                      │
                  ┌──── HTTP / MCP ───┘
                  │
         ┌────────┴──────────┐
         │                   │
         ▼                   ▼
  ┌──────────────┐     ┌──────────────┐
  │  Dev 1 PC    │     │  Dev 2 PC    │
  │              │     │              │
  │  XppAtlas    │     │  XppAtlas    │
  │  client      │     │  client      │
  │              │     │              │
  │  VENDOR+     │     │  VENDOR+     │
  │  CUSTOM      │     │  CUSTOM      │
  │  indexed     │     │  indexed     │
  │  locally     │     │  locally     │
  │              │     │              │
  │  Claude Code │     │  Claude Code │
  │  ↕           │     │  ↕           │
  │  Customer    │     │  Customer    │
  │  project     │     │  project     │
  │  repo (from  │     │  repo (from  │
  │  template)   │     │  template)   │
  └──────────────┘     └──────────────┘
         │                   │
         ▼                   ▼
       TFVC check-in to customer's D365 codeline
```

**Key invariants:**

- STANDARD models live exactly once, on the server. Phase 23 refuses `build-core ApplicationSuite` from a client.
- VENDOR + CUSTOM models live on each developer's client. Phase 23 refuses `build-core MyCustomModel` from a server.
- Task folders live in the customer project repo, one folder per task per model.
- Check-ins go to the customer's D365 TFVC codeline, outside Claude, using the comment from `/prep-comment`.
- The MCP source store (where XppAtlas indexes from) is refreshed manually by copying from `Models/{ModelName}/Tasks/{TaskID}_*/code/` into `models-src/custom/{ModelName}/` and re-indexing. User-driven, outside Claude.

## 8. Separation of concerns

Three cleanly separated responsibilities:

| Layer | Responsibility | Owner |
|-------|-----------------|--------|
| **XppAtlas server** | Index, search, pattern catalogue, decision engine, log reader, readiness gates | XppAtlas project |
| **XppAtlas client** | Local VENDOR + CUSTOM indexing, MCP stdio for AI tools, task workspace storage | XppAtlas project |
| **XppAtlas-Template** | Skills, rules, hooks, agent definitions, task folder conventions | This template |

The template does not reach into XppAtlas internals. It consumes the MCP surface and adds a workflow layer on top. An XppAtlas version bump that preserves the MCP surface (even a major one like V5.3 → V5.4 → Phase 23) does not require a template change.

## 9. Why this shape

Short rationale for the non-obvious design choices:

**One task = one folder, not one branch.** Branches work across one repository; the workflow crosses the customer project repo, the XppAtlas source store, and TFVC. Folders travel; branches do not.

**Baseline commits in the customer repo, not in TFVC.** TFVC check-ins happen once at the end; reviews happen in the customer project repo as Git PRs. The baseline commit is what makes the Git diff reviewable before TFVC.

**Per-task SNAPSHOT, not a global one.** Global snapshots accumulate stale state from closed tasks and become noise. Per-task snapshots get archived with the task folder and disappear cleanly when the task closes.

**Claude / Codex / Gemini share the same skill catalogue.** Customer teams use different tools. The template meets them where they are rather than forcing one. The cost is duplicated skill files; `validate-ai-setup.ps1` pays the consistency-check tax.

**Hooks, not prompts, for anti-degradation.** "Please remember to update the snapshot" in a prompt is ignored 60% of the time. A `PreCompact` hook that forces it is ignored 0% of the time.

---

## See also

- [User Guide](03-user-guide.md) — daily workflow
- [Tool Reference](06-tool-reference.md) — every skill, hook, and rule
- [XppAtlas Architecture Reference](https://github.com/AndreYaro/XppAtlas/blob/main/docs/release/05-architecture.md) — server-side module layering, split topology, Phase 21 lifecycle
