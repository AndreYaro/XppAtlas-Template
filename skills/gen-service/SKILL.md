---
name: gen-service
description: Generate a D365 F&O Custom Service class scaffold (JSON/REST endpoint). Usage: /gen-service [Name]
---

Generate a Custom Service class for the given name.

## Arguments
Parse `$ARGUMENTS` as: `{Name}` (e.g. `InvoiceImport`)
- If no argument provided, ask the user for the service name and its operations.

## Steps

1. Read `context_setup.md` to get `ProjectPrefix`, `UserVISA`, `code_path`.
2. Ask the user:
   - What **operations** does the service expose? (e.g. `importInvoices`, `getStatus`)
   - For each operation: input type, return type, HTTP verb (GET/POST).
3. Generate the service class and data contract(s).
4. Output to `code/AxClass/`.

## Generated: Service Class — `{Prefix}{Name}Service`

```xpp
/// <summary>
/// Custom service for {Name} operations.
/// TODO: [{UserVISA}] Register in AOT under Services node
/// </summary>
[SysEntryPointAttribute(true)]
class {Prefix}{Name}Service
{
    /// <summary>
    /// TODO: [{UserVISA}] Describe operation
    /// </summary>
    /// <param name = "_request">Request contract</param>
    /// <returns>Response contract</returns>
    public {Prefix}{Name}Response {operationName}({Prefix}{Name}Request _request)
    {
        {Prefix}{Name}Response response = new {Prefix}{Name}Response();

        try
        {
            // TODO: [{UserVISA}] Implement operation logic
            response.parmSuccess(true);
        }
        catch (Exception::Error)
        {
            response.parmSuccess(false);
            response.parmMessage(strFmt("TODO: [{UserVISA}] Error label — %1", infolog.text()));
        }

        return response;
    }
}
```

## Generated: Request Contract — `{Prefix}{Name}Request`

```xpp
[DataContractAttribute]
class {Prefix}{Name}Request
{
    private str externalId;

    [DataMemberAttribute('ExternalId')]
    public str parmExternalId(str _externalId = externalId)
    {
        externalId = _externalId;
        return externalId;
    }
}
```

## Generated: Response Contract — `{Prefix}{Name}Response`

```xpp
[DataContractAttribute]
class {Prefix}{Name}Response
{
    private boolean success;
    private str     message;

    [DataMemberAttribute('Success')]
    public boolean parmSuccess(boolean _success = success)
    {
        success = _success;
        return success;
    }

    [DataMemberAttribute('Message')]
    public str parmMessage(str _message = message)
    {
        message = _message;
        return message;
    }
}
```

## AOT Registration Checklist
- [ ] Create a **Service** node in AOT and point to `{Prefix}{Name}Service`.
- [ ] Create a **Service Group** and add the service to it.
- [ ] Add `[SysEntryPointAttribute(true)]` on the class.
- [ ] Assign the correct **Service Group** to an Application Integration Framework (AIF) port or register as a custom OData action.
- [ ] Set up security: create a **Privilege** and assign to the appropriate **Duty**.

## Output
1. Show all three classes (Service, Request, Response) in code blocks.
2. Show file paths.
3. Show AOT registration checklist.
