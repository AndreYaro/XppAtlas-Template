---
name: testing
description: Scope-aware validation for a D365 F&O task. Runs static checks against the active task folder and reports what CAN and CANNOT be verified without a live X++ build.
---

# /testing

There are no unit tests in this repository. "Testing" here means static validation against project rules plus whatever user-side confirmation is available. **Never** claim a build or functional test passed — Claude cannot run the X++ compiler.

## Scope

Operate strictly inside `Models/{ModelName}/Tasks/{TaskID}_*/code/**`. Do not recurse into other tasks or other models.

## Steps

1. **Confirm active task** (as `/session-start` step 1).
2. **Enumerate files changed since baseline.** Use `git diff --name-only <baseline>..HEAD` plus the current working tree.
3. **For each changed file, run the applicable static checks:**

   - **AxClass XML:**
     - Every `<Method>` has `<Name>`, `<Source>`, and `<![CDATA[ ... ]]>` brackets intact.
     - `[ExtensionOf(...)]` classes are `final` and each augmented method calls `next`.
     - No `select *`, no row-by-row DML over > 1 record, no X++ reserved keywords as variable names.
     - All variables declared at top of method (X++ syntax rule).
     - No hardcoded user-facing strings — label references instead.
     - `ttsbegin`/`ttscommit` open and close in the same method; `throw error(...)`, never `ttsAbort`.
   - **AxTable XML:**
     - Section order: `DeleteActions`, `FieldGroups` (AutoReport, AutoLookup, AutoIdentification, AutoSummary, AutoBrowse), `FullTextIndexes`, `Mappings`, `Relations`, `StateMachines`.
     - Field elements carry `xmlns=""` and correct `i:type`.
     - FK relations carry `xmlns=""` and `i:type="AxTableRelationForeignKey"`.
   - **AxForm / AxMenuItem / AxSecurityPrivilege:**
     - MenuItem exists for every new display form.
     - Maintain + View privileges exist for every new table-backed form.
     - Privileges are wired into a duty/role — or the SNAPSHOT §5 explicitly records "security wiring deferred".
   - **Labels:**
     - Every new label ID exists in all `LabelLanguages` declared in `context_setup.md`.

4. **Report, do not auto-fix.** Produce a structured list:

   ```
   FILE: <relative path>
     - PASS: <check name>
     - FAIL: <check name> — <one-line reason> — <suggested fix>
     - SKIP: <check name> — <why not applicable>
   ```

5. **Explicitly list what CANNOT be verified without a build or human step:**
   - X++ compilation
   - Runtime behavior
   - Performance under realistic data volumes
   - Integration round-trip with live counterparty
   - Security role effective access

6. **Update SNAPSHOT §8 Validation status** with what was actually run. Do not mark anything "passing" that this skill did not actually verify.

## Anti-patterns

- **Never** fabricate a unit test framework, a mock, or a test file under `code/**`.
- **Never** write "all tests pass" in chat or in SNAPSHOT.
- **Never** run `/testing` across tasks — scope is the active task only.
