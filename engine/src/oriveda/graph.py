"""Evidence-provider adapters: turn a provider's code graph into file-level edges (ADR-0005 rule 3)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Relations that mean "the source file depends on the target file".
# Structural membership (`contains`, `method`) stays inside one file and is
# never a cross-domain dependency.
DEPENDENCY_RELATIONS = frozenset({
    "imports", "imports_from", "re_exports", "calls", "references",
    "inherits", "implements", "mixes_in", "uses",
})


class GraphError(ValueError):
    """The provider's graph file can't be read as a code graph."""


@dataclass(frozen=True)
class Edge:
    source_file: str
    target_file: str
    relation: str
    provenance: str        # EXTRACTED | INFERRED | AMBIGUOUS
    score: float
    location: str          # "<file>:<line>" where the dependency is stated
    source_label: str
    target_label: str


@dataclass(frozen=True)
class CodeGraph:
    provider: str
    built_at_commit: str | None
    edges: tuple[Edge, ...]


def load_graphify(path: Path) -> CodeGraph:
    """Read a Graphify graph.json.

    Direction comes from each link's source -> target order, not from the
    file's `directed` flag, which is false on default builds even though
    the links keep subject -> object order (Graphify#3495).
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphError(f"{path}: {exc}") from exc
    if not isinstance(data, dict) or "nodes" not in data:
        raise GraphError(f"{path}: not a Graphify graph.json (no `nodes`)")

    links = data.get("links", data.get("edges"))
    if not isinstance(links, list):
        raise GraphError(f"{path}: no `links` list")
    nodes = {n.get("id"): n for n in data["nodes"] if isinstance(n, dict)}

    edges = []
    for link in links:
        relation = link.get("relation", "")
        if relation not in DEPENDENCY_RELATIONS:
            continue
        src, tgt = nodes.get(link.get("source")), nodes.get(link.get("target"))
        # External packages have no source_file and can't belong to a domain.
        if not src or not tgt or not src.get("source_file") or not tgt.get("source_file"):
            continue
        provenance = str(link.get("confidence") or "EXTRACTED").upper()
        score = link.get("confidence_score")
        edges.append(Edge(
            source_file=src["source_file"],
            target_file=tgt["source_file"],
            relation=relation,
            provenance=provenance,
            score=float(score) if isinstance(score, (int, float)) else (1.0 if provenance == "EXTRACTED" else 0.5),
            location=f"{link.get('source_file') or src['source_file']}:{link.get('source_location') or '?'}",
            source_label=str(src.get("label", src.get("id"))),
            target_label=str(tgt.get("label", tgt.get("id"))),
        ))
    commit = data.get("built_at_commit")
    return CodeGraph(provider="graphify", built_at_commit=commit if isinstance(commit, str) else None,
                     edges=tuple(edges))
