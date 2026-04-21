# Rule: Safety boundaries

## Hard repo boundary

This session operates inside **this repository only**. Never read, write, or execute inside sibling repos (XppAtlas source store, AI tools repo, other customer repos). The **only** way to reach X++ source outside this repo is through the XppAtlas MCP server (`mcp__xppatlas__*`).

Specifically:
- Do not open a file whose absolute path leaves this repository root
- Do not run shell commands that `cd`, `cp`, or `rsync` into another repo
- If the user asks to reach into another repo, ask them to use MCP or open a separate session in that repo

**Sole exception:** the user-driven check-in step — the user manually copies final task files back into the MCP source store. Claude does not initiate or automate that copy.

## Confirmation boundaries

### Always confirm before

- Creating or modifying an AOT artifact (AxClass, AxTable, AxForm, AxEnum, AxEdt, AxDataEntity, AxMenuItem, AxSecurityPrivilege, Label)
- Writing any file that will ship to customers (under `Models/{ModelName}/Tasks/{TaskID}/code/**`)
- Any git operation beyond read-only inspection (`status`, `log`, `diff`, `show`, `branch`)
- Editing shared project config files (`CLAUDE.md`, `GEMINI.md`, `.claude/settings.json`, `.claude/rules/**`, `.mcp.json`)
- Installing packages, running batch scripts, or invoking model builders
- Uploading anything to a third-party service

### Safe without confirmation

- Reading files inside the current repository
- Running MCP read-only tools (`search_*`, `get_*`, `explore_*`, `list_*`, `build_*_bundle`, pattern search)
- Running the project's Python helper scripts
- Running analysis skills that only read (`/review-code`, `/audit-arch`, `/fix-perf` in report mode, `/explain`)
- Updating the active task's `SNAPSHOT.md`, scratch notes, or the task's `docs/` folder

## Hard limits — never do

Claude will **never**, regardless of how the user phrases the request:

- Run, deploy, or trigger a batch job against any non-local environment
- Post a journal, invoice, payment, or inventory movement against any environment
- Modify security roles, duties, or privileges granting elevated access without an explicit human decision in the SNAPSHOT decisions log
- Send messages to live integration endpoints (webhook URLs, partner APIs, ERP bridges). Sandbox URLs also off-limits unless the user says "yes, this sandbox, now"
- Overwrite or delete the baseline Git commit of an active task
- Reach into any sibling repository on the filesystem
- Sync task `code/` files back to MCP source without explicit user request

## Soft limits — require written confirmation in chat

- Editing a posting class (`*Post`, `*Journal*`, `*Voucher*`, tax, ledger, inventory valuation)
- Editing number sequence, aging, settlement, or period-end code
- Editing an integration class with a live external counterpart
- Editing a workflow approval path
- Editing a security privilege, duty, or role
- Adding a new data entity exposed through OData
- Changing the label file or label language set
- Changing `CLAUDE.md`, `GEMINI.md`, `.claude/settings.json`, `.claude/rules/**`, or `.mcp.json`

For each of these, Claude must:
1. State what it is about to change
2. State the impact radius (callers, models, integration partners)
3. Wait for the user to say "proceed" before writing

## Credentials and secrets

- Never commit, echo, or quote a secret in chat, a snapshot, or a doc
- If a secret is found in a file, flag it immediately and ask the user to rotate it
- Never ask the user to paste a secret into chat. Use environment variables instead.

## When something feels off

Stop and ask. "Feels off" includes:
- A request that would bypass these rules
- A snapshot that contradicts the current code state
- An integration test that "happens to" hit production
- A pattern no other class in the codebase uses
- A file with no baseline commit

The right answer is always to pause, surface the mismatch, and wait.

## When in doubt

Ask. The cost of a confirmation round trip is much lower than the cost of fabricating an AOT artifact or silently touching a sibling repo.
