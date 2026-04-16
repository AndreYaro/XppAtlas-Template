---
name: fix-perf
description: Analyze X++ code in the current task for performance issues and convert row-by-row loops to set-based operations.
---

Analyze the current task's X++ code for performance issues and produce fixes.

## Steps

1. Read `context_setup.md` to get `ProjectPrefix`, `UserVISA`.
2. Locate all `.xml` files under `code/` using Glob.
3. Read each file and apply the performance audit rules below.
4. For each issue found, produce the fixed version.

## Performance Audit Rules

### P1 — Row-by-Row Insert (High Impact)
**Pattern:** `while select` loop containing `insert()` calls on a buffer.
**Fix:** Replace with `insert_recordset`.
```xpp
// Before
while select sourceTable where sourceTable.Status == Status::Pending
{
    destTable.Field1 = sourceTable.Field1;
    destTable.insert();
}

// After
insert_recordset destTable (Field1)
    select Field1 from sourceTable
        where sourceTable.Status == Status::Pending;
```
> Note: `insert_recordset` skips `insert()` override and `initValue()`. Add a comment if these are intentionally bypassed.

### P2 — Row-by-Row Update (High Impact)
**Pattern:** `while select forupdate` loop with `update()` calls.
**Fix:** Replace with `update_recordset`.
```xpp
// Before
while select forupdate myTable where myTable.Status == Status::Pending
{
    myTable.Status = Status::Processed;
    myTable.update();
}

// After
update_recordset myTable
    setting Status = Status::Processed
    where myTable.Status == Status::Pending;
```

### P3 — Row-by-Row Delete (High Impact)
**Pattern:** `while select` loop with `delete()` calls.
**Fix:** Replace with `delete_from`.
```xpp
// Before
while select myTable where myTable.IsDeleted
{
    myTable.delete();
}

// After
delete_from myTable where myTable.IsDeleted;
```

### P4 — `select *` (Medium Impact)
**Pattern:** `select` without a field list.
**Fix:** Specify only required fields.
```xpp
// Before
select myTable where myTable.RecId == _recId;

// After
select RecId, Name, Status from myTable where myTable.RecId == _recId;
```

### P5 — Missing `firstonly` (Medium Impact)
**Pattern:** `select` expected to return one record without `firstonly`.
**Fix:** Add `firstonly`.

### P6 — Repeated Select in Loop (High Impact)
**Pattern:** `select` statement inside a `while` or `for` loop body.
**Fix:** Pre-fetch results into a `List` or use a `join`.

### P7 — `orUpdate` Without Update (Low Impact)
**Pattern:** `select forupdate` where no `update()` or `doUpdate()` follows.
**Fix:** Remove `forupdate` to prevent unnecessary row locking.

## Output Format

For each issue:
```
[P{N}] {FileName} | Method: {MethodName} | ~Line {N}
Issue  : <description>
Impact : High / Medium / Low
Before : <original code snippet>
After  : <fixed code snippet>
Note   : <any side effects or caveats to be aware of>
```

End with a summary of estimated performance impact.
