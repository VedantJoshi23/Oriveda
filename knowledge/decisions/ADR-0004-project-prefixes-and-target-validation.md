---
id: ADR-0004
title: Project Prefixes for Discovery, Constitution and Architecture; Target-Project Validation
version: 0.2.0
status: Draft
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-09-26
updated: 2026-10-29
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
  - ADR-0005
  - ADR-0007
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

#### Project validator settings (v0.2.0)

A project that wrote its specifications before adopting Oriveda may use
its own lifecycle words, keep its Constitution outside the `CONST-`
prefix, and link documents that don't bind. The validator can't infer
any of these, so the project states them in an optional `validator:`
section of the `knowledge/manifest.yaml` it already keeps. Oriveda
supplies the mechanism, and the values belong to the project:

```yaml
validator:
  lifecycle_aliases: {Review: Proposal, Accepted: Frozen}
  constitution: knowledge/constitution/CONSTITUTION.md
  advisory_paths: ["docs/**", "*.md"]
```

- **`lifecycle_aliases`** maps a project word onto one of the seven
  lifecycle stages. Every lifecycle rule runs on the mapped stage, so an
  alias of `Frozen` takes on every Frozen obligation. A value that is not
  a stage is an error, and so is a key that already is one: a project
  can add words but cannot redefine `Frozen`. Findings show both words,
  and the run reports how many specifications use each alias.
- **`constitution`** is the path to the project's Constitution.
  References to its frontmatter `id` or to the path itself resolve. With
  it unset, discovery is unchanged (`CONST-` files only).
- **`advisory_paths`** lists globs for documents that may be linked but
  don't bind (`*` stays within one directory and `**` crosses them). A
  bare stem (`DESIGN`) matches an existing `DESIGN.md`. In
  `related_documents`, `related_decisions` or `required_by`, a
  reference to an existing advisory file is info, so it stays visible. In
  `depends_on` it is not. A Frozen spec that depends on advisory content
  is an error, because content that doesn't bind can't hold up content
  that does (`ADR-0005`). On a spec that isn't Frozen it is a warning.
  A matching path that doesn't exist is still an error.

Every key is optional. With no section, or an empty one, the output is
byte-identical to the release before. An unknown key is a warning, so a
project can set a key that its pinned validator predates. Validators
that predate the section ignore it.

The engine (`ADR-0006`) does not read these settings yet. It treats only
the word `Frozen` (in any case) as Frozen, so a Domain Specification whose
status is an alias of `Frozen` is checked as non-Frozen: findings on it
are reported as divergences, not violations. Until the engine reads the
section, Domain Specifications keep canonical status words.

### Consequences

- A project's validator shrinks to whatever is genuinely project-specific
  (for example, checks on evidence-log citations), or disappears.
- A project that invented different prefixes renames its documents to
  adopt these. The rename is mechanical, and optional until the project
  wants the shared validator.

- A project that adopts Oriveda mid-life can validate without renaming
  its lifecycle words or moving its Constitution, and without falsely
  promoting advisory documents to specifications. The cost is a second
  vocabulary for readers. The validator's output names both words, so
  the mapping is never hidden.

### Revisit Criteria

A second consuming project needs a document type none of these prefixes
covers, or needs checks the target mode cannot express generically.
