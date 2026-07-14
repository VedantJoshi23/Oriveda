---
id: OV-002
title: M2 Constitution Protocol
version: 0.1.0
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-07-08
updated: 2026-07-08
milestone: M2
category: Constitution
priority: Critical
depends_on:
  - OV-001
required_by: []
related_documents:
  - OV-000
  - OV-001
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - constitution
  - protocol
  - governance
risk: High
complexity: Medium
---

# OV-002 — M2 Constitution Protocol

### 1. Human Layer

#### Purpose

M1 Discovery produces ten investigations' worth of Keep/Improve/Remove
recommendations about a target project. Left as-is, that's a pile of
opinions with no binding force. M2 turns the highest-value subset of those
recommendations — plus a small number of choices only a human can make —
into a small set of **non-negotiable rules** that every later milestone
(Architecture, Standards, Domains, Features, Implementation) must satisfy.

Like `OV-000` and `OV-001`, this is a **protocol** describing how any
target project's Constitution gets authored — not a specific project's
Constitution itself. A produced Constitution is a per-project artifact; see
`ADR-0002` for where per-project output belongs (a consuming project, or
`examples/` for a validation dry-run).

This document does not duplicate Oriveda's own 8 Principles (in
`README.md`) — those govern how Oriveda's *specifications* get written and
apply to every project unconditionally. A target project's Constitution is
a different, narrower thing: it governs how *that project's engineering*
gets done, and different target projects will reasonably choose different
constitutions.

#### Explanation

**Inputs, not a blank page.** A Constitution is not invented from
scratch. It's derived from two sources:

1. **M1's investigations** (see `OV-001`) — primarily the `recommendations`
   synthesis's Keep items (candidate Constitution rules), Improve items
   (candidate rules with a stated migration path), and Remove items
   (inform what the Constitution should explicitly prohibit). But a
   specific finding buried in any individual investigation — most often
   `hidden-business-rules` — can also be a valid Law source in its own
   right, if it meets the promotion bar below, even if it wasn't
   independently surfaced as a Keep item in the `recommendations` rollup.
   A hidden rule found once should not have to wait to be re-surfaced by
   synthesis before it can be made explicit.
2. **A short, fixed set of choices only the target project's owner can
   make** — these were not derivable from evidence in the founding
   conversation, and won't be derivable from evidence for any future
   project either:

   | Choice | Options | Why it can't be inferred |
   | --- | --- | --- |
   | Engineering rigor level | Production-grade / Enterprise-grade / FAANG-level discipline | Trades velocity against ceremony (ADRs-per-change, RFC process, formal threat modeling); a resourcing and risk-appetite decision, not a technical one. |
   | AI collaboration mode | Code Generator / Senior Engineer / Principal Engineer (technical partner) | Defines how much the agent should challenge vs. execute requests; a working-relationship preference. |
   | Architecture ambition | Monolith / Modular Monolith / Hybrid (monolith now, event-contracts for future extraction) / Microservices | A team-size and growth-trajectory bet, not something discoverable from a reference codebase. |

   These three map directly to Questions 2–5 from Oriveda's own founding
   conversation — generalized here into a reusable interview rather than
   one-off questions asked only once.

**Not every Keep recommendation becomes a Law.** A Constitution rule
should be something that would be expensive or dangerous to violate
silently — not every good practice deserves "non-negotiable" status. The
bar: would violating this rule, if discovered six months later, require
non-trivial rework to fix? If yes, it's a candidate Law. If it's just good
practice worth following but survivable if occasionally skipped, it
belongs in a future Standard (M4), not the Constitution.

**Constitution structure.** Every target project's Constitution follows
this shape (see `templates/constitution-template.md`):

```text
1. Engineering Philosophy    — one or two paragraphs, the project's own
                                 version of "what does good mean here"
2. Rigor Level                — which of the three, and what that concretely
                                 includes/excludes (mirroring the founding
                                 conversation's explicit A/B/C breakdown)
3. AI Collaboration Contract  — which mode, and what it obligates the agent
                                 to do (challenge weak requests, preserve
                                 boundaries, etc.)
4. Architecture Ambition      — which of the four, stated plainly
5. Laws                       — the actual numbered, non-negotiable rules,
                                 each traceable back to a Discovery
                                 recommendation or an explicit owner choice
6. Amendment Process          — see Lifecycle below
```

