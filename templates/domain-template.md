---
id:
title: <Project Name> — Domain: <Name>
version: 0.1.0
status: Proposal
owner:
reviewers: []
created:
updated:
milestone: M5
category: Domains
priority:
depends_on: []
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions: []
tags:
  - domain
risk:
complexity:
---

# Domain: <Name>

**Tier:** Full | Thin — *(if Thin, state the justification against the
architecture's context map right here)*

## 1. Overview

One paragraph: what this domain is responsible for in the business.

## 2. Ownership

### Owns

### Explicitly Does NOT Own

*(restated from the architecture's Service Boundaries table — not
re-derived here)*

## 3. Invariants

Business rules that must always hold. Each entry cites its source.

### Invariant 1

> Statement of the rule.

**Source:** `<OV-001 claim id>` | Constitution `<Law N>` | New decision
(state rationale if new).

*(repeat per invariant; Thin-tier domains may state "N/A — derived from
`<owning domain>`")*

## 4. API Surface

Endpoints this domain exposes (from the architecture/technology
decisions, not reinvented here).

## 5. Events

### Publishes

### Consumes

*(must match the architecture's event catalog exactly)*

## 6. Data Ownership

Tables/aggregates this domain owns.

## 7. Dependencies

### Allowed

*(must match the architecture's context map exactly — if it doesn't,
the architecture needs revising first, not this document)*

### Forbidden

*(explicit — not just "everything else")*

## 8. Edge Cases & Validations

Specific scenarios a future implementer must handle correctly.

*(Thin-tier domains may state "N/A — derived from `<owning domain>`")*

## 9. Open Questions

Anything genuinely unresolved, tagged with which investigation or
milestone it belongs to if it isn't this domain's own to resolve.
