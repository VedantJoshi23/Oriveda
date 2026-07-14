---
id: OV-000
title: Knowledge Acquisition Specification
version: 0.1.1
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
depends_on: []
required_by:
  - OV-001
related_documents: []
related_domains: []
related_features: []
related_decisions: []
tags:
  - discovery
  - evidence
  - protocol
risk: Medium
complexity: Medium
---

# OV-000 — Knowledge Acquisition Specification

## 1. Human Layer

### Purpose

Before Oriveda can reverse-engineer a product (M1 Discovery), it needs to
know what evidence about that product actually exists. Not every user
starting a project has a Git repository. Some have only an idea, a PRD, a
Figma file, screenshots of a competitor, or a video demo. This specification
defines how the Oriveda agent inventories available evidence, extracts
knowledge claims from it with explicit confidence, and decides — without
guessing or asking generic questions — what evidence is still worth
requesting before Discovery begins.

Knowledge Acquisition is a gate, not a formality: M1 Discovery should not
start investigating a topic until Knowledge Acquisition has established what
evidence that topic can even be answered from.

### Explanation

**Where this sits in the pipeline:**

```text
Knowledge Acquisition   (this document)
        ↓
Evidence Collection      (ongoing, append-only evidence log)
        ↓
Reverse Engineering      (per-evidence-type pipelines, below)
        ↓
Knowledge Synthesis      (claims roll up into M1 investigations)
        ↓
Specification Authoring  (OV-001 Discovery Report, and onward)
```

**The Knowledge Inventory.** The agent maintains a checklist of evidence
categories. This is presented to the user once, up front, and re-checked
whenever a gap blocks a specific investigation. It is not a form the user
must fill out exhaustively — most projects will have partial coverage, and
that's expected.

| Category | Examples |
| --- | --- |
| Vision | Product idea, business vision, PRD, user stories, mission statement |
| Existing Product | Git repository, live website/app, backend, API, database |
| UX | Figma, screenshots, mockups, videos, user recordings, design system |
| Technical | Infrastructure, CI/CD, deployment, cloud provider, auth |
| Business | Competitors, existing customers, pricing, analytics, support tickets, feature requests |

**Evidence Pipelines.** Each evidence *type* has a distinct extraction
strategy — you don't read a video the way you read source code. When new
evidence is logged, the agent applies the matching pipeline:

| Evidence type | Pipeline output |
| --- | --- |
| Repository | Architecture, module boundaries, inferred business rules |
| Screenshots / mockups | UI components, design language, partial user flow |
| Video | Interaction flow, feature inventory, workflow sequence |
| Figma | Component inventory, navigation, design tokens, responsive rules |
| API (OpenAPI/Postman/etc.) | Contracts, resource model, auth scheme |
| Database schema | Entities, relationships, inferred constraints |
| Competitor site/app | Feature benchmarks, business-model hints (low confidence — external inference only) |
| Vision docs / conversation | Goals, constraints, non-negotiables, prior decisions |

Every pipeline produces **knowledge claims**, not prose summaries. A claim is
a single, atomic assertion with a confidence score and a pointer back to the
evidence it came from (see `.oriveda/schemas/evidence.schema.yaml`). This is
what makes Discovery evidence-driven instead of assumption-driven.

**The Confidence Engine.** Every claim is tagged:

- **Fact** (90–100%) — directly observed, no interpretation.
- **Inference** (60–89%) — reasonably derived, but not certain.
- **Assumption** (0–59%) — should not be treated as settled.

When two pieces of evidence produce conflicting or reinforcing claims about
the same thing, the higher-confidence claim wins, but the lower-confidence
one is kept (marked `superseded_by`) rather than deleted — Principle 1
("knowledge outlives implementation") applies to superseded claims too.

**Gap detection, not generic questions.** The agent must never ask "tell me
about your product" style questions. Instead, before asking anything, it:

1. Computes which of the ten M1 investigations (repo-structure,
   business-vision, feature-inventory, user-journeys, data-model,
   domain-discovery, technical-architecture, hidden-business-rules,
   technical-debt, recommendations) currently have zero or low-confidence
   claims.
2. Ranks those gaps by how much they block downstream work — e.g. a gap in
   `user-journeys` blocks Discovery entirely if no UX evidence exists at
   all; a gap in `technical-debt` might not block anything yet.
