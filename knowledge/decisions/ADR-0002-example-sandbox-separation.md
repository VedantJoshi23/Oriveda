---
id: ADR-0002
title: Example Sandbox Separation
version: 1.0.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M1
category: Decision
priority: High
depends_on:
  - OV-000
required_by: []
related_documents:
  - OV-000
related_domains: []
related_features: []
related_decisions: []
tags:
  - governance
  - examples
  - discovery
risk: Low
complexity: Low
---

# ADR-0002 — Example Sandbox Separation

## Context

Rulebooks for each milestone (starting with M1 Discovery) read better and
are more trustworthy when validated against a real, messy input rather than
written in the abstract and never exercised. `jwel-main.zip` is available
as exactly that kind of input.

But on 2026-07-08, validating `OV-000` against `jwel-main.zip` was done by
writing the run's output directly into `knowledge/discovery/evidence/`,
Oriveda's own live specification set. That merged one specific product's
domain content (jewelry personas, NestJS module names, gold-rate pricing
rules) into files meant to stay reusable across arbitrary future domains.
It had to be identified and reverted. The underlying problem wasn't running
the validation — it was where the validation's output was allowed to live.

### The Convention

- **`knowledge/`** is Oriveda's own specification set: protocols, schemas,
  and rulebooks. Everything here must remain domain-agnostic and reusable
  by any project that adopts Oriveda, indefinitely.
- **`examples/`** is a sandbox: worked demonstrations of a protocol run
  against a real input. Content here may freely reference a specific
  project (jwel or otherwise) because nothing here is treated as
  framework truth — it exists purely to show a rulebook working, for both
  this project's own validation and as a reference for future users of the
  framework.

## Options Considered

- **Validate rulebooks in the abstract only, no real input.** Cheapest, but
  risks shipping a rulebook that reads well and fails on first real use —
  which is exactly what surfaced in `OV-000` once it met real evidence
  (the confidence-tiering and gap-detection behavior needed refinement
  that abstract drafting alone didn't surface).
- **Validate against a real project, discard the output afterward.** Gets
  the validation benefit, but relies on remembering to strip
  project-specific content back out before it's frozen — the exact step
  that was missed on 2026-07-08.
- **Validate against a real project, but write the output somewhere that
  was never part of the live specification set to begin with (`examples/`).**
  Chosen. No discard step is needed because domain-specific content never
  enters `knowledge/` in the first place.

## Decision

Rulebooks are validated by running them against real evidence, but the
output of any such run is written to `examples/`, never to `knowledge/`.
`knowledge/` files may describe the protocol and may *reference* an example
by path, but must not embed project-specific facts, names, or terminology
in their own body text.

## Consequences

- Every milestone rulebook going forward should ship with at least one
  `examples/` walkthrough demonstrating it end-to-end.
- Examples double as onboarding material for future users of the
  framework — a new adopter can read `examples/` to see the protocol in
  action before running it on their own project.
- Slightly more file-management overhead per rulebook (protocol +
  example, two files instead of one) — accepted as a small, one-time cost
  in exchange for removing an entire class of contamination mistakes.

## Revisit Criteria

If `examples/` grows large enough that it becomes unclear which example
corresponds to which rulebook, introduce a naming/indexing convention
(e.g. one subfolder per `OV-NNN`) rather than reconsidering the separation
itself — the separation is the part that should not be revisited lightly.
