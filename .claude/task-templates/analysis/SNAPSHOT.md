---
task_id: "{TaskID}"
task_name: "{TaskName}"
task_type: analysis
model: "{ModelName}"
owner: "{UserVISA}"
status: not-started
last_updated: "{Date}"
---

# Task SNAPSHOT — {TaskID} {TaskName}

Per-task cross-session state. Read this **first** at the start of any session on this task, and update it at every checkpoint. This is the single source of truth for "where we are" — not scratch notes in chat.

**Task type: analysis** — explore, gather evidence, compare options, produce structured findings. Do not create code artifacts.

## 1. Purpose

Why this analysis exists. What question are we trying to answer? What decision does it inform?

## 2. Scope

**In scope** — what areas, modules, artifacts, and questions this analysis covers.

**Out of scope** — what this analysis does not attempt to answer.

**Model** — `{ModelName}`. Analysis is scoped to this model unless secondary models are explicitly listed.

## 3. Constraints

- Deadlines for delivering the analysis
- Stakeholder availability for decisions
- Known gaps in documentation or access
- Related ongoing work that might affect conclusions

## 4. Artifacts inspected

| Artifact | Type | Model | Tool used | Key finding |
|----------|------|-------|-----------|-------------|
| | | | | |

## 5. Decisions and findings log

Running list of findings and decisions. Each entry: date, finding/decision, evidence source.

## 6. Options considered

For each decision point, document the options compared and why the recommended one was chosen.

## 7. Documents produced

| Document | Path | Status |
|----------|------|--------|
| | `docs/` | draft / final |

## 8. Validation status

- Evidence reviewed against multiple sources — yes / no / partial
- Stakeholder review — pending / completed / not needed

## 9. Next steps

1. …
2. …
3. …

## 10. Open questions for the user

Anything blocked on a user/stakeholder decision. If non-empty, the session should open by surfacing these.
