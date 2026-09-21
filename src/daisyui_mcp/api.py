"""Stable, serializable types shared by the MCP server and its adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Protocol


class ContentOrigin(str, Enum):
    """Where the currently served documentation was loaded from."""

    BUNDLED = "bundled"
    CACHE = "cache"
    REMOTE = "remote"


@dataclass(frozen=True, slots=True)
class ComponentSummary:
    """The discoverable metadata for one DaisyUI component."""

    name: str
    description: str


@dataclass(frozen=True, slots=True)
class ComponentDocument:
    """A complete DaisyUI component document."""

    name: str
    markdown: str
    source_url: str | None = None


@dataclass(frozen=True, slots=True)
class SearchMatch:
    """A component or skill match returned by a text search."""

    name: str
    description: str
    score: float


@dataclass(frozen=True, slots=True)
class SkillSummary:
    """The discoverable metadata for one official DaisyUI skill."""

    name: str
    description: str


@dataclass(frozen=True, slots=True)
class SkillDocument:
    """A complete official DaisyUI skill document."""

    name: str
    markdown: str
    source_url: str | None = None


@dataclass(frozen=True, slots=True)
class ResourceDocument:
    """A named MCP resource represented as Markdown or another text payload."""

    uri: str
    mime_type: str
    text: str


@dataclass(frozen=True, slots=True)
class RefreshResult:
    """The outcome of a bounded content refresh attempt."""

    origin: ContentOrigin
    component_count: int
    skill_count: int
    refreshed_at: datetime | None
    message: str


@dataclass(frozen=True, slots=True)
class SkillInstallResult:
    """The outcome of installing the official DaisyUI skill tree."""

    target: Path
    file_count: int
    source_url: str
    used_fallback: bool


@dataclass(frozen=True, slots=True)
class ServerStatus:
    """A point-in-time summary of the content served by the application."""

    origin: ContentOrigin
    component_count: int
    skill_count: int
    refreshed_at: datetime | None
    cache_path: Path | None


class ContentStore(Protocol):
    """Typed boundary for bundled, cached, or refreshed DaisyUI content."""

    def list_components(self) -> tuple[ComponentSummary, ...]:
        """Return all known components in stable display order."""

    def get_component(self, name: str) -> ComponentDocument | None:
        """Return one component document, if it exists."""

    def search(self, query: str) -> tuple[SearchMatch, ...]:
        """Search the discoverable component and skill metadata."""

    def list_skills(self) -> tuple[SkillSummary, ...]:
        """Return all known official skills in stable display order."""

    def get_skill(self, name: str) -> SkillDocument | None:
        """Return one official skill document, if it exists."""

    def refresh(self, *, timeout: float | None = None) -> RefreshResult:
        """Refresh content from its configured official source."""

    def status(self) -> ServerStatus:
        """Return the current content status."""

    def get_resource(self, uri: str) -> ResourceDocument | None:
        """Return a named MCP resource, if it exists."""
