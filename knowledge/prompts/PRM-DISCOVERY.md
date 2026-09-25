---
id: PRM-DISCOVERY
title: "Oriveda — Prompt: Discovery"
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
  - OV-000
  - OV-001
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

# PRM-DISCOVERY

One of the seven catalog prompts defined by `OV-008`. Paste it (or point an
agent at this file) to start a Knowledge Acquisition and Discovery (M1) session in a target project. It
points at specifications by ID and never restates them; the session loads
them itself. Paths to Oriveda files assume the submodule location from
`ADR-0003` (`.oriveda-framework/`).

## Prompt: Discovery

### Context

The bootstrapping case (`OV-008`): the target project has no Frozen
specification yet, so this prompt points at Oriveda itself.

- `OV-000` Knowledge Acquisition, with `.oriveda/schemas/evidence.schema.yaml`
- `OV-001` Discovery Protocol
- If the project already has an evidence log, that log (append-only; new
  entries continue its numbering)

### Task

Ask the owner what evidence exists (code, documents, designs, recordings,
conversations) and acquire knowledge from what they actually have. Log each
evidence item and the claims extracted from it with confidence and
citations, then run the ten investigations and roll them up into
recommendations.

### Constraints

- No Constitution exists yet, so no Law binds this session; `OV-000` and
  `OV-001` Validation Layer rules do.
- Every claim cites evidence; inferences are labelled as such (`OV-000`).

### Expected Deliverables

- The project's evidence log (`EVD-`, `KC-` entries)
- The ten `DISC-` investigations and the recommendations roll-up (`OV-001`)

### Definition of Done

- `OV-000` §4, exit criteria for Knowledge Acquisition
- `OV-001` §4, Definition of Done for Milestone M1
