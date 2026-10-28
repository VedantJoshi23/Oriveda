---
id: PRM-STANDARDS
title: "Oriveda — Prompt: Standards"
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
  - OV-005
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

# PRM-STANDARDS

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a Standards (M4) session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Standards

### Context

- `OV-005` Standards Protocol
- The target project's Frozen Constitution
- Its architecture document and technology ADRs: their High-tier parts
  Frozen, the rest Frozen, or Draft and passing the `ADR-0005` confidence gate; mark each with its status

### Task

Decide which of `OV-005`'s candidate categories apply to this project and
why, then write one Standard per applicable category. A single Standard can
also be added later without re-running the whole catalog.

### Constraints

- Every Law of the project's Frozen Constitution, by ID; a Standard refines
  a Law and never contradicts one.
- Each rule states how it is enforced (`OV-005`).

### Expected Deliverables

- The applicability decisions and the `STD-` documents

### Definition of Done

- `OV-005` §4, Definition of Done for Milestone M4
