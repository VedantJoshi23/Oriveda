#!/usr/bin/env python3
"""oriveda validate — mechanizes OV-000's Validation Layer against knowledge/.

Checks, per specification file under knowledge/**/*.md matching OV-*.md,
ADR-*.md or PRM-*.md (or, with --root PROJECT, a target project's
knowledge/**/*.md matching its project-scope prefixes; ADR-0004):
  - frontmatter present and parses as YAML
  - all fields required by templates/document-template.md are present
  - Frozen/Approved specs have non-blank values for fields the template
    allows to stay blank only pre-Approval
  - id matches its prefix's pattern in .oriveda/taxonomy.yaml, and is
    unique across the repo
  - status is one of the seven lifecycle stages in the root README
  - depends_on / required_by / related_documents / related_decisions
    reference ids that actually exist
  - Frozen/Approved specs with empty reviewers pass only with an explicit
    `reviewers_unrecorded: true` marker, reported as info (ADR-0007 rule 4)
  - with --root: the divergence log at knowledge/decisions/DIVERGENCE-LOG.md
    has no open row against a Frozen spec without a Due date, and no open
    row past its Due date (ADR-0007 rules 2 and 5)
  - every file is listed in .oriveda/manifest.yaml (a target project's
    knowledge/manifest.yaml with --root) with matching
    id/status/version/milestone, and every manifest entry's path exists
    (bidirectional sync, catches orphans per Contribution Rule 6)

Frontmatter may be written two ways in this repo: raw `---`-delimited at
the very top of the file (what the template specifies), or wrapped in a
```yaml fenced block under a "# Metadata" heading. Both parse; the second
form is flagged as a warning, since the template only documents the first.

Exit code 1 if any error is found. Warnings alone do not fail the run
unless --strict is passed.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
TAXONOMY_PATH = REPO_ROOT / ".oriveda" / "taxonomy.yaml"
MANIFEST_PATH = REPO_ROOT / ".oriveda" / "manifest.yaml"

# The repository being validated: this one by default, a target project with
# --root (ADR-0004). Paths in findings and manifests are relative to it.
BASE = REPO_ROOT

LIFECYCLE_STATUSES = {
    "Proposal",
    "Draft",
    "Architecture Review",
    "Revision",
    "Approved",
    "Frozen",
    "Superseded",
}

# Fields templates/document-template.md and templates/decision-template.md
# both declare. Order mirrors the template.
REQUIRED_FIELDS = [
    "id", "title", "version", "status", "owner", "reviewers", "created",
    "updated", "milestone", "category", "priority", "depends_on",
    "required_by", "related_documents", "related_domains",
    "related_features", "related_decisions", "tags", "risk", "complexity",
]

# Fields the template leaves blank in Proposal state but which a mature
# (Approved/Frozen) spec should have filled in.
FILLED_WHEN_MATURE = [
    "title", "version", "owner", "created", "updated", "milestone",
    "category", "priority", "risk", "complexity",
]
MATURE_STATUSES = {"Approved", "Frozen", "Superseded"}

RAW_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCED_FRONTMATTER_RE = re.compile(
    r"```yaml\n---\n(.*?)\n---\n```", re.DOTALL
)


@dataclass
class Finding:
    file: str
    level: str  # "error" | "warning" | "info"
    message: str


@dataclass
class ParsedDoc:
    path: Path
    frontmatter: dict
    format: str  # "raw" | "fenced"


def load_taxonomy() -> dict:
    return yaml.safe_load(TAXONOMY_PATH.read_text())["prefixes"]


def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def parse_frontmatter(path: Path, findings: list[Finding]) -> ParsedDoc | None:
    text = path.read_text()
    rel = str(path.relative_to(BASE))

    m = RAW_FRONTMATTER_RE.match(text)
    if m:
        fmt = "raw"
    else:
        m = FENCED_FRONTMATTER_RE.search(text)
        fmt = "fenced"

    if not m:
        findings.append(Finding(rel, "error", "no parseable frontmatter found"))
        return None

    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        findings.append(Finding(rel, "error", f"frontmatter is not valid YAML: {e}"))
        return None

    if not isinstance(data, dict):
        findings.append(Finding(rel, "error", "frontmatter did not parse to a mapping"))
        return None

    if fmt == "fenced":
        findings.append(Finding(
            rel, "warning",
            "frontmatter is wrapped in a fenced code block under a heading; "
            "templates/document-template.md specifies raw frontmatter at the "
            "top of the file",
        ))

    return ParsedDoc(path=path, frontmatter=data, format=fmt)


def check_required_fields(doc: ParsedDoc, findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(BASE))
    for f in REQUIRED_FIELDS:
        if f not in doc.frontmatter:
            findings.append(Finding(rel, "error", f"missing required field '{f}'"))

    status = doc.frontmatter.get("status")
    if status in MATURE_STATUSES:
        for f in FILLED_WHEN_MATURE:
            v = doc.frontmatter.get(f)
            if v in (None, "", []):
                findings.append(Finding(
                    rel, "error",
                    f"status is '{status}' but field '{f}' is still blank",
                ))
        reviewers = doc.frontmatter.get("reviewers") or []
        if not reviewers and doc.frontmatter.get("reviewers_unrecorded") is True:
            # Honest history (ADR-0007 rule 4): never back-fill a review that
            # was not recorded at the time.
            findings.append(Finding(
                rel, "info",
                f"status is '{status}' with reviewers unrecorded (reviewers_unrecorded: true)",
            ))
        elif not reviewers:
            findings.append(Finding(
                rel, "error",
                f"status is '{status}' but 'reviewers' is empty; if they were never "
                f"recorded, set reviewers_unrecorded: true instead of adding names (ADR-0007)",
            ))


def check_status(doc: ParsedDoc, findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(BASE))
    status = doc.frontmatter.get("status")
    if status is not None and status not in LIFECYCLE_STATUSES:
        findings.append(Finding(
            rel, "error",
            f"status '{status}' is not one of the lifecycle stages: "
            f"{sorted(LIFECYCLE_STATUSES)}",
        ))


def check_id(doc: ParsedDoc, taxonomy: dict, seen_ids: dict[str, Path],
             findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(BASE))
    doc_id = doc.frontmatter.get("id")
    if not doc_id:
        return

    prefix = doc_id.split("-")[0]
    rule = taxonomy.get(prefix)
    if rule is None:
        findings.append(Finding(rel, "error", f"id '{doc_id}' has no matching prefix rule in taxonomy.yaml"))
    elif not re.fullmatch(rule["pattern"], doc_id):
        findings.append(Finding(
            rel, "error",
            f"id '{doc_id}' does not match pattern '{rule['pattern']}' for prefix '{prefix}'",
        ))

    if doc_id in seen_ids and seen_ids[doc_id] != doc.path:
        other = seen_ids[doc_id].relative_to(BASE)
        findings.append(Finding(rel, "error", f"id '{doc_id}' is also used by {other}"))
    else:
        seen_ids[doc_id] = doc.path


def check_dependency_graph(doc: ParsedDoc, known_ids: set[str],
                            findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(BASE))
    for field_name in ("depends_on", "required_by", "related_documents", "related_decisions"):
        refs = doc.frontmatter.get(field_name) or []
        for ref in refs:
            if ref not in known_ids:
                findings.append(Finding(
                    rel, "error",
                    f"{field_name} references '{ref}', which does not exist",
                ))


def check_manifest_sync(docs: list[ParsedDoc], manifest: dict,
                         findings: list[Finding]) -> None:
    manifest_entries = {
        e["id"]: e
        for e in (manifest.get("documents") or []) + (manifest.get("decisions") or [])
        + [p for p in (manifest.get("prompts") or []) if "path" in p]
    }

    docs_by_id = {d.frontmatter.get("id"): d for d in docs if d.frontmatter.get("id")}

    for doc_id, entry in manifest_entries.items():
        manifest_path = BASE / entry["path"]
        if not manifest_path.exists():
            findings.append(Finding(
                str(entry["path"]), "error",
                f"manifest lists '{doc_id}' at this path, but the file does not exist",
            ))
            continue
        doc = docs_by_id.get(doc_id)
        if doc is None:
            continue
        for field_name in ("status", "version", "milestone"):
            manifest_val = entry.get(field_name)
            doc_val = doc.frontmatter.get(field_name)
            if manifest_val != doc_val:
                findings.append(Finding(
                    str(entry["path"]), "error",
                    f"manifest says {field_name}='{manifest_val}' but file has "
                    f"{field_name}='{doc_val}'",
                ))

    for doc_id, doc in docs_by_id.items():
        if doc_id not in manifest_entries:
            findings.append(Finding(
                str(doc.path.relative_to(BASE)), "error",
                f"'{doc_id}' exists on disk but is not listed in .oriveda/manifest.yaml",
            ))


DIVERGENCE_LOG = Path("knowledge") / "decisions" / "DIVERGENCE-LOG.md"
_SPEC_REF_RE = re.compile(r"\b([A-Z]+-[A-Z0-9][A-Z0-9-]*)\b")


def check_divergence_log(docs: list[ParsedDoc], findings: list[Finding],
                         today: datetime.date | None = None) -> None:
    """ADR-0007 rules 2 and 5: open rows against Frozen specs need a Due date,
    and no open row may be past its Due date."""
    path = BASE / DIVERGENCE_LOG
    if not path.exists():
        return
    today = today or datetime.date.today()
    rel = str(DIVERGENCE_LOG)
    status_by_id = {d.frontmatter.get("id"): d.frontmatter.get("status") for d in docs}
    header: list[str] | None = None
    for line in path.read_text().splitlines():
        if not line.lstrip().startswith("|"):
            header = None  # any non-table line ends the current table
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue  # the |---|---| separator row
        row = dict(zip(header, cells))
        div_id = row.get("id", "")
        if not re.fullmatch(r"DIV-[0-9]{3}", div_id) or row.get("status", "").lower() != "open":
            continue
        ref = _SPEC_REF_RE.search(row.get("spec §", "").replace("`", ""))
        spec_id = ref.group(1) if ref else None
        due_text = row.get("due", "")
        due = None
        if due_text:
            try:
                due = datetime.date.fromisoformat(due_text)
            except ValueError:
                findings.append(Finding(rel, "error", f"{div_id}: Due '{due_text}' is not a YYYY-MM-DD date"))
                continue
        if due is not None and due < today:
            findings.append(Finding(rel, "error", f"{div_id}: still open after its Due date {due} (ADR-0007 rule 2)"))
        elif due is None and spec_id and status_by_id.get(spec_id) == "Frozen":
            findings.append(Finding(
                rel, "error",
                f"{div_id}: open against Frozen spec {spec_id} without a Due date; a disagreement "
                f"with a Frozen spec is a violation unless logged as a dated adoption entry (ADR-0007 rule 2)",
            ))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Oriveda specifications.")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--root", type=Path, metavar="PROJECT",
                        help="validate a target project's knowledge/ instead of this repository "
                             "(ADR-0004): its project-scope prefixes, knowledge/manifest.yaml, "
                             "and references to Oriveda's own OV-/ADR-/PRM- ids")
    args = parser.parse_args()

    global BASE
    findings: list[Finding] = []
    taxonomy = load_taxonomy()
    framework_manifest = load_manifest()
    external_ids: set[str] = set()

    if args.root is None:
        manifest = framework_manifest
        knowledge_dir = KNOWLEDGE_DIR
        prefixes = ["OV", "ADR", "PRM"]
    else:
        BASE = args.root.resolve()
        knowledge_dir = BASE / "knowledge"
        manifest_path = knowledge_dir / "manifest.yaml"
        if not manifest_path.exists():
            print(f"[ERROR] {manifest_path}: a target project lists its specifications here")
            return 1
        manifest = yaml.safe_load(manifest_path.read_text())
        # Project-scope prefixes, plus the project's own ADR series and any prefixes the
        # project adds in knowledge/taxonomy.yaml (ADR-0004).
        taxonomy = {k: v for k, v in taxonomy.items() if v.get("scope") == "project" or k == "ADR"}
        project_taxonomy = knowledge_dir / "taxonomy.yaml"
        if project_taxonomy.exists():
            for k, v in (yaml.safe_load(project_taxonomy.read_text()).get("prefixes") or {}).items():
                taxonomy.setdefault(k, v)
        prefixes = sorted(taxonomy)
        external_ids = {
            e["id"] for e in (framework_manifest.get("documents") or [])
            + (framework_manifest.get("decisions") or []) + (framework_manifest.get("prompts") or [])
        }

    spec_files = sorted(
        p for p in knowledge_dir.rglob("*.md")
        if re.match(r"^(" + "|".join(prefixes) + r")-", p.name)
    )

    docs: list[ParsedDoc] = []
    seen_ids: dict[str, Path] = {}
    for path in spec_files:
        doc = parse_frontmatter(path, findings)
        if doc is None:
            continue
        docs.append(doc)
        check_required_fields(doc, findings)
        check_status(doc, findings)
        check_id(doc, taxonomy, seen_ids, findings)

    known_ids = {d.frontmatter.get("id") for d in docs if d.frontmatter.get("id")} | external_ids
    for doc in docs:
        check_dependency_graph(doc, known_ids, findings)

    check_manifest_sync(docs, manifest, findings)
    if args.root is not None:
        check_divergence_log(docs, findings)

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]
    infos = [f for f in findings if f.level == "info"]

    for f in sorted(findings, key=lambda f: (f.file, f.level)):
        print(f"[{f.level.upper()}] {f.file}: {f.message}")

    print(f"\n{len(spec_files)} specification(s) checked, "
          f"{len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info.")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
