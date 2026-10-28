---
id: PRM-FEATURE
title: "Oriveda — Prompt: Feature"
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
  - OV-007
  - OV-008
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0003
  - ADR-0005
  - ADR-0006
tags:
  - prompt
risk: Low
complexity: Low
---

# PRM-FEATURE

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a Feature specification and implementation (M6 onward) session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Feature

### Context

- `OV-007` Feature Specification Protocol
- The project's Frozen Constitution
- The owning `DOM-` specification (§2, §6 and §7 Frozen) and the Standards
  that apply to the change. State which loaded specs are still Draft:
  they inform the work but don't bind it (`ADR-0005`)
- The project's divergence log
- The feature's existing `FEAT-` specification, if it has one

### Task

Specify the feature (or update its specification) before changing code,
then implement it against that specification. This is the workhorse prompt,
used for the life of the project.

### Constraints

- Every Law of the project's Frozen Constitution, by ID.
- The owning domain's invariants and allowed dependencies.
- Rigor tier (`ADR-0005`): the feature's tier is stated with a reason.
  A Low-tier feature may use a spec card. Implementation starts only once
  the feature passes the confidence gate.
- A disagreement with a Draft spec is logged in the divergence log in the
  same change, never resolved silently.
- The Standards the project's applicability decisions select for this
  kind of change.

### Expected Deliverables

- The `FEAT-` specification (new or revised)
- The implementation, with the tests and documentation the specification's
  own Definition of Done lists
- Divergence-log entries for any disagreement with a Draft spec

### Definition of Done

- `OV-007` §4 (protocol readiness)
- `oriveda check boundaries` reports no violations for the owning domain
  (`ADR-0006`), where the project uses the engine
- The feature specification's own Definition of Done section (`OV-007`
  section 9 of the feature template)
