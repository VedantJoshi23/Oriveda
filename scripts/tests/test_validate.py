"""Tests for scripts/validate.py: the optional `validator:` project settings
(ADR-0004), and proof that without them the output is unchanged from v0.2.0.

Run with: python -m pytest scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS.parent
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "project-vocabulary"
V020 = "8ed8df1"  # the release before project settings existed

FULL_SETTINGS = """
validator:
  lifecycle_aliases: {Review: Proposal, Accepted: Frozen}
  constitution: knowledge/constitution/CONSTITUTION.md
  advisory_paths: ["docs/**", "*.md"]
"""


def _load(path: Path, name: str):
    """A fresh copy of a validator module, so module globals don't leak between runs."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up here
    spec.loader.exec_module(module)
    # A copy loaded from elsewhere must still read this repository's taxonomy/manifest.
    module.REPO_ROOT = module.BASE = REPO_ROOT
    module.KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
    module.TAXONOMY_PATH = REPO_ROOT / ".oriveda" / "taxonomy.yaml"
    module.MANIFEST_PATH = REPO_ROOT / ".oriveda" / "manifest.yaml"
    return module


def _run(module, *args: str) -> tuple[int, str]:
    out = io.StringIO()
    argv, sys.argv = sys.argv, ["validate.py", *args]
    try:
        with contextlib.redirect_stdout(out):
            code = module.main()
    finally:
        sys.argv = argv
    return code, out.getvalue()


def validate(*args: str) -> tuple[int, str]:
    return _run(_load(SCRIPTS / "validate.py", "validate_current"), *args)


@pytest.fixture
def v020(tmp_path_factory):
    try:
        source = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{V020}:scripts/validate.py"],
                                capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip(f"git history with {V020} is not available")
    path = tmp_path_factory.mktemp("v020") / "validate_v020.py"
    path.write_text(source)
    return lambda *args: _run(_load(path, "validate_v020"), *args)


def project(tmp_path: Path, settings: str = "") -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    if settings:
        with (root / "knowledge" / "manifest.yaml").open("a") as f:
            f.write(settings)
    return root


def lines(output: str, level: str) -> list[str]:
    return [line for line in output.splitlines() if line.startswith(f"[{level}]")]


# --- Without settings, nothing changes -------------------------------------

@pytest.mark.parametrize("strict", [[], ["--strict"]])
def test_framework_output_is_identical_to_v020(v020, strict):
    assert validate(*strict) == v020(*strict)


@pytest.mark.parametrize("strict", [[], ["--strict"]])
def test_project_output_without_settings_is_identical_to_v020(v020, tmp_path, strict):
    root = str(project(tmp_path))
    assert validate("--root", root, *strict) == v020("--root", root, *strict)


@pytest.mark.parametrize("empty", ["\nvalidator:\n", "\nvalidator: {}\n",
                                   "\nvalidator:\n  lifecycle_aliases: {}\n  advisory_paths: []\n"])
def test_empty_settings_are_identical_to_v020(v020, tmp_path, empty):
    plain = str(project(tmp_path / "plain"))
    configured = str(project(tmp_path / "configured", empty))
    assert validate("--root", configured) == v020("--root", plain)


def test_fixture_reproduces_all_three_groups_without_settings(tmp_path):
    code, out = validate("--root", str(project(tmp_path)))
    errors = lines(out, "ERROR")
    assert code == 1
    assert sum("is not one of the lifecycle stages" in e for e in errors) == 2   # A
    assert sum("'CONSTITUTION', which does not exist" in e for e in errors) == 3  # B
    assert len(errors) == 9                                                      # + 4 advisory (C)


# --- Done-when: all three settings together --------------------------------

def test_all_settings_clear_every_group(tmp_path):
    code, out = validate("--root", str(project(tmp_path, FULL_SETTINGS)))
    assert code == 0, out
    assert lines(out, "ERROR") == [] and lines(out, "WARNING") == []
    assert len([i for i in lines(out, "INFO") if "links advisory document" in i]) == 4


