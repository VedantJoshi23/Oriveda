#!/usr/bin/env python3
"""oriveda validate — mechanizes OV-000's Validation Layer against knowledge/.

Checks, per specification file under knowledge/**/*.md matching OV-*.md or
ADR-*.md:
  - frontmatter present and parses as YAML
  - all fields required by templates/document-template.md are present
  - Frozen/Approved specs have non-blank values for fields the template
    allows to stay blank only pre-Approval
  - id matches its prefix's pattern in .oriveda/taxonomy.yaml, and is
    unique across the repo
  - status is one of the seven lifecycle stages in the root README
  - depends_on / required_by / related_documents / related_decisions
    reference ids that actually exist
  - every file is listed in .oriveda/manifest.yaml with matching
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
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
TAXONOMY_PATH = REPO_ROOT / ".oriveda" / "taxonomy.yaml"
MANIFEST_PATH = REPO_ROOT / ".oriveda" / "manifest.yaml"

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
    level: str  # "error" | "warning"
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
    rel = str(path.relative_to(REPO_ROOT))

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
    rel = str(doc.path.relative_to(REPO_ROOT))
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
        if not reviewers:
            findings.append(Finding(
                rel, "error",
                f"status is '{status}' but 'reviewers' is empty",
            ))


def check_status(doc: ParsedDoc, findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(REPO_ROOT))
    status = doc.frontmatter.get("status")
    if status is not None and status not in LIFECYCLE_STATUSES:
        findings.append(Finding(
            rel, "error",
            f"status '{status}' is not one of the lifecycle stages: "
            f"{sorted(LIFECYCLE_STATUSES)}",
        ))


def check_id(doc: ParsedDoc, taxonomy: dict, seen_ids: dict[str, Path],
             findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(REPO_ROOT))
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
        other = seen_ids[doc_id].relative_to(REPO_ROOT)
        findings.append(Finding(rel, "error", f"id '{doc_id}' is also used by {other}"))
    else:
        seen_ids[doc_id] = doc.path


def check_dependency_graph(doc: ParsedDoc, known_ids: set[str],
                            findings: list[Finding]) -> None:
    rel = str(doc.path.relative_to(REPO_ROOT))
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
        e["id"]: e for e in (manifest.get("documents") or []) + (manifest.get("decisions") or [])
    }

    docs_by_id = {d.frontmatter.get("id"): d for d in docs if d.frontmatter.get("id")}

    for doc_id, entry in manifest_entries.items():
        manifest_path = REPO_ROOT / entry["path"]
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
                str(doc.path.relative_to(REPO_ROOT)), "error",
                f"'{doc_id}' exists on disk but is not listed in .oriveda/manifest.yaml",
            ))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Oriveda specifications.")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    findings: list[Finding] = []
    taxonomy = load_taxonomy()
    manifest = load_manifest()

    spec_files = sorted(
        p for p in KNOWLEDGE_DIR.rglob("*.md")
        if re.match(r"^(OV|ADR)-", p.name)
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

    known_ids = {d.frontmatter.get("id") for d in docs if d.frontmatter.get("id")}
    for doc in docs:
        check_dependency_graph(doc, known_ids, findings)

    check_manifest_sync(docs, manifest, findings)

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    for f in sorted(findings, key=lambda f: (f.file, f.level)):
        print(f"[{f.level.upper()}] {f.file}: {f.message}")

    print(f"\n{len(spec_files)} specification(s) checked, "
          f"{len(errors)} error(s), {len(warnings)} warning(s).")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
