# Metadata

```yaml
---
id:
title: <Project Name> — Spec Card: <Name>
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
related_decisions:
  - ADR-0004
tags:
  - feature
  - spec-card
risk: Low
complexity:
---
```

## Spec Card: < Name >

The Low-tier form of a Feature Specification (`ADR-0004` rule 2,
`OV-007`). Use it only when **all three** of these hold, and say why in
one line:

- [ ] No new invariant: the feature only uses rules its domain already
      declares.
- [ ] No cross-domain flow: no call or event crosses a domain boundary.
- [ ] No High-tier dependency: nothing on its path is High tier.

**Tier reason:** <one line>

If any box stops being true during the build, the card moves up to a
full Feature Specification (`templates/feature-template.md`). It is not
patched to fit.

### 1. Purpose

One or two sentences: what this does and for whom.

### 2. Owning Domain

`<DOM-XXX>`, exactly one.

### 3. Acceptance Criteria

Concrete, testable statements.

- [ ]
- [ ]

### 4. Open Questions

Assumption-tier claims (<60%) this card relies on, each with what would
settle it. Do not build on any of these silently.

-
