# Examples

This folder is a **sandbox**, not part of Oriveda's own knowledge base. See
`ADR-0002` for the full reasoning; the short version:

- Files here are worked demonstrations of a `knowledge/` rulebook running
  against a real input. They exist to (a) validate that the rulebook
  actually works before it's frozen, and (b) show future adopters of
  Oriveda what running a given protocol looks like in practice.
- Files here **may** reference a specific project (product names, tech
  stacks, business rules, whatever the source evidence contains). That's
  expected and fine — it's the whole point of a worked example.
- Nothing here is authoritative. If an example and a `knowledge/`
  specification ever disagree, the specification wins; the example gets
  updated or removed, not the other way around.
- `knowledge/` files may link to an example (e.g. "see
  `examples/discovery-repo-structure-walkthrough.md`") but must never pull
  project-specific facts back into their own body text.

## Index

`m1-discovery-*-walkthrough.md` is a complete run of `OV-001` against
`jwel-main.zip` — all ten investigations, in the same order as `OV-001`'s
investigation table. `m1-discovery-recommendations-walkthrough.md` is the
synthesis step and cross-references the other nine.

| Example | Investigation | Confidence |
| --- | --- | --- |
| [`m1-discovery-repo-structure-walkthrough.md`](m1-discovery-repo-structure-walkthrough.md) | repo-structure | 85% |
| [`m1-discovery-business-vision-walkthrough.md`](m1-discovery-business-vision-walkthrough.md) | business-vision | 90% |
| [`m1-discovery-feature-inventory-walkthrough.md`](m1-discovery-feature-inventory-walkthrough.md) | feature-inventory | 90% |
| [`m1-discovery-user-journeys-walkthrough.md`](m1-discovery-user-journeys-walkthrough.md) | user-journeys | 60% |
| [`m1-discovery-data-model-walkthrough.md`](m1-discovery-data-model-walkthrough.md) | data-model | 85% |
| [`m1-discovery-domain-discovery-walkthrough.md`](m1-discovery-domain-discovery-walkthrough.md) | domain-discovery | 85% |
| [`m1-discovery-technical-architecture-walkthrough.md`](m1-discovery-technical-architecture-walkthrough.md) | technical-architecture | 90% |
| [`m1-discovery-hidden-business-rules-walkthrough.md`](m1-discovery-hidden-business-rules-walkthrough.md) | hidden-business-rules | 70% |
| [`m1-discovery-technical-debt-walkthrough.md`](m1-discovery-technical-debt-walkthrough.md) | technical-debt | 90% |
| [`m1-discovery-recommendations-walkthrough.md`](m1-discovery-recommendations-walkthrough.md) | recommendations (synthesis) | 90% |

Source evidence for all ten: `jwel-main.zip` (`README.md`, `ARCHITECTURE.md`,
`PRODUCT.md`, `SECURITY.md`, `apps/api/src/modules/*` listing).

| Example | Demonstrates |
| --- | --- |
| [`m2-constitution-jwel-walkthrough.md`](m2-constitution-jwel-walkthrough.md) | `OV-002`, a full Constitution derived from the M1 walkthroughs above |

Each new example should get one row here, plus a short intro at the top of
its own file naming: which `knowledge/` rulebook it exercises, and what
input it was run against.
