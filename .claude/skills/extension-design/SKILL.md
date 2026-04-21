---
name: extension-design
description: Design the extension strategy for modifying a standard D365 artifact. Finds extension points, evaluates options, produces a decision record. Usage: /extension-design [TargetArtifact]
---

# /extension-design

Analyze a standard D365 artifact and design the best extension strategy before any code is written.

## Arguments

Parse `$ARGUMENTS` as the target artifact name (e.g. `CustInvoiceJour`, `SalesFormLetter`, `VendInvoiceInfoTable`).

## Steps

1. **Confirm the active task** and read `context_setup.md` for `ProjectPrefix`.

2. **Explore the target artifact via MCP:**
   - `explore_artifact` — list all methods, fields, relations, delegates, events
   - `search_chunks` — find existing CoC and event handlers targeting this artifact (in the active model and across models)
   - `propose_extension_strategy` or `rank_extension_points` — get MCP-recommended extension approach
   - `search_artifacts(model_name="ApplicationSuite")` or `explore_artifact` — understand the standard behavior being extended (scan top-5 for exact-name match per `tool-usage.md`; inspect `meta.standard_server.status` — on non-`ok`, fall through the cascade in `fallback-and-evidence.md`)

3. **Evaluate extension options** against the priority order from `project-main.md`:

   | Priority | Mechanism | When to use |
   |----------|-----------|-------------|
   | 1 | Event handler | Delegate or post-event exists for the needed hook point |
   | 2 | Chain of Command | Method exists and needs pre/post logic or modified behavior |
   | 3 | Table/Form/Entity extension | Need to add fields, field groups, controls, mappings |
   | 4 | New artifact with `{ProjectPrefix}` | No extension point fits the requirement |
   | 5 | Overlayering | User explicitly authorizes (never default to this) |

4. **Check for conflicts.** Are there existing CoC or handlers on the same method? Extending the same target twice creates hard-to-maintain stacking. If a handler already exists, prefer extending it over creating a new one.

5. **Produce a decision record** in `docs/extension_design_{ArtifactName}.md`:

   ```
   ## Extension Design — {ArtifactName}
   
   ### Target
   - Artifact: {name}
   - Type: {AxClass/AxTable/AxForm/...}
   - Model: {source model}
   
   ### Available extension points
   (list delegates, hookable methods, events, with brief description)
   
   ### Existing extensions in this project
   (list any CoC or handlers already targeting this artifact)
   
   ### Recommended approach
   - Mechanism: {Event handler / CoC / Extension / New artifact}
   - Target method/event: {specific method or delegate}
   - Rationale: {why this is the lowest-risk, most maintainable option}
   
   ### Rejected alternatives
   (list other options considered and why they were rejected)
   
   ### Impact assessment
   - Callers affected: (list)
   - Cross-model risk: (yes/no, detail)
   - Upgrade risk: (low/medium/high)
   ```

6. **Update SNAPSHOT §6** with the chosen extension strategy.

## Anti-patterns

- Do not skip the "existing extensions" check — creating a second CoC on the same method when one exists is a common mistake.
- Do not default to CoC when an event handler would suffice — event handlers are lower risk.
- Do not recommend overlayering without the user's explicit authorization.
