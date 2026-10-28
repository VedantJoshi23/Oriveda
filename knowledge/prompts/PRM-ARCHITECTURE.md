---
id: PRM-ARCHITECTURE
title: "Oriveda — Prompt: Architecture"
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
  - OV-003
  - OV-004
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

# PRM-ARCHITECTURE

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a Architecture and technology decisions (M3) session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Architecture

### Context

- `OV-003` System Architecture Protocol and `OV-004` Technology Decisions
  Protocol
- The target project's Frozen Constitution
- Its `DISC-` investigations (Frozen, or Draft and passing the `ADR-0005` confidence gate; mark each with its status)

### Task

Define service boundaries, the domain model, events, folder structure and
scalability strategy, each classified Adopted, Adapted or Designed
(`OV-003`); ask the owner the stack-freedom question and record one
decision per significant technology layer (`OV-004`).

### Constraints

- Every Law of the project's Frozen Constitution, by ID.
- The owner's architecture-ambition choice recorded in the Constitution.

### Expected Deliverables

- The project's architecture document (`ARCH-` series)
- One project `ADR-` per significant technology decision

### Definition of Done

- `OV-003` §4, Definition of Done for Milestone M3 (Architecture half)
- `OV-004` §4, Definition of Done for Milestone M3 (Technology half)
