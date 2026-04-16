# Code Review Checklist — {TaskID}_{TaskName}

## Naming & Prefixing

- [ ] Every new AOT object starts with `{ProjectPrefix}`
- [ ] Variables use `camelCase` — no Hungarian notation
- [ ] Extensions follow `{Prefix}{Original}_Cls/Tab/Form/Entity_Extension` pattern
- [ ] All names, comments, and strings are in English

## Labels & Strings

- [ ] No hardcoded UI strings — all use Label IDs from `{LabelFile}`
- [ ] `DataMemberAttribute` uses double-quoted strings: `[DataMemberAttribute("field")]`

## Queries & Performance

- [ ] No `select *` — fields explicitly listed
- [ ] Row-by-row loops replaced with set-based operations where applicable
- [ ] Indexes used appropriately; no unnecessary full-table scans

## Architecture

- [ ] No business logic in form methods
- [ ] Logic repeated 3+ times is refactored into a shared method
- [ ] Methods are < 50 lines and single-responsibility

## Safety

- [ ] `ttsbegin` / `ttscommit` open and close in the same method
- [ ] No `ttsAbort` — uses `throw error(...)`
- [ ] Null checks present before record field access (`if (!myTable)`)
- [ ] CoC extensions call `next methodName(...)` — never omitted

## File Placement

- [ ] All modified/new XML in `code/Ax{ObjectType}/` (never in MCP source or legacy `Source/` mirrors)
- [ ] XML structure verified against a real `.xml` reference file of the same type
- [ ] `AxTableField` elements carry `xmlns=""` and correct `i:type`

## Code Quality

- [ ] Dead code removed (not commented out)
- [ ] TODOs use format `// TODO: [{UserVISA}] description`
- [ ] No magic numbers — constants or EDTs used
