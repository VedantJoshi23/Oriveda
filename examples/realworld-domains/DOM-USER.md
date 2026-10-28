# Metadata

```yaml
---
id: DOM-USER
title: "RealWorld — Domain: User"
version: 0.1.0
status: Frozen
owner: Example
milestone: M5
category: Domains
related_decisions:
  - ADR-0005
risk: High
---
```

## Domain: User

*Abbreviated for the `oriveda check boundaries` worked example: only
§2 and §7 are shown. A real Domain Specification has all nine sections
(`templates/domain-template.md`).*

## 2. Ownership

### Owns

Identity: accounts, credentials, JWT issuance, the authenticated-user decorator.

## 7. Dependencies

### Allowed

- `DOM-SHARED`

### Forbidden

- `DOM-ARTICLE`

Core domain: nothing depends *upward*. Articles reference users; users never reference articles.

```yaml oriveda-boundary
domain: DOM-USER
paths:
  - "src/user/**"
allowed_dependencies:
  - "DOM-SHARED"
forbidden_dependencies:
  - "DOM-ARTICLE"
```
