"""Command-line entry point: `oriveda check boundaries`."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .check_boundaries import Report, check
from .graph import CATEGORIES, CodeGraph, GraphError, load_graphify
from .specs import SpecError, SpecSet, load_specs

EXIT_OK, EXIT_VIOLATIONS, EXIT_ERROR = 0, 1, 2

_REASONS = {
    "forbidden": "explicitly forbidden",
    "undeclared": "not in allowed_dependencies",
    "shared-depends-on-domain": "a shared unit may depend on no domain",
}


@dataclass(frozen=True)
class Notice:
    text: str
    fails_strict: bool   # with --strict, this notice fails the run


def _head_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def _notices(specs: SpecSet, graph: CodeGraph, head: str | None) -> list[Notice]:
    out = []
    commit = graph.built_at_commit
    if commit is None:
        out.append(Notice("graph records no build commit, so staleness was not checked "
                          "(ADR-0006 rule 3); rebuild with a provider mode that records it", True))
    elif head and not head.startswith(commit) and not commit.startswith(head):
        out.append(Notice(f"graph is stale (built at {commit[:8]}, checkout is {head[:8]}); "
                          "rebuild it before trusting this report", True))
    for s in specs.unblocked:
        if s.frozen:
            out.append(Notice(f"{s.spec_id} is Frozen but has no oriveda-boundary block "
                              f"(ADR-0006 rule 4), so it was not checked: {s.source}", True))
    return out


def _coverage(report: Report, specs: SpecSet, graph: CodeGraph, count_type_only: bool) -> dict:
    return {
        "checked": [c for c in CATEGORIES if c in graph.supplies],
        "not_checked": [c for c in CATEGORIES if c not in graph.supplies],
        "type_only_edges": "counted" if count_type_only else f"ignored ({report.type_only_ignored})",
        "excluded_files": len(report.excluded_files),
        "unowned_source_files": list(report.unowned_files),
        "unowned_other_files": len(report.unowned_other),
        "unowned_units": [{"unit": u, "source_files": n} for u, n in report.unowned_units],
        "specs_without_block": [{"id": s.spec_id, "status": s.status, "path": str(s.source)}
                                for s in specs.unblocked],
    }


def _render_text(report: Report, specs: SpecSet, graph: CodeGraph, notices: list[Notice],
                 coverage: dict) -> str:
    lines = [f"oriveda {__version__} — check boundaries",
             f"  provider: {graph.provider}  graph built at: {graph.built_at_commit or 'unknown'}",
             f"  domains: {len(report.domains)}  dependency edges: {report.edges_checked}"
             f"  cross-domain: {report.cross_domain_edges}"]
    lines += [f"  WARNING: {n.text}" for n in notices]
    lines.append("")
    for f in report.findings:
        tier, pct = f.confidence
        label = "VIOLATION " if f.kind == "violation" else "DIVERGENCE"
        type_only = f", {f.type_only_count} type-only" if f.type_only_count else ""
        lines.append(f"{label} {f.source.domain} -> {f.target_domain} ({_REASONS[f.reason]}); "
                     f"{f.edge_count} edge(s){type_only}; {tier} {pct}%")
        lines.append(f"  spec: {f.source.spec_id} [{f.source.status}] {f.source.source}")
        for e in f.evidence:
            marker = " type-only" if e.type_only else ""
            lines.append(f"  - {e.location}  {e.source_label} -{e.relation}-> {e.target_label}"
                         f"  [{e.provenance}{marker}]")
        if f.edge_count > len(f.evidence):
            lines.append(f"  … {f.edge_count - len(f.evidence)} more")
        if f.kind == "divergence":
            e = f.evidence[0]
            lines.append("  suggested divergence-log row:")
            lines.append(f"  | DIV-??? | `{f.source.spec_id}` §7 | {f.target_domain} not allowed | "
                         f"{f.source.domain} depends on {f.target_domain} ({e.location}) | "
                         f"`<commit/PR>` | open | | |")  # Due empty: an ordinary divergence
        lines.append("")
    if not report.findings:
        lines += ["No boundary violations or divergences found.",
                  "  This is an absence claim: Inference, not Fact. It covers only what is listed",
                  "  as checked below, and the code graph is not guaranteed complete (ADR-0006 rule 5).", ""]

    lines.append("Coverage:")
    lines.append(f"  checked: {', '.join(coverage['checked'])} (type-only edges {coverage['type_only_edges']})")
    if coverage["not_checked"]:
        lines.append(f"  not checked: {', '.join(coverage['not_checked'])} "
                     f"({graph.provider} supplies no such edges)")
    if coverage["excluded_files"]:
        lines.append(f"  excluded: {coverage['excluded_files']} file(s) matching --exclude")
    src = coverage["unowned_source_files"]
    if src or coverage["unowned_other_files"]:
        sample = f", e.g. {', '.join(src[:5])}" if src else ""
        lines.append(f"  unowned: {len(src)} source file(s){sample}; "
                     f"{coverage['unowned_other_files']} docs/config file(s)")
    for u in coverage["unowned_units"]:
        lines.append(f"  unowned unit: {u['unit']} ({u['source_files']} source file(s)); "
                     "no Domain Specification owns it")
    if coverage["specs_without_block"]:
        listed = ", ".join(f"{s['id']} [{s['status']}]" for s in coverage["specs_without_block"])
        lines.append(f"  specs without a boundary block (not checked): {listed}")

    violations = sum(f.kind == "violation" for f in report.findings)
    divergences = len(report.findings) - violations
    lines.append(f"Summary: {violations} violation(s), {divergences} divergence(s), "
                 f"{len(notices)} warning(s).")
    return "\n".join(lines)


def _render_json(report: Report, graph: CodeGraph, head: str | None, notices: list[Notice],
                 coverage: dict) -> str:
    return json.dumps({
        "oriveda": __version__,
        "check": "boundaries",
        "provider": graph.provider,
        "graph_built_at_commit": graph.built_at_commit,
        "checkout_commit": head,
        "edges_checked": report.edges_checked,
        "cross_domain_edges": report.cross_domain_edges,
        "warnings": [n.text for n in notices],
        "coverage": coverage,
        # Kept for 0.1.x consumers; same list as coverage.unowned_source_files.
        "unowned_files": list(report.unowned_files),
        "findings": [{
            "kind": f.kind,
            "source_domain": f.source.domain,
            "target_domain": f.target_domain,
            "reason": f.reason,
            "spec": {"id": f.source.spec_id, "status": f.source.status, "path": str(f.source.source)},
            "explicitly_forbidden": f.explicitly_forbidden,
            "confidence": {"status": f.confidence[0], "value": f.confidence[1]},
            "edge_count": f.edge_count,
            "type_only_count": f.type_only_count,
            "evidence": [{"location": e.location, "relation": e.relation, "provenance": e.provenance,
                          "score": e.score, "type_only": e.type_only,
                          "source": e.source_label, "target": e.target_label}
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
    b.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                   help="skip edges touching matching files, e.g. a composition root or tests; "
                        "repeatable; excluded files are counted in the report")
    b.add_argument("--units", action="append", default=[], metavar="GLOB",
                   help="unit roots, e.g. 'src/modules/*': each matching directory with unowned "
                        "source files is reported by name; repeatable")
    b.add_argument("--type-only", choices=("count", "ignore"), default="count",
                   help="whether compile-time-only dependencies count (default: count)")
    b.add_argument("--format", choices=("text", "json"), default="text")
    b.add_argument("--strict", action="store_true",
                   help="also fail on divergences and warnings (missing or stale build commit, "
                        "Frozen spec without a block)")
    args = parser.parse_args(argv)

    count_type_only = args.type_only == "count"
    try:
        specs = load_specs(args.specs)
        if not specs.boundaries:
            print(f"error: no oriveda-boundary blocks found under {args.specs}", file=sys.stderr)
            return EXIT_ERROR
        graph = load_graphify(args.graph)
        report = check(graph, list(specs.boundaries), exclude=tuple(args.exclude),
                       units=tuple(args.units), count_type_only=count_type_only)
    except (SpecError, GraphError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR

    head = _head_commit(args.root)
    notices = _notices(specs, graph, head)
    coverage = _coverage(report, specs, graph, count_type_only)
    if args.format == "json":
        print(_render_json(report, graph, head, notices, coverage))
    else:
        print(_render_text(report, specs, graph, notices, coverage))
    if any(f.kind == "violation" for f in report.findings):
        return EXIT_VIOLATIONS
    if args.strict and (report.findings or any(n.fails_strict for n in notices)):
        return EXIT_VIOLATIONS
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