**Lifecycle — higher bar than ordinary specifications.** Ordinary
specifications freeze via the standard Proposal → Draft → Review →
Approved → Frozen cycle. A Constitution uses the same states, but revising
a *Frozen* Constitution additionally requires: (a) an ADR justifying the
change, and (b) an explicit statement of what existing work becomes
non-compliant and needs remediation. This is intentionally heavier than
`OV-000`/`OV-001`'s own revision bar (which only required a version bump)
— the Constitution is supposed to be the thing everything else is checked
against, so it should not drift casually.

#### Examples

No worked example exists yet — see `examples/README.md` for the sandbox
rules a future worked example must follow (source material must be safe
to publish, e.g. synthetic data or an open-source project).

---

### 2. AI Layer

```yaml
owns:
  - The Constitution structure (six sections above)
  - The Keep-recommendation-to-Law promotion criterion
  - The three fixed owner-choice questions and their option sets
publishes:
  - ConstitutionFrozen   # logged when a target project's Constitution is frozen
consumes:
  - InvestigationFrozen   # specifically the recommendations investigation from OV-001
forbidden_dependencies:
  - Same domain-agnostic rule as OV-000/OV-001: no project-specific Laws,
    rigor-level answers, or architecture choices may be hardcoded into this
    protocol's own body. Worked runs belong in examples/.
```

---

### 3. Decision Layer

#### Why

The founding conversation's Questions 2, 4, and 5 (tech stack freedom,
rigor level, agent behavior mode) were asked once, informally, in prose.
Generalizing them into a fixed interview here means every future target
project gets the same deliberate choice-making instead of the agent
silently assuming defaults or re-inventing the question set each time.

#### Alternatives Considered

- **Let the Constitution be entirely derived from Discovery, no owner
  interview.** Rejected — rigor level and AI collaboration mode are
  genuinely not inferable from a codebase; guessing them risks building
  the wrong kind of partnership with the project owner from the start.
- **Skip formalizing a promotion criterion; let every Keep recommendation
  become a Law.** Rejected — produces Constitution bloat and devalues the
  "non-negotiable" label. Not every good pattern needs the heaviest
  governance tier.
- **Use the same revision bar as ordinary specifications.** Rejected — a
  Constitution that can be casually revised isn't functioning as a
  constitution; the explicit ADR-plus-remediation-statement requirement is
  the actual mechanism that keeps it meaningful.

#### Trade-offs

The heavier revision bar means Constitution changes are slower and more
deliberate than other specification changes. That's the intended
trade-off — velocity is meant to live in `OV-001`-derived investigations
and later Standards, not in whether the Constitution itself is stable.

#### Future Considerations

- The three fixed owner-choice questions may not be exhaustive forever. If
  a future target project surfaces a fourth recurring question that
  can't be derived from evidence, add it to the table in the same
  disciplined way — don't let ad hoc questions creep back in per project.
- Nothing here yet defines what happens if a target project's Discovery
  recommendations actively conflict with the owner's stated rigor-level
  choice (e.g. Keep-recommendations that assume heavy process, but owner
  picks Production-grade). Revisit once a real run surfaces this, per the
  same "don't design in the abstract" approach used in `OV-001`.

---

### 4. Validation Layer

#### Rules

- No Law may be added to a Constitution without a traceable source: either
  an `OV-001` recommendation, a specific finding from any individual
  investigation (investigation + claim IDs cited either way), or an
  explicit owner-choice answer.
- The three owner-choice questions must be asked and answered before a
  Constitution can be marked Draft-complete; none may be silently
  defaulted.
- A Frozen Constitution may not be edited without an accompanying ADR and
  remediation statement (see Lifecycle above).

#### Checklists

**Definition of Done for Milestone M2 (Constitution):**

- [ ] `OV-001`'s `recommendations` investigation exists and is Frozen for
      the target project (M1 must be complete first).
- [ ] All three owner-choice questions asked and answered.
- [ ] Constitution drafted using the six-section structure, reviewed, and
      Frozen.
- [ ] Every Law traces to a specific source (recommendation or owner
      choice) — no orphan Laws.
- [ ] At least one worked example exists under `examples/`, per `ADR-0002`.

#### Cross References

- `OV-001` is `depends_on` — the Constitution's Laws are sourced from its
  `recommendations` investigation.
- `ADR-0002` governs where this protocol's validation output may live.
- `templates/constitution-template.md` (to be authored alongside the first
  worked example) implements the six-section structure described above.

#### Required Updates When This Changes

If the Constitution structure (the six sections) or the owner-choice
question set changes, `templates/constitution-template.md` and any
already-produced target-project Constitutions should be reconciled in the
same change, or explicitly marked as authored against a prior version of
this protocol.
