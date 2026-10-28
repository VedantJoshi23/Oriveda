# Metadata

```yaml
---
id:
title: "<Project Name> — Divergence Log"
version: 0.1.0
status: Draft
owner:
reviewers: []
created:
updated:
milestone: M8
category: Decision
priority: High
depends_on: []
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0004
tags:
  - divergence
risk: Medium
complexity: Low
---
```

## Divergence Log

A divergence is a recorded disagreement between code and a
specification that is **not yet Frozen** (`ADR-0004` rule 1). A
disagreement with a Frozen specification is not a divergence: the code
is wrong, and it is fixed or the spec is formally revised.

Rules (`ADR-0004` rule 4):

- A change that introduces a divergence logs it **in the same change**.
  An unlogged divergence counts as a defect.
- A specification cannot be Frozen while it has `open` entries here.
- Entries are never deleted. A resolved entry keeps its history.

This is a living log, never Frozen. Its own `status` stays `Draft`.

## Entries

| ID | Spec § | Spec says | Code does | Found in | Status | Resolved |
| --- | --- | --- | --- | --- | --- | --- |
| DIV-001 | `<DOM-XXX>` §3 | | | `<commit/PR>` | open | |

**Status values:** `open` · `spec-updated` · `code-fixed` · `both`.

### Notes

Use this section only when a one-line row can't explain a resolution
(for example a divergence that led to an ADR). Head each note with its
`DIV-NNN` ID.
