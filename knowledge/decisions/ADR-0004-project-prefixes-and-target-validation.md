---
id: ADR-0004
title: Project Prefixes for Discovery, Constitution and Architecture; Target-Project Validation
version: 0.1.0
status: Draft
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-09-26
updated: 2026-09-26
milestone: M7
category: Decision
priority: Medium
depends_on:
  - OV-001
  - OV-002
  - OV-003
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0001
  - ADR-0003
tags:
  - taxonomy
  - validation
risk: Low
complexity: Low
---

# ADR-0004 — Project Prefixes for Discovery, Constitution and Architecture; Target-Project Validation

### Context

The taxonomy gave target projects prefixes for domains, features,
standards, decisions, evidence and claims, but none for the documents that
`OV-001`, `OV-002` and `OV-003` produce. The first real consuming project
had to invent its own (`DISC-`, `CONST-`, `ARCH-`, recorded in that
project's ADR-0001, which asks for the gap to be reported upstream).
Without IDs those documents cannot be cross-referenced in frontmatter or
checked for dangling references.

The same project found that `scripts/validate.py` could only check this
repository, so it wrote its own validator mirroring this one. Every
further project would have to do the same.

### Options Considered

- **Leave both to each project.** Every project re-invents prefixes and a
  validator, and their conventions drift apart.
- **Reuse `OV-` numbers in projects.** Rejected: `OV-` names this
  framework's own protocols (`ADR-0001`).
- **Adopt the prefixes the first project already uses, and give the
  framework validator a target-project mode.** Evidence-based: one real
  project has used both for its full M1–M6 run.

### Decision

The third option.

- `.oriveda/taxonomy.yaml` gains three project-scope prefixes: `DISC-`
  (Discovery investigations and their roll-up), `CONST-` (Constitution)
  and `ARCH-` (Architecture).
- `scripts/validate.py --root PROJECT` validates a target project. It
  checks the project's `knowledge/` files whose names start with a
  project-scope prefix or the project's own `ADR-` series, against the
  project's `knowledge/manifest.yaml`. It resolves references to Oriveda's
  own `OV-`, `ADR-` and `PRM-` ids through this repository's manifest. A
  project may add prefixes in its own `knowledge/taxonomy.yaml`; the
  framework's entries win on a clash.
- The framework-mode run also validates the `PRM-` prompt files.

### Consequences

- A project's validator shrinks to whatever is genuinely project-specific
  (for example, checks on evidence-log citations), or disappears.
- A project that invented different prefixes renames its documents to
  adopt these. The rename is mechanical, and optional until the project
  wants the shared validator.

### Revisit Criteria

A second consuming project needs a document type none of these prefixes
covers, or needs checks the target mode cannot express generically.
