---
name: explain
description: Explain a D365 F&O concept, pattern, or API with a practical code example. Usage: /explain [Topic]
---

Explain the D365 F&O topic given in `$ARGUMENTS`.

Before explaining implementation details or showing code, use the D365 MCP search server first to find real project or standard examples of the pattern. Use model indexes for navigation when helpful, then confirm important details in the real XML/X++ source.

## Arguments
Parse `$ARGUMENTS` as: `{Topic}` (e.g. `Chain of Command`, `SysOperationFramework`, `Business Events`, `OData`)
- If no argument provided, ask the user what they want to understand.

## Explanation Format

Produce all four sections:

### 1. What It Is (2–3 sentences)
Plain-English definition. What problem does it solve? When did it replace the old approach?

### 2. When to Use It
A short bullet list of scenarios where this pattern is the right choice.
Include one counter-example: when NOT to use it.

### 3. How It Works — Code Example
A minimal, self-contained X++ code example using the project's `{ProjectPrefix}` prefix if `context_setup.md` is available.
Add `// TODO: [{UserVISA}] ...` comments on lines the user needs to customize.

### 4. Common Pitfalls
2–4 bullet points of the most frequent mistakes developers make with this topic, with a one-line fix for each.

## Topics Reference

Be ready to explain any of these (non-exhaustive):

**Extension Model**
- Chain of Command (CoC)
- Event Handlers (DataEventHandler, FormControlEventHandler, etc.)
- Table / Form / Class Extensions
- Delegates and Hookable methods

**Framework Classes**
- SysOperationFramework (SOF) — Controller, Service, Contract, DP, UIBuilder
- RunBaseBatch
- SysPlugin / SysExtension
- SysSetup / SysPostInit

**Data Access**
- Query object model vs. direct select
- `insert_recordset` / `update_recordset` / `delete_from`
- `RecordInsertList`
- Cross-company queries

**Integration**
- Custom Services (WCF/JSON)
- Data Entities (OData / DMF)
- Recurring Integration API
- Business Events

**Other**
- Financial Dimensions
- Number sequences
- Workflow
- SSRS Report Data Provider (RDP)
- SysTest framework
