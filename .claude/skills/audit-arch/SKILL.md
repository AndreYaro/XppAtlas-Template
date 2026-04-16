---
name: audit-arch
description: Audit X++ files in the current task for separation-of-concerns violations — business logic in forms, missing refactoring opportunities, and method length issues.
---

Perform a separation-of-concerns architecture audit on the current task's code.

## Steps

1. Read `context_setup.md` to get `ProjectPrefix`.
2. Locate all `.xml` files under `code/` using Glob.
3. For each file, apply the audit rules below.

## Audit Rules

### Rule A — No Business Logic in Forms
Scan all `AxForm` files. Flag any form method or data source event that contains:
- Database queries (`select`, `while select`)
- Calculations or transformations
- Calls to posting routines
- Direct table updates

**Fix:** Move the logic to a table method or a dedicated service class.

### Rule B — Rule of Three (Refactoring)
Scan all class files. If the same block of logic (> 5 lines) appears in 3 or more places:

**Fix:** Extract into a `static` helper method or a shared service class.

### Rule C — Method Length
Flag any method exceeding 50 lines.

**Fix:** Split into private methods, each with a single responsibility.

### Rule D — Direct SQL in UI Layer
Flag any `select` statement inside a form method, display method on a form, or `clicked()` handler.

**Fix:** Move to a data provider class or table method; call from form.

### Rule E — God Classes
Flag any class with more than 10 public methods that mixes multiple concerns (e.g., validation + posting + UI interaction).

**Fix:** Split into focused classes (validator, poster, controller).

## Output Format

```
[RULE {Letter}] {FileName} | Method: {MethodName} | ~Line {N}
Violation : <description of what was found>
Fix       : <concrete refactoring action>
```

End with an overall assessment: **Clean** or **Needs Refactoring** with a count of violations per rule.
