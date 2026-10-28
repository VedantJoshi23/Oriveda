---
id: DOM-ARTICLE
title: "RealWorld — Domain: Article"
version: 0.1.0
status: Frozen
owner: Example
milestone: M5
category: Domains
related_decisions:
  - ADR-0006
risk: High
---

# Domain: Article

*Abbreviated for the `oriveda check boundaries` worked example: only
§2 and §7 are shown. A real Domain Specification has all nine sections
(`templates/domain-template.md`).*

## 2. Ownership

### Owns

Articles, comments, favorites, feeds.

## 7. Dependencies

### Allowed

- `DOM-USER`
- `DOM-SHARED`

### Forbidden

- `DOM-PROFILE`

Feeds need "who follows whom", but that data belongs to DOM-PROFILE and must be obtained through its API surface, never by reading its table.

```yaml oriveda-boundary
domain: DOM-ARTICLE
paths:
  - "src/article/**"
allowed_dependencies:
  - "DOM-USER"
  - "DOM-SHARED"
forbidden_dependencies:
  - "DOM-PROFILE"
```
