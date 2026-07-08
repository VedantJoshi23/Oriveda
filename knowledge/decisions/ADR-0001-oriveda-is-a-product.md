---
id: ADR-0001
title: Oriveda Itself Is a Product
version: 1.0.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M0
category: Decision
priority: Critical
depends_on: []
required_by:
  - ADR-0002
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - governance
  - vision
risk: Low
complexity: Low
---

# ADR-0001 — Oriveda Itself Is a Product

## Context

The founding conversation for this repository started as a request for a
prompt to build a jewelry e-commerce website. It evolved into designing a
reusable, domain-agnostic engineering knowledge framework, with the
jewelry platform positioned as merely the first implementation to use it.
That shift needed to be made explicit and binding, not left as an implied
mood carried only in conversation — otherwise later work would drift back
toward treating this repository as "the jewelry project's docs."

*(Backfilled 2026-07-08: this decision was made and named in the founding
conversation but never committed as its own ADR file. Recorded now so the
ADR series doesn't have a missing first entry, and so `ADR-0002` — which
depends on this project staying domain-agnostic — has something concrete
to point back to.)*

## Options Considered

- **Treat this repository as the jewelry project's own documentation,**
  organized well. Rejected — this is the default failure mode for
  AI-assisted projects: architecture decisions, standards, and process end
  up permanently entangled with one product's specifics, making them
  non-transferable to the next project.
- **Treat this repository as a framework, with the jewelry platform as a
  separate consumer.** Chosen. The framework is engineered with the same
  discipline as any product would be — versioned, reviewed, given its own
  lifecycle — and any specific product (jewelry included) is scoped as an
  external consumer of it, not commingled with it.

## Decision

This repository (`oriveda/`) is Oriveda the framework, full stop. It carries
no permanent content specific to any one product. Product-specific work —
including the jewelry platform — happens in a separate consuming project
that depends on Oriveda, or, until that separation is set up, in
`examples/` as clearly-labeled, disposable illustrations (see `ADR-0002`).

## Consequences

- Every specification under `knowledge/` must justify itself as reusable
  across arbitrary future products, not just useful for jewelry.
- Enables reuse: 80%+ of `knowledge/` should be applicable, largely
  unmodified, to an unrelated future project (SaaS, healthcare, ERP, etc.).
- Creates an ongoing discipline cost — every contribution has to be
  checked for domain leakage. `ADR-0002` exists because that discipline
  was missed once already.

## Revisit Criteria

If this framework is ever deliberately narrowed to serve only e-commerce
or only jewelry (a legitimate future choice, just a different one), this
decision should be explicitly superseded, not silently ignored.
