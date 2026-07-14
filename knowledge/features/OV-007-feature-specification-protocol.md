# Metadata

```yaml
---
id: OV-007
title: M6 Feature Specification Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M6
category: Features
priority: High
depends_on:
  - OV-002
  - OV-005
  - OV-006
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - features
  - protocol
risk: Medium
complexity: Medium
---
```

## OV-007 — M6 Feature Specification Protocol

### 1. Human Layer

#### Purpose

`OV-006` makes every bounded context deeply understood. This protocol
defines how a single unit of product work — a feature — gets specified
against that understanding, so that implementing it (`M8`) means reading
one small, precise document instead of re-deriving context every time.

#### Explanation

**Features are open-ended; Domains are not.** `OV-006` produces one
Domain Specification per boundary declared in `OV-003` — a closed,
enumerable set. Features are the opposite: a project accumulates them
continuously for its entire life. M6's Definition of Done is therefore not
"every feature is specified" (there is no fixed count), but **the protocol
itself is established and demonstrated** against a real initial slice —
typically whatever `OV-001`'s `feature-inventory` investigation or a
Constitution-referenced MVP scope names as the starting set.

**Exactly one owning domain, per Contribution Guideline Rule 3.**
`README.md`'s Rule 3 ("every feature references exactly one domain") is a
pre-existing Oriveda rule this protocol operationalizes. Even a feature
that visibly touches several domains (a checkout flow touching Cart,
Pricing, Coupon, Order, Payment, Inventory) must name exactly one owning
domain — whichever domain the feature's core business capability actually
belongs to (see the worked example for how to make this call when a
feature's entry point and its "true owner" differ) — with every other
domain treated as a dependency, never a co-owner.

**No new cross-domain dependencies invented here either — checked
per-call, not per-owner.** This is the third layer with this rule (`OV-006`
forbade inventing dependencies not already in `OV-003`'s context map; this
protocol forbids inventing dependencies not already declared Allowed
somewhere in the domains involved). The check is **not** "does the owning
domain's `OV-006` Allowed list contain every other domain touched" — a
feature's flow can hand off between domains sequentially (domain A calls
domain B, which then independently calls domain C), and domain A was
never going to have C in its own Allowed list, because A never calls C
directly. The correct check: **each individual cross-domain call in the
feature's flow must match the Allowed list of whichever domain initiates
that specific call.** If any call in the chain has no matching Allowed
entry anywhere, that's a Domain Specification revision first, not a
feature-layer workaround.

**Feature Specification structure** (see `templates/feature-template.md`):

```text
1. Overview                    — one paragraph: what this does, for whom
2. Owning Domain                — exactly one; other involved domains
                                   listed as dependencies, not co-owners
3. Acceptance Criteria          — concrete, testable statements
4. API Surface                  — new/changed endpoints; must be consistent
                                   with the owning domain's API surface
5. Events                       — Publishes/Consumes; must be a subset of
                                   what the owning domain's OV-006 spec
                                   already declares
6. Data Changes                 — new tables/fields; must stay within the
                                   owning domain's Data Ownership
7. Edge Cases & Validations     — feature-specific scenarios
8. Non-Functional Considerations — checked against every Applicable
                                    Standard (OV-005) relevant to this
                                    feature's shape (e.g. a UI feature
                                    checks the Accessibility standard; an
                                    API feature checks the API standard)
9. Definition of Done            — testing, docs, and deployment checklist
                                    for this specific feature
```

**Non-Functional Considerations is not optional boilerplate.** Section 8
must name which Applicable Standards (from the target project's `OV-005`
output) actually bear on this feature, and how — not restate every
Standard regardless of relevance. A backend-only feature with no UI has
nothing to say about Accessibility; that absence should be stated, not
silently skipped.

#### Examples

