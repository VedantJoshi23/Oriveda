"""`oriveda check boundaries`: cross-domain dependencies vs. declared Allowed lists (ADR-0005 rule 5)."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

from .graph import CodeGraph, Edge
from .specs import DomainBoundary, SpecError

MAX_EVIDENCE = 5


@lru_cache(maxsize=None)
def _glob_regex(pattern: str) -> re.Pattern[str]:
    """`**` crosses directories, `*` and `?` stay within one path segment."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?"); i += 3
        elif pattern.startswith("**", i):
            out.append(".*"); i += 2
        elif pattern[i] == "*":
            out.append("[^/]*"); i += 1
        elif pattern[i] == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(pattern[i])); i += 1
    return re.compile("".join(out) + r"\Z")


def domain_of(path: str, boundaries: list[DomainBoundary]) -> DomainBoundary | None:
    path = path.replace("\\", "/").removeprefix("./")
    owners = [b for b in boundaries if any(_glob_regex(p).match(path) for p in b.paths)]
    if len(owners) > 1:
        raise SpecError(f"{path} is owned by more than one domain: {sorted(b.domain for b in owners)}")
    return owners[0] if owners else None


@dataclass(frozen=True)
class Finding:
    kind: str                 # "violation" (Frozen spec) | "divergence" (not yet Frozen)
    source: DomainBoundary
    target_domain: str
    explicitly_forbidden: bool
    evidence: tuple[Edge, ...]
    edge_count: int

    @property
    def confidence(self) -> tuple[str, int]:
        """OV-000 tier: Fact if any supporting edge was EXTRACTED, else Inference at the best score."""
        if any(e.provenance == "EXTRACTED" for e in self.evidence):
            return "fact", 95
        best = max((e.score for e in self.evidence), default=0.0)
        return ("inference", round(best * 100)) if best >= 0.6 else ("assumption", round(best * 100))


@dataclass(frozen=True)
class Report:
    findings: tuple[Finding, ...]
    domains: tuple[DomainBoundary, ...]
    edges_checked: int
    cross_domain_edges: int
    unowned_files: tuple[str, ...]


def check(graph: CodeGraph, boundaries: list[DomainBoundary]) -> Report:
    grouped: dict[tuple[str, str], list[Edge]] = defaultdict(list)
    by_domain = {b.domain: b for b in boundaries}
    unowned: set[str] = set()
    cross = 0
    for edge in graph.edges:
        src, tgt = domain_of(edge.source_file, boundaries), domain_of(edge.target_file, boundaries)
        for f, owner in ((edge.source_file, src), (edge.target_file, tgt)):
            if owner is None:
                unowned.add(f)
        if src is None or tgt is None or src.domain == tgt.domain:
            continue
        cross += 1
        if tgt.domain in src.allowed:
            continue
        grouped[(src.domain, tgt.domain)].append(edge)

    findings = []
    for (src_name, tgt_name), edges in sorted(grouped.items()):
        src = by_domain[src_name]
        # Strongest evidence first: EXTRACTED before INFERRED, then score.
        ranked = sorted(edges, key=lambda e: (e.provenance != "EXTRACTED", -e.score, e.location))
        findings.append(Finding(
            kind="violation" if src.frozen else "divergence",
            source=src,
            target_domain=tgt_name,
            explicitly_forbidden=tgt_name in src.forbidden,
            evidence=tuple(ranked[:MAX_EVIDENCE]),
            edge_count=len(edges),
        ))
    return Report(tuple(findings), tuple(boundaries), len(graph.edges), cross, tuple(sorted(unowned)))
