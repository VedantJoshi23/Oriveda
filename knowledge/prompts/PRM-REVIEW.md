---
id: PRM-REVIEW
title: "Oriveda — Prompt: Review"
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

# PRM-REVIEW

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a review session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Review

### Context

- Every Frozen specification of the target project that the change touches
- Every Draft specification it touches, marked as Draft (`ADR-0005`)
- The project's divergence log, and `oriveda check boundaries` output where
  the project uses the engine (`ADR-0006`)
- `templates/review-template.md`
- The change under review: a spec draft at Architecture Review, or a diff,
  commit or pull request

### Task

Check the change against every Law, Standard and domain boundary it could
affect, and record each check with its result. Disagreement with a Frozen
spec is a violation. Disagreement with a Draft spec is acceptable only if
it is logged in the divergence log; an unlogged divergence is a finding
(`ADR-0005`). The relevance of a Standard
to a change follows `OV-005` and `OV-007` (`OV-008` §3, Future
Considerations: the mechanics are inherited, not redefined here).

### Constraints

- Every Law of the project's Frozen Constitution, by ID.
- The Standards the project's applicability decisions select.
- The context map of the project's architecture document.

### Expected Deliverables

- One review in the shape of `templates/review-template.md`: checks with
  their source and result, findings, verdict, follow-ups

### Definition of Done

- Every check cites what it checked; a Fail blocks freezing or merging
  until it is resolved or explicitly waived with a rationale
  (`templates/review-template.md`).
- `OV-005` §4 and `OV-007` §4, for Standards and feature changes.
