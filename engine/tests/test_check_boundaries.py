"""Tests for `oriveda check boundaries` (ADR-0006 rules 3-5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oriveda.check_boundaries import check, domain_of
from oriveda.cli import EXIT_ERROR, EXIT_OK, EXIT_VIOLATIONS, main
from oriveda.graph import load_graphify
from oriveda.specs import SpecError, load_boundaries, parse_domain_spec


def spec(domain: str, status: str, paths: list[str], allowed=(), forbidden=()) -> str:
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
domain: {domain}
paths:{items(paths)}
allowed_dependencies:{items(allowed)}
forbidden_dependencies:{items(forbidden)}
```
"""


def node(nid: str, source_file: str | None) -> dict:
    n = {"id": nid, "label": nid}
    if source_file is not None:
        n["source_file"] = source_file
    return n


def link(src: str, tgt: str, relation: str, confidence="EXTRACTED", score=1.0, line="L1") -> dict:
    # source_file of a link is where the dependency is stated: the source's file.
    return {"source": src, "target": tgt, "relation": relation, "confidence": confidence,
            "confidence_score": score, "source_file": "", "source_location": line}


@pytest.fixture
def project(tmp_path: Path):
    specs = tmp_path / "domains"
    specs.mkdir()

    def write(specs_text: dict[str, str], nodes: list[dict], links: list[dict]):
        for name, text in specs_text.items():
            (specs / f"{name}.md").write_text(text, encoding="utf-8")
        graph = tmp_path / "graph.json"
        graph.write_text(json.dumps({"directed": False, "nodes": nodes, "links": links,
                                     "built_at_commit": "abc1234"}), encoding="utf-8")
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
