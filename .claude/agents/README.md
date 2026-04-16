# .claude/agents — specialist agents

Two specialist agents aligned across Claude Code, Codex / VS Code, and Gemini.

| Agent | File | When to use |
|-------|------|-------------|
| `d365-developer` | `d365-developer.md` | X++ coding, bug fixes, code generation, code review, performance fixes, check-in prep |
| `d365-architect` | `d365-architect.md` | Integration design, architecture decisions, system-level analysis, design docs |

## Generic roles map to specialists

- **Research / exploration** → `d365-architect` (wide read) or `Explore` for pure file-and-symbol hunts
- **Implementation across multiple artifacts** → `d365-developer`; use `d365-architect` for pre-implementation impact review if ≥ 3 artifacts or any posting/integration boundary
- **Code review** → `d365-developer` with `/review-code`
- **Architecture audit** → `d365-developer` with `/audit-arch`

## When to delegate

- Wide cross-model research → `d365-architect` (keeps main context clean)
- Multi-artifact review pass → `d365-developer` with `/review-code`
- Everything else (small edits, single-file questions, lookups) → stay in main session

## Non-goals

- Do not spawn agents to "save time" on work fitting in the main session
- Do not spawn agents to bypass confirmation rules — agents inherit the same rules
- Do not spawn agents that reach outside this repo
