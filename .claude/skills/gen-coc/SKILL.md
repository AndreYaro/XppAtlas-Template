---
name: gen-coc
description: Generate a Chain of Command (CoC) extension class scaffold for a given target class and method. Usage: /gen-coc [TargetClass] [MethodName]
---

Generate a Chain of Command extension class for the specified target.

## Arguments
Parse `$ARGUMENTS` as: `{TargetClass} {MethodName}`
- If no arguments provided, ask the user for `TargetClass` and `MethodName`.

## Steps

1. Read `context_setup.md` to get `ProjectPrefix`, `UserVISA`, `code_path`.
2. Find the target class in `Source/` using Glob to read its method signature.
3. Generate the CoC extension class with the correct signature.
4. Output the file to `code/AxClass/{Prefix}{TargetClass}_Cls_Extension.xml`.

## Generated Code Pattern

```xpp
[ExtensionOf(classStr({TargetClass}))]
final class {Prefix}{TargetClass}_Cls_Extension
{
    /// <summary>
    /// Extension of {TargetClass}.{MethodName}
    /// TODO: [{UserVISA}] Describe what this extension does
    /// </summary>
    public {ReturnType} {MethodName}({Parameters})
    {
        {ReturnCapture}next {MethodName}({ParameterNames});

        // TODO: [{UserVISA}] Add extension logic here

        {ReturnStatement}
    }
}
```

## Rules
- The `next` call must be the **first statement** in the method (before extension logic) unless pre-processing is explicitly required — in that case, add a comment explaining why.
- If the original method returns `void`, omit the return capture and return statement.
- If the method has no parameters, generate with empty parentheses.
- The extension class name must follow: `{Prefix}{TargetClass}_Cls_Extension`.

## Output
1. Show the generated X++ code in a code block.
2. Show the target file path: `code/AxClass/{Prefix}{TargetClass}_Cls_Extension.xml`
3. Ask the user if they want the file written to disk.
