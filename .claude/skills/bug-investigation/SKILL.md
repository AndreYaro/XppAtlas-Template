---
name: bug-investigation
description: Structured bug investigation — trace the execution path, identify root cause, distinguish symptom from cause, document findings. Usage: /bug-investigation [description or error message]
---

# /bug-investigation

Structured investigation of a reported bug. Produces evidence and root cause analysis before any fix is attempted.

## Arguments

Parse `$ARGUMENTS` as the bug description, error message, or symptom (e.g. `"Division by zero in settlement posting"`, `"DMS invoice import fails with duplicate key"`, `"Batch job hangs after 100 records"`).

## Steps

1. **Confirm the active task** is a bugfix task. Read its SNAPSHOT and rules.

2. **Understand the symptom.**
   - What does the user see? (error message, wrong data, hang, crash)
   - When does it happen? (specific form, batch, process, data condition)
   - How critical is it? (blocking production, intermittent, cosmetic)

3. **Trace the execution path using MCP:**
   - `search_artifacts` — find the artifact mentioned in the error or symptom
   - `explore_artifact` — inspect its methods, fields, relations
   - `search_chunks` — find the specific code path where the error occurs
   - `search_chunks` — look for existing CoC or handlers that might interfere
   - `estimate_change_radius` — understand what else is affected

4. **Identify the root cause.** Ask:
   - Is this a symptom or the actual cause?
   - Could an extension (CoC/handler) be altering the expected flow?
   - Is the data in an unexpected state?
   - Is there a timing/concurrency issue?
   - Is there a missing null check, wrong field selection, or incorrect join?

5. **Document findings** in the task SNAPSHOT §5:
   ```
   - {Date} — Symptom: {what the user sees}
   - {Date} — Execution path: {entry point → ... → failure point}
   - {Date} — Root cause: {what actually causes the problem}
   - {Date} — Contributing factors: {data conditions, extensions, config}
   ```

6. **Assess regression risk.** Who else calls the affected code? What else could break if we change it? Write this into SNAPSHOT §5.

7. **Recommend a fix approach.**
   - The smallest correct change
   - Which artifact(s) need to change
   - Which extension mechanism to use
   - What edge cases to consider
   - How to verify the fix

8. **Do NOT implement the fix yet.** Present the findings and recommendation. Wait for the user to approve the approach before making code changes.

## Anti-patterns

- Do not jump to a fix before understanding the root cause.
- Do not patch symptoms — fixing the wrong thing creates harder bugs later.
- Do not ignore existing extensions — they often interact with the bug.
- Do not make code changes during investigation. Investigation produces documents; implementation is a separate step.
