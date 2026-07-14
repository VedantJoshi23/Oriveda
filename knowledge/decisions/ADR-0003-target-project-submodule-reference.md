---
id: ADR-0003
title: Target Projects Reference Oriveda via Git Submodule
version: 1.0.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M7
category: Decision
priority: High
depends_on:
  - OV-008
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0001
  - ADR-0002
tags:
  - governance
  - onboarding
risk: Medium
complexity: Low
---

# ADR-0003 — Target Projects Reference Oriveda via Git Submodule

### Context

`OV-008`'s prompts point at Frozen specs by ID rather than restating
their content — "point, don't copy." That only works if whatever is
running a `PRM-*` prompt can actually *read* `OV-000`–`OV-008`. A target
project consuming Oriveda lives in its own, separate repository (per
`ADR-0001`: this repo stays domain-agnostic, product-specific work
belongs elsewhere). No mechanism for that cross-repository reference has
been defined until now.

### Options Considered

- **Git submodule.** The target project adds this Oriveda repository as a
  submodule at a conventional path. References resolve as real relative
  file paths; updates are explicit (`git submodule update`), never
  silent.
- **Manual copy at genesis time.** Copy `OV-000`–`OV-008` into the target
  project once, at setup. Simplest to explain, but the copy immediately
  starts drifting from any future Oriveda revision — in spirit, this is
  exactly what "point, don't copy" exists to prevent, just moved one
  level up (the target project's *copy* of the framework, not its specs,
  becomes the stale artifact).
- **Published package.** Version and distribute Oriveda like a library
  (npm/PyPI-style or a custom registry). Requires publishing
  infrastructure that doesn't exist yet and would be designed against
  exactly one real consuming project's needs — premature.

### Decision

A target project references Oriveda by adding this repository as a git
submodule, conventionally at `.oriveda-framework/` in the target
project's root. The target project's bootstrap file (see the root
`README.md`'s Genesis Prompt) references protocol files via that
relative path — e.g. `.oriveda-framework/knowledge/discovery/
OV-000-knowledge-acquisition.md` — never by copying their content inline.

### Consequences

- Requires the target project's contributors to be comfortable with git
  submodules (an init step, an explicit update step) — a real but
  well-understood cost.
- Oriveda framework updates never silently propagate into a target
  project; a submodule bump is a deliberate, reviewable commit, which
  fits Principle 7 (every architectural shortcut/change is intentional).
- No publishing infrastructure needed — works fully offline, immediately,
  for the first real consuming project.

### Revisit Criteria

Once a second real consuming project exists and submodule friction
(contributors unfamiliar with submodules, forgotten update steps) proves
costly in practice — not before. Designing a package-distribution
mechanism against zero real usage data would be exactly the kind of
premature architecture Oriveda's own principles warn against.
