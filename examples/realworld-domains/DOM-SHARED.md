---
id: DOM-SHARED
title: "RealWorld — Domain: Shared"
version: 0.1.0
status: Frozen
owner: Example
milestone: M5
category: Domains
related_decisions:
  - ADR-0006
risk: High
---

# Domain: Shared

*Abbreviated for the `oriveda check boundaries` worked example: only
§2 and §7 are shown. A real Domain Specification has all nine sections
(`templates/domain-template.md`).*

## 2. Ownership

### Owns

Shared kernel: cross-cutting pipes and utilities with no business rules (Thin tier).

## 7. Dependencies

### Allowed

- None.

### Forbidden

- Everything not listed under Allowed.

```yaml oriveda-boundary
domain: DOM-SHARED
paths:
  - "src/shared/**"
allowed_dependencies: []
forbidden_dependencies: []
```
