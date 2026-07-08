# Metadata

```yaml
---
id: OV-001
title: M1 Discovery Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M1
category: Discovery
priority: Critical
depends_on:
  - OV-000
required_by: []
related_documents:
  - OV-000
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - discovery
  - investigation
  - protocol
risk: Medium
complexity: Medium
---
```

## OV-001 — M1 Discovery Protocol

### 1. Human Layer

#### Purpose

`OV-000` establishes what evidence exists and extracts atomic knowledge
claims from it. This document defines what happens next: how those claims
get organized, interpreted, and turned into a trustworthy understanding of
a target product — without ever assuming, and without writing a 100-page
document nobody will read.

Like `OV-000`, this is a **protocol**, not a report. It is written once,
here, and reused unmodified for every product Oriveda is ever pointed at.
The actual output of running this protocol against a real product — the
Discovery Report itself — is a per-project artifact, not a framework
specification. It does not live in `knowledge/`; see `ADR-0002` for why.

#### Explanation

**The ten investigations.** Discovery is split into ten fixed areas, not
one undifferentiated pass over "the product." Each has its own focus and
its own exit condition. These slugs are the same ones already used by
`.oriveda/schemas/evidence.schema.yaml`'s `investigation` field — every
knowledge claim logged under `OV-000` already declares which investigation
it belongs to, so this protocol's job is largely to synthesize claims that
already exist, not to go looking for new ones from scratch.

| Slug | Investigation | Answers |
| --- | --- | --- |
| `repo-structure` | Repository Structure | How is the code/asset organization arranged? What patterns and anti-patterns exist? |
| `business-vision` | Business Vision | What business is this? Who is it for? What problem does it solve? |
| `feature-inventory` | Feature Inventory | What capabilities exist today, fully or partially? |
| `user-journeys` | User Journeys | How do customers and admins actually move through the product? |
| `data-model` | Data Model | What are the core entities, aggregates, and relationships? |
| `domain-discovery` | Domain Discovery | What are the bounded contexts? Who owns what? |
| `technical-architecture` | Technical Architecture | What architectural style, stack, and patterns are in play? |
| `hidden-business-rules` | Hidden Business Rules | What rules are implicit in the implementation but never stated? |
| `technical-debt` | Technical Debt | What's fragile, deferred, or would bite a future team? |
| `recommendations` | Recommendations | What should Oriveda preserve, improve, or discard going forward? |

**The investigation template.** Every investigation, regardless of topic,
is written to the same shape:

```text
Purpose             — what this investigation is trying to establish
Observed Facts      — claims at fact-tier (from OV-000's evidence log)
Interpretation      — what those facts imply, stated as interpretation, not fact
Hidden Assumptions  — where the interpretation is doing work the evidence didn't
Strengths           — what's working, worth keeping
Weaknesses          — what's fragile, worth changing
Questions           — anything genuinely unresolved after the evidence is exhausted
Recommendations     — Keep / Improve / Remove, one line each
Confidence Level    — rolled up from the underlying claims (see OV-000 §1)
```

This mirrors `OV-000`'s fact/inference/assumption distinction on purpose:
an investigation is not allowed to quietly upgrade an assumption into a
stated fact just because it's now inside a tidier document.

**Per-investigation lifecycle.** Each of the ten investigations moves
through its own small cycle before the next one starts:

```text
Draft investigation (from evidence log claims)
        ↓
Discussion               — user confirms/corrects interpretation
        ↓
Revision
        ↓
Architecture Review       — does this hold up? does it contradict another investigation?
        ↓
Freeze
        ↓
Next investigation
```

No investigation takes more than one focused session. Investigations are
frozen individually — Discovery as a whole doesn't wait for all ten before
any of them can be trusted.

**Cross-investigation questions.** An investigation will sometimes surface
a question that only another investigation's scope can resolve (e.g. a
`repo-structure` pass notices a naming mismatch that can only be settled by
reading source the way `technical-architecture` does). When this happens,
the question is logged in the current investigation's `Questions` section
as normal, but tagged with which investigation it actually belongs to. It
does not block the current investigation from freezing, and it does not
get silently answered outside its proper scope — it gets picked up when
that later investigation runs.

