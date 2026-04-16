---
name: design-integration
description: Produce a full integration architecture proposal for a D365 F&O integration. Usage: /design-integration [Name]
---

Design a complete integration architecture for the given integration name.

## Arguments
Parse `$ARGUMENTS` as: `{Name}` (e.g. `BillingToDMS`, `VendorPortalImport`)
- If no argument provided, ask the user for the integration name.

## Steps

1. Ask the user the following before designing:
   - **Direction:** Which system initiates? (external → D365, D365 → external, bidirectional)
   - **Pattern:** Synchronous (real-time) or asynchronous (batch/queue)?
   - **Volume:** Estimated records per run and frequency.
   - **Existing systems:** What is the external system? Any middleware (Azure Service Bus, Logic Apps)?
   - **Error tolerance:** What happens on failure — retry, manual correction, skip?

2. Based on answers, select the appropriate D365 pattern (see Technology Selection below).

3. Produce all five sections of the architecture document.

## Technology Selection

| Requirement | Recommended D365 Pattern |
|-------------|--------------------------|
| External pushes data to D365 | Custom Service + staging table |
| D365 exposes data for read | OData (Data Entity) |
| Bulk load / migration | DMF Package API |
| Event notification out of D365 | Business Events → Service Bus |
| Heavy transformation | Azure Function between systems |
| Scheduled export | Recurring Integration export job |
| Low-latency synchronous lookup | Custom Service (GET endpoint) |

## Document Structure to Produce

### 1. Overview Table
| Aspect | Specification |
|--------|---------------|
| Direction | ... |
| Pattern | Synchronous / Asynchronous |
| Protocol | REST / SOAP / DMF |
| Format | JSON / XML |
| Authentication | OAuth 2.0 Client Credentials |
| Volume | N records / frequency |

### 2. Flow Diagram (Mermaid)
Produce a `graph LR` or `sequenceDiagram` showing all systems, message directions, and async/sync boundaries.

### 3. Payload Contract
JSON schema with all fields, types, nullable flag, max length, and one example value per field.

### 4. Error Handling Matrix
| Error Condition | HTTP Status / Infolog | Retry Strategy |
|-----------------|----------------------|----------------|
| Validation failure | 400 | No retry — fix payload |
| Auth failure | 401 | Refresh token; retry once |
| Duplicate (idempotent) | 200 + warning | Skip silently |
| Server error | 500 | Exponential backoff × 3 |

### 5. Staging Table Design
List fields, status enum values (Pending / Processing / Posted / Error / Skipped), key indexes, and retention policy.

### 6. Security Model
- Entra ID app registration name and required API permissions
- D365 duty/privilege that grants access to the service or entity
- Data sensitivity classification

### 7. Open Items
List any unresolved decisions requiring stakeholder input before implementation can begin.

## Output
Produce the full architecture document in Markdown with all seven sections.
After the document, suggest which `/gen-*` skill to run next (e.g., `/gen-service`, `/gen-entity`).
