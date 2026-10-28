# Metadata

```yaml
---
id: ADR-0005
title: The Oriveda Engine — Specs That Check Themselves Against Code
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
  - OV-000
  - OV-006
  - ADR-0004
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions:
  - ADR-0001
  - ADR-0002
  - ADR-0003
  - ADR-0004
tags:
  - engine
  - tooling
  - evidence
risk: High
complexity: Medium
---
```

## ADR-0005 — The Oriveda Engine: Specs That Check Themselves Against Code

### Context

Through M8, every Oriveda check was performed by reading: an agent or a
human compared a specification with the code by hand. That is slow, it
doesn't repeat reliably, and it can't run on every change. `ADR-0004`
makes this more pressing. Its authority rule depends on noticing when
code and specs disagree, and an unlogged divergence counts as a defect.
Nobody can log what nobody notices.

The Graphify pilot (`examples/graphify-pilot-walkthrough.md`) showed
that a code graph can supply the raw facts cheaply and offline. A
20-line script over Graphify's `graph.json` found a real cross-domain
data access. It also showed what a graph does **not** provide:
communities are not domains, docs are not linked to code, and the graph
is incomplete. The last point became upstream issue
Graphify-Labs/graphify#4839, where two-file import cycles are dropped
from the default build. Supplying those missing pieces is Oriveda's job:
knowing which domain owns which code, what each domain may depend on,
how sure we are, and which specification has authority.

### Options Considered

- **Keep checks manual.** No tooling to maintain. But `ADR-0004`'s
  divergence rule becomes unenforceable in practice, and Oriveda stays
  a set of documents with nothing to run.
- **Fork Graphify and add Oriveda's checks to it.** One tool. But
  Graphify ships several releases a week across about 40 languages, so
  a fork would go stale within weeks. It would also tie Oriveda's
  knowledge to one tool's internals, against Principles 1 and 6.
- **A separate engine that reads code graphs as input (chosen).** A
  small Oriveda-owned engine reads target-project specifications plus a
  code graph produced by an *evidence provider*. Graphify is the first
  provider. The engine owns the spec-side meaning: domains, authority,
  confidence. Fixes to code-graph quality go upstream to the provider.

### Decision

Oriveda ships an **engine**: a Python package and CLI named `oriveda`,
living in this repository under `engine/`. It reads a target project's
specifications and a provider's code graph, and reports where the code
and the specifications agree or disagree, using `ADR-0004`'s authority
rule and `OV-000`'s confidence tiers.

**1. Location.** The engine lives in this repository under `engine/`,
replacing the never-built `scripts/` placeholder. Protocols and the
checks that enforce them version together. A target project that
references Oriveda as a submodule (`ADR-0003`) gets the matching engine
version automatically.

**2. Language and dependencies.** Python 3.10+, installable with `pip`,
`uv` or `pipx`. The only runtime dependency is PyYAML. No provider is a
dependency: the engine reads the provider's output *file*, never its
Python API. Licensed Apache-2.0, like the rest of the repository.

**3. Evidence providers.** A provider is anything that produces a code
graph the engine has an adapter for. The engine's internal model is a
list of directed, file-level dependency edges, each with a relation, a
provenance (`EXTRACTED` or `INFERRED`), a score and a source location.
Adapters convert a provider's format into that model. The first adapter
reads Graphify `graph.json`, and reads edge direction from each link's
`source` → `target` order, not from the file's `directed` flag
(Graphify#3495). The pilot's six provider rules apply to every
provider:

- Code-only extraction by default. An LLM-backed pass needs the owner's
  per-target approval, and never runs on confidential material without
  it.
- Pin the provider version, and record it together with the commit the
  graph was built from.
- `EXTRACTED` presence claims may be Fact. `INFERRED` claims are
  Inference at the provider's score. **Absence claims are never Fact.**
- Provider clustering is never treated as a domain proposal. Domains
  come from Domain Specifications.
- Never install a provider's agent hooks or skills into a target
  project without the owner's opt-in.
- Divergence detection is the engine's job, not the provider's.

**4. Machine-checkable boundaries live in the Domain Specification.**
Each Domain Specification's §7 Dependencies carries a small fenced
block, with info string `yaml oriveda-boundary`, next to the
human-readable Allowed and Forbidden lists:

````markdown
```yaml oriveda-boundary
domain: DOM-ARTICLE
paths:
  - src/article/**
allowed_dependencies:
  - DOM-USER
forbidden_dependencies:
  - DOM-PAYMENT
```
````

The block is part of §7, so it is High tier and freezes with
§2/§6/§7. It is not a second source of truth: if the block and the
prose disagree, the spec is internally inconsistent and cannot be
Frozen. No separate configuration file exists.

**5. Findings follow the authority rule.** A dependency that crosses
domain boundaries without being allowed is reported as:

- a **violation** when the depending domain's spec is Frozen. The code
  is wrong. The command exits non-zero.
- a **divergence** when that spec is not Frozen. The engine prints a
  ready-to-paste `DIV` row for the divergence log. It exits zero unless
  `--strict` is given.

Each finding carries its evidence edges and a confidence. It is Fact
if at least one supporting edge is `EXTRACTED`, otherwise Inference at
the highest score. A clean result is reported as an absence claim:
"no violations found", at Inference tier, never as proof of
compliance.

**6. Commands are added one slice at a time.** The first slice is
`oriveda check boundaries`. Planned next, each only after the previous
one has been used on a real target: `oriveda evidence` (graph to
`EVD`/`KC` claims), `oriveda drift` (other spec claims against the
graph), and `oriveda gate` (`ADR-0004` rule 3 for a given slice).

### Consequences

- **Easier:** boundary rules stop depending on someone remembering to
  check them. They can run on every commit, in CI, or before a freeze.
  `ADR-0004`'s divergence log gets a steady supply of candidates.
  Oriveda gains something people can run.
- **Harder:** this repository now contains code. That brings tests,
  releases and a compatibility promise for the `oriveda-boundary` block
  format. The engine also depends on providers' output formats, so a
  provider format change needs an adapter update.
- **Risk:** a clean engine report could be read as proof of
  compliance. That risk is mitigated by rule 5's absence wording, by
  recording the provider version and graph commit in every report, and
  by staleness warnings when the graph's commit differs from the
  checked-out commit.

### Revisit Criteria

- A second provider is needed and the internal edge model can't
  represent what it supplies.
- Python packaging becomes a real adoption barrier for target projects
  (for example, users asking for a single binary).
- The `oriveda-boundary` block cannot express a boundary that a real
  Domain Specification needs, without the block becoming a second spec
  language.
- After `oriveda check boundaries` has run on two real target projects,
  re-evaluate the order of the next commands.