No published example yet — see `examples/README.md` for the sandbox
rules a future worked example must follow. A future example should
cover a small representative slice (not an exhaustive feature list,
since M6 doesn't have one), chosen to include at least one feature that
spans multiple domains, to exercise the "exactly one owner, others as
dependencies" rule under real pressure.

---

### 2. AI Layer

```yaml
owns:
  - The nine-section Feature Specification structure
  - The exactly-one-owning-domain rule (Contribution Guideline Rule 3)
publishes:
  - FeatureSpecFrozen
consumes:
  - DomainSpecFrozen          # OV-006; owning domain's declared surface,
                                events, data ownership, allowed dependencies
  - StandardFrozen            # OV-005; Applicable Standards to check against
  - ConstitutionFrozen        # OV-002; Laws a feature must not violate
forbidden_dependencies:
  - Same domain-agnostic rule as the rest of the OV-00X series: no
    project-specific feature names, acceptance criteria, or domain
    references in this protocol's own body. Worked runs belong in
    examples/.
```

---

### 3. Decision Layer

#### Why

Keeping Feature Specifications thin and dependent on already-established
Constitution/Architecture/Domain context is the entire payoff of doing
M2–M5 first: the founding conversation's own observation was that a
feature prompt can be two to three pages instead of thirty once the
foundation exists. This protocol formalizes what goes in those two or
three pages, and — just as importantly — what does not (re-deriving
architecture, inventing new cross-domain calls).

#### Alternatives Considered

- **Allow features to name multiple owning domains.** Rejected — directly
  contradicts an existing Oriveda rule (`README.md` Rule 3) and would make
  it ambiguous who's responsible for a feature when domains disagree on
  its behavior.
- **Require full feature-inventory coverage before M6 is "done," like
  M5's domain coverage requirement.** Rejected — features aren't a closed
  set the way declared bounded contexts are; treating M6 like M5 would
  either block indefinitely or force speculative specs for features that
  may never be built.
- **Let features declare new cross-domain dependencies freely if the
  domain spec seems to allow it implicitly.** Rejected — same reasoning
  as `OV-006`'s equivalent rule: architecture-level decisions belong at
  the architecture/domain layer, not scattered across feature specs where
  they'd be easy to lose track of.

#### Trade-offs

Restricting features to already-declared dependencies means a genuinely
novel feature idea sometimes has to pause and go revise a Domain
Specification (or even `OV-003`) before it can be specified. That friction
is intentional — it's the same protection against architectural drift the
founding conversation asked for from the start.

#### Future Considerations

- No guidance yet on feature *sequencing* or prioritization — this
  protocol defines how one feature gets specified, not which feature to
  specify next. That likely belongs to a lighter-weight roadmap artifact
  outside the OV-00X series, not designed yet.

---

### 4. Validation Layer

#### Rules

- Every Feature Specification names exactly one owning domain.
- Every cross-domain call within a feature's flow must match the Allowed
  list of whichever domain initiates that specific call (not necessarily
  the feature's single owning domain) — a feature may not introduce a
  call with no matching Allowed entry anywhere in the chain.
- Section 8 (Non-Functional Considerations) must explicitly address every
  Applicable Standard relevant to the feature's shape, including stating
  "not applicable" where genuinely true.
- No Feature Specification may violate a Constitution Law.

#### Checklists

**Definition of Done for Milestone M6 (Features) — protocol readiness, not
feature coverage:**

- [ ] `OV-002`, `OV-005`, `OV-006` are Frozen for the target project.
- [ ] The nine-section structure has been exercised against at least one
      real feature spanning more than one domain.
- [ ] No Feature Specification produced so far violates a Constitution Law
      or invents an undeclared cross-domain dependency.
- [ ] At least one worked example exists under `examples/`, per `ADR-0002`.

*(Ongoing, per-feature: each new Feature Specification is Frozen
individually before implementation begins — M6 as a milestone is "ready,"
not "finished," once the above is met.)*

#### Cross References

- `OV-006` is `depends_on` — a Feature Specification's owning-domain
  section restates that domain's already-declared surface, not new
  invention.
- `OV-005` is `depends_on` — Section 8 checks against Applicable
  Standards.
- `OV-002` is `depends_on` — no Feature Specification may violate a Law.
- `templates/feature-template.md` implements the nine-section structure.

#### Required Updates When This Changes

If the nine-section structure changes, `templates/feature-template.md`
and any already-produced target-project Feature Specifications should be
reconciled, or explicitly marked as authored against a prior protocol
version.
