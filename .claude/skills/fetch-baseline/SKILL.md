---
name: fetch-baseline
description: Fetch the current (untouched) version of one or more AOT artifacts from the XppAtlas MCP server into the active task folder, so the user can commit the baseline before edits begin. Usage: /fetch-baseline AxClass:Foo AxTable:Bar AxForm:Baz
---

# /fetch-baseline

Pull artifacts from MCP into the active task's `code/Ax{Type}/` folder **byte-for-byte**. The user then commits those files as the baseline "before" state. Only after that commit may Claude edit them.

The XppAtlas MCP server (`mcp__xppatlas__*`) is the **only** source of truth for X++ source. This skill never reads from a local `Source/` folder and never reaches into a sibling repo. On `meta.standard_server.status != "ok"` / `meta.standard_server_detail.reason != "none"`, handle per `.claude/rules/fallback-and-evidence.md` (retry once on `timeout`, stop on `unauthorized`, otherwise fall through the cascade — **never abort the baseline fetch silently**).

## Arguments

Parse `$ARGUMENTS` as a whitespace-separated list of `{ObjectType}:{ObjectName}` pairs.

- `ObjectType` ∈ `AxClass`, `AxTable`, `AxForm`, `AxEnum`, `AxEdt`, `AxDataEntity`, `AxMenuItem`, `AxSecurityPrivilege`, `AxLabelFile`, `AxView`, `AxQuery`, `AxMap`, `AxService`, `AxServiceGroup`, and other standard AOT types.
- `ObjectName` is the bare AOT name, no prefix path, no file extension.

Example:

```
/fetch-baseline AxClass:CustInvoiceJour AxTable:CustInvoiceJour AxForm:CustInvoiceJournal
```

If `$ARGUMENTS` is empty, ask the user for the list. Never guess.

## Steps

1. **Confirm active task and model** as in `/session-start`. Fetching into the wrong task folder is a corrupting mistake; do not skip this.

2. **Per artifact, call MCP `get_artifact`:**

   ```
   mcp__xppatlas__get_artifact(
     model_name = <active model>,
     object_type = <ObjectType>,
     object_name = <ObjectName>
   )
   ```

   - Always pass `model_name`. Never let MCP pick a model.
   - If the artifact does not exist in the active model, **stop**. Do not silently fall back to another model. Report the gap and ask the user what to do — most common answer is "I'll add it as a new artifact in this task", which means there is no baseline to fetch.
   - If multiple models expose the same object and the user wants the baseline from a *different* model (e.g. to extend a standard object), ask explicitly and record the decision in SNAPSHOT §5.

3. **Write the result byte-for-byte** to `Models/{ModelName}/Tasks/{TaskID}_*/code/Ax{Type}/{ObjectName}.xml`.
   - No reformatting, no whitespace normalization, no re-indenting, no line-ending conversion.
   - Create `code/Ax{Type}/` if missing.
   - If the file already exists locally, **do not overwrite** without the user's explicit say-so in this session — an existing file may already contain in-progress edits.

4. **Update SNAPSHOT §4 "Source artifacts (read-only baseline)"** by appending one row per fetched artifact with `ObjectName`, `ObjectType`, model, `mcp__xppatlas__get_artifact`, and an empty "Baseline commit" cell.

5. **Stop and tell the user, verbatim:**

   > Baseline files written. Please review and commit them before I make any edits. After you commit, reply with the commit short SHA so I can record it in SNAPSHOT §4 and begin work.

6. **Do not make any edits to the fetched files** until the user confirms the baseline commit. This is the step the whole lifecycle depends on — skipping it produces an unreviewable diff and silently destroys the pre-change state.

7. **After the user confirms the baseline commit,** fill in the commit SHA in SNAPSHOT §4 and acknowledge that edit work may now begin.

## Anti-patterns

- **Never** reformat or "tidy" the fetched XML. The whole point is a byte-identical capture of the current production state.
- **Never** fetch across models in the same call without explicit user direction.
- **Never** begin editing a fetched file before the baseline commit exists.
- **Never** fetch from a local `Source/` folder or a sibling repo — MCP only.
- **Never** write the final edited file back to the MCP source store. That happens at check-in time, manually, by the user.
