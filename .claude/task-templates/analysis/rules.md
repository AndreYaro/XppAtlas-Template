# Task rules — analysis

This task is an **analysis** task. These rules override project defaults where specified.

## Behavioral emphasis

- **Explore before editing.** Do not create or modify code artifacts. Gather evidence first.
- **Gather evidence.** Use MCP tools to inspect artifacts, trace flows, compare patterns, and understand existing behavior.
- **Compare options.** When multiple approaches exist, document at least two with trade-offs before recommending one.
- **Identify risks and constraints.** Every recommendation must include a risk assessment.
- **Avoid premature code changes.** Analysis tasks produce documents, not code. If code changes are needed, they belong in a follow-up development task.
- **Produce structured output.** Results go in `docs/` as markdown. Use tables, Mermaid diagrams, and decision records.

## What to record in SNAPSHOT

- Findings and evidence (§5 Decisions log)
- Which artifacts were inspected and what was learned (§7)
- Open questions requiring stakeholder input (§10)
- Recommended next steps — typically "create development task" or "get stakeholder decision" (§9)

## MCP usage in analysis

Analysis tasks make heavy use of read-only MCP tools:
- `semantic_search` / `search_patterns` — for understanding existing patterns
- `explore_artifact` — for deep inspection of objects
- `search_chunks` — for finding references and usage patterns
- `find_references` / `find_related` — for impact analysis
- `explain_process_flow` / `trace_posting_flow` — for understanding business processes

## What this task does NOT do

- Create or modify files under `code/`
- Run `/fetch-baseline` (no baseline needed — no code changes)
- Produce check-in comments
- Commit or push code

If during analysis you discover that code changes are needed, record the finding in `docs/` and recommend creating a development or bugfix task.
