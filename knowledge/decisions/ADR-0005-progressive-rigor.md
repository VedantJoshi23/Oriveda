---
id: ADR-0005
title: Progressive Rigor — Only Frozen Specifications Win
version: 1.0.1
status: Frozen
owner: Architecture
reviewers:
  - Vedant
  - Oriveda AI
created: 2026-10-28
updated: 2026-10-28
milestone: M8
category: Decision
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
  - OV-008
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0001
  - ADR-0002
tags:
  - governance
  - lifecycle
  - principles
risk: High
complexity: Medium
---

# ADR-0005 — Progressive Rigor: Only Frozen Specifications Win

### Context

As written through M7, every protocol from `OV-002` onward gates its own
work on its upstream specifications being **Frozen**. `OV-003` requires a
Frozen Constitution, `OV-005` a Frozen `OV-002`–`OV-004`, `OV-007` a
Frozen `OV-002`/`OV-005`/`OV-006`, and each Feature Specification must be
Frozen before implementation begins. Read together, these rules make a
strict sequence: no code until the whole chain above it is Frozen.

Running M0–M8 end to end against a real target project showed two
things:

- **The method works.** Constitution Laws written in the abstract caught
  real violations once checked against code, and the confidence-tier
  discipline held up under audit.
- **The sequence is too slow, and it fails on contact.** Specs written
  before any code existed were the ones that turned out wrong. A
  Standard that read well in the abstract failed as soon as it met a real
  schema. Every "spec is stale" finding came from specs that had never
  been checked against an implementation. Freezing earlier did not make
  them more correct; it only made them more expensive to fix.

Meanwhile, real client requirements are often unclear at the start and
settle only as the product takes shape. A process that needs settled
requirements before any code cannot serve those projects. The options
are to fight that, or to build it into the method.

The constraint in the other direction is Principle 4: *documentation is
executable knowledge*, and the authoritative description of how a system
should behave. Dropping that would turn Oriveda into a documentation
generator, which defeats ADR-0001's premise. Any change has to keep a
clear answer to "when code and specs disagree, who wins?"

### Options Considered

- **Keep strict sequential freezing (status quo).** The authority rule
  is simple and the method has been validated. But it front-loads the
  specs most likely to be wrong, makes freezing a formality done before
  any proof exists, and cannot handle requirements that are discovered
  during the build.
- **Code wins; specs only describe it.** This is the fastest option and
  matches how most teams work in practice. But it abandons Principle 4,
  and with it the reason Oriveda exists. Decisions drift back into code
  and chat, which is exactly what Principle 2 says must not happen.
- **Freeze everything early, but make amendments cheap.** This keeps the
  sequence and allows fast revision. In practice it produces endless
  version bumps, and "Frozen" stops meaning settled: the authority rule
  survives in name only.
- **Progressive rigor (chosen).** Authority comes from lifecycle state,
  not from the fact that a document exists. Work starts on specs that
  are confident enough. Specs freeze once an implementation has proved
  them. Rigor scales with risk, using the `risk` field every spec
  already carries. This costs a new artifact (the divergence log) and
  the discipline to reconcile it.

### Decision

**Only Frozen specifications win.** When code disagrees with a Frozen
specification, the code is wrong. When code disagrees with a
specification that is not yet Frozen, that is a *divergence*. It must be
logged and reconciled, and either side may change, but it may never be
left unrecorded. Specifications freeze once an implementation has proved
them, not before any code exists, and the rigor required scales with
risk.

The rules that put this into practice:

**1. The authority rule (amends Principle 4).**

| Spec state | Code disagrees with it → |
| --- | --- |
| Frozen | The code is wrong. Fix the code, or revise the spec through its normal lifecycle (a version bump; only a Constitution also needs an ADR plus remediation statement, per `OV-002`). |
| Proposal / Draft / Architecture Review / Revision / Approved | A divergence. Log it (rule 4). Resolve it by changing the spec, the code, or both. |

Code never becomes the authority by default. A divergence nobody logged
counts as a defect, just as a silent violation of a Frozen spec does.

**2. Rigor tiers, set by the spec's `risk` field.**

| Tier | Typical content | Form | Must be Frozen before… |
| --- | --- | --- | --- |
| **High** | Constitution; data ownership and domain boundaries; auth, payments, anything security- or money-bearing; any decision that is costly to reverse | Full protocol output | …implementation of any slice that touches it starts |
| **Medium** | Most domain and feature specs; Standards | Full protocol output | …the first release that ships behavior it governs |
| **Low** | Routine features with no new invariants, no cross-domain flow and no High-tier dependency | **Spec card** (purpose, owning domain, acceptance criteria, open questions) | …the first release that ships it (a spec card can be Frozen in minutes) |

The agent proposes a tier when a spec enters Proposal, with a one-line
reason. The owner can override it. A spec may move up a tier at any
time, for example when a "Low" feature turns out to add an invariant. It
moves down only with the owner's explicit agreement. A target project's
Constitution is always High.

