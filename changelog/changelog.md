# Changelog

## v0.1.0-genesis

The birth of Oriveda.

### Added

- Repository structure
- Engineering philosophy
- Naming conventions
- Metadata specification
- Contribution guidelines
- Versioning strategy
- Repository vision

This marks the first public milestone of Oriveda.

The framework now exists independently of any implementation and establishes the foundation for AI-assisted engineering through structured knowledge.

---

## M1 — Discovery

### Added

- `OV-000` Knowledge Acquisition Specification (Frozen): evidence
  inventory, per-evidence-type reverse-engineering pipelines,
  confidence-tiered knowledge claims, gap-detection protocol.
- `OV-001` M1 Discovery Protocol (Frozen): the ten-investigation
  structure, shared investigation template, per-investigation lifecycle.
- `ADR-0001` (backfilled), `ADR-0002`: this repository is the framework
  itself, domain-agnostic; protocol validation output belongs in
  `examples/`, never in `knowledge/`.
- `templates/document-template.md`, `templates/decision-template.md`
  filled in (previously empty stubs).
- Ten `examples/m1-discovery-*-walkthrough.md` files: `OV-001` run
  end-to-end against a reference codebase.

### Changed

- `OV-001` later revised to v0.1.1 (see M4) after a recurring gap was
  found across two milestones' dry runs.

---

## M2 — Constitution

### Added

- `OV-002` M2 Constitution Protocol (Frozen): derives a target project's
  Engineering Constitution from `OV-001` Discovery findings plus three
  owner-choice questions (rigor level, AI collaboration mode,
  architecture ambition) that can't be inferred from evidence.
- `templates/constitution-template.md`.
- `examples/m2-constitution-jwel-walkthrough.md`: a full 8-Law
  Constitution draft.

---

## M3 — Architecture

### Added

- `OV-003` M3 System Architecture Protocol (Frozen): service boundaries,
  domain model, event flow, folder structure, scalability strategy —
  each classified Adopted/Adapted/Designed depending on available
  Discovery evidence.
- `OV-004` M3 Technology Decisions Protocol (Frozen): the stack-freedom
  owner-choice question plus one ADR-shaped decision per significant
  technology layer.
- Two worked examples (`m3-architecture-jwel-walkthrough.md`,
  `m3-technology-decisions-jwel-walkthrough.md`). Found and fixed a real
  leak (tech-specific content embedded in `OV-003`'s own body) before
  freezing.

---

## M4 — Standards

### Added

- `OV-005` M4 Standards Protocol (Frozen): a nine-category candidate
  catalog with applicability detection against a target project's
  architecture/technology/constitution, a shared necessity bar, and one
  common template all produced Standards follow.
- `examples/m4-standards-jwel-walkthrough.md`.

### Changed

- `OV-001` revised to v0.1.1 (versioned revision, not a silent edit):
  added a cross-cutting extraction checklist after three independent dry
  runs found the same gap shape — domain events and NFRs present in
  evidence but not captured by the investigation responsible for them.

---

## M5 — Domains

### Added

- `OV-006` M5 Domain Specification Protocol (Frozen): explodes each
  `OV-003` bounded context into a full eight-section Domain
  Specification. Full/Thin depth tiers avoid busywork for pure
  projection domains while still requiring every declared boundary to
  have a spec.
- `templates/domain-template.md`.
- `examples/m5-domains-jwel-walkthrough.md`: two Full specs, one Thin —
  surfaced a real inconsistency in the reference project's own
  architecture doc (correctly flagged, not silently resolved).

---

## M6 — Features

### Added

- `OV-007` M6 Feature Specification Protocol (Frozen): nine-section
  Feature Specification structure operationalizing "exactly one owning
  domain." Unlike M1–M5, M6's Definition of Done is protocol readiness,
  not full feature coverage — features are open-ended.
- `templates/feature-template.md`.
- `examples/m6-features-jwel-walkthrough.md`: a multi-domain,
  sequential-hand-off feature found and fixed a real structural gap in
  the dependency rule before freezing.

---

## M7 — Prompt Library

### Added

- `OV-008` M7 Prompt Library Protocol (Frozen): a fixed seven-prompt
  catalog (`PRM-DISCOVERY` through `PRM-REVIEW`), one per prior
  milestone's protocol plus a cross-cutting review prompt, sharing a
  common Context/Task/Constraints/Deliverables/DoD shape.
- `templates/prompt-template.md`.
- `examples/m7-prompts-jwel-walkthrough.md`: all seven prompts
  instantiated; `PRM-FEATURE` put to a real sufficiency test.
- Root `README.md`: a "Getting Started With a New Project" section with
  a copy-pasteable Genesis Prompt for bootstrapping Oriveda governance
  in a new target project, including the no-repository case.
- `ADR-0003`: git submodule as the mechanism for a target project to
  reference `OV-000`–`OV-008` without copying their content.

**M0 through M7 of the roadmap are complete. M8 — Implementation —
remains: applying these eight protocols to a real target project.**

---

## Repository Audit (post-M7)

A full walk-through of the repository structure, prompted by noticing
several `.oriveda/*.yaml` files and directories had sat empty since M0
without anyone deciding whether they were actually needed.

### Added

- `.oriveda/glossary.yaml`, `.oriveda/taxonomy.yaml` populated
  (framework-level vocabulary and ID-prefix rules — previously empty
  stubs since M0).
- `.oriveda/knowledge_graph.md`: a Mermaid diagram rendered from every
  spec's own frontmatter, replacing the never-populated
  `knowledge_graph.yaml`. Building it surfaced a real cross-reference bug
  (`ADR-0001`/`ADR-0002` disagreed about their own dependency direction),
  fixed as part of this change (`ADR-0002` → v1.0.1).
- `templates/review-template.md` filled in — the Architecture Review
  lifecycle stage and `PRM-REVIEW` previously had no defined output
  shape.

### Fixed

- README's Naming Convention and Knowledge Hierarchy sections corrected
  to match what was actually built, replacing stale M0-era placeholders.
- `.oriveda/manifest.yaml`: stale comments corrected, the fixed `PRM-*`
  catalog registered (previously an empty list despite `OV-008` defining
  seven concrete entries).

### Removed

- Unused, never-git-tracked `assets/` and `knowledge/vision/`
  directories. Vision is covered by `OV-000`/`OV-001` — a standalone
  Vision artifact was considered and deliberately not built, not
  forgotten.
- Phantom top-level `standards/` from the README's structure diagram —
  never actually existed; `knowledge/standards/` is what's real.
