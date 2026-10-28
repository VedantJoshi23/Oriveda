"""Load Domain Specifications and their `oriveda-boundary` blocks (ADR-0006 rule 4)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Frontmatter as Oriveda writes it: optionally wrapped in a ```yaml fence
# under a "# Metadata" heading, delimited by --- lines.
_FRONTMATTER = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*$", re.S | re.M)
_BOUNDARY_BLOCK = re.compile(r"^```yaml[ \t]+oriveda-boundary[ \t]*\n(.*?)^```", re.S | re.M)


class SpecError(ValueError):
    """A specification is malformed or internally inconsistent."""


@dataclass(frozen=True)
class DomainBoundary:
    domain: str
    spec_id: str
    status: str
    source: Path
    paths: tuple[str, ...]
    allowed: frozenset[str] = field(default_factory=frozenset)
    forbidden: frozenset[str] = field(default_factory=frozenset)

    @property
    def frozen(self) -> bool:
        return self.status.lower() == "frozen"


def _str_list(value, key: str, source: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise SpecError(f"{source}: `{key}` must be a list of strings")
    return tuple(value)


def _load_yaml(text: str, what: str, source: Path):
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        hint = ""
        if "alias" in str(exc):
            hint = " (a value starting with `*` must be quoted, e.g. \"**/billing/**\")"
        raise SpecError(f"{source}: invalid YAML in {what}{hint}: {exc}") from exc


def parse_domain_spec(path: Path) -> DomainBoundary | None:
    """Return the spec's boundary, or None if it has no oriveda-boundary block."""
    text = path.read_text(encoding="utf-8")
    blocks = _BOUNDARY_BLOCK.findall(text)
    if not blocks:
        return None
    if len(blocks) > 1:
        raise SpecError(f"{path}: more than one oriveda-boundary block")

    # Frontmatter precedes the first section heading; a `---` rule further
    # down the body must not be mistaken for it.
    heading = re.search(r"^## ", text, re.M)
    fm_match = _FRONTMATTER.search(text[: heading.start()] if heading else text)
    meta = (_load_yaml(fm_match.group(1), "frontmatter", path) if fm_match else None) or {}
    if not isinstance(meta, dict):
        raise SpecError(f"{path}: frontmatter is not a mapping")

    block = _load_yaml(blocks[0], "oriveda-boundary block", path) or {}
    if not isinstance(block, dict):
        raise SpecError(f"{path}: oriveda-boundary block is not a mapping")
    domain = block.get("domain")
    if not isinstance(domain, str) or not domain:
        raise SpecError(f"{path}: oriveda-boundary block needs a `domain`")
    paths = _str_list(block.get("paths"), "paths", path)
    if not paths:
        raise SpecError(f"{path}: oriveda-boundary block needs at least one path")

    allowed = frozenset(_str_list(block.get("allowed_dependencies"), "allowed_dependencies", path))
    forbidden = frozenset(_str_list(block.get("forbidden_dependencies"), "forbidden_dependencies", path))
    if allowed & forbidden:
        raise SpecError(f"{path}: {sorted(allowed & forbidden)} both allowed and forbidden")

    return DomainBoundary(
        domain=domain,
        spec_id=str(meta.get("id") or domain),
        status=str(meta.get("status") or "Proposal"),
        source=path,
        paths=paths,
        allowed=allowed,
        forbidden=forbidden,
    )


def load_boundaries(specs_dir: Path) -> list[DomainBoundary]:
    """Every boundary declared under specs_dir; duplicate domains are an error."""
    found: dict[str, DomainBoundary] = {}
    for path in sorted(specs_dir.rglob("*.md")):
        boundary = parse_domain_spec(path)
        if boundary is None:
            continue
        if boundary.domain in found:
            raise SpecError(
                f"{boundary.domain} declared twice: {found[boundary.domain].source} and {path}"
            )
        found[boundary.domain] = boundary
    return list(found.values())
