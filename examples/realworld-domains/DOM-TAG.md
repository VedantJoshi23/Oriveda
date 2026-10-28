---
id: DOM-TAG
title: "RealWorld — Domain: Tag"
version: 0.1.0
status: Draft
owner: Example
milestone: M5
category: Domains
related_decisions:
  - ADR-0006
risk: High
---

# Domain: Tag

*Abbreviated for the `oriveda check boundaries` worked example: only
§2 and §7 are shown. A real Domain Specification has all nine sections
(`templates/domain-template.md`).*

## 2. Ownership

### Owns

Tag catalogue.

## 7. Dependencies

### Allowed

- `DOM-SHARED`

### Forbidden

- Everything not listed under Allowed.

```yaml oriveda-boundary
domain: DOM-TAG
paths:
  - "src/tag/**"
allowed_dependencies:
  - "DOM-SHARED"
forbidden_dependencies: []
```
