# Changelog

## v0.1.0-genesis

The birth of Oriveda.

### Added

- Repository structure
- Engineering philosophy
- Naming conventions
- Metadata specification
- Contribution guidelines
- Versioning strategy
- Repository vision

This marks the first public milestone of Oriveda.

The framework now exists independently of any implementation and establishes the foundation for AI-assisted engineering through structured knowledge.

---

## M1 — Discovery

### Added

- `OV-000` Knowledge Acquisition Specification (Frozen): evidence
  inventory, per-evidence-type reverse-engineering pipelines,
  confidence-tiered knowledge claims, gap-detection protocol.
- `OV-001` M1 Discovery Protocol (Frozen): the ten-investigation
  structure, shared investigation template, per-investigation lifecycle.
- `ADR-0001` (backfilled), `ADR-0002`: this repository is the framework
  itself, domain-agnostic; protocol validation output belongs in
  `examples/`, never in `knowledge/`.
- `templates/document-template.md`, `templates/decision-template.md`
  filled in (previously empty stubs).
- Ten `examples/m1-discovery-*-walkthrough.md` files: `OV-001` run
  end-to-end against a reference codebase.

### Changed

- `OV-001` later revised to v0.1.1 (see M4) after a recurring gap was
  found across two milestones' dry runs.

---

## M2 — Constitution

### Added

- `OV-002` M2 Constitution Protocol (Frozen): derives a target project's
  Engineering Constitution from `OV-001` Discovery findings plus three
  owner-choice questions (rigor level, AI collaboration mode,
  architecture ambition) that can't be inferred from evidence.
- `templates/constitution-template.md`.
- A worked example: a full 8-Law Constitution draft (later removed from
  `examples/` — confidential source material, see `ADR-0002`).

---

## M3 — Architecture

### Added

- `OV-003` M3 System Architecture Protocol (Frozen): service boundaries,
  domain model, event flow, folder structure, scalability strategy —
  each classified Adopted/Adapted/Designed depending on available
  Discovery evidence.
- `OV-004` M3 Technology Decisions Protocol (Frozen): the stack-freedom
  owner-choice question plus one ADR-shaped decision per significant
  technology layer.
