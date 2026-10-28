"""Tests for `oriveda check boundaries` (ADR-0006 rules 3-5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oriveda.check_boundaries import check, domain_of
from oriveda.cli import EXIT_ERROR, EXIT_OK, EXIT_VIOLATIONS, main
from oriveda.graph import load_graphify
from oriveda.specs import SpecError, load_boundaries, parse_domain_spec


def spec(domain: str, status: str, paths: list[str], allowed=(), forbidden=(), kind=None) -> str:
    def items(xs):
        return "".join(f'\n  - "{x}"' for x in xs) if xs else " []"
    return f"""# Metadata

```yaml
---
id: {domain}
status: {status}
---
```

## Domain: {domain}

---

## 7. Dependencies

```yaml oriveda-boundary
domain: {domain}{f"{chr(10)}kind: {kind}" if kind else ""}
paths:{items(paths)}
allowed_dependencies:{items(allowed)}
forbidden_dependencies:{items(forbidden)}
```
"""


def node(nid: str, source_file: str | None, file_type: str = "code") -> dict:
    n = {"id": nid, "label": nid, "file_type": file_type}
    if source_file is not None:
        n["source_file"] = source_file
    return n


def link(src: str, tgt: str, relation: str, confidence="EXTRACTED", score=1.0, line="L1",
         type_only=False) -> dict:
    # source_file of a link is where the dependency is stated: the source's file.
    out = {"source": src, "target": tgt, "relation": relation, "confidence": confidence,
           "confidence_score": score, "source_file": "", "source_location": line}
    if type_only:
        out["type_only"] = True
    return out


@pytest.fixture
def project(tmp_path: Path):
    specs = tmp_path / "domains"
    specs.mkdir()

    def write(specs_text: dict[str, str], nodes: list[dict], links: list[dict], commit="abc1234"):
        for name, text in specs_text.items():
            (specs / f"{name}.md").write_text(text, encoding="utf-8")
        graph = tmp_path / "graph.json"
        data = {"directed": False, "nodes": nodes, "links": links}
        if commit is not None:
            data["built_at_commit"] = commit
        graph.write_text(json.dumps(data), encoding="utf-8")
        return specs, graph
    return write


BASE_NODES = [
    node("ArticleService", "src/article/article.service.ts"),
    node("UserEntity", "src/user/user.entity.ts"),
    node("FollowsEntity", "src/profile/follows.entity.ts"),
    node("ArticleEntity", "src/article/article.entity.ts"),
    node("typeorm", None),                       # external package: no source_file
    node("Logger", "src/shared/logger.ts"),      # owned by no domain
]


def three_domains(article_status="Frozen"):
    return {
        "article": spec("DOM-ARTICLE", article_status, ["src/article/**"], allowed=["DOM-USER"],
                        forbidden=["DOM-PAYMENT"]),
        "user": spec("DOM-USER", "Frozen", ["src/user/**"]),
        "profile": spec("DOM-PROFILE", "Draft", ["src/profile/**"], allowed=["DOM-USER"]),
    }


def test_allowed_dependency_is_not_reported(project):
    specs, graph = project(three_domains(), BASE_NODES,
                           [link("ArticleService", "UserEntity", "imports")])
    report = check(load_graphify(graph), load_boundaries(specs))
    assert report.findings == ()
    assert report.cross_domain_edges == 1


def test_undeclared_dependency_from_frozen_spec_is_a_violation(project):
    specs, graph = project(three_domains("Frozen"), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "references", line="L15")])
    [finding] = check(load_graphify(graph), load_boundaries(specs)).findings
    assert finding.kind == "violation"
    assert (finding.source.domain, finding.target_domain) == ("DOM-ARTICLE", "DOM-PROFILE")
    assert finding.confidence == ("fact", 95)
    assert finding.evidence[0].location.endswith(":L15")


def test_undeclared_dependency_from_draft_spec_is_a_divergence(project):
    specs, graph = project(three_domains("Draft"), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "references")])
    [finding] = check(load_graphify(graph), load_boundaries(specs)).findings
    assert finding.kind == "divergence"


def test_direction_comes_from_link_order_not_the_directed_flag(project):
    # user -> article is undeclared (DOM-USER allows nothing); article -> user is allowed.
    specs, graph = project(three_domains(), BASE_NODES,
                           [link("UserEntity", "ArticleEntity", "imports")])
    [finding] = check(load_graphify(graph), load_boundaries(specs)).findings
    assert (finding.source.domain, finding.target_domain) == ("DOM-USER", "DOM-ARTICLE")


def test_inferred_only_evidence_is_inference_not_fact(project):
    specs, graph = project(three_domains(), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "calls", confidence="INFERRED", score=0.85)])
    [finding] = check(load_graphify(graph), load_boundaries(specs)).findings
    assert finding.confidence == ("inference", 85)


def test_external_and_structural_edges_are_ignored_and_unowned_files_listed(project):
    specs, graph = project(three_domains(), BASE_NODES, [
        link("ArticleService", "typeorm", "imports"),
        link("ArticleService", "FollowsEntity", "contains"),
        link("ArticleService", "Logger", "imports"),
    ])
    report = check(load_graphify(graph), load_boundaries(specs))
    assert report.findings == ()
    assert report.unowned_files == ("src/shared/logger.ts",)


def test_explicitly_forbidden_is_flagged(project):
    texts = three_domains()
    texts["payment"] = spec("DOM-PAYMENT", "Frozen", ["src/payment/**"])
    nodes = BASE_NODES + [node("Charge", "src/payment/charge.ts")]
    specs, graph = project(texts, nodes, [link("ArticleService", "Charge", "calls")])
    [finding] = check(load_graphify(graph), load_boundaries(specs)).findings
    assert finding.explicitly_forbidden


def test_overlapping_ownership_is_a_spec_error(project):
    texts = three_domains()
    texts["greedy"] = spec("DOM-GREEDY", "Draft", ["src/**"])
    specs, graph = project(texts, BASE_NODES, [link("ArticleService", "UserEntity", "imports")])
    with pytest.raises(SpecError, match="more than one domain"):
        check(load_graphify(graph), load_boundaries(specs))


def test_spec_without_block_is_skipped_and_duplicate_domain_is_an_error(tmp_path):
    (tmp_path / "notes.md").write_text("# Just notes\n", encoding="utf-8")
    assert parse_domain_spec(tmp_path / "notes.md") is None
    (tmp_path / "a.md").write_text(spec("DOM-X", "Draft", ["a/**"]), encoding="utf-8")
    (tmp_path / "b.md").write_text(spec("DOM-X", "Draft", ["b/**"]), encoding="utf-8")
    with pytest.raises(SpecError, match="declared twice"):
        load_boundaries(tmp_path)


def test_raw_frontmatter_is_read_like_fenced(tmp_path):
    """Raw `---` frontmatter at the top of the file, the form the validator expects."""
    fenced = spec("DOM-X", "Frozen", ["x/**"])
    raw = fenced.replace("# Metadata\n\n```yaml\n", "").replace("---\n```\n", "---\n", 1)
    assert raw.startswith("---\nid: DOM-X")
    p = tmp_path / "x.md"
    p.write_text(raw, encoding="utf-8")
    b = parse_domain_spec(p)
    assert (b.spec_id, b.status, b.frozen) == ("DOM-X", "Frozen", True)


def test_allowed_and_forbidden_overlap_is_a_spec_error(tmp_path):
    p = tmp_path / "x.md"
    p.write_text(spec("DOM-X", "Draft", ["x/**"], allowed=["DOM-Y"], forbidden=["DOM-Y"]), encoding="utf-8")
    with pytest.raises(SpecError, match="both allowed and forbidden"):
        parse_domain_spec(p)


@pytest.mark.parametrize("pattern, path, expected", [
    ("src/article/**", "src/article/dto/create.ts", True),
    ("src/article/**", "src/articles/x.ts", False),
    ("src/*/entity.ts", "src/user/entity.ts", True),
    ("src/*/entity.ts", "src/user/deep/entity.ts", False),
    ("**/billing/*.py", "pkg/billing/charge.py", True),
    ("**/billing/*.py", "billing/charge.py", True),
])
def test_glob_semantics(tmp_path, pattern, path, expected):
    p = tmp_path / "d.md"
    p.write_text(spec("DOM-D", "Draft", [pattern]), encoding="utf-8")
    assert (domain_of(path, [parse_domain_spec(p)]) is not None) is expected


def test_cli_exit_codes_and_absence_wording(project, capsys):
    specs, graph = project(three_domains("Draft"), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "references")])
    args = ["check", "boundaries", "--specs", str(specs), "--graph", str(graph)]
    assert main(args) == EXIT_OK                       # divergence only
    assert "suggested divergence-log row" in capsys.readouterr().out
    assert main(args + ["--strict"]) == EXIT_VIOLATIONS
    capsys.readouterr()

    specs2, graph2 = project(three_domains("Frozen"), BASE_NODES,
                             [link("ArticleService", "UserEntity", "imports")])
    assert main(["check", "boundaries", "--specs", str(specs2), "--graph", str(graph2)]) == EXIT_OK
    assert "absence claim: Inference, not Fact" in capsys.readouterr().out


def test_cli_reports_bad_input_as_error(tmp_path, capsys):
    assert main(["check", "boundaries", "--specs", str(tmp_path), "--graph", str(tmp_path / "g.json")]) == EXIT_ERROR
    assert "no oriveda-boundary blocks" in capsys.readouterr().err


def test_cli_json_output(project, capsys):
    specs, graph = project(three_domains("Frozen"), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "references")])
    assert main(["check", "boundaries", "--specs", str(specs), "--graph", str(graph),
                 "--format", "json"]) == EXIT_VIOLATIONS
    out = json.loads(capsys.readouterr().out)
    assert out["findings"][0]["kind"] == "violation"
    assert out["graph_built_at_commit"] == "abc1234"


def test_unquoted_star_glob_gets_a_helpful_error(tmp_path):
    p = tmp_path / "d.md"
    p.write_text(spec("DOM-D", "Draft", ["x"]).replace('- "x"', "- **/x/**"), encoding="utf-8")
    with pytest.raises(SpecError, match="must be quoted"):
        parse_domain_spec(p)


# --- 0.2.0: findings from the first run on a real consuming project -------------

def run(args, capsys):
    code = main(["check", "boundaries", *args])
    return code, capsys.readouterr().out


def test_missing_build_commit_warns_and_fails_strict(project, capsys):
    specs, graph = project(three_domains(), BASE_NODES,
                           [link("ArticleService", "UserEntity", "imports")], commit=None)
    base = ["--specs", str(specs), "--graph", str(graph)]
    code, out = run(base, capsys)
    assert code == EXIT_OK
    assert "no build commit" in out and "graph built at: unknown" in out
    assert run(base + ["--strict"], capsys)[0] == EXIT_VIOLATIONS


def test_coverage_names_what_was_not_checked(project, capsys):
    specs, graph = project(three_domains(), BASE_NODES, [link("ArticleService", "UserEntity", "imports")])
    _, out = run(["--specs", str(specs), "--graph", str(graph)], capsys)
    assert "checked: code-dependency" in out
    assert "not checked: data-access, messaging (graphify supplies no such edges)" in out
    assert "covers only what is listed" in out


def test_specs_without_block_are_listed_and_frozen_ones_fail_strict(project, capsys):
    texts = three_domains()
    texts["risk"] = "---\nid: DOM-RISK\nstatus: Proposal\n---\n\n# Risk\n"
    specs, graph = project(texts, BASE_NODES, [link("ArticleService", "UserEntity", "imports")])
    base = ["--specs", str(specs), "--graph", str(graph)]
    code, out = run(base, capsys)
    assert "specs without a boundary block (not checked): DOM-RISK [Proposal]" in out
    assert "Frozen but has no oriveda-boundary block" not in out

    (specs / "risk.md").write_text("---\nid: DOM-RISK\nstatus: Frozen\n---\n\n# Risk\n", encoding="utf-8")
    code, out = run(base, capsys)
    assert code == EXIT_OK and "DOM-RISK is Frozen but has no oriveda-boundary block" in out
    assert run(base + ["--strict"], capsys)[0] == EXIT_VIOLATIONS


def test_non_domain_notes_without_block_are_ignored(tmp_path):
    from oriveda.specs import load_specs
    (tmp_path / "README.md").write_text("# Notes about domains\n", encoding="utf-8")
    (tmp_path / "a.md").write_text(spec("DOM-A", "Draft", ["a/**"]), encoding="utf-8")
    assert load_specs(tmp_path).unblocked == ()


SHARED_NODES = BASE_NODES + [node("AuditLog", "src/audit/audit.service.ts")]


def with_shared():
    texts = three_domains()
    texts["audit"] = spec("DOM-AUDIT", "Frozen", ["src/audit/**"], kind="shared")
    return texts


def test_any_domain_may_depend_on_a_shared_unit(project):
    specs, graph = project(with_shared(), SHARED_NODES, [link("ArticleService", "AuditLog", "calls"),
                                                          link("UserEntity", "AuditLog", "imports")])
    assert check(load_graphify(graph), load_boundaries(specs)).findings == ()


def test_a_shared_unit_may_depend_on_no_domain(project):
    specs, graph = project(with_shared(), SHARED_NODES, [link("AuditLog", "UserEntity", "imports")])
    [finding] = check(load_graphify(graph), load_boundaries(specs)).findings
    assert (finding.source.domain, finding.reason, finding.kind) == (
        "DOM-AUDIT", "shared-depends-on-domain", "violation")


def test_shared_unit_with_dependency_lists_is_a_spec_error(tmp_path):
    p = tmp_path / "s.md"
    p.write_text(spec("DOM-S", "Draft", ["s/**"], allowed=["DOM-X"], kind="shared"), encoding="utf-8")
    with pytest.raises(SpecError, match="may depend on no domain"):
        parse_domain_spec(p)


def test_exclude_skips_composition_root_and_tests_and_counts_them(project):
    nodes = BASE_NODES + [node("AppModule", "src/app.module.ts"),
                          node("ArticleSpec", "src/article/article.service.spec.ts")]
    texts = three_domains()
    texts["app"] = spec("DOM-APP", "Frozen", ["src/app.module.ts"])
    specs, graph = project(texts, nodes, [link("AppModule", "FollowsEntity", "imports"),
                                          link("ArticleSpec", "FollowsEntity", "imports")])
    boundaries = load_boundaries(specs)
    assert len(check(load_graphify(graph), boundaries).findings) == 2
    report = check(load_graphify(graph), boundaries,
                   exclude=("src/app.module.ts", "**/*.spec.ts"))
    assert report.findings == ()
    assert report.excluded_files == ("src/app.module.ts", "src/article/article.service.spec.ts")


def test_unit_roots_name_undeclared_units(project):
    nodes = BASE_NODES + [node("ShipIt", "src/modules/shipping/ship.service.ts"),
                          node("Label", "src/modules/shipping/label.ts")]
    specs, graph = project(three_domains(), nodes, [link("ShipIt", "Label", "imports"),
                                                    link("ShipIt", "UserEntity", "imports")])
    report = check(load_graphify(graph), load_boundaries(specs), units=("src/modules/*",))
    assert report.unowned_units == (("src/modules/shipping", 2),)


def test_type_only_edges_counted_by_default_and_ignorable(project):
    specs, graph = project(three_domains(), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "imports", type_only=True)])
    g, b = load_graphify(graph), load_boundaries(specs)
    [finding] = check(g, b).findings
    assert finding.type_only_count == 1 and finding.evidence[0].type_only
    report = check(g, b, count_type_only=False)
    assert report.findings == () and report.type_only_ignored == 1


def test_unowned_docs_are_counted_apart_from_source(project):
    nodes = BASE_NODES + [node("ARCHITECTURE", "ARCHITECTURE.md", file_type="document"),
                          node("deps", "package.json")]   # config tagged "code" by the provider
    specs, graph = project(three_domains(), nodes, [link("ARCHITECTURE", "UserEntity", "references"),
                                                    link("deps", "UserEntity", "references"),
                                                    link("ArticleService", "Logger", "imports")])
    report = check(load_graphify(graph), load_boundaries(specs))
    assert report.unowned_files == ("src/shared/logger.ts",)
    assert report.unowned_other == ("ARCHITECTURE.md", "package.json")


def test_json_reports_coverage_and_warnings(project, capsys):
    specs, graph = project(three_domains(), BASE_NODES,
                           [link("ArticleService", "UserEntity", "imports")], commit=None)
    code, out = run(["--specs", str(specs), "--graph", str(graph), "--format", "json"], capsys)
    data = json.loads(out)
    assert data["coverage"]["not_checked"] == ["data-access", "messaging"]
    assert any("no build commit" in w for w in data["warnings"])


def test_suggested_divergence_row_matches_the_log_template_columns(project, capsys):
    specs, graph = project(three_domains("Draft"), BASE_NODES,
                           [link("ArticleService", "FollowsEntity", "references")])
    _, out = run(["--specs", str(specs), "--graph", str(graph)], capsys)
    row = next(l for l in out.splitlines() if l.strip().startswith("| DIV-???"))
    template = (Path(__file__).parents[2] / "templates" / "divergence-log-template.md").read_text()
    header = next(l for l in template.splitlines() if l.startswith("| ID |"))
    assert row.strip().count("|") == header.count("|")