# --- lifecycle_aliases ------------------------------------------------------

ALIASES = "\nvalidator:\n  lifecycle_aliases: {Review: Proposal, Accepted: Frozen}\n"


def test_aliases_accept_project_words_and_report_both(tmp_path):
    _, out = validate("--root", str(project(tmp_path, ALIASES)))
    assert not any("lifecycle stages" in e for e in lines(out, "ERROR"))
    infos = lines(out, "INFO")
    assert any("'Review' -> Proposal" in i and "1 specification(s)" in i for i in infos)
    assert any("'Accepted' -> Frozen" in i and "1 specification(s)" in i for i in infos)
    # Only the aliases changed; the Constitution and advisory errors remain.
    assert len(lines(out, "ERROR")) == 7


def test_lifecycle_rules_run_on_the_mapped_stage(tmp_path):
    root = project(tmp_path, ALIASES)
    adr = root / "knowledge" / "decisions" / "ADR-0001-payment-provider.md"
    adr.write_text(adr.read_text().replace("reviewers:\n  - Owner\n", "reviewers: []\n"))
    _, out = validate("--root", str(root))
    assert any("ADR-0001" in e and "status is 'Accepted' (alias of Frozen) but 'reviewers' is empty" in e
               for e in lines(out, "ERROR"))


def test_divergence_log_sees_the_mapped_stage(tmp_path):
    root = project(tmp_path, ALIASES)
    (root / "knowledge" / "decisions" / "DIVERGENCE-LOG.md").write_text(
        "| ID | Spec § | Status | Due |\n|---|---|---|---|\n| DIV-001 | ADR-0001 §2 | open | |\n")
    _, out = validate("--root", str(root))
    assert any("DIV-001: open against Frozen spec ADR-0001" in e for e in lines(out, "ERROR"))


def test_alias_to_an_unknown_stage_is_rejected(tmp_path):
    code, out = validate("--root", str(project(
        tmp_path, "\nvalidator:\n  lifecycle_aliases: {Review: Reviewing}\n")))
    assert code == 1
    assert any("maps 'Review' to 'Reviewing', which is not one of the lifecycle stages" in e
               for e in lines(out, "ERROR"))
    # The rejected alias is not applied.
    assert any("status 'Review' is not one of the lifecycle stages" in e for e in lines(out, "ERROR"))


def test_alias_cannot_redefine_a_canonical_stage(tmp_path):
    code, out = validate("--root", str(project(
        tmp_path, "\nvalidator:\n  lifecycle_aliases: {Draft: Frozen}\n")))
    assert code == 1
    assert any("cannot redefine 'Draft'" in e for e in lines(out, "ERROR"))


# --- constitution -----------------------------------------------------------

def test_constitution_resolves_by_id_and_path_when_set(tmp_path):
    root = project(tmp_path, "\nvalidator:\n  constitution: knowledge/constitution/CONSTITUTION.md\n")
    dom = root / "knowledge" / "domains" / "DOM-ORDERS.md"
    dom.write_text(dom.read_text().replace(
        "depends_on: [CONSTITUTION, ADR-0001]",
        "depends_on: [knowledge/constitution/CONSTITUTION.md, ADR-0001]"))
    _, out = validate("--root", str(root))
    assert not any("CONSTITUTION" in e for e in lines(out, "ERROR"))
    assert any("Constitution 'CONSTITUTION' is at knowledge/constitution/CONSTITUTION.md" in i
               for i in lines(out, "INFO"))


def test_constitution_unset_keeps_current_discovery(v020, tmp_path):
    root = str(project(tmp_path, "\nvalidator:\n  lifecycle_aliases: {Review: Proposal}\n"))
    _, out = validate("--root", root)
    _, old = v020("--root", root)
    constitution_errors = [e for e in lines(out, "ERROR") if "CONSTITUTION" in e]
    assert len(constitution_errors) == 3
    assert constitution_errors == [e for e in lines(old, "ERROR") if "CONSTITUTION" in e]


