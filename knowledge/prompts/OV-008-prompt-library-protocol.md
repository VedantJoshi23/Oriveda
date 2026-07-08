# Metadata

```yaml
---
id: OV-008
title: M7 Prompt Library Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M7
category: Prompts
priority: High
depends_on:
  - OV-000
  - OV-001
  - OV-002
  - OV-003
  - OV-004
  - OV-005
  - OV-006
  - OV-007
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - prompts
  - protocol
risk: Medium
complexity: Low
---
```

## OV-008 — M7 Prompt Library Protocol

### 1. Human Layer

#### Purpose

`OV-000` through `OV-007` are full protocols — detailed enough for an
agent to follow directly, but too long to retype at the start of every
session. This protocol defines the compression layer: short, reusable
prompt templates that kick off a specific kind of session by *pointing
at* the right Frozen specs rather than re-explaining them. This is the
founding conversation's own observation formalized: once Constitution,
Architecture, and Domain context exist, a feature prompt becomes two or
three pages instead of thirty. M7 is where that shrinkage becomes a
reusable artifact instead of something re-invented per session.

#### Explanation

**A closed set, unlike M6.** Unlike Feature Specifications
(open-ended), the Prompt Library is a fixed catalog — one prompt per
prior milestone's protocol, plus one cross-cutting Review prompt. M7's
Definition of Done is full coverage of this catalog, similar to M5's
domain coverage requirement, not "protocol readiness" like M6.

**Catalog:**

| Prompt | Kicks off | Used |
| --- | --- | --- |
| `PRM-DISCOVERY` | `OV-000` + `OV-001` | Once per target project, at the start (see the bootstrapping note below). |
| `PRM-CONSTITUTION` | `OV-002` | Once per target project, after Discovery. |
| `PRM-ARCHITECTURE` | `OV-003` + `OV-004` | Once per target project, after the Constitution — revisited only via that protocol's own revision rules. |
| `PRM-STANDARDS` | `OV-005` | Once per target project initially; individual Standards can be added later without re-running the whole catalog. |
| `PRM-DOMAIN` | `OV-006` | Once per bounded context declared in `OV-003`. |
| `PRM-FEATURE` | `OV-007` | Repeatedly, for the life of the project — this is the workhorse prompt. |
| `PRM-REVIEW` | All Frozen specs for the target project | Repeatedly, on any change — the cross-cutting companion to `PRM-FEATURE`. |

**Common template shape**, every prompt follows this, carried over
directly from the founding conversation's own proposal:

```text
Context      — the specific Frozen spec IDs to load (never their content
                restated — point, don't copy, same discipline as every
                OV-00X document's own cross-referencing rule)
Task         — what to do, stated briefly, since Context does the
                heavy lifting
Constraints  — which Constitution Law IDs and Standard IDs bind this work
                (referenced by ID, not restated)
Expected
Deliverables — what artifact(s) this session should produce
Definition
of Done      — pulled from the relevant protocol's own DoD/exit criteria,
                not re-invented per prompt
```

**The bootstrapping case.** `PRM-DISCOVERY`'s Context section is
different in kind from the other six: for a brand-new target project,
there is no prior Frozen target-project spec to point to yet. Its Context
instead points to the Oriveda framework's own `OV-000`/`OV-001`
protocols directly — this is the one prompt in the catalog whose job is
to *start* the chain, not continue it.

**Point, don't copy — enforced here too.** A `PRM-FEATURE` prompt does
not restate a Domain Specification's invariants or a Constitution's Laws
inline; it cites their IDs and trusts the session to load them. This is
the same discipline `OV-003` through `OV-007` each enforced against
inventing new content at their own layer — M7 enforces it one layer
further out, at the point where a human or agent actually starts typing.

#### Examples

See `examples/m7-prompts-jwel-walkthrough.md` once drafted — expected to
exercise `PRM-FEATURE` against one of M6's dry-run features (Wishlist
Save, the simpler of the two), to check whether the compressed prompt is
actually sufficient to start real implementation work without the full
`OV-007` spec being retyped.

