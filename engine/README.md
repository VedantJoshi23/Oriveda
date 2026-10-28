# oriveda engine

Checks a codebase against its Oriveda specifications (`ADR-0006`).

```
$ oriveda check boundaries
VIOLATION  DOM-ARTICLE -> DOM-PROFILE (explicitly forbidden); 5 edge(s); fact 95%
  spec: DOM-ARTICLE [Frozen] knowledge/domains/DOM-ARTICLE.md
  - src/article/article.service.ts:L15  .constructor() -references-> FollowsEntity  [EXTRACTED]
  ...
Summary: 2 violation(s), 1 divergence(s).
```

Code graphs tell you what the code *is*. The engine tells you whether
that matches what you *decided*, which specification has authority, and
how sure the answer is.

## Install

```
pip install ./engine          # from a checkout of this repository
# or, in a target project that uses Oriveda as a submodule (ADR-0003):
pip install ./.oriveda-framework/engine
```

It needs Python 3.10+ and PyYAML. The code graph comes from an
evidence provider, which you install separately. Today that means
[Graphify](https://github.com/Graphify-Labs/graphify), run in code-only
mode (no LLM calls):

```
pip install "graphifyy==0.9.89"     # pin the version (ADR-0006 rule 3)
graphify update .                   # writes graphify-out/graph.json
```

## `oriveda check boundaries`

The command compares every cross-domain dependency in the code graph
with the `oriveda-boundary` block in each Domain Specification's §7:

````markdown
```yaml oriveda-boundary
domain: DOM-ARTICLE
paths:
  - "src/article/**"
allowed_dependencies:
  - DOM-USER
forbidden_dependencies:
  - DOM-PROFILE
```
````

`**` matches across directories; `*` and `?` match within a single
path segment. Quote any pattern that starts with `*`, because YAML
reads an unquoted leading `*` as an alias.

The block is a checkable *subset* of §7. It must be consistent with the
prose, which stays authoritative for rules the block can't express,
such as "may read but not command".

A shared kernel or platform unit declares `kind: shared` and no
dependency lists. Any domain may depend on it, and it may depend on no
domain. Its depending on a domain is reported like any other finding.

```yaml oriveda-boundary
domain: DOM-AUDIT
kind: shared
paths:
  - "src/audit/**"
```

| Flag | Default | |
| --- | --- | --- |
| `--specs` | `knowledge/domains` | Directory searched recursively for Domain Specifications |
| `--graph` | `graphify-out/graph.json` | Provider graph file |
| `--root` | `.` | Project root, used to warn when the graph is older than the checkout |
| `--exclude GLOB` | none | Skip edges touching matching files, e.g. a composition root or `**/*.spec.ts`. Repeatable. Excluded files are counted in the report |
| `--units GLOB` | none | Unit roots, e.g. `src/modules/*`. A unit with unowned source files is reported by name. Repeatable |
| `--type-only` | `count` | `count` or `ignore` compile-time-only edges (e.g. `import type`), where the provider marks them |
| `--format` | `text` | `text` or `json` |
| `--strict` | off | Also fail on divergences and on warnings |

**Findings follow the `ADR-0005` authority rule:**

- **Violation:** the depending domain's spec is Frozen, so the code is
  wrong. The command exits `1`.
- **Divergence:** the spec is not Frozen yet. The engine prints a
  ready-to-paste divergence-log row. The command exits `0`, or `1` with
  `--strict`.

Each finding is labelled Fact if at least one supporting edge is
`EXTRACTED`, otherwise Inference at the provider's score. A clean run is
reported as an absence claim, at Inference tier, never as proof.

**Every report ends with its coverage**, so it's clear what a clean run
does and doesn't cover:

```
Coverage:
  checked: code-dependency (type-only edges counted)
  not checked: data-access, messaging (graphify supplies no such edges)
  excluded: 2 file(s) matching --exclude
  unowned: 3 source file(s), e.g. src/app.controller.ts, ...; 1 docs/config file(s)
  unowned unit: src/modules/shipping (6 source file(s)); no Domain Specification owns it
  specs without a boundary block (not checked): DOM-RISK [Proposal]
```

A domain that writes another domain's data store through a shared
client, or publishes another domain's events, is **not** seen by
import-based providers. Until a provider supplies data-access and
messaging edges, check those rules with project-specific tests.

**Warnings** (each fails the run with `--strict`):

- the graph records no build commit, so staleness can't be checked;
- the graph is stale;
- a Frozen Domain Specification has no boundary block.

Exit code `2` means the specs or the graph couldn't be read.

## Develop

```
pip install -e "./engine[test]"
pytest engine
```