- Two worked examples (later removed from `examples/` — confidential
  source material, see `ADR-0002`). Found and fixed a real leak
  (tech-specific content embedded in `OV-003`'s own body) before
  freezing.

---

## M4 — Standards

### Added

- `OV-005` M4 Standards Protocol (Frozen): a nine-category candidate
  catalog with applicability detection against a target project's
  architecture/technology/constitution, a shared necessity bar, and one
  common template all produced Standards follow.
- A worked example (later removed from `examples/` — confidential source
  material, see `ADR-0002`).

### Changed

- `OV-001` revised to v0.1.1 (versioned revision, not a silent edit):
  added a cross-cutting extraction checklist after three independent dry
  runs found the same gap shape — domain events and NFRs present in
  evidence but not captured by the investigation responsible for them.

---

## M5 — Domains

### Added

- `OV-006` M5 Domain Specification Protocol (Frozen): explodes each
  `OV-003` bounded context into a full eight-section Domain
  Specification. Full/Thin depth tiers avoid busywork for pure
  projection domains while still requiring every declared boundary to
  have a spec.
- `templates/domain-template.md`.
- A worked example: two Full specs, one Thin — surfaced a real
  inconsistency in the reference project's own architecture doc
  (correctly flagged, not silently resolved). Later removed from
  `examples/` — confidential source material, see `ADR-0002`.

---

## M6 — Features

### Added

- `OV-007` M6 Feature Specification Protocol (Frozen): nine-section
  Feature Specification structure operationalizing "exactly one owning
  domain." Unlike M1–M5, M6's Definition of Done is protocol readiness,
  not full feature coverage — features are open-ended.
- `templates/feature-template.md`.
- A worked example: a multi-domain, sequential-hand-off feature found
  and fixed a real structural gap in the dependency rule before
  freezing. Later removed from `examples/` — confidential source
  material, see `ADR-0002`.

---

## M7 — Prompt Library

### Added

- `OV-008` M7 Prompt Library Protocol (Frozen): a fixed seven-prompt
  catalog (`PRM-DISCOVERY` through `PRM-REVIEW`), one per prior
  milestone's protocol plus a cross-cutting review prompt, sharing a
  common Context/Task/Constraints/Deliverables/DoD shape.
- `templates/prompt-template.md`.
- A worked example: all seven prompts instantiated; `PRM-FEATURE` put to
  a real sufficiency test. Later removed from `examples/` — confidential
  source material, see `ADR-0002`.
- Root `README.md`: a "Getting Started With a New Project" section with
  a copy-pasteable Genesis Prompt for bootstrapping Oriveda governance
  in a new target project, including the no-repository case.
- `ADR-0003`: git submodule as the mechanism for a target project to
  reference `OV-000`–`OV-008` without copying their content.

**M0 through M7 of the roadmap are complete. M8 — Implementation —
remains: applying these eight protocols to a real target project.**

---

## Repository Audit (post-M7)

A full walk-through of the repository structure, prompted by noticing
several `.oriveda/*.yaml` files and directories had sat empty since M0
without anyone deciding whether they were actually needed.

### Added

- `.oriveda/glossary.yaml`, `.oriveda/taxonomy.yaml` populated
  (framework-level vocabulary and ID-prefix rules — previously empty
  stubs since M0).
- `.oriveda/knowledge_graph.md`: a Mermaid diagram rendered from every
  spec's own frontmatter, replacing the never-populated
  `knowledge_graph.yaml`. Building it surfaced a real cross-reference bug
  (`ADR-0001`/`ADR-0002` disagreed about their own dependency direction),
  fixed as part of this change (`ADR-0002` → v1.0.1).
- `templates/review-template.md` filled in — the Architecture Review
  lifecycle stage and `PRM-REVIEW` previously had no defined output
  shape.

### Fixed

- README's Naming Convention and Knowledge Hierarchy sections corrected
  to match what was actually built, replacing stale M0-era placeholders.
- `.oriveda/manifest.yaml`: stale comments corrected, the fixed `PRM-*`
  catalog registered (previously an empty list despite `OV-008` defining
  seven concrete entries).

### Removed

- Unused, never-git-tracked `assets/` and `knowledge/vision/`
  directories. Vision is covered by `OV-000`/`OV-001` — a standalone
  Vision artifact was considered and deliberately not built, not
  forgotten.
- Phantom top-level `standards/` from the README's structure diagram —
  never actually existed; `knowledge/standards/` is what's real.

---

## Feedback from the first consuming project

Gaps found while running M1–M6 on the first real target project
(DecisionMakingUsingData) and fixed here.

### Added

- The seven `PRM-*` prompts in `knowledge/prompts/` (Draft). `OV-008`
  defined the catalog, but no prompt had a body, so "identify the `PRM`
  that applies and load its Context" could not actually be followed.
- `ADR-0004` (Draft): project-scope prefixes `DISC-`, `CONST-` and `ARCH-`
  for the documents `OV-001`–`OV-003` produce (adopted from the project,
  which had to invent them), and `scripts/validate.py --root PROJECT` to
  validate a target project's `knowledge/` against its own manifest.
  Checked against that project: 62 specifications, no errors.
- The framework-mode validator also checks the `PRM-*` files.

### Fixed

- README: `scripts/` described as empty (the validator exists), a
  non-existent `knowledge/appendix/` in the structure diagram, and "no
  separate prompt library" contradicting `OV-008`.

### Known, not yet addressed

- The worked examples removed under `ADR-0002` leave the DoD items that
  cite `examples/` (for example `OV-008` item 4) unmet.
- No protocol for M8 (Implementation) yet: keeping specifications in step
  with code, marking Discovery findings resolved, and governing releases.
- No rule for a project whose specifications are all still Draft: "load
  only Frozen specs" then loads nothing.

---

## Progressive Rigor (post-M8)

Running M0–M8 end to end against a real target project showed the method
works, but strict sequential freezing front-loads the specs most likely
to be wrong and can't absorb requirements that only settle during the
build.

### Resolves

Two items from the "Known, not yet addressed" list above:

- *No rule for a project whose specifications are all still Draft.* The
  `ADR-0005` confidence gate lets work load Draft specs, marked as such,
  when the claims it relies on are ≥60% and owner-acknowledged.
- *Keeping specifications in step with code.* This is handled by the
  divergence log, and by the rule that a spec with open divergences
  can't be Frozen. A full M8 protocol is still open.

### Added

- `ADR-0005` Progressive Rigor (Frozen): only Frozen specifications are
  authoritative over code. A disagreement with a not-yet-Frozen spec is
  a logged *divergence*. Rigor tiers (High/Medium/Low) come from each
  spec's `risk` field; a confidence gate (≥60%, owner-acknowledged)
  replaces "upstream must be Frozen" for starting work; specs freeze on
  proof, and open divergences block freezing.
- `templates/spec-card-template.md` (Low-tier feature form) and
  `templates/divergence-log-template.md`.
- `DIV` ID prefix (`.oriveda/taxonomy.yaml`); glossary terms
  *divergence*, *rigor tier*, *confidence gate*, *slice*, *spec card*.
- `LICENSE`: Apache License 2.0.
- `examples/graphify-pilot-walkthrough.md`: Graphify (code-only, pinned
  0.9.89) piloted as an `OV-000` evidence provider against an
  open-source NestJS app. Verdict: adopt, under six stated rules.

### Changed

- Root `README.md`: Principle 4 now states that only Frozen
  specifications bind code. The Specification Lifecycle section gains
  the tier table; Getting Started recommends a walking skeleton. Removed
  the stale "first implementation" line from Long-Term Vision. The
  License section now points to `LICENSE`.
- `OV-002` through `OV-008` revised to v0.2.0: each "upstream is Frozen"
  gate is replaced by the `ADR-0005` confidence gate, except where the
  upstream spec is High tier. The Constitution, `OV-003` §1–§2 and
  `OV-006` §2/§6/§7 remain Frozen-before-implementation. `OV-008`'s
  `PRM-REVIEW` now also checks for unlogged divergences.

---

## Oriveda Engine v0.1.0 (post-M8)

### Added

- `ADR-0006` The Oriveda Engine (Frozen): a Python 3.10+ CLI under
  `engine/` that reads target-project specifications plus an evidence
  provider's code graph (Graphify first, read as a file and never
  imported), and reports disagreements under the `ADR-0005` authority
  rule. Commands ship one slice at a time.