def test_constitution_path_without_a_spec_is_an_error(tmp_path):
    code, out = validate("--root", str(project(
        tmp_path, "\nvalidator:\n  constitution: knowledge/constitution/MISSING.md\n")))
    assert code == 1
    assert any("validator.constitution is 'knowledge/constitution/MISSING.md'" in e
               for e in lines(out, "ERROR"))


# --- advisory_paths ---------------------------------------------------------

ADVISORY = '\nvalidator:\n  advisory_paths: ["docs/**", "*.md"]\n'


def test_advisory_links_are_info_not_errors(tmp_path):
    _, out = validate("--root", str(project(tmp_path, ADVISORY)))
    infos = [i for i in lines(out, "INFO") if "links advisory document" in i]
    assert sorted(i.split("advisory document ")[1].split(" ")[0] for i in infos) == [
        "DESIGN.md", "PRODUCT.md", "docs/architecture.md", "docs/guides/theming.md"]
    assert not any("advisory" in e or "PRODUCT" in e for e in lines(out, "ERROR"))


def test_frozen_spec_depending_on_advisory_content_stays_an_error(tmp_path):
    root = project(tmp_path, ADVISORY)
    dom = root / "knowledge" / "domains" / "DOM-ORDERS.md"
    dom.write_text(dom.read_text().replace("[CONSTITUTION, ADR-0001]", "[ADR-0001, docs/architecture.md]"))
    code, out = validate("--root", str(root))
    assert code == 1
    assert any("DOM-ORDERS" in e and "depends_on advisory document docs/architecture.md" in e
               for e in lines(out, "ERROR"))


def test_unfrozen_spec_depending_on_advisory_content_is_a_warning(tmp_path):
    root = project(tmp_path, ADVISORY)
    adr = root / "knowledge" / "decisions" / "ADR-0002-theme.md"
    adr.write_text(adr.read_text().replace("depends_on: [CONSTITUTION]", "depends_on: [PRODUCT.md]"))
    _, out = validate("--root", str(root))
    assert any("ADR-0002" in w and "depends_on advisory document PRODUCT.md" in w
               for w in lines(out, "WARNING"))


def test_advisory_reference_to_a_missing_file_stays_an_error(tmp_path):
    root = project(tmp_path, ADVISORY)
    (root / "docs" / "architecture.md").unlink()
    _, out = validate("--root", str(root))
    assert any("'docs/architecture.md', which matches validator.advisory_paths but "
               "docs/architecture.md does not exist" in e for e in lines(out, "ERROR"))


def test_dangling_bare_id_is_not_mistaken_for_an_advisory_stem(v020, tmp_path):
    # `CONSTITUTION` + ".md" matches "*.md", but no such file exists: it is a dangling id.
    root = str(project(tmp_path, ADVISORY))
    _, out = validate("--root", root)
    _, old = v020("--root", root)
    errors = [e for e in lines(out, "ERROR") if "CONSTITUTION" in e]
    assert len(errors) == 3
    assert errors == [e for e in lines(old, "ERROR") if "CONSTITUTION" in e]


def test_single_star_does_not_cross_directories(tmp_path):
    _, out = validate("--root", str(project(tmp_path, '\nvalidator:\n  advisory_paths: ["*.md"]\n')))
    errors = lines(out, "ERROR")
    assert any("'docs/architecture.md', which does not exist" in e for e in errors)
    assert not any("PRODUCT.md" in e for e in errors)


# --- forward compatibility --------------------------------------------------

def test_unknown_setting_is_a_warning_not_a_failure(tmp_path):
    code, out = validate("--root", str(project(tmp_path, FULL_SETTINGS + "  future_setting: true\n")))
    assert code == 0
    assert any("validator.future_setting is not a setting this validator knows" in w
               for w in lines(out, "WARNING"))