**3. Confidence gates replace Frozen gates for starting work.** A
vertical slice (one Feature Specification or spec card, owned by exactly
one domain, delivering user-visible behavior) may begin implementation
when:

- the target project's Constitution is Frozen;
- every High-tier spec on the slice's path is Frozen;
- every other spec the slice depends on is at least Draft, and the
  specific claims the slice relies on are at the Fact or Inference tier
  (≥60%, per `OV-000`) and the owner has acknowledged them; and
- assumption-tier claims (<60%) on the slice's path are listed in the
  slice's spec as open questions, not built on silently.

Protocol work (M1–M7) can proceed in parallel with implementation, and
can lag it, under the same rule.

**4. The divergence log.** Each target project keeps a log of
`DIV-NNN` entries. Each entry records the spec ID and section, what the
spec says, what the code does, where it was found (commit/PR), its
status (`open` / `spec-updated` / `code-fixed` / `both`), and the date
resolved. A change that introduces a divergence logs it in the same
change. A specification **cannot be Frozen while it has open
divergences**. Reconciling them is what freezing means under this ADR.

**5. Release checkpoint.** Before a release reaches production, every
spec covering shipped behavior is either Frozen or explicitly deferred.
A deferral is a dated Principle 7 shortcut entry that states why, the
risk, and when it will be reconciled. High-tier specs cannot be
deferred.

**6. Recommended sequencing: walking skeleton first.** For a new target
project, run M1–M7 at the minimum depth that one slice needs, build that
slice, and then deepen the specs with what the build taught. After that,
specs and code advance slice by slice. This is the default, not a rule.
A project with stable, well-evidenced requirements may still run the
protocols to full depth first.

**What does not change:** the lifecycle states themselves, metadata
frontmatter, the `OV-000` confidence engine, `OV-002`'s heavier bar for
amending a Frozen Constitution, "point, don't copy" (`OV-008`), and
ADR-0001 through ADR-0003.

### Consequences

- **Easier:** implementation can start as soon as the High-tier
  foundation is settled, which usually means the Constitution and domain
  boundaries. Requirements that emerge mid-build have a defined place to
  go (the divergence log, then a spec revision) instead of being either
  blocked or lost. Frozen specs carry more weight, because each one has
  been checked against a working implementation.
- **Harder:** the authority rule now depends on state. Agents and
  reviewers must check a spec's `status` before deciding which side is
  wrong. The divergence log is a new obligation, and it fails silently
  if people stop logging. `PRM-REVIEW` must check for unlogged
  divergences, or the rule loses its force.
- **Risk:** the tiering can be gamed by labelling specs "Low" to skip
  rigor. This is mitigated by the stated reason at Proposal, owner
  override, and the rule that a spec moves up the moment it touches an
  invariant or a High-tier dependency.
- **For whom:** target-project owners get earlier working software.
  The Oriveda agent takes on reconciliation as standing work, not a
  one-off review step.

### Required Updates

Applied in the same change that froze this ADR. Each protocol listed
was revised from v0.1.0 to v0.2.0:

- Root `README.md`: Principle 4 wording ("Frozen specifications are
  executable knowledge…"); the Specification Lifecycle section (freeze
  on proof; divergences block freezing); Getting Started (the
  walking-skeleton default).
- `OV-002` through `OV-008`: replace each "upstream is Frozen" checklist
  item with the rule-3 confidence gate. Keep "Frozen" only where the
  upstream spec is High tier. `OV-007`'s "Frozen before implementation
  begins" becomes tier-dependent.
- `OV-008`: `PRM-REVIEW` gains an unlogged-divergence check, and
  `PRM-FEATURE` loads Draft specs alongside Frozen ones, stating which is
  which.
- New `templates/spec-card-template.md` (the Low tier) and
  `templates/divergence-log-template.md`.
- `.oriveda/taxonomy.yaml`: a `DIV` prefix with `scope: project`.
  `.oriveda/glossary.yaml`: *divergence*, *rigor tier*, *slice*,
  *spec card*.
- `.oriveda/manifest.yaml`, `.oriveda/knowledge_graph.md`,
  `changelog/changelog.md`: register this ADR.

### Revisit Criteria

- **Too loose:** across a target project, open divergences routinely
  outlive two slices, or a release checkpoint repeatedly ends in
  deferrals rather than freezes. Either means reconciliation is not
  actually happening, and the gates should tighten.
- **Too tight:** High-tier freezes still routinely block slices for
  more than one working session. That means the High tier is drawn too
  wide.
- **Unclear authority:** reviewers or agents get the authority rule
  wrong (treating a Draft as binding, or overriding a Frozen spec from
  code). That means the state-dependent rule is too subtle to work as
  written.
- Re-evaluate in any case after the first two target projects have
  shipped a release under this ADR.

*v1.0.1 (2026-10-28), non-semantic (`ADR-0007` rule 3): the Frozen
row of rule 1 now says plainly that ADR-plus-remediation applies to a
Constitution only.*