---

### 2. AI Layer

```yaml
owns:
  - The seven-prompt catalog
  - The common Context/Task/Constraints/Deliverables/DoD template shape
publishes:
  - PromptLibraryFrozen
consumes:
  - Frozen status of OV-000 through OV-007  # each prompt's Context section
                                              # depends on its corresponding
                                              # protocol already being usable
forbidden_dependencies:
  - Same domain-agnostic rule as the rest of the OV-00X series: no
    project-specific spec content restated inside a prompt template's own
    body — only spec IDs. Worked runs belong in examples/.
```

---

### 3. Decision Layer

#### Why

Every earlier protocol in this series produces a document meant to be
read once and referenced many times. Prompts are the opposite shape —
short, typed fresh each session — and conflating the two (e.g. asking
someone to paste `OV-007` into a chat window every time) defeats the
entire point of having built the earlier layers. A dedicated,
ID-referencing prompt format is what actually makes the foundation pay
off day to day.

#### Alternatives Considered

- **No separate prompt layer; users reference OV-00X docs directly each
  time.** Rejected — exactly the "retyping thirty pages" problem the
  founding conversation wanted to avoid; a protocol document is not
  optimized for being typed into a chat window repeatedly.
- **Prompts that restate relevant spec content inline for convenience.**
  Rejected — recreates the sync problem every other "point, don't copy"
  rule in this series exists to prevent; a restated Law that drifts from
  its source is worse than no restatement at all.
- **Open-ended prompt catalog, grown ad hoc per project.** Rejected —
  the seven-prompt catalog maps 1:1 onto already-fixed protocol
  boundaries (`OV-000` through `OV-007`); there's no reason for prompts
  to proliferate independently of the protocols they invoke.

#### Trade-offs

A fixed catalog means a genuinely novel session type (not covered by any
of the seven) has no ready-made prompt — acceptable, since anything not
covered by an existing protocol shouldn't have a compressed invocation
for it yet either.

#### Future Considerations

- `PRM-REVIEW`'s exact mechanics (how it selects which Standards/Laws are
  relevant to a given change) aren't designed in depth here — it inherits
  `OV-005`/`OV-007`'s relevance-checking logic by reference, but a
  worked example exercising `PRM-REVIEW` specifically hasn't been done
  yet; only `PRM-FEATURE` is dry-run in this milestone's examples.

---

### 4. Validation Layer

#### Rules

- Every prompt's Context section references spec IDs only — no restated
  spec content.
- Every prompt's Definition of Done is drawn from its corresponding
  protocol's own DoD/exit criteria, not independently invented.
- `PRM-DISCOVERY` is the only prompt permitted to point directly at
  Oriveda's own `OV-000`/`OV-001` rather than a target-project artifact,
  and only for a project with no prior Frozen specs.

#### Checklists

**Definition of Done for Milestone M7 (Prompt Library):**

- [ ] All seven prompts in the catalog are authored using the common
      template shape.
- [ ] Each prompt's Context section correctly maps to its corresponding
      protocol(s).
- [ ] No prompt restates spec content instead of referencing it by ID.
- [ ] At least one worked example exists under `examples/`, per `ADR-0002`,
      demonstrating a prompt is actually sufficient to start real work.

#### Cross References

- `OV-000` through `OV-007` are all `depends_on` — every prompt's Context
  section maps onto one or more of them.
- `templates/prompt-template.md` implements the common template shape.

#### Required Updates When This Changes

If the seven-prompt catalog or template shape changes, `templates/
prompt-template.md` and any already-produced target-project prompt usage
should be reconciled, or explicitly marked as authored against a prior
protocol version. If a future milestone (M8+) introduces a new protocol,
a corresponding prompt should be added to this catalog in the same spirit
— one prompt per protocol, not invented independently.
