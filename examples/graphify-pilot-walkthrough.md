# Worked Example — Graphify as an OV-000 Evidence Provider (Pilot)

**Rulebook exercised:** `OV-000` (the `repository` evidence pipeline),
plus a feasibility check for `ADR-0005` rule 4: can a code graph
detect spec-vs-code divergence?

**Input:** [`lujakob/nestjs-realworld-example-app`](https://github.com/lujakob/nestjs-realworld-example-app)
at commit `c1c2cc4`. It is open source (ISC), and a NestJS + TypeORM
modular backend with four feature modules (`article`, `profile`, `tag`,
`user`), 35 TypeScript files. It is safe to publish under `ADR-0002`.

**Tool:** [Graphify](https://github.com/Graphify-Labs/graphify),
PyPI package `graphifyy==0.9.89`, installed into an isolated virtualenv
and run as a plain CLI (`graphify update .`). Code-only mode was used,
so no LLM was involved. It ran with an empty environment, a throwaway
`HOME`, no `claude` binary on `PATH` and query logging disabled.
`graphify install` (which edits the agent's config and hooks) was **not**
run.

This is a sandbox file (`ADR-0002`). Nothing here is authoritative, and
nothing in it has been written into `knowledge/`.

---

## 1. What Graphify produced

| Output | Result |
| --- | --- |
| Graph | 340 nodes, 656 edges, 13 communities, built in seconds |
| Cost | 0 tokens |
| Edge provenance | 634 `EXTRACTED` (97%) and 22 `INFERRED` (3%, all with score 0.85) |
| Relations | `references` 187, `imports_from` 129, `contains` 120, `imports` 107, `method` 70, `calls` 33, `re_exports` 10 |
| Report | `GRAPH_REPORT.md`: most-connected nodes (`UserEntity`, `ArticleEntity`, `ArticleService`…), communities, isolated nodes, an import-cycle check, suggested questions |
| Freshness | The graph records the commit it was built from (`built_at_commit`) |

## 2. Accuracy spot-check

Each claim was checked by reading the source.

| Claim from the graph | Provenance | Verified? |
| --- | --- | --- |
| `ArticleService` constructor references `FollowsEntity` (`profile` module) | EXTRACTED | ✅ It injects `Repository<FollowsEntity>` |
| `ArticleService` imports `UserEntity` (`user` module) | EXTRACTED | ✅ It injects `Repository<UserEntity>` |
| `user.entity.ts` imports `ArticleEntity` | EXTRACTED | ✅ `@ManyToMany`/`@OneToMany` relations |
| `AuthMiddleware.use()` calls `UserService.findById()` | INFERRED 0.85 | ✅ |
| `UserController.login()` calls `UserService.findOne()` | INFERRED 0.85 | ✅ |
| `UserController.login()` calls `UserService.generateJWT()` | INFERRED 0.85 | ✅ |
| **"Import Cycles: None detected"** | report | ❌ **False negative** (see below) |

All six edges that were present and sampled are correct. All 22
`INFERRED` edges belong to one pattern: a controller calling a service
injected through `this.xService`. That is reasonable to treat as
inference-tier.

**The false negative.** `article.entity.ts` and `user.entity.ts` import
each other, which is a real file-level cycle. The graph has the
symbol-level edge `user.entity.ts → ArticleEntity` but **no** file-level
`imports_from` edge in that direction, so the cycle check never sees the
cycle. Each edge Graphify reports was correct in this sample, but the
set of edges is incomplete.

## 3. Mapping to the evidence schema

Rule this pilot suggests: **presence claims ("X depends on Y") built from
`EXTRACTED` edges can be Fact. Absence claims ("there are no cycles",
"nothing else touches this table") are at most Inference, because the
graph is demonstrably incomplete.**

```yaml
evidence_item:
  id: EVD-001
  type: repository
  source: github.com/lujakob/nestjs-realworld-example-app@c1c2cc4
  pipeline: repository / provider=graphify@0.9.89 (code-only)
  claims:
    - id: KC-001
      statement: The article module reads and writes the profile module's
        follows table directly (ArticleService injects Repository<FollowsEntity>).
      status: fact
      confidence: 95          # EXTRACTED edge, source-verified
      investigation: domain-discovery
    - id: KC-002
      statement: The user and article modules depend on each other at the
        entity level (bidirectional TypeORM relations).
      status: fact
      confidence: 92          # EXTRACTED symbol edges in both directions
      investigation: technical-debt
    - id: KC-003
      statement: Controllers delegate all persistence to their module's service.
      status: inference
      confidence: 85          # 22 INFERRED call edges at 0.85, consistent pattern
      investigation: technical-architecture
    - id: KC-004
      statement: The codebase has no import cycles.
      status: assumption
      confidence: 30          # tool reports "none", but a cycle is known to exist (KC-002)
      superseded_by: KC-002
      investigation: technical-debt
```

## 4. What worked and what didn't

**Worked**

- **Fast, offline extraction of structural facts that are correct.** For
  `OV-000`'s repository pipeline this replaces most hand-reading of files
  for the `repo-structure`, `data-model` and `domain-discovery`
  investigations.
- **The tool already labels its own confidence.** `EXTRACTED`/`INFERRED`
  plus a numeric score map directly onto the Fact/Inference bands.
- **`graph.json` is plain JSON, easy to query.** A 20-line script
  (§5) produced the cross-module dependency matrix that `OV-006`
  boundary checks need. It found the article→profile table access in
  KC-001, which is exactly the kind of violation a Constitution law
  against cross-domain data access would forbid.

**Did not work (in code-only mode)**

- **Communities are not domains.** Five of the eleven reported
  communities are configuration noise (`package.json` fields,
  `tsconfig` options, npm scripts). Community 0 mixes the article
  module, the profile module and `AppController`. Without the LLM pass,
  labels are just file names. Grouping by directory was more useful than
  community detection for proposing domains.
- **No doc-to-code linking.** The README's title still says
  "Node/Express/Mongoose Example App" while the code is NestJS/TypeORM.
  Graphify put the README in its own separate community and never
  flagged the contradiction. This mirrors the M8 audit's main lesson
  (aspirational docs mistaken for reality). **Graphify does not supply
  ADR-0005's divergence detection out of the box.** That check has to be
  an Oriveda-side comparison of spec claims against `graph.json`.
- **Absence claims are unreliable.** See the false negative in §2.

**Operational notes**

- **Fast-moving releases.** There were 265 PyPI releases between
  2026-04-04 and 2026-10-27. Pin an exact version, and record it in each
  evidence item's `pipeline` field.
- **The README's privacy statement is out of date.** In 0.9.89, query
  logging is opt-in (`GRAPHIFY_QUERY_LOG_ENABLE`); the README says it is
  on by default. Set `GRAPHIFY_QUERY_LOG_DISABLE=1` anyway.
- **It picks up an LLM automatically.** If the `claude` CLI is on `PATH`
  or an API key is set, LLM-backed commands (community labeling, the
  docs pass) will use it. For confidential or NDA material, run
  code-only, in an isolated environment as this pilot did.

## 5. The cross-module script used

```python
# usage: python3 -I xmod.py graphify-out/graph.json
import json, sys, collections, re
g = json.load(open(sys.argv[1]))
nodes = {n['id']: n for n in g['nodes']}
def mod(nid):
    m = re.match(r'src/([^/]+)/', nodes.get(nid, {}).get('source_file') or '')
    return m.group(1) if m else None
mat = collections.Counter()
for e in g['links']:
    a, b = mod(e['source']), mod(e['target'])
    if a and b and a != b and e['relation'] != 'contains':
        mat[(a, b, e['relation'])] += 1
for (a, b, r), v in sorted(mat.items()):
    print(f"{a:8} -> {b:8} {r:13} {v}")
```

Output, condensed: `article→user` (21 edges), `profile→user` (16),
`article→profile` (5), `tag→user` (2), `user→article` (1),
`user→shared` (2).

## 6. Verdict

**Adopt Graphify as a recommended evidence provider for
`repository`-type evidence, under these rules.** These are candidate
content for an evidence-provider ADR (`ADR-0006`):

1. Run code-only by default. The LLM pass requires the owner's explicit
   approval for each target, and is never used on confidential material
   without it.
2. Pin the exact version, and record `provider=graphify@<version>` plus
   the `built_at_commit` value in each evidence item.
3. An `EXTRACTED` presence claim can be Fact once it has been
   spot-checked. `INFERRED` claims are Inference at the tool's score.
   **Absence claims are never Fact.**
4. Do not treat communities as domain proposals. Use directory or module
   structure plus the cross-module matrix.
5. Do not run `graphify install` or its hooks in a target project
   unless the owner opts in. Oriveda reads `graph.json`; it does not
   hand control of the agent's workflow to the tool.
6. Divergence detection (ADR-0005) is Oriveda's own check, built on
   `graph.json`, not a Graphify feature.

**Exit check**

- [x] Run against publishable source only (`ADR-0002`).
- [x] No LLM calls, no writes outside the sandbox, no changes to agent
      configuration.
- [x] Every claim in §3 traced to a verified edge or a stated limitation.
- [x] Nothing written into `knowledge/`.
