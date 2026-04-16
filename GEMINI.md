# {ProjectName} — D365 F&O Project Rules

## Session Bootstrap

At the start of every session, read `context_setup.md` bottom-up: task → model → project.

| Variable | Purpose |
|----------|---------|
| `ProjectPrefix` | Prefix for all new AOT objects |
| `LabelFile` | Target label file for new labels |
| `LabelLanguages` | Translation targets |
| `UserVISA` | Used in TODO markers and check-in comments |
| `reference_paths` | Logical MCP source references — load code with D365 MCP tools, never from local `Source` folders |

If absent, ask for `ProjectPrefix` and `UserVISA` before generating any code.

## Code And Pattern Discovery

When searching for existing X++ code, framework usage, helper methods, extension points, or standard implementation patterns, use the D365 MCP search server first.

Preferred discovery order:
1. Use the D365 MCP server to search for objects, references, related methods, and intent-style patterns.
2. Use model indexes such as `.claude/index/{ModelName}_summary.json` and `.claude/index/_all_summary.json` for navigation and impact analysis.
3. Read the real XML/X++ source files before editing or citing a concrete implementation.

Use the MCP server especially for:
- finding standard or project examples of a pattern before proposing code
- locating helper methods, facade classes, and extension points
- checking whether the repository already contains a reusable implementation
- comparing multiple real examples before recommending an approach

Indexes are navigation aids and the MCP server is the default search surface. Real source XML/X++ remains the final source of truth before edits.

## D365 MCP Workflow

Use the local D365 MCP server before making X++ or metadata changes.

Workflow:
1. For intent-style lookup, use `find_pattern` first.
2. For a known object, use `resolve_object` first.
3. If the object is a table, use `find_table_usage`.
4. If the object is a service, use `find_service_usage`.
5. If the object is a form, use `find_form_usage`.
6. Use `find_references`, `get_object_context`, `get_object_relations`, and `find_relation_uses` for narrower follow-up analysis.
7. Use `get_chunk` or `get_file` to open exact source before implementing changes. Treat MCP output as the only authoritative model source.
8. Prefer standard D365 patterns found through the MCP tools over inventing new patterns.

## Shared Specialist Agents

Keep the same specialist agent names across Codex, Claude Code, and Gemini:

| Agent | When to use | Claude Code | Codex / VS Code |
|-------|-------------|-------------|-----------------|
| `d365-developer` | X++ coding, bug fixes, code generation, code review, performance fixes, check-in prep | `.claude/agents/d365-developer.md` | `skills/d365-developer/` |
| `d365-architect` | Integration design, architecture decisions, system-level analysis, design docs | `.claude/agents/d365-architect.md` | `skills/d365-architect/` |

## Shared Skills

Keep the same skill names across `.claude/skills/` and `skills/`. Gemini should use the same catalog when the user asks for one of them:

| Skill | Purpose |
|-------|---------|
| `new-task` | Scaffold a new task folder |
| `review-code` | Full code review against project rules |
| `prep-comment` | Generate TFVC check-in comment |
| `audit-arch` | Separation-of-concerns audit |
| `gen-coc` | CoC extension scaffold |
| `gen-batch` | SysOperationFramework batch job |
| `gen-entity` | Data Entity plus staging table |
| `gen-service` | Custom Service class |
| `design-integration` | Integration architecture proposal |
| `fix-perf` | Convert row-by-row loops to set-based |
| `explain` | D365 pattern explanation with code example |

## X++ Standards

## 1. Naming

| Element | Convention |
|---------|------------|
| AOT objects | `{Prefix}CamelCase` — prefix from `context_setup.md` |
| Variables | `camelCase` — no Hungarian notation |
| Suffixes | `*Entity`, `*View`, `*Map`, `*DP`, `*Controller`, `*Contract`, `*EventHandler` |
| Language | English only — all names, comments, and commit messages |

## 2. Extension Naming

| Type | Pattern |
|------|---------|
| Class | `{Prefix}{OriginalClass}_Cls_Extension` |
| Table | `{Prefix}{OriginalTable}_Tab_Extension` |
| Form | `{Prefix}{OriginalForm}_Form_Extension` |
| Data Entity | `{Prefix}{OriginalEntity}_Entity_Extension` |

## 3. Architecture

- Business logic lives in **tables or classes only** — never in forms
- If logic appears in **3+ places** → refactor into a shared method
- Methods must be **< 50 lines** and single-responsibility

## 4. Queries & Performance

- **No `select *`** — always enumerate required fields
- Prefer `insert_recordset`, `update_recordset`, `delete_from` over row-by-row loops
- Row-by-row loops that touch > 1 record **must** be converted to set-based

## 5. Safety & Error Handling

- `ttsbegin` / `ttscommit` must open **and** close in the **same method**
- Use `throw error(...)` — never `ttsAbort`
- **No hardcoded strings** — use Label IDs from `{LabelFile}`
- Validate record existence before field access: `if (!myTable) { ... }`

## 6. Code Quality

- Comments explain **why**, not what
- TODO format: `// TODO: [{UserVISA}] description`
- Replace magic numbers with constants or EDTs
- Remove dead code — never comment it out

## 7. XML Structure Rules

Before finalising any generated XML file, verify its structure against `StandardModels/ExpenseManagement/Ax{ObjectType}/`.

### Field & Relation Rules

| Object | Rule |
|--------|------|
| `AxTableField` | Must carry `xmlns=""` and correct `i:type` (e.g., `i:type="AxTableFieldString"`) |
| Enum fields | No `<EnumValue>` element |
| `AxTableRelation` | Must carry `xmlns=""` and `i:type="AxTableRelationForeignKey"` for FK |
| `AxTable` | Sections in order: `<DeleteActions />`, `<FieldGroups>` (AutoReport, AutoLookup, AutoIdentification, AutoSummary, AutoBrowse), `<FullTextIndexes />`, `<Mappings />`, `<Relations>`, `<StateMachines />` |

### Class Rules

| Scenario | Rule |
|----------|------|
| DataContract fields | Declare as `private` |
| Static utility classes | Must be `final` |
| `DataMemberAttribute` | Double-quoted strings only: `[DataMemberAttribute("fieldName")]` |
| parm methods | Use `this.field` in body |
| CoC extension | `[ExtensionOf(classStr(...))] final class {Prefix}Target_Cls_Extension` — no extra modifiers |
| CoC override | Always call `next methodName(...)` — never omit |

### AxClass XML Editing Safety

- Treat each X++ method as an XML unit in `AxClass/*.xml` — add, move, or remove code by editing whole `<Method>` blocks.
- Never paste a new X++ method directly inside an existing `<![CDATA[ ... ]]>` body.
- Every added method must keep the full structure: `<Method>` → `<Name>` → `<Source><![CDATA[ ... ]]></Source>` → `</Method>`.
- Preserve the existing XML layout and make minimal in-place edits instead of large rewrites.
- After any `AxClass` XML edit, re-open the surrounding lines and verify the `<Method>` boundaries are still intact.
