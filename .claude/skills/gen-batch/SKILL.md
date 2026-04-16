---
name: gen-batch
description: Generate a complete SysOperationFramework batch job scaffold (Controller + Service + Contract). Usage: /gen-batch [Name]
---

Generate a full SysOperationFramework batch job for the given name.

## Arguments
Parse `$ARGUMENTS` as: `{Name}` (logical name, e.g. `InvoicePosting`)
- If no argument provided, ask the user for the batch job name.

## Steps

1. Read `context_setup.md` to get `ProjectPrefix`, `UserVISA`, `code_path`.
2. Ask the user for the contract parameters needed (field name, type, label) — or generate with one `TransDate` parameter as placeholder.
3. Generate three class files.
4. Output each to `code/AxClass/`.

## Generated Classes

### 1. Contract — `{Prefix}{Name}Contract`
```xpp
[DataContractAttribute]
class {Prefix}{Name}Contract
{
    private TransDate fromDate;

    [DataMemberAttribute('FromDate'),
     SysOperationLabelAttribute("TODO: [{UserVISA}] From date label"),
     SysOperationHelpTextAttribute("TODO: [{UserVISA}] Help text")]
    public TransDate parmFromDate(TransDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }
}
```

### 2. Service — `{Prefix}{Name}Service`
```xpp
class {Prefix}{Name}Service extends SysOperationServiceBase
{
    public void process({Prefix}{Name}Contract _contract)
    {
        TransDate fromDate = _contract.parmFromDate();

        // TODO: [{UserVISA}] Implement business logic
        ttsbegin;

        ttscommit;
    }
}
```

### 3. Controller — `{Prefix}{Name}Controller`
```xpp
class {Prefix}{Name}Controller extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        {Prefix}{Name}Controller controller;

        controller = new {Prefix}{Name}Controller(
            classStr({Prefix}{Name}Service),
            methodStr({Prefix}{Name}Service, process),
            SysOperationExecutionMode::Synchronous);

        controller.parmShowDialog(true);
        controller.startOperation();
    }

    public ClassDescription description()
    {
        return "TODO: [{UserVISA}] Replace with Label ID";
    }

    public boolean canGoBatchJournal()
    {
        return true;
    }
}
```

## Output
1. Show all three classes in code blocks with their file paths.
2. Remind the user to:
   - Replace all `TODO` placeholders with real Label IDs.
   - Add the Controller's `main()` as an Action Menu Item in AOT.
   - Add proper security privilege for the menu item.
