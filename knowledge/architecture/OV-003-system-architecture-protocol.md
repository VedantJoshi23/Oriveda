# Metadata

```yaml
---
id: OV-003
title: M3 System Architecture Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M3
category: Architecture
priority: Critical
depends_on:
  - OV-001
  - OV-002
required_by: []
related_documents:
  - OV-004
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - architecture
  - protocol
risk: High
complexity: High
---
```

## OV-003 — M3 System Architecture Protocol

### 1. Human Layer

#### Purpose

Turn the Constitution's binding choices (Architecture Ambition, Laws) into
a concrete system shape: service boundaries, domain model, event flow, a
design-level folder structure, and a scalability strategy. Like `OV-001`/
`OV-002`, this is a **protocol**; a produced architecture is a per-project
artifact (`examples/` or a consuming project, per `ADR-0002`).

#### Explanation

**Two architecture sources, not one.** `OV-001` Discovery assumes a target
project already has something to reverse-engineer. That won't always be
true — a project starting from an idea or a PRD alone has no
`domain-discovery`/`technical-architecture`/`data-model` investigations to
draw on. This protocol handles both cases explicitly rather than silently
assuming a codebase exists:

| Source | When | What happens |
| --- | --- | --- |
| **Adopted** | M1's `domain-discovery`/`technical-architecture`/`data-model` findings already match the Constitution's Architecture Ambition | Carry the Discovery findings forward largely as-is; this document mainly formalizes what was already found. |
| **Adapted** | Discovery findings exist but conflict with the Constitution (e.g. Discovery found a monolith, Constitution mandates Hybrid) | Discovery findings are the starting point, revised to satisfy the Constitution; the revision itself gets documented as a deviation (Law 3-style, if the target project adopted that Law). |
| **Designed** | No Discovery findings exist for these areas (greenfield, idea-only evidence) | Architecture is designed fresh from the Constitution's Architecture Ambition plus whatever `business-vision`/`feature-inventory` evidence exists. Lower starting confidence, same rigor. |

Every architecture document states which source applies, per section — a
project can be `Adopted` for domain boundaries but `Designed` for
scalability strategy if Discovery never covered performance.

**Contents**, each carried at whatever confidence its source supports:

1. **Service Boundaries** — bounded contexts, each with an explicit Owns /
   Does NOT own statement (this is the generalized form of the pattern
   found valuable in `examples/m1-discovery-domain-discovery-walkthrough.md`
   and promoted to Law in the `m2-constitution-jwel-walkthrough.md`
   example — if a target project's Constitution contains a boundary-
   ownership Law, this section is how that Law gets satisfied concretely).
2. **Domain Model** — aggregate roots and their relationships (built from
   `data-model` findings if `Adopted`/`Adapted`, designed fresh otherwise).
3. **Event Flow / Domain Events Catalog** — producer/consumer table for
   any event-driven communication the Architecture Ambition requires
   (mandatory if the Constitution's ambition is Hybrid or Microservices;
   optional for a plain Monolith).
4. **Folder Structure (design-level)** — one folder/module per bounded
   context, matching §1's boundaries; this is a design artifact, not a
   scaffolding script.
5. **Scalability Strategy** — how the system is expected to grow, tied to
   any NFRs found in `business-vision`, or stated as open/unknown if none
   exist.

**What this protocol does not do.** Technology selection (frameworks,
databases, hosting) is `OV-004`'s job, not this one. A Service Boundary
here is described in terms of responsibility and ownership, not
implementation technology — "Order owns order lifecycle and status
history" is in scope here; which framework or datastore implements that
module is `OV-004`.

#### Examples

See `examples/m3-architecture-jwel-walkthrough.md` once drafted — expected
to be mostly `Adopted`, since `jwel-main.zip`'s own `ARCHITECTURE.md` was
already thorough and largely consistent with the Constitution's Hybrid
ambition (Law 1 in `m2-constitution-jwel-walkthrough.md` restates jwel's
own boundary-enforcement rule as a binding Law).

---

### 2. AI Layer

```yaml
owns:
  - The Adopted/Adapted/Designed source classification
  - The five-section architecture structure
publishes:
  - ArchitectureFrozen
consumes:
  - ConstitutionFrozen           # Architecture Ambition, and any Laws
                                   # constraining boundaries or folder structure
  - InvestigationFrozen          # domain-discovery, technical-architecture,
                                   # data-model, business-vision (for NFRs)
forbidden_dependencies:
  - Same domain-agnostic rule as OV-000/001/002: no project-specific
    boundaries, aggregates, or folder names in this protocol's own body.
    Worked runs belong in examples/.
```

---

### 3. Decision Layer

#### Why

Splitting Architecture from Technology Decisions (`OV-004`) mirrors the
founding conversation's own distinction: "why did we choose this
technology" is a different question from "what does the system look
like," and conflating them makes both harder to revise independently — a
tech-stack change (e.g. swapping databases) shouldn't require reopening
the boundary/ownership model, and vice versa.

#### Alternatives Considered

- **Re-derive architecture from scratch every time, ignore Discovery.**
  Rejected — wastes the M1 investigation work and risks contradicting
  findings that were already validated with the project owner.
- **Assume Discovery always exists.** Rejected — breaks for greenfield
  projects with only vision-tier evidence; the Adopted/Adapted/Designed
  split exists specifically to keep this protocol usable regardless of
  how much prior evidence exists.
- **Merge Architecture and Technology Decisions into one document.**
  Rejected per the M3 scoping decision — kept separate, matching `OV-004`.

#### Trade-offs

The three-way source classification adds a small amount of bookkeeping
(every section states its source) in exchange for the protocol working
identically whether given a mature reference codebase or nothing but an
idea.

#### Future Considerations

- No guidance yet on what happens when an `Adapted` revision is expensive
  enough that it should itself become an ADR (e.g. a Discovery-found
  monolith being forced into a Hybrid ambition might be a large rewrite,
  not a documentation change). Revisit if a real run surfaces this.

---

### 4. Validation Layer

#### Rules

- Every Service Boundary must state its source (Adopted/Adapted/Designed)
  and, if `Adopted`/`Adapted`, cite the `OV-001` investigation/claim it
  came from.
- No Service Boundary may violate a Constitution Law — if a boundary would
  require violating one, the conflict must be surfaced, not silently
  resolved in the boundary's favor.
- Folder Structure must be structurally consistent with the Constitution's
  Architecture Ambition (e.g. a Hybrid ambition requires one folder/module
  per bounded context, not a layered-by-technical-concern structure).

#### Checklists

**Definition of Done for Milestone M3 (Architecture half):**

- [ ] `OV-002`'s Constitution is Frozen for the target project (M2 must be
      complete first).
- [ ] All five sections drafted, each with a stated source.
- [ ] No section conflicts with a Constitution Law.
- [ ] At least one worked example exists under `examples/`, per `ADR-0002`.

#### Cross References

- `OV-001`, `OV-002` are `depends_on`.
- `OV-004` (Technology Decisions) is a sibling document — see there for
  how the technologies implementing this architecture are chosen.
- `ADR-0002` governs where this protocol's validation output may live.

#### Required Updates When This Changes

If the five-section structure changes, `examples/m3-architecture-jwel-
walkthrough.md` (once it exists) should be reconciled or explicitly
marked as authored against a prior protocol version.