3. Asks for the *single specific artifact* that would close the
   highest-ranked gap, and says why. Example (from the reference case in
   this repo's own evidence log): *"I can infer the architecture from the
   repository at 95%+ confidence. The largest gap is user-journeys — no UX
   evidence has been supplied. If you have the screenshot you mentioned
   pasting into Untitled-1, please re-share it; otherwise a couple of key
   screens or a short walkthrough would unblock that investigation."*

### Examples

See `knowledge/discovery/evidence/README.md` for the evidence log
mechanism in use — it currently holds only `EVD-001` (meta-evidence about
Oriveda's own design, from the founding conversation) plus a note on the
gap-detection protocol flagging that no target-project evidence has been
processed yet. This log is scoped per target project: when Oriveda is
pointed at an actual product to discover, that project's evidence gets its
own `EVD-NNN` sequence here — this file does not accumulate one
project's data across unrelated future uses.

---

## 2. AI Layer

```yaml
owns:
  - Knowledge Acquisition protocol
  - Evidence log schema
  - Gap-detection algorithm (informal, described above)
publishes:
  - EvidenceReceived      # logged whenever new evidence is added
  - KnowledgeClaimAdded   # logged whenever a claim is extracted
consumes: []
forbidden_dependencies:
  - This log, schema, and protocol must remain domain-agnostic — no
    product-specific evidence, terminology, or tech-stack detail may be
    hardcoded into OV-000, the evidence schema, or their templates. Any
    target project's evidence belongs only in that project's own
    EVD-NNN entries, never in this specification's body.
```

---

## 3. Decision Layer

### Why

The original M1 plan (see the founding conversation, `EVD-001`) assumed the
starting point would always be a Git repository. That's the exception, not
the rule, for a domain-agnostic framework: most future projects using
Oriveda will start from partial, mixed-type evidence. Building the gap-aware
acquisition step now — rather than retrofitting it after M1 is written
around "repository" as the sole input — keeps M1 Discovery reusable.

### Alternatives Considered

- **Skip this phase; let Discovery ask ad hoc questions.** Rejected —
  produces exactly the "random questions" failure mode called out in the
  founding conversation, and gives no traceability from claim back to
  source evidence.
- **Require a fixed evidence checklist before Discovery can start.**
  Rejected — too rigid; most real projects have partial evidence and
  Discovery should proceed with what's available plus honestly-labeled
  confidence, not block on completeness.
- **Store evidence/claims only in prose docs, no schema.** Rejected —
  violates Principle 5 (humans and AI consume the same knowledge); without
  a minimal machine-readable shape, gap detection can't be computed, only
  guessed at.

### Trade-offs

Adds one more artifact type (`evidence.schema.yaml`) and one more folder
(`knowledge/discovery/evidence/`) to maintain. In exchange, every downstream
Discovery claim is traceable to its source and confidence, which the
founding conversation identified as a differentiator most AI-assisted
workflows lack.

### Future Considerations

- The evidence log is currently a single markdown file with embedded YAML
  blocks. If evidence volume grows large (dozens of items), consider
  splitting into one file per `EVD-NNN` under `evidence/items/`. Not needed
  yet — premature at two entries.
- `pipeline` extraction logic here is described narratively, not automated.
  Automating it (e.g. a script that reads a repository and pre-populates
  claims) is plausible future tooling but out of scope for this spec.
- Confidence bands (90/60/0) are a starting heuristic, not derived from
  data. Revisit if they prove miscalibrated in practice.

---

## 4. Validation Layer

### Rules

- No knowledge claim may be added to the evidence log without an
  `evidence_ids` pointer to at least one logged evidence item.
- No claim may be marked `fact` (≥90% confidence) unless directly observed
  in evidence; claims derived by reasoning are capped at `inference`.
- The agent must not proceed to write M1 investigation content for an area
  where every claim is `assumption`-tier without first surfacing that gap
  to the user.

### Checklists

**Exit criteria — Knowledge Acquisition is "enough" to enter M1 Discovery
when:**

- [ ] At least one evidence item has been logged.
- [ ] Every one of the ten M1 investigation areas has either (a) at least
      one `fact`- or `inference`-tier claim, or (b) an explicit, visible gap
      entry explaining why it doesn't yet.
- [ ] Any gap that would materially change Discovery's conclusions has been
      surfaced to the user at least once (not necessarily resolved).

No target project's evidence has been processed against this checklist
yet — see `knowledge/discovery/evidence/README.md`. This is expected: this
framework repository's evidence log only holds meta-evidence about
Oriveda's own design (`EVD-001`). Exit criteria get evaluated per target
project, the first time this protocol is actually pointed at one.

### Cross References

- `OV-001` (M1 Discovery Protocol) is `required_by` this spec — it consumes
  the evidence log's claims as its primary input. Note `OV-001` is itself a
  reusable protocol, not a per-project Discovery Report; per-project output
  lives in `examples/` or a consuming project, not in `knowledge/` (see
  `ADR-0002`).
- `.oriveda/schemas/evidence.schema.yaml` defines the data shape this
  document's protocol produces.
- `templates/document-template.md` is the base this document was authored
  from.

### Required Updates When This Changes

If the investigation list, confidence bands, or evidence type taxonomy
change here, `.oriveda/schemas/evidence.schema.yaml` and any already-logged
evidence entries using the old taxonomy must be updated in the same change.
