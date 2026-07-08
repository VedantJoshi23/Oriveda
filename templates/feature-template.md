# Metadata

```yaml
---
id:
title: <Project Name> — Feature: <Name>
version: 0.1.0
status: Proposal
owner:
reviewers: []
created:
updated:
milestone: M6
category: Features
priority:
depends_on: []
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions: []
tags:
  - feature
risk:
complexity:
---
```

## Feature: < Name >

### 1. Overview

One paragraph: what this does, for whom, and why it matters.

### 2. Owning Domain

**Owning domain:** `<DOM-XXX>` — exactly one.

**Other domains involved** (as dependencies only — each cross-domain call
in the flow must match the Allowed list of whichever domain *initiates
that specific call*, not necessarily the owning domain above; no new
cross-domain calls invented here):

### 3. Acceptance Criteria

Concrete, testable statements.

- [ ]
- [ ]

### 4. API Surface

New or changed endpoints. Must be consistent with the owning domain's
declared API surface.

### 5. Events

#### Publishes

#### Consumes

*(must be a subset of what the owning domain's Domain Specification
already declares)*

### 6. Data Changes

New tables/fields. Must stay within the owning domain's Data Ownership.

### 7. Edge Cases & Validations

Feature-specific scenarios.

### 8. Non-Functional Considerations

Checked against every Applicable Standard relevant to this feature's
shape. State "not applicable" explicitly where genuinely true — don't
omit silently.

| Standard | Relevant? | Notes |
| --- | --- | --- |

### 9. Definition of Done

Testing, docs, and deployment checklist for this specific feature.

- [ ]
- [ ]
