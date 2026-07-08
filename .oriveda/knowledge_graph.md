# Oriveda Knowledge Graph

Rendered from every Frozen specification's own frontmatter
(`depends_on`/`required_by`/`related_decisions`) — this file is a
**view**, not a second source of truth. If it ever disagrees with a
spec's frontmatter, the frontmatter wins; fix this file to match, not the
other way around.

**Maintenance:** update this diagram by hand at each milestone
checkpoint, alongside `.oriveda/manifest.yaml` — same discipline, same
moment, not a separate pass. There are only ~12 nodes today; this stays
cheap to keep current as long as it's done at the same time a new
protocol or ADR gets frozen, not batched up later.

An arrow `A --> B` means **A depends on B** (B is a prerequisite of A).

```mermaid
graph TD
    OV000["OV-000<br/>Knowledge Acquisition"]
    OV001["OV-001<br/>M1 Discovery"]
    OV002["OV-002<br/>M2 Constitution"]
    OV003["OV-003<br/>M3 System Architecture"]
    OV004["OV-004<br/>M3 Technology Decisions"]
    OV005["OV-005<br/>M4 Standards"]
    OV006["OV-006<br/>M5 Domain Spec"]
    OV007["OV-007<br/>M6 Feature Spec"]
    OV008["OV-008<br/>M7 Prompt Library"]

    ADR0001["ADR-0001<br/>Oriveda Is a Product"]
    ADR0002["ADR-0002<br/>Sandbox Separation"]
    ADR0003["ADR-0003<br/>Submodule Reference"]

    OV001 --> OV000
    OV002 --> OV001
    OV003 --> OV001
    OV003 --> OV002
    OV004 --> OV002
    OV004 --> OV003
    OV005 --> OV001
    OV005 --> OV002
    OV005 --> OV003
    OV005 --> OV004
    OV006 --> OV001
    OV006 --> OV002
    OV006 --> OV003
    OV006 --> OV004
    OV007 --> OV002
    OV007 --> OV005
    OV007 --> OV006
    OV008 --> OV000
    OV008 --> OV001
    OV008 --> OV002
    OV008 --> OV003
    OV008 --> OV004
    OV008 --> OV005
    OV008 --> OV006
    OV008 --> OV007

    ADR0002 --> ADR0001
    ADR0002 --> OV000
    ADR0003 --> OV008

    classDef adr fill:#4a3b6b,stroke:#8b7bb8,color:#fff
    class ADR0001,ADR0002,ADR0003 adr
```

## Reading this graph

- **The spine (`OV-000` → `OV-008`) is almost entirely linear** by
  design — each milestone's protocol depends on the ones before it. The
  one branch is `OV-003`/`OV-004` (Architecture splits into two sibling
  documents, per the M3 scoping decision) which both feed `OV-005`,
  `OV-006`, and `OV-008`.
- **`OV-007`does not depend on `OV-003`/`OV-004` directly** — it reaches
  architecture-level context only through `OV-006` (Domain
  Specifications), which already absorbed and restated what `OV-007`
  needs. This is the "point, don't copy" discipline visible structurally:
  `OV-007` doesn't re-depend on something a closer layer already covers.
- **`ADR-0002` depends on `ADR-0001`** — fixed as part of this audit; the
  frontmatter previously claimed this relationship one-directionally
  (`ADR-0001` listed `ADR-0002` as `required_by` without the reverse
  `depends_on` existing), which this graph would have silently rendered
  wrong had it been built before the fix.
