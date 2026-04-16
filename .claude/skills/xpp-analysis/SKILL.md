---
name: xpp-analysis
description: Deep X++ investigation — trace execution flows, analyze extension points, compare patterns, assess impact. Usage: /xpp-analysis [topic or artifact]
---

# /xpp-analysis

Structured investigation of an X++ topic, artifact, or flow. Produces findings in the task's `docs/` folder.

## Arguments

Parse `$ARGUMENTS` as a topic or artifact name (e.g. `CustInvoiceJour posting flow`, `VAUPaymentService extension points`, `batch performance of DYSVendorImport`).

## Steps

1. **Confirm the active task** and verify this is an analysis or investigation context.

2. **Plan the investigation.** Before calling MCP tools, decide:
   - What specific question are we answering?
   - Which artifacts are likely involved?
   - What evidence would answer the question?

3. **Gather evidence using MCP tools:**
   - `semantic_search` — for intent-style discovery ("how does X work?")
   - `explore_artifact` — for deep object inspection (fields, methods, relations, delegates)
   - `search_chunks` — for finding specific code patterns across the codebase
   - `search_patterns` / `recommend_patterns` — for established implementation patterns
   - `search_standard_artifacts` — for standard D365 reference implementations
   - `estimate_change_radius` — for impact analysis
   - `propose_extension_strategy` — for extension point analysis

4. **Limit MCP queries.** Max 3 queries on the same artifact. If you're going in circles, write what you know to `docs/` and re-plan.

5. **Write findings** to `docs/{topic}_analysis.md` in the task folder. Structure:
   - **Question** — what we investigated
   - **Artifacts inspected** — with key findings per artifact
   - **Patterns found** — existing implementations, extension points, usage patterns
   - **Impact assessment** — what would change, what would break
   - **Options** — at least two approaches with trade-offs
   - **Recommendation** — with rationale and risk assessment

6. **Update SNAPSHOT** — add findings to §5, documents to §7, next steps to §9.

## Anti-patterns

- Do not modify code artifacts during analysis. Write findings to `docs/`.
- Do not explore indefinitely. Cap at 3 rounds of MCP queries per sub-question.
- Do not recommend without evidence. Every recommendation should cite the MCP tool output that supports it.