**Role split** (carried over unchanged from the founding conversation):
the agent analyzes evidence, infers patterns, flags assumptions, and drafts
each investigation; the human confirms whether the interpretation matches
reality, supplies context the evidence can't contain, and approves or
redirects recommendations.

**Definition of Done for M1** is in the Validation Layer below.

#### Examples

No worked example exists yet. The first run of this protocol should be
recorded as a walkthrough in `examples/` (see `ADR-0002`) — likely starting
with `repo-structure`, since `OV-000`'s evidence log already has repository
evidence available to draw on once a target project is chosen.

---

### 2. AI Layer

```yaml
owns:
  - The ten-investigation structure and per-investigation template
  - The per-investigation lifecycle (Draft → Discussion → Revision → Review → Freeze)
publishes:
  - InvestigationFrozen   # logged whenever one of the ten investigations is frozen
consumes:
  - KnowledgeClaimAdded   # from OV-000; an investigation cannot be drafted for
                           # a topic with zero claims logged against it
forbidden_dependencies:
  - Same domain-agnostic rule as OV-000: this document's own body must
    contain no project-specific facts. Worked runs belong in examples/.
```

---

### 3. Decision Layer

#### Why

The founding conversation's original instinct — one large Discovery
Report — was explicitly revised there into ten smaller investigations,
each independently reviewable and freezable. Keeping that structure here
(rather than collapsing back to one document) is what makes Discovery
tractable for large or messy target projects: a weak signal in
`technical-debt` doesn't have to block freezing `business-vision`.

#### Alternatives Considered

- **One consolidated Discovery Report, single pass.** Rejected — reviving
  the "100-page document nobody reviews carefully" failure mode the
  founding conversation specifically wanted to avoid.
- **Investigations without a fixed template.** Rejected — inconsistent
  shape across ten documents makes them hard to compare and makes
  automation (e.g. a future knowledge-graph tool) much harder to build.
- **Skip per-investigation review; review the whole Discovery Report at the
  end.** Rejected — defers catching a wrong interpretation until after
  nine other investigations may have already built on top of it.

#### Trade-offs

Ten smaller review cycles cost more total interaction than one big
document dumped at the end. In exchange, each investigation is
independently trustworthy and independently revisable without reopening
the whole Discovery phase.

#### Future Considerations

- The investigation list (ten areas) is fixed here as a starting set. If a
  future target project surfaces a need for an eleventh recurring
  investigation area, add it here and to `evidence.schema.yaml`'s
  `investigation` enum in the same change (see Required Updates below) —
  don't invent one-off investigation types per project.
- Nothing here yet defines how conflicting investigations (e.g.
  `domain-discovery` implying something `data-model` contradicts) get
  resolved. Revisit once a real run surfaces an actual conflict — not
  worth designing in the abstract.

---

### 4. Validation Layer

#### Rules

- No investigation may be drafted for a topic with zero logged knowledge
  claims (`OV-000` gap-detection should have already surfaced this before
  Discovery starts).
- An investigation's `Confidence Level` may not exceed the confidence of
  its weakest load-bearing claim — synthesis cannot manufacture certainty
  the underlying evidence doesn't have.
- No investigation may be marked Frozen without the per-investigation
  lifecycle's Discussion and Architecture Review steps having occurred.

#### Checklists

**Definition of Done for Milestone M1 (Discovery):**

- [ ] `OV-000` exit criteria met for the target project (all ten
      investigation areas have at least fact/inference-tier claims or an
      explicit surfaced gap).
- [ ] All ten investigations drafted, discussed, and Frozen.
- [ ] Each investigation's Recommendations (Keep/Improve/Remove) captured
      and available to inform M2 Constitution and M3 Architecture.
- [ ] At least one worked example of this protocol exists under
      `examples/`, per `ADR-0002`.

#### Cross References

- `OV-000` is `depends_on` — this protocol consumes its evidence log and
  knowledge claims directly; it does not re-derive evidence itself.
- `ADR-0002` governs where this protocol's validation output may live.
- `.oriveda/schemas/evidence.schema.yaml`'s `investigation` enum must stay
  in sync with the ten-investigation table above.

#### Required Updates When This Changes

If the investigation list changes (added, removed, renamed), update in the
same change: `.oriveda/schemas/evidence.schema.yaml`'s `investigation`
enum, and any already-logged knowledge claims in any evidence log that
reference the old slug.
