---
id: PRM-CONSTITUTION
title: "Oriveda — Prompt: Constitution"
version: 0.1.0
status: Draft
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-09-26
updated: 2026-09-26
milestone: M7
category: Prompts
priority: High
depends_on:
  - OV-002
  - OV-008
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0003
tags:
  - prompt
risk: Low
complexity: Low
---

# PRM-CONSTITUTION

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a Constitution (M2) session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Constitution

### Context

- `OV-002` Constitution Protocol
- The target project's Frozen `DISC-` investigations, above all its
  recommendations roll-up

### Task

Ask the owner the three owner-choice questions `OV-002` defines, then
derive the project's Engineering Constitution and its Laws from the
Discovery recommendations that meet `OV-002`'s promotion bar.

### Constraints

- Each Law cites the Discovery recommendation or owner choice it comes
  from (`OV-002`).
- Owner choices are recorded as the owner's, not inferred.

### Expected Deliverables

- The project's Constitution document (`CONST-` series)

### Definition of Done

- `OV-002` §4, Definition of Done for Milestone M2
