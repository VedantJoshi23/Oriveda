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

This folder is currently empty. Prior worked examples were run against a
confidential client codebase and have been removed — see
`knowledge/decisions/ADR-0002-example-sandbox-separation.md` for the
sandbox rules that make this possible without touching `knowledge/`.
Future examples must run against source material that is safe to publish
(synthetic data, a project the user owns outright, or something
open-source) — never against confidential or NDA-covered material.

Each new example should get one row here, plus a short intro at the top of
its own file naming: which `knowledge/` rulebook it exercises, and what
input it was run against.
