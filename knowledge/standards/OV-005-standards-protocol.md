# Metadata

```yaml
---
id: OV-005
title: M4 Standards Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M4
category: Standards
priority: High
depends_on:
  - OV-001
  - OV-002
  - OV-003
  - OV-004
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - standards
  - protocol
risk: Medium
complexity: Medium
---
```

## OV-005 — M4 Standards Protocol

### 1. Human Layer

#### Purpose

A Constitution (`OV-002`) holds a small number of non-negotiable Laws.
Everything below that bar — conventions that make day-to-day engineering
consistent, but that would be survivable if occasionally missed — belongs
in Standards. This protocol defines how a target project ends up with the
*right set* of Standards documents: not a fixed nine every time, and not
zero, but exactly the ones its own architecture and technology choices
actually call for.

#### Explanation

**Candidate catalog.** Nine categories, carried over from the founding
conversation: API, Database, Code, Testing, Security, Observability,
CI/CD, Performance, Accessibility, SEO. This catalog is a starting set,
not a ceiling — see Future Considerations.

**Applicability detection**, mirroring `OV-000`'s gap-detection
philosophy (ask/produce only what's actually needed, and say why):

| Category | Always applicable? | Signal that triggers it |
| --- | --- | --- |
| Code | Always | Every project has code. |
| Testing | Always | Every project needs a testing convention. |
| Security | Always | Every project handles some trust boundary, however small. |
| API | Conditional | `OV-003` declares a service boundary with an external-facing interface. |
| Database | Conditional | `OV-004` records a datastore technology decision. |
| CI/CD | Conditional | The project ships/deploys at all (true for nearly everything, but not, say, a one-off analysis script). |
| Observability | Conditional | `OV-002`'s rigor level is Production-grade or higher (Enterprise/FAANG rigor tiers include it by definition; Production-grade includes it per the founding conversation's own breakdown — so in practice this is close to "always," but stays conditional so a deliberately lighter-weight project can skip it explicitly rather than by omission). |
| Performance | Conditional | `OV-003`'s Scalability Strategy is non-trivial, or `business-vision` evidence names a performance NFR. |
| Accessibility | Conditional | `OV-003`/`OV-004` include any user-facing UI layer. |
| SEO | Conditional | The project has a public, discoverable, server-rendered or crawlable surface. |

A category being "conditional" doesn't mean skippable by default — it
means the applicability decision must be **stated**, not silently assumed.
"Accessibility: not applicable — this project has no UI layer (see
`OV-003` §1, all boundaries are backend services)" is a valid, complete
answer. Silence is not.

**The necessity bar within an applicable category.** Not every good
practice inside an applicable category earns a written rule. The bar:
would inconsistency here cause friction or rework across more than one
contributor or session? If yes, write it down. If it's a one-off
preference with no real consistency cost, it doesn't need a Standard.
(This is the same shape as `OV-002`'s Law-promotion bar, one tier lower —
Laws ask "expensive if silently violated," Standards ask "costs
consistency if left unwritten.")

**Primary input.** `OV-001`'s `recommendations` investigation produces
Improve items that weren't promoted to Constitution Laws (`OV-002`
explicitly scopes Laws to Keep items and high-severity findings) — those
Improve items, plus any Keep items that are good practice but don't meet
the Law bar, are the natural first draft of a project's Standards.

**Common template.** Every produced Standard, regardless of category,
follows the same shape:

```text
Scope         — what this covers, and what it explicitly does not
Rules         — the actual conventions, each with its rationale
Examples      — a compliant example and a non-compliant one
Exceptions    — when deviation is permitted and how it must be documented
Enforcement   — how violations get caught (lint rule, review checklist,
                 CI check, or "human review only" if nothing automates it)
```

**Lifecycle.** Ordinary specification lifecycle (version-bump revision),
*not* the Constitution's heavier ADR-plus-remediation bar — Standards are
meant to evolve more freely than Laws as a project learns. A Standard may
never contradict a Law; if evidence suggests it should, that's a
Constitution amendment, not a Standards revision.

#### Examples

See `examples/m4-standards-jwel-walkthrough.md` once drafted — expected to
exercise the applicability table against jwel's actual architecture (API
and Database clearly applicable; Accessibility applicable since it has a
storefront UI; worth checking whether SEO is applicable given the
storefront is server-rendered per `OV-004`'s technology decisions).

