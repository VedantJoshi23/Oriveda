---
id: ADR-0007
title: Adopting Oriveda Upgrades — Obligations, Grandfathering and Honest History
version: 1.0.0
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
  - ADR-0003
  - ADR-0004
  - ADR-0005
  - ADR-0006
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0002
tags:
  - governance
  - adoption
  - validation
risk: High
complexity: Medium
---

# ADR-0007 — Adopting Oriveda Upgrades: Obligations, Grandfathering and Honest History

### Context

A target project consumes Oriveda as a git submodule (`ADR-0003`), so
upgrading is a one-line pointer change. The first project to upgrade
across `ADR-0004`–`ADR-0006` already held fifteen Frozen Domain
Specifications. The upgrade imposed obligations that no Oriveda document
sequenced, and none of them showed in the size of the change:

- **Boundary blocks:** every Frozen §7 needed an `oriveda-boundary`
  block (`ADR-0006` rule 4). Read literally, that meant fifteen full
  revisions before the engine could run.
- **The manifest:** `scripts/validate.py --root` requires a
  `knowledge/manifest.yaml`, and the project had none.
- **Rigor tiers** (`ADR-0005`) applied retroactively. A High-tier spec
  still at Proposal, whose code was already live, became a breach on
  the day of upgrade, for work done before the rule existed.
- **Divergences:** "an unlogged divergence is a defect" turned every
  existing silent divergence into a defect the moment the pointer moved.
- **Reviewers:** the validator rejected `reviewers: []` on specs Frozen
  before reviewers were recorded. The cheapest way to clear the error
  was to type a name in, which rewrites the approval record. That
  happened once and was caught in review. A framework built on
  traceable decisions must not have a check whose easiest fix is a
  fabricated record.

The validator also rejected digits in project IDs (`ARCH-001`), the most
common ID convention there is. Oriveda's own `OV-000` uses digits.

### Options Considered

- **No grandfathering.** New rules apply at once, and a project fixes
  everything before it upgrades. Strict and simple. In practice it
  means projects stop upgrading, which is the drift Oriveda exists to
  prevent.
- **A separate adoption backlog.** Upgrade debt goes in its own file.
  That keeps the divergence log pure, but adds a second place to look
  and a second format to validate.
- **Grandfathering through the divergence log, with stated obligations
  and honest-history markers (chosen).** Each release says what it
  obliges. Pre-existing non-conformance becomes a dated, logged entry in
  the log the project already keeps. Changes that add no decision get a
  cheap revision path. History that was never recorded is marked as
  such, not invented.

### Decision

**1. Every release states its obligations.** Each changelog section that
changes what a consuming project must do has an **"Obligations for
consuming projects"** subsection. It lists each new requirement, whether
it applies to existing work, and the cheapest compliant path. A release
with no obligations says so.

**2. Grandfathering by adoption entry.** A rule that arrives with an
upgrade applies from the upgrade commit (the submodule bump). Existing
work that breaks it at that moment is **not a defect**, provided the
upgrade change itself logs it in the divergence log, as an `open` row
with a **Due** date. An adoption entry may name a Frozen spec. That is
the one exception to divergences being against non-Frozen specs only.
It records a known violation, and it does not make the code right. The
engine still reports violations of Frozen specs. An adoption entry
becomes a defect once its Due date passes while it is still `open`.

**3. Non-semantic revisions.** A change to a Frozen specification that
adds no decision is a **non-semantic revision**: a patch version bump
(`x.y.Z`), no re-review, and a change note saying "non-semantic". It
covers:

- adding an `oriveda-boundary` block that is consistent with its §7
  prose (`ADR-0006` rule 4);
- fixing frontmatter that doesn't parse, or moving it to the raw
  format;
- adding metadata fields whose values were already true;
- fixing broken links or typos.

Anything that changes what the spec allows, forbids or requires is a
normal revision.

**4. Honest history.** A specification Frozen before its reviewers were
recorded keeps `reviewers: []` and sets **`reviewers_unrecorded: true`**.
The validator reports it as information, never as an error. More
generally: **no Oriveda check may be satisfiable only by fabricating
provenance.** Any check on a recorded fact (who reviewed, when,
from what evidence) accepts an explicit "unrecorded" marker. Names,
dates and sources are never back-filled.

**5. The divergence log has a fixed home.** Each target project keeps
exactly one log, at `knowledge/decisions/DIVERGENCE-LOG.md`, with the
fixed id `DIVERGENCE-LOG`. `DIV-NNN` numbers are per project. Its rows
carry a **Due** column (empty for ordinary divergences).
`scripts/validate.py --root` checks that no Frozen spec has an `open`
row without a Due date, and no `open` row is past its Due date.

**6. Project IDs may contain digits.** Project-scope ID patterns allow
digits (`ARCH-001`, `DISC-006`, `FEAT-PAYMENT-E2E`).

### Consequences

- **Easier:** an upgrade can land the same day. The work it creates is
  visible and dated, not hidden in a pointer bump. Adding boundary
  blocks to existing Frozen specs costs patch bumps, not reviews.
  Validators stop pushing adopters to falsify approval records.
- **Harder:**
  - Every release author must write the obligations subsection.
  - The divergence log now holds two kinds of row: ordinary divergences,
    and adoption entries against Frozen specs.
  - "Non-semantic" is a judgement call. A reviewer who disagrees can
    still require a normal revision.
- **Risk:** adoption entries could pile up with ever-moving Due dates.
  Each date change is a visible edit in the log's history, and a
  passed date is a validator error, so this can't happen silently.

### Revisit Criteria

- Adoption entries in any project routinely have their Due dates moved
  more than once. That would mean grandfathering has become indefinite
  deferral.
- A non-semantic revision is later found to have changed meaning.
  Narrow the list in rule 3.
- A second consuming project needs the validator to accept vocabulary
  this ADR doesn't cover: lifecycle aliases, manifest-based file
  discovery, or advisory reference paths. Those are planned as
  separate, smaller changes.
