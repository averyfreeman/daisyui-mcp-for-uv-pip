"""Typed local catalog used by the compatibility MCP tools."""

from __future__ import annotations

import re
from pathlib import Path

from .api import ComponentDocument, ComponentSummary

_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_COMPONENT_DIRECTORY_NAME = "components"


def default_components_directory() -> Path:
    """Return the first component directory available in this checkout/install."""

    package_directory = Path(__file__).parent
    repository_directory = package_directory.parents[1]
    candidates = (
        package_directory / "data" / _COMPONENT_DIRECTORY_NAME,
        repository_directory / _COMPONENT_DIRECTORY_NAME,
    )
    return next(
        (candidate for candidate in candidates if candidate.is_dir()),
        candidates[0],
    )


def _normalise_name(name: str) -> str:
    """Normalise and validate a user-supplied component name."""

    normalised = name.strip().lower()
    if not _NAME_PATTERN.fullmatch(normalised):
        return ""
    return normalised


def _parse_summary(path: Path, markdown: str) -> ComponentSummary | None:
    """Extract the first component heading and its following description."""

    fallback_name = _normalise_name(path.stem)
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("### "):
            continue
        name = _normalise_name(line[4:]) or fallback_name
        if not name:
            return None
        description = next(
            (
                candidate.strip()
                for candidate in lines[index + 1 :]
                if candidate.strip()
            ),
            "",
        )
        return ComponentSummary(name=name, description=description)
    if fallback_name:
        return ComponentSummary(name=fallback_name, description="")
    return None


class ComponentCatalog:
    """Read component Markdown files from one controlled directory."""

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or default_components_directory()

    def list_components(self) -> tuple[ComponentSummary, ...]:
        """Return parseable component summaries sorted by canonical name."""

        summaries: list[ComponentSummary] = []
        if not self.directory.is_dir():
            return ()
        for path in sorted(self.directory.glob("*.md")):
            try:
                markdown = path.read_text(encoding="utf-8")
            except OSError:
                continue
            summary = _parse_summary(path, markdown)
            if summary is not None:
                summaries.append(summary)
        return tuple(summaries)

    def get_component(self, name: str) -> ComponentDocument | None:
        """Return one component document without permitting path traversal."""

        normalised = _normalise_name(name)
        if not normalised or not self.directory.is_dir():
            return None
        path = self.directory / f"{normalised}.md"
        try:
            markdown = path.read_text(encoding="utf-8")
        except OSError:
            return None
        summary = _parse_summary(path, markdown)
        if summary is None:
            return None
        return ComponentDocument(name=summary.name, markdown=markdown)