---

### 2. AI Layer

```yaml
owns:
  - The nine-category candidate catalog and applicability signals
  - The necessity bar within an applicable category
  - The common Standard template (Scope/Rules/Examples/Exceptions/Enforcement)
publishes:
  - StandardFrozen   # per produced category
consumes:
  - ConstitutionFrozen        # Laws (must not be contradicted), rigor level
  - ArchitectureFrozen        # OV-003; API/Accessibility/Performance signals
  - TechnologyDecisionFrozen  # OV-004; Database/CI-CD signals
  - InvestigationFrozen       # OV-001 recommendations, specifically Improve items
forbidden_dependencies:
  - Same domain-agnostic rule as the rest of the OV-00X series: no
    project-specific rules, category applicability answers, or examples
    embedded in this protocol's own body. Worked runs belong in examples/.
```

---

### 3. Decision Layer

#### Why

Separating Standards from the Constitution keeps Laws few, stable, and
genuinely non-negotiable, while giving practice-level conventions room to
evolve at normal speed. Applicability detection exists specifically to
avoid the bloat of nine documents being produced for every project
regardless of shape — a backend-only service doesn't need an Accessibility
standard, and pretending otherwise devalues the ones that do matter.

#### Alternatives Considered

- **Fixed catalog, all nine always produced.** Rejected — guarantees
  wasted effort and eventually-ignored documents for categories that
  don't apply, which erodes trust in the ones that do.
- **No fixed catalog; ad hoc standards per project, invented fresh each
  time.** Rejected — loses the consistency and reusability of known
  category names and a common template, which is exactly what let this
  protocol be written once and reused.
- **One protocol per category.** Rejected per the M4 scoping decision —
  the categories share enough structure (template, necessity bar,
  relationship to Constitution) that one meta-protocol with a catalog is
  less repetitive than nine near-identical protocols.

#### Trade-offs

Applicability detection is an extra judgment step compared to "just
produce all nine" — every skipped category needs a stated reason. That
cost is accepted because a silently-produced-but-unused Standard is worse
than an explicitly-skipped one: the former looks authoritative and isn't,
the latter is honest about its own scope.

#### Future Considerations

- The nine-category catalog is a starting set from one founding
  conversation about one kind of product (e-commerce). A future target
  project might need a category not on this list (Internationalization,
  Mobile Platform, Data Pipeline/ML). When that happens, extend the
  catalog here rather than inventing a one-off standard outside it —
  keeps future applicability detection consistent.
- No guidance yet on what happens when two applicable Standards give
  conflicting guidance (e.g. a Performance standard suggesting a
  denormalization the Database standard's normalization rule would
  forbid). Revisit if a real run surfaces this — likely resolved by
  precedence (Constitution Laws > Standards > nothing), but not yet tested.

---

### 4. Validation Layer

#### Rules

- Every candidate category must have a stated applicability decision —
  Applicable-with-justification or Not Applicable-with-reason. None may be
  silently omitted.
- Every applicable category's Standard must use the common template; a
  bare list of rules with no Scope/Examples/Exceptions/Enforcement is
  incomplete.
- No Standard may contradict a Constitution Law. A conflict found during
  drafting must be surfaced as a candidate Constitution amendment, not
  quietly resolved in the Standard's favor.

#### Checklists

**Definition of Done for Milestone M4 (Standards):**

- [ ] `OV-002`, `OV-003`, `OV-004` are Frozen for the target project (M2
      and M3 complete first).
- [ ] Applicability determined and stated for all nine candidate
      categories (plus any project-specific additions).
- [ ] Every applicable category's Standard drafted, reviewed, and Frozen
      using the common template.
- [ ] No Standard contradicts a Constitution Law.
- [ ] At least one worked example exists under `examples/`, per `ADR-0002`.

#### Cross References

- `OV-001` is `depends_on` — Improve recommendations are the primary
  Standards input.
- `OV-002` is `depends_on` — Laws bound what a Standard may say; rigor
  level affects Observability applicability.
- `OV-003`/`OV-004` are `depends_on` — architecture and technology signals
  drive applicability detection.

#### Required Updates When This Changes

If the candidate catalog or applicability signals change, reconcile
against any already-produced target-project Standards, or mark them as
authored against a prior protocol version.
