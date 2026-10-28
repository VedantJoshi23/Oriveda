"""Command-line entry point: `oriveda check boundaries`."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .check_boundaries import Report, check
from .graph import GraphError, load_graphify
from .specs import SpecError, load_boundaries

EXIT_OK, EXIT_VIOLATIONS, EXIT_ERROR = 0, 1, 2


def _head_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def _render_text(report: Report, graph_commit: str | None, head: str | None) -> str:
    lines = [f"oriveda {__version__} — check boundaries",
             f"  provider: graphify  graph built at: {graph_commit or 'unknown'}",
             f"  domains: {len(report.domains)}  dependency edges: {report.edges_checked}"
             f"  cross-domain: {report.cross_domain_edges}"]
    if graph_commit and head and not head.startswith(graph_commit) and not graph_commit.startswith(head):
        lines.append(f"  WARNING: graph is stale (built at {graph_commit[:8]}, checkout is {head[:8]}); "
                     "rebuild it before trusting this report")
    lines.append("")
    for f in report.findings:
        tier, pct = f.confidence
        label = "VIOLATION " if f.kind == "violation" else "DIVERGENCE"
        why = "explicitly forbidden" if f.explicitly_forbidden else "not in allowed_dependencies"
        lines.append(f"{label} {f.source.domain} -> {f.target_domain} ({why}); "
                     f"{f.edge_count} edge(s); {tier} {pct}%")
        lines.append(f"  spec: {f.source.spec_id} [{f.source.status}] {f.source.source}")
        for e in f.evidence:
            lines.append(f"  - {e.location}  {e.source_label} -{e.relation}-> {e.target_label}  [{e.provenance}]")
        if f.edge_count > len(f.evidence):
            lines.append(f"  … {f.edge_count - len(f.evidence)} more")
        if f.kind == "divergence":
            e = f.evidence[0]
            lines.append("  suggested divergence-log row:")
            lines.append(f"  | DIV-??? | `{f.source.spec_id}` §7 | {f.target_domain} not allowed | "
                         f"{f.source.domain} depends on {f.target_domain} ({e.location}) | "
                         f"`<commit/PR>` | open | |")
        lines.append("")
    if not report.findings:
        lines += ["No boundary violations or divergences found.",
                  "  This is an absence claim: Inference, not Fact. The code graph is not "
                  "guaranteed complete (ADR-0006 rule 5).", ""]
    if report.unowned_files:
        lines.append(f"{len(report.unowned_files)} file(s) belong to no declared domain and were not checked, e.g. "
                     + ", ".join(report.unowned_files[:5]))
    violations = sum(f.kind == "violation" for f in report.findings)
    divergences = len(report.findings) - violations
    lines.append(f"Summary: {violations} violation(s), {divergences} divergence(s).")
    return "\n".join(lines)


def _render_json(report: Report, graph_commit: str | None, head: str | None) -> str:
    return json.dumps({
        "oriveda": __version__,
        "check": "boundaries",
        "provider": "graphify",
        "graph_built_at_commit": graph_commit,
        "checkout_commit": head,
        "edges_checked": report.edges_checked,
        "cross_domain_edges": report.cross_domain_edges,
        "unowned_files": list(report.unowned_files),
        "findings": [{
            "kind": f.kind,
            "source_domain": f.source.domain,
            "target_domain": f.target_domain,
            "spec": {"id": f.source.spec_id, "status": f.source.status, "path": str(f.source.source)},
            "explicitly_forbidden": f.explicitly_forbidden,
            "confidence": {"status": f.confidence[0], "value": f.confidence[1]},
            "edge_count": f.edge_count,
            "evidence": [{"location": e.location, "relation": e.relation, "provenance": e.provenance,
                          "score": e.score, "source": e.source_label, "target": e.target_label}
                         for e in f.evidence],
        } for f in report.findings],
    }, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="oriveda", description="Check a codebase against its Oriveda specifications.")
    parser.add_argument("--version", action="version", version=f"oriveda {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    check_p = sub.add_parser("check", help="run a check")
    check_sub = check_p.add_subparsers(dest="check", required=True)
    b = check_sub.add_parser("boundaries", help="cross-domain dependencies vs. Domain Specification §7")
    b.add_argument("--specs", type=Path, default=Path("knowledge/domains"),
                   help="directory of Domain Specifications (default: knowledge/domains)")
    b.add_argument("--graph", type=Path, default=Path("graphify-out/graph.json"),
                   help="provider graph file (default: graphify-out/graph.json)")
    b.add_argument("--root", type=Path, default=Path("."), help="project root, for the staleness check")
    b.add_argument("--format", choices=("text", "json"), default="text")
    b.add_argument("--strict", action="store_true", help="also exit non-zero on divergences")
    args = parser.parse_args(argv)

    try:
        boundaries = load_boundaries(args.specs)
        if not boundaries:
            print(f"error: no oriveda-boundary blocks found under {args.specs}", file=sys.stderr)
            return EXIT_ERROR
        graph = load_graphify(args.graph)
        report = check(graph, boundaries)
    except (SpecError, GraphError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR

    head = _head_commit(args.root)
    render = _render_json if args.format == "json" else _render_text
    print(render(report, graph.built_at_commit, head))
    if any(f.kind == "violation" for f in report.findings):
        return EXIT_VIOLATIONS
    if args.strict and report.findings:
        return EXIT_VIOLATIONS
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
