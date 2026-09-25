---
id: PRM-DOMAIN
title: "Oriveda — Prompt: Domain"
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
  - OV-006
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

# PRM-DOMAIN

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a Domain specification (M5) session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Domain

### Context

- `OV-006` Domain Specification Protocol
- The target project's Frozen architecture document (the bounded context
  and its allowed dependencies), Constitution and Standards

### Task

Specify one bounded context declared in the architecture: what it owns and
does not own, its invariants, API surface, events, data ownership and
allowed dependencies. Run once per bounded context.

### Constraints

- The context map in the project's architecture document: a domain never
  gains a dependency the map does not allow.
- Every Law of the project's Frozen Constitution and every applicable
  Standard, by ID.

### Expected Deliverables

- One `DOM-` specification

### Definition of Done

- `OV-006` §4, Definition of Done for Milestone M5 (coverage counts across
  all bounded contexts, not per run)
