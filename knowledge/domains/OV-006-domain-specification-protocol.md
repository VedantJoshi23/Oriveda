---
id: OV-006
title: M5 Domain Specification Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M5
category: Domains
priority: Critical
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
  - domains
  - protocol
risk: High
complexity: Medium
---

# OV-006 — M5 Domain Specification Protocol

## 1. Human Layer

### Purpose

`OV-003` declares service boundaries as one row in a table — a name, an
Owns statement, a Does-NOT-own statement. That's enough to reason about
the system's shape, but not enough to safely implement or modify a
feature inside any one boundary without re-deriving its rules from
scratch each time. This protocol explodes each `OV-003` boundary into a
full Domain Specification: the single place a future feature (`M6`) or
implementation session (`M8`) looks to understand one bounded context
completely, without needing the whole system in context.

### Explanation

**One spec per declared boundary, no applicability filtering.** Unlike
`OV-005` Standards (where a category might genuinely not apply), every
bounded context `OV-003` declares gets a Domain Specification — if it
wasn't worth specifying, it shouldn't have been declared a boundary in the
first place. What varies is depth, not whether a spec exists at all.

**Depth tiers:**

| Tier | When | What's still required |
|---|---|---|
| **Full** | The domain owns data and/or has invariants of its own (the common case) | All eight sections below, in full. |
| **Thin** | The domain is a pure derived/read-only projection with no independent business rules (e.g. a search index that only reflects another domain's data) | All eight sections still present, but Invariants/Edge Cases may state "N/A — derived from `<owning domain>`," not be left blank. |

A Thin classification must be justified against `OV-003`'s context map
(e.g. "this context only consumes `ProductUpserted` and has no other
inbound dependency" is a valid justification; an assertion with no
context-map backing is not).

**Domain Specification structure** (see `templates/domain-template.md`):

```text
1. Overview          — one paragraph: what this domain is responsible for
2. Ownership          — Owns / Explicitly Does NOT Own (from OV-003 §1,
                         restated here, not re-derived)
3. Invariants         — business rules that must always hold, each
                         sourced (OV-001 claim, Constitution Law, or an
                         explicit new decision — never unsourced)
4. API Surface        — endpoints this domain exposes (from OV-003/OV-004,
                         not reinvented here)
5. Events             — Publishes / Consumes (from OV-003's event catalog)
6. Data Ownership     — tables/aggregates this domain owns (from OV-003's
                         Domain Model + OV-004's datastore decision)
7. Dependencies       — Allowed (must match OV-003's context map exactly)
                         / Forbidden (explicit, not just "everything else")
8. Edge Cases &
   Validations        — specific scenarios a future implementer must handle
```

**No new dependencies invented here.** A Domain Specification's §7
Dependencies must match `OV-003`'s context map. If drafting a spec
reveals a dependency `OV-003` didn't capture, that's a signal `OV-003`
itself needs a revision (version-bumped, since it's Frozen) — not
something to silently add at the domain-spec layer. This mirrors why
`OV-001` was revised in M4 rather than patched around: a gap in an
earlier milestone's protocol gets fixed at its source.

**Every Invariant is sourced**, same discipline as Constitution Laws and
Standards Rules: cite the `OV-001` claim it came from (commonly
`hidden-business-rules` or `domain-discovery`), the Constitution Law it
implements, or state it's a new decision made at this layer (rare — most
invariants should already exist somewhere upstream by M5).

### Examples

No published example yet — see `examples/README.md` for the sandbox
rules a future worked example must follow. A future example should
cover a representative subset in full depth (matching `OV-005`'s "three
full, rest abbreviated" precedent) plus at least one Thin-tier domain to
exercise that path.

---

## 2. AI Layer

```yaml
owns:
  - The eight-section Domain Specification structure
  - The Full/Thin depth-tier criterion
publishes:
  - DomainSpecFrozen   # per bounded context
consumes:
  - ArchitectureFrozen        # OV-003; boundaries, domain model, event catalog
  - TechnologyDecisionFrozen  # OV-004; which datastore implements ownership
  - InvestigationFrozen       # OV-001 domain-discovery, hidden-business-rules
  - ConstitutionFrozen        # OV-002; Laws each Invariant must not violate
forbidden_dependencies:
  - Same domain-agnostic rule as the rest of the OV-00X series: no
    project-specific domain names, invariants, or events in this
    protocol's own body. Worked runs belong in examples/.
```

---

## 3. Decision Layer

### Why

A boundary declared in one row of an architecture table is not
actionable enough for someone (human or agent) to implement a feature
inside it correctly six months later without re-reading the whole
system. Exploding each boundary into a full specification — while
explicitly forbidding new dependencies from being invented at this
layer — keeps `OV-003` as the single source of truth for *what talks to
what*, with Domain Specifications adding depth, not new structure.

### Alternatives Considered

- **Skip individual domain specs; rely on OV-003's boundary table alone.**
  Rejected — insufficient detail for safe implementation; this is exactly
  the gap M6 Features and M8 Implementation would otherwise hit.
- **Let each Domain Specification declare its own dependencies
  independently of OV-003.** Rejected — would let the architecture drift
  across N documents instead of staying centralized in one; the
  "no new dependencies invented here, revise OV-003 instead" rule exists
  specifically to prevent this.
- **Uniform depth for every domain (no Thin tier).** Rejected — forces
  busywork for genuinely simple projection-only contexts (e.g. a search
  index) to fill out Invariants/Edge-Cases sections that don't
  meaningfully apply, without gaining anything real.

### Trade-offs

Requiring every declared boundary to get a spec (even Thin ones) is more
upfront work than only specifying "important" domains, but it closes the
same silent-omission risk `OV-005`'s applicability rule addresses for
Standards — an un-specified domain is indistinguishable from a
forgotten one.

### Future Considerations

- No guidance yet on how a Domain Specification should be revised when
  its owning Architecture (`OV-003`) changes — likely needs a
  "Domain Specifications affected" step added to `OV-003`'s own revision
  process, but not designed yet; revisit if a real `OV-003` revision
  happens with domain specs already in place.

---

## 4. Validation Layer

### Rules

- Every bounded context in `OV-003` §1 must have exactly one Domain
  Specification — no orphan boundaries, no duplicate specs for one
  boundary.
- Every Invariant must cite a source (`OV-001` claim, Constitution Law, or
  explicit new decision).
- Every §7 Dependency must match `OV-003`'s context map exactly; a
  mismatch blocks freezing the Domain Specification until `OV-003` is
  reconciled first.
- A Thin-tier classification must be justified against the context map,
  not asserted without backing.

### Checklists

**Definition of Done for Milestone M5 (Domains):**

- [ ] `OV-003` and `OV-004` are Frozen for the target project.
- [ ] Every declared bounded context has a Domain Specification, tiered
      Full or Thin, each justified.
- [ ] No orphan or duplicate domain specs relative to `OV-003`.
- [ ] Every Invariant sourced; no unsourced rules.
- [ ] At least one Full and one Thin worked example exist under
      `examples/`, per `ADR-0002`.

### Cross References

- `OV-003` is `depends_on` — the authoritative source for boundaries,
  domain model, and the event catalog every Domain Specification restates
  rather than re-derives.
- `OV-001`, `OV-002`, `OV-004` are `depends_on` for invariant sourcing,
  Law compliance, and data-ownership technology respectively.
- `templates/domain-template.md` implements the eight-section structure.

### Required Updates When This Changes

If the eight-section structure or the Full/Thin criterion changes,
`templates/domain-template.md` and any already-produced target-project
Domain Specifications should be reconciled, or explicitly marked as
authored against a prior protocol version.
