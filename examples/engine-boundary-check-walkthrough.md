# Worked Example — `oriveda check boundaries` on RealWorld

**Rulebook exercised:** `ADR-0006` (the engine's first slice), using the
`OV-006` §7 `oriveda-boundary` block and the `ADR-0005` authority rule.

**Input:** the same open-source target as the Graphify pilot
([`lujakob/nestjs-realworld-example-app`](https://github.com/lujakob/nestjs-realworld-example-app)
@ `c1c2cc4`, ISC licence). The graph was built with `graphifyy==0.9.89`
in code-only mode. The input also includes five abbreviated Domain
Specifications in [`realworld-domains/`](realworld-domains/), written for
this example. They describe what a team *would plausibly decide*, not
what the code does today. That gap is what the check exists to expose.

This is a sandbox file (`ADR-0002`). Nothing here is authoritative.

---

## 1. The declared boundaries

| Domain | Status | Paths | Allowed | Forbidden |
| --- | --- | --- | --- | --- |
| `DOM-USER` | Frozen | `src/user/**` | `DOM-SHARED` | `DOM-ARTICLE` |
| `DOM-ARTICLE` | Frozen | `src/article/**` | `DOM-USER`, `DOM-SHARED` | `DOM-PROFILE` |
| `DOM-PROFILE` | Draft | `src/profile/**` | `DOM-USER`, `DOM-SHARED` | — |
| `DOM-TAG` | Draft | `src/tag/**` | `DOM-SHARED` | — |
| `DOM-SHARED` | Frozen | `src/shared/**` | — | — |

## 2. The run

```
$ cd nestjs-realworld-example-app
$ oriveda check boundaries --specs <oriveda>/examples/realworld-domains
oriveda 0.1.0 — check boundaries
  provider: graphify  graph built at: c1c2cc4e448b279ff083272df1ac50d20c3304fa
  domains: 5  dependency edges: 342  cross-domain: 47

VIOLATION  DOM-ARTICLE -> DOM-PROFILE (explicitly forbidden); 5 edge(s); fact 95%
  spec: DOM-ARTICLE [Frozen] examples/realworld-domains/DOM-ARTICLE.md
  - src/article/article.module.ts:L7  article.module.ts -imports-> FollowsEntity  [EXTRACTED]
  - src/article/article.module.ts:L7  article.module.ts -imports_from-> follows.entity.ts  [EXTRACTED]
  - src/article/article.service.ts:L15  .constructor() -references-> FollowsEntity  [EXTRACTED]
  - src/article/article.service.ts:L7  article.service.ts -imports-> FollowsEntity  [EXTRACTED]
  - src/article/article.service.ts:L7  article.service.ts -imports_from-> follows.entity.ts  [EXTRACTED]

DIVERGENCE DOM-TAG -> DOM-USER (not in allowed_dependencies); 2 edge(s); fact 95%
  spec: DOM-TAG [Draft] examples/realworld-domains/DOM-TAG.md
  - src/tag/tag.module.ts:L3  tag.module.ts -imports-> UserModule  [EXTRACTED]
  - src/tag/tag.module.ts:L3  tag.module.ts -imports_from-> user.module.ts  [EXTRACTED]
  suggested divergence-log row:
  | DIV-??? | `DOM-TAG` §7 | DOM-USER not allowed | DOM-TAG depends on DOM-USER (src/tag/tag.module.ts:L3) | `<commit/PR>` | open | |

VIOLATION  DOM-USER -> DOM-ARTICLE (explicitly forbidden); 1 edge(s); fact 95%
  spec: DOM-USER [Frozen] examples/realworld-domains/DOM-USER.md
  - src/user/user.entity.ts:L4  user.entity.ts -imports-> ArticleEntity  [EXTRACTED]

4 file(s) belong to no declared domain and were not checked, e.g. package.json, src/app.controller.ts, src/app.module.ts, src/main.ts
Summary: 2 violation(s), 1 divergence(s).
$ echo $?
1
```

## 3. Reading the result

- **`DOM-ARTICLE → DOM-PROFILE` is a violation.** `ArticleService`
  injects `Repository<FollowsEntity>` and reads the profile domain's
  table directly. The Frozen spec says feeds must go through
  `DOM-PROFILE`'s API instead. This is the same finding as the pilot's
  KC-001, now reported automatically against a stated rule.
- **`DOM-USER → DOM-ARTICLE` is a violation, found despite a
  provider gap.** Graphify drops the file-level `imports_from` edge for
  this pair (Graphify#4839). The engine still catches it through the
  surviving symbol-level `imports` edge, because it counts every
  dependency relation, not only file-level imports.
- **`DOM-TAG → DOM-USER` is a divergence, not a violation.**
  `DOM-TAG` is still Draft. Either the spec is missing an allowed
  dependency, or `tag.module.ts` imports `UserModule` without needing
  to. The engine doesn't decide which. It produces the divergence-log
  row and leaves the resolution to people (`ADR-0005` rule 4).
- **Coverage is reported, not hidden.** Four files (the app shell and
  `package.json`) are owned by no domain. Before a project could claim
  full coverage, they would need an owner or an explicit exclusion.

## 4. What this run found in Oriveda itself

The first run failed with exit code 2. The example specs copied a title
pattern from `templates/domain-template.md`
(`title: <Project Name> — Domain: <Name>`). In YAML, the second colon
makes that line invalid. Five templates had the same bug, including the
spec card added the same day. Their frontmatter had never been parsed by
a machine, so nobody had noticed. The titles are now quoted. This
illustrates `ADR-0006`'s premise: specs that only humans read can be
wrong without anyone finding out.

## Exit check

- [x] Run against publishable source only (`ADR-0002`).
- [x] Every finding traced to `EXTRACTED` edges at the stated source
      locations.
- [x] The clean-run wording, divergence rows and exit codes match
      `ADR-0006` rule 5. These are covered by `engine/tests`.
- [x] Nothing written into `knowledge/` from this example.
