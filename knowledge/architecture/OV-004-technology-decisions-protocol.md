# Metadata

```yaml
---
id: OV-004
title: M3 Technology Decisions Protocol
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
  - OV-002
  - OV-003
required_by: []
related_documents:
  - OV-003
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - architecture
  - technology
  - protocol
risk: Medium
complexity: Medium
---
```

## OV-004 — M3 Technology Decisions Protocol

### 1. Human Layer

#### Purpose

`OV-003` establishes *what* the system looks like — boundaries, domain
model, event flow. This protocol establishes *why each technology
implementing it was chosen* — deliberately not "what technologies are we
using," which is just a list. A stack list goes stale the moment someone
asks "could we swap X?" and there's no recorded reasoning to answer with.

#### Explanation

**The stack-freedom question.** Before any technology gets chosen, the
target project's owner answers one question — this is the fourth
owner-choice question, alongside `OV-002`'s three, and for the same
reason: it isn't inferable from evidence.

| Option | Description |
| --- | --- |
| Full autonomy | The agent evaluates current industry standards and chooses per layer, justifying each. |
| Partial autonomy | Owner specifies some technologies; agent chooses the rest. |
| Fixed stack | Owner provides the complete stack; agent must use only those. |
| Hybrid (recommended) | For each layer, agent compares 2–3 production-grade options with trade-offs, recommends one, and waits for approval before proceeding. |

Recommended default is **Hybrid** — it forces trade-off reasoning before
commitment without the overhead of a fully owner-specified stack. This
mirrors the founding conversation's own Question 2, where Hybrid (there
called option D) was the protocol's recommendation, even though the actual
project owner chose Full-autonomy-with-constraints instead. Both are valid
answers; the point is that the question gets asked explicitly, not
defaulted silently.

**Constraint preferences**, asked alongside the stack-freedom question
(not assumed, but commonly answered "yes" — offer as a default, don't
hardcode as universal): prefer free/open-source, well-maintained,
industry-standard technologies with active communities; avoid vendor
lock-in where practical; prefer self-hostable options when mature.

**One entry per significant choice, not a flat list.** For every layer
identified by `OV-003` needing a technology (frontend framework, backend
framework, primary datastore, search/cache if the architecture needs one,
hosting/cloud, CI/CD, and any domain-specific infra like payments or
email), record a decision using `templates/decision-template.md`:
Context, Options Considered (with real trade-offs, not a strawman),
Decision, Consequences, Revisit Criteria. This is deliberately the same
shape as an Oriveda framework ADR — a target project's technology
decisions are its own ADR series, numbered independently of Oriveda's own
`ADR-0001`/`ADR-0002` (which govern the framework, not any product).

**Where these decisions live.** Per `ADR-0002`, a target project's
technology-decision ADRs are that project's own artifacts — in a
consuming project's own `decisions/` folder once that separation exists,
or in `examples/` for a validation dry-run. They do not join Oriveda's own
`knowledge/decisions/` ADR series.

#### Examples

See `examples/m3-technology-decisions-jwel-walkthrough.md` once drafted.

---

### 2. AI Layer

```yaml
owns:
  - The stack-freedom question and its four options
  - The one-ADR-per-significant-choice convention
publishes:
  - TechnologyDecisionFrozen   # per individual technology ADR
consumes:
  - ArchitectureFrozen          # OV-003; determines which layers need a decision
  - ConstitutionFrozen          # rigor level bears on how much trade-off
                                  # documentation each decision needs
forbidden_dependencies:
  - Same domain-agnostic rule as the rest of the OV-00X series: no
    specific technology names are prescribed by this protocol itself.
    Worked runs belong in examples/.
```

---

### 3. Decision Layer

#### Why

Recording *why* rather than *what* is the entire value of this protocol —
a stack list is reconstructable from `package.json`/`go.mod`/whatever at
any time; the reasoning behind it is not, once forgotten.

#### Alternatives Considered

- **One combined "Tech Stack" document, no per-choice ADRs.** Rejected —
  loses the ability to revisit and supersede a single decision (e.g.
  "why Postgres") independently of the rest of the stack.
- **Skip the stack-freedom question, always assume full autonomy.**
  Rejected — some target projects will have real constraints (existing
  team expertise, existing infra) that full autonomy would ignore.

#### Trade-offs

Per-decision ADRs are more files than a single stack list, but each is
independently supersedable, matching how technology choices actually
change over a project's life — one at a time, not all together.

#### Future Considerations

- No guidance yet on how many "significant" choices is too many for a
  small project — revisit if a real run produces an unwieldy number of
  micro-ADRs for trivial choices (e.g. a linter config probably doesn't
  need one).

---

### 4. Validation Layer

#### Rules

- The stack-freedom question must be answered before any technology
  decision is drafted.
- Every technology decision must use the decision-template shape (Context,
  Options Considered with real trade-offs, Decision, Consequences, Revisit
  Criteria) — a bare "we chose X" is not sufficient.
- A technology decision may not contradict a Constitution Law (e.g. a
  choice that makes boundary-enforcement unenforceable would violate a
  Law-1-style rule).

#### Checklists

**Definition of Done for Milestone M3 (Technology half):**

- [ ] `OV-003`'s architecture is Frozen (layers needing decisions are known).
- [ ] Stack-freedom question and constraint preferences answered.
- [ ] One decision entry per significant layer, each Frozen.
- [ ] At least one worked example exists under `examples/`, per `ADR-0002`.

#### Cross References

- `OV-003` is `depends_on` — determines which layers need a decision.
- `OV-002` is `depends_on` — rigor level and any relevant Laws.
- `templates/decision-template.md` is the shape every entry follows.

#### Required Updates When This Changes

If the stack-freedom question's options change, reconcile against any
already-produced technology decisions or mark them as authored against a
prior protocol version.