- `engine/` v0.1.0: `oriveda check boundaries`. It compares every
  cross-domain dependency with each Domain Specification's §7
  `oriveda-boundary` block. Findings on Frozen specs are violations
  (exit 1); findings on Draft specs are divergences, printed with a
  ready-to-paste `DIV` row. Every finding carries a confidence tier,
  and a clean run is reported as an absence claim. Ships with 20 tests.
- `examples/engine-boundary-check-walkthrough.md` and
  `examples/realworld-domains/`: on the RealWorld target the check found
  2 violations and 1 divergence. One of them was found through
  symbol-level edges, despite Graphify#4839.
- Glossary terms *engine*, *evidence provider*.

### Changed

- `OV-006` revised to v0.3.0: §7 carries an `oriveda-boundary` block that
  must agree with its prose; a disagreement blocks freezing.
  `templates/domain-template.md` gains the block.
- Root `README.md`: documents `engine/` next to `scripts/validate.py`.
  The genesis prompt now loads Draft specs, marked as such, instead of
  "only Frozen specs".

### Fixed

- Frontmatter in five templates (domain, feature, prompt, review, spec
  card) was invalid YAML: an unquoted colon in `title:`. Titles are now
  quoted. Found by the engine's first real run.

---

## Field Report Fixes: Engine v0.2.0, ADR-0007 (post-M8)

The first run of `oriveda check boundaries` on a real consuming project
(fifteen Frozen Domain Specifications, a NestJS + ORM backend) produced
a field report. Each issue was sorted into a gap in Oriveda's concepts,
fixed here, or a gap in that project's own usage, which stays with the
project. Nothing here is specific to any one stack.

### Added

- `ADR-0007` Adopting Oriveda Upgrades (Frozen):
  - each release lists its obligations for consuming projects;
  - existing work that breaks a newly arrived rule becomes a dated
    *adoption entry* in the divergence log, not an instant breach;
  - *non-semantic revisions* to Frozen specs take a patch bump and no
    re-review;
  - `reviewers_unrecorded: true` for specs Frozen before reviewers were
    recorded, and the general rule that no check may be satisfiable only
    by fabricating provenance;
  - the divergence log's fixed home is
    `knowledge/decisions/DIVERGENCE-LOG.md`.
- Engine v0.2.0:
  - **Coverage** in every report: what was checked, what wasn't
    (data-access and messaging edges aren't supplied by import-based
    providers), excluded files, unowned source files apart from
    docs/config, unowned units, and specs without a block.
  - **Warnings**, each failing `--strict`: a graph with no build commit,
    a stale graph, a Frozen spec without a boundary block.
  - **`kind: shared`** in the boundary block. Any domain may depend on
    a shared unit, and a shared unit may depend on no domain.
  - **Flags:** `--exclude` (composition roots, tests), `--units` (an
    unowned unit is reported by name), and `--type-only count|ignore`,
    using the provider's existing `type_only` marking.
  - 34 tests.
- `scripts/validate.py`:
  - accepts `reviewers_unrecorded: true`, reported as info;
  - with `--root`, checks the divergence log: an `open` row against a
    Frozen spec needs a Due date, and no `open` row may be past it.

### Changed

- `ADR-0006` v1.1.0: rule 4 now says the boundary block is a
  *consistent, checkable subset* of §7, not an equivalent; the prose
  stays authoritative for what the block can't express. Rule 5 adds
  coverage reporting and warnings.
- `ADR-0005` v1.0.1 (non-semantic): the authority table says plainly
  that ADR-plus-remediation applies to a Constitution only.
- `OV-006` v0.4.0: the §7 block rule follows `ADR-0006` v1.1.0.
- Project-scope ID patterns (`DOM`, `FEAT`, `STD`, `DISC`, `CONST`,
  `ARCH`) accept digits, e.g. `ARCH-001`. New `DIVERGENCE` prefix for the
  log's fixed id.
