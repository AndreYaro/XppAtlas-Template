---
name: gen-entity
description: Generate a D365 F&O Data Entity scaffold with staging table and field mappings. Usage: /gen-entity [Name]
---

Generate a Data Entity and its associated staging table for the given name.

## Arguments
Parse `$ARGUMENTS` as: `{Name}` (e.g. `CustomerInvoice`)
- If no argument provided, ask the user for the entity name and target table.

## Steps

1. Read `context_setup.md` to get `ProjectPrefix`, `UserVISA`, `code_path`.
2. Ask the user:
   - What is the **root data source table**? (e.g. `CustInvoiceJour`)
   - Is this entity for **import**, **export**, or **both**?
   - Is it **public** (external-facing OData) or **internal** (DMF only)?
3. Generate the staging table and entity class.
4. Output files to `code/AxTable/` and `code/AxClass/`.

## Generated: Staging Table — `{Prefix}{Name}Staging`

Key fields to include:
- `DefinitionGroup` (string 60) — DMF group identifier
- `ExecutionId` (string 90) — DMF execution ID
- `IsSelected` (NoYes enum)
- `TransferStatus` (DMFTransferStatus enum)
- All payload fields mapped from the source table

## Generated: Data Entity Class — `{Prefix}{Name}Entity`

```xpp
[
    DataEntityAttribute("{Prefix}{Name}"),
    SysOperationLabelAttribute("TODO: [{UserVISA}] Entity label"),
    DataManagementStagingTable(tableStr({Prefix}{Name}Staging))
]
public class {Prefix}{Name}Entity extends common
{
    // Root data source: {RootTable}
    // TODO: [{UserVISA}] Verify field mappings in AOT entity designer

    public static {Prefix}{Name}Entity find(
        str _keyField,
        boolean _forUpdate = false)
    {
        {Prefix}{Name}Entity entity;

        select firstonly entity
            where entity.KeyField == _keyField;

        if (_forUpdate && entity)
        {
            entity.selectForUpdate(_forUpdate);
        }

        return entity;
    }
}
```

## Entity Properties to Set in AOT

| Property | Value |
|----------|-------|
| `IsPublic` | `true` (if external) / `false` (if internal) |
| `DataManagementEnabled` | `true` |
| `DataManagementStagingTable` | `{Prefix}{Name}Staging` |
| `PublicEntityName` | `{Name}` |
| `PublicCollectionName` | `{Name}s` |
| `EntityCategory` | `Transaction` / `Master` / `Reference` |

## Output
1. Show staging table fields list.
2. Show entity class scaffold.
3. Show file paths for both outputs.
4. Remind the user to map fields in the AOT Data Entity designer and verify `initializeEntityDataSource`.
