"""`oriveda check boundaries`: cross-domain dependencies vs. declared Allowed lists (ADR-0006 rule 5)."""

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


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    path = path.replace("\\", "/").removeprefix("./")
    return any(_glob_regex(p).match(path) for p in patterns)


def _unit_of(path: str, units: tuple[str, ...]) -> str | None:
    """The shortest directory prefix of path that matches a unit-root glob."""
    parts = path.split("/")
    for i in range(1, len(parts)):
        prefix = "/".join(parts[:i])
        if _matches(prefix, units):
            return prefix
    return None


@dataclass(frozen=True)
class Finding:
    kind: str                 # "violation" (Frozen spec) | "divergence" (not yet Frozen)
    source: DomainBoundary
    target_domain: str
    reason: str               # "forbidden" | "undeclared" | "shared-depends-on-domain"
    evidence: tuple[Edge, ...]
    edge_count: int
    type_only_count: int = 0  # how many of edge_count are compile-time-only

    @property
    def explicitly_forbidden(self) -> bool:
        return self.reason == "forbidden"

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
    unowned_files: tuple[str, ...]            # source files no domain owns
    unowned_other: tuple[str, ...] = ()       # docs/config files no domain owns
    unowned_units: tuple[tuple[str, int], ...] = ()  # (unit root, unowned source files)
    excluded_files: tuple[str, ...] = ()
    type_only_ignored: int = 0


def check(graph: CodeGraph, boundaries: list[DomainBoundary], *,
          exclude: tuple[str, ...] = (), units: tuple[str, ...] = (),
          count_type_only: bool = True) -> Report:
    grouped: dict[tuple[str, str], list[Edge]] = defaultdict(list)
    by_domain = {b.domain: b for b in boundaries}
    unowned_src: set[str] = set()
    unowned_other: set[str] = set()
    excluded: set[str] = set()
    cross = ignored_type_only = 0
    for edge in graph.edges:
        if _matches(edge.source_file, exclude) or _matches(edge.target_file, exclude):
            excluded.update(f for f in (edge.source_file, edge.target_file) if _matches(f, exclude))
            continue
        src, tgt = domain_of(edge.source_file, boundaries), domain_of(edge.target_file, boundaries)
        for f, owner, is_code in ((edge.source_file, src, edge.source_is_code),
                                  (edge.target_file, tgt, edge.target_is_code)):
            if owner is None:
                (unowned_src if is_code else unowned_other).add(f)
        if src is None or tgt is None or src.domain == tgt.domain:
            continue
        cross += 1
        if tgt.shared and src.shared:
            continue                      # shared units may build on each other
        if tgt.shared or tgt.domain in src.allowed:
            continue
        if edge.type_only and not count_type_only:
            ignored_type_only += 1
            continue
        grouped[(src.domain, tgt.domain)].append(edge)

    findings = []
    for (src_name, tgt_name), edges in sorted(grouped.items()):
        src = by_domain[src_name]
        reason = ("shared-depends-on-domain" if src.shared
                  else "forbidden" if tgt_name in src.forbidden else "undeclared")
        # Strongest evidence first: EXTRACTED before INFERRED, then score.
        ranked = sorted(edges, key=lambda e: (e.provenance != "EXTRACTED", -e.score, e.location))
        findings.append(Finding(
            kind="violation" if src.frozen else "divergence",
            source=src,
            target_domain=tgt_name,
            reason=reason,
            evidence=tuple(ranked[:MAX_EVIDENCE]),
            edge_count=len(edges),
            type_only_count=sum(e.type_only for e in edges),
        ))

    unit_counts: dict[str, int] = defaultdict(int)
    for f in unowned_src:
        unit = _unit_of(f, units)
        if unit is not None:
            unit_counts[unit] += 1
    return Report(tuple(findings), tuple(boundaries), len(graph.edges), cross,
                  tuple(sorted(unowned_src)), tuple(sorted(unowned_other)),
                  tuple(sorted(unit_counts.items())), tuple(sorted(excluded)), ignored_type_only)