- `templates/divergence-log-template.md`: fixed id and path, a Due
  column, adoption entries explained. The engine's suggested row has
  the matching columns.

### Obligations for consuming projects

Upgrading to this release from any earlier one:

- **Domain Specifications:** add an `oriveda-boundary` block to each §7
  before `oriveda check boundaries` can check that domain. On a Frozen
  spec, this is a non-semantic revision (patch bump, no re-review) when
  the block is consistent with the prose. Until then the engine lists
  the spec as unchecked and warns for Frozen ones.
- **Divergence log:** create `knowledge/decisions/DIVERGENCE-LOG.md` from
  the template, or move an existing log there. Add the Due column.
- **Adoption entries:** in the upgrade change, log existing breaches of
  `ADR-0005` tiers (for example a High-tier spec still at Proposal with
  live code), and known Frozen-spec violations, as `open` rows with a Due
  date.
- **Validator:** `scripts/validate.py --root` needs
  `knowledge/manifest.yaml`. For Frozen specs whose reviewers were never
  recorded, set `reviewers_unrecorded: true`; never back-fill names.
- **Engine flags:** decide your project's `--exclude` patterns
  (composition root, tests), `--units` roots and `--type-only` policy,
  and declare shared units with `kind: shared`.
- **Unchanged:** no existing boundary block, divergence-log row or spec
  needs editing, except to add the Due column.

### Not yet addressed (from the same report)

- Data-store and message ownership in the block (`owns_stores`,
  `owns_messages`), and providers that supply those edges.
- Dependency modes in the block (read vs. command).
- A validator check that architecture contexts and Domain
  Specifications match one-to-one.
- Validator vocabulary for pre-existing projects: lifecycle-name aliases,
  file discovery from the manifest, and advisory reference paths.

---

## v0.3.0: Project Validator Settings (post-M8)

From the second field report by the same consuming project. On that
project `oriveda check boundaries --strict` passed, but
`scripts/validate.py --root` reported 97 errors. None was a spec defect.
Each came from a project fact the validator had no way to be told.
Oriveda now supplies the mechanism, and each project supplies its own
values.

**No action needed unless you want to use these settings.**

### Added

- An optional `validator:` section in a target project's
  `knowledge/manifest.yaml`, read by `scripts/validate.py --root`
  (`ADR-0004` v0.2.0):
  - `lifecycle_aliases`: maps the project's own status words onto
    Oriveda's lifecycle stages, e.g. `{Review: Proposal, Accepted: Frozen}`.
    Lifecycle rules run on the mapped stage, and findings show both
    words. An alias to a word that isn't a stage, or one that redefines a
    stage, is an error.
  - `constitution`: the path to the project's Constitution. References
    to its id or path resolve.
  - `advisory_paths`: globs for documents that may be linked but don't
    bind. A link to one is reported as info. A Frozen spec's `depends_on`
    on one stays an error, and on any other spec it is a warning.
  - An unknown key is a warning, not a failure.
- `scripts/tests/`: 24 tests for the validator. Among them is a
  regression check that its output, with no settings or empty ones, is
  byte-identical to the previous release's on this repository and on a
  project fixture. Run with `python -m pytest scripts/tests`.

### Changed

- `ADR-0004` v0.2.0 (Draft): records the settings. The engine does not
  read them yet, so Domain Specifications keep canonical status words.
- `.oriveda/manifest.yaml` `version` is now the release number, 0.3.0.
  It had stayed at 0.1.0 since genesis while releases were numbered by
  the engine. The engine is unchanged and stays at 0.2.0.

### Obligations for consuming projects

None. Every key is optional. Without the section, the validator's output
is byte-identical to the previous release's. No spec, manifest entry or
file needs changing, no field became required, and the default stage
vocabulary is unchanged.

To use the settings, add the section to `knowledge/manifest.yaml`.
Validators older than this release ignore it, so the section is safe to
add before bumping the submodule. Expect two effects:

- **An alias of `Frozen` brings Frozen's obligations.** A spec rejected
  before for an unknown status word is now checked as Frozen, and may
  show a real defect that the vocabulary error hid. An example is empty
  `reviewers`: per `ADR-0007` rule 4, set `reviewers_unrecorded: true`,
  and never back-fill names.
- **Advisory documents stay advisory.** A Frozen spec that `depends_on`
  one is still an error. Move what it relies on into a specification,
  or cite the document under `related_documents`.

### Not yet addressed

From the first field report:

- data-store and message ownership in the boundary block, and providers
  that supply those edges;
- a one-to-one check between architecture contexts and Domain
  Specifications;
- dependency modes in the block (read vs. command).

Also not yet addressed: the engine reading `lifecycle_aliases`.
