# Metadata

```yaml
---
id: DOM-PROFILE
title: "RealWorld — Domain: Profile"
version: 0.1.0
status: Draft
owner: Example
milestone: M5
category: Domains
related_decisions:
  - ADR-0006
risk: High
---
```

## Domain: Profile

*Abbreviated for the `oriveda check boundaries` worked example: only
§2 and §7 are shown. A real Domain Specification has all nine sections
(`templates/domain-template.md`).*

## 2. Ownership

### Owns

Public profiles and follow relationships.

## 7. Dependencies

### Allowed

- `DOM-USER`
- `DOM-SHARED`

### Forbidden

- Everything not listed under Allowed.

```yaml oriveda-boundary
domain: DOM-PROFILE
paths:
  - "src/profile/**"
allowed_dependencies:
  - "DOM-USER"
  - "DOM-SHARED"
forbidden_dependencies: []
```
