# Evidence Log

This folder holds the running record of evidence supplied by the user and the
knowledge claims extracted from it, per `OV-000 — Knowledge Acquisition
Specification`. Structure follows `.oriveda/schemas/evidence.schema.yaml`.

Each entry below is one evidence item. New evidence gets appended with the
next `EVD-NNN` id; it is never renumbered or deleted, only marked
`superseded_by` if a claim it produced is later revised.

---

## EVD-001

```yaml
id: EVD-001
type: vision
source: Complete_chat.md (ChatGPT conversation, saved 2026-07-08)
received: 2026-07-08
summary: >
  Founding design conversation for Oriveda itself. Not evidence about the
  jewelry product — evidence about the framework's own philosophy, naming,
  structure, and lifecycle. Captures the decision to build a "Knowledge
  Acquisition" phase ahead of Discovery.
pipeline: vision
processed: true
claims:
  - id: KC-001
    statement: >
      Oriveda is designed to be domain-agnostic; the jewelry platform is its
      first implementation, not its purpose.
    status: fact
    confidence: 100
    evidence_ids: [EVD-001]
    investigation: business-vision
  - id: KC-002
    statement: >
      The user wants the in-editor agent to accept any evidence type (idea,
      repo, Figma, screenshots, video, competitor site, API, DB schema —
      not just a Git repository) and only ask for evidence that closes a
      specific, material gap.
    status: fact
    confidence: 100
    evidence_ids: [EVD-001]
    investigation: recommendations
```

---

## Investigation Coverage

This is a **generic evidence log mechanism**, meant to be populated once
per target project (not once per Oriveda framework checkout). Right now it
holds only `EVD-001`, which is meta-evidence about Oriveda's own design —
not evidence about any product Oriveda will be used to build.

No product/target-project evidence has been processed yet. `jwel-main.zip`
was supplied only as background material for the ChatGPT conversation that
designed Oriveda (`EVD-001`'s source) — it was never intended as the first
real subject of Discovery, and an earlier pass in this session mistakenly
ran the repository pipeline against it and wrote 14 jewelry-specific
claims here. Those have been reverted per explicit instruction: this
framework repository should not carry any one product's discovery data,
so that the same mechanism can be run again unmodified against a
completely different target repository/domain later.

Per OV-000's exit checklist, entering M1 Discovery for an actual target
project requires processing that project's own evidence through this same
log — using a fresh `EVD-NNN` sequence scoped to that project — not
reusing anything logged here.

## Open Gaps (per OV-000 gap-detection protocol)

- **No target-project evidence exists yet.** This log currently only
  demonstrates the mechanism's shape via `EVD-001`. The first real use of
  this protocol should begin with whatever evidence exists for the actual
  project Oriveda is being pointed at — repository, PRD, Figma, screenshots,
  etc. — following the Knowledge Inventory categories in OV-000 §1.
