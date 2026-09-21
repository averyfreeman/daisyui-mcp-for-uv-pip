"""Bundled, cached, and bounded-runtime DaisyUI content."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import cast
from urllib.request import Request, urlopen

from platformdirs import user_cache_dir

from .api import (
    ComponentDocument,
    ComponentSummary,
    ContentOrigin,
    RefreshResult,
    ResourceDocument,
    SearchMatch,
    ServerStatus,
    SkillDocument,
    SkillInstallResult,
    SkillSummary,
)
from .catalog import ComponentCatalog
from .skills import install_official_skills

INSTALL_DOCS_URL = "https://daisyui.com/docs/install/"
LLMS_URL = "https://daisyui.com/llms.txt"
SKILLS_URL = "https://daisyui.com/docs/skill/"
_COMPONENTS_HEADING = "## daisyUI components"
_MAX_TEXT_BYTES = 2 * 1024 * 1024
_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TextFetcher = Callable[[str, float], str]


def _fetch_text(url: str, timeout: float) -> str:
    request = Request(
        url,
        headers={
            "Accept": "text/plain,text/markdown;q=0.9,*/*;q=0.1",
            "User-Agent": "daisyui-mcp/0.1",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = cast(bytes, response.read(_MAX_TEXT_BYTES + 1))
    if len(payload) > _MAX_TEXT_BYTES:
        raise ValueError("DaisyUI documentation exceeded the safety size limit")
    return payload.decode("utf-8")


def _slugify(title: str) -> str:
    aliases = {
        "browser mockup": "mockup-browser",
        "code mockup": "mockup-code",
        "phone mockup": "mockup-phone",
        "window mockup": "mockup-window",
        "fab": "fab",
        "file input": "file-input",
        "hover 3d": "hover-3d",
        "join": "join",
        "text rotate": "text-rotate",
        "theme controller": "theme-controller",
    }
    cleaned = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return aliases.get(cleaned, cleaned.replace(" ", "-"))


def _component_description(markdown: str) -> str:
    lines = markdown.splitlines()[1:]
    for line in lines:
        candidate = line.strip()
        if (
            candidate
            and not candidate.startswith("#")
            and not candidate.startswith("[")
        ):
            return candidate
    return ""


def parse_remote_components(text: str) -> dict[str, ComponentDocument]:
    """Parse component sections from the official DaisyUI llms document."""

    marker = re.search(
        rf"^{re.escape(_COMPONENTS_HEADING)}\s*$", text, flags=re.MULTILINE
    )
    if marker is None:
        raise ValueError("DaisyUI llms document has no component section")
    section = text[marker.end() :]
    headers = list(re.finditer(r"^### (.+?)\s*$", section, flags=re.MULTILINE))
    components: dict[str, ComponentDocument] = {}
    for index, header in enumerate(headers):
        start = header.start()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(section)
        markdown = section[start:end].strip() + "\n"
        if "#### Class names" not in markdown or "#### Syntax" not in markdown:
            continue
        title = header.group(1).strip()
        name = _slugify(title)
        if not name:
            continue
        components[name] = ComponentDocument(
            name=name,
            markdown=markdown,
            source_url=f"https://daisyui.com/components/{name}/",
        )
    if not components:
        raise ValueError("DaisyUI llms document contained no parseable components")
    return components


def _summary(document: ComponentDocument) -> ComponentSummary:
    return ComponentSummary(
        name=document.name,
        description=_component_description(document.markdown),
    )


def _normalise_name(name: str) -> str:
    candidate = name.strip().lower()
    return candidate if _NAME_PATTERN.fullmatch(candidate) else ""


def _normalise_query(query: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", query.strip().lower()).strip("-")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DaisyUIContentStore:
    """Serve official DaisyUI content with cache and bundled fallback semantics."""

    def __init__(
        self,
        *,
        cache_directory: Path | None = None,
        fetcher: TextFetcher | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.bundled_directory = Path(__file__).parent / "data"
        self.bundled_catalog = ComponentCatalog(self.bundled_directory / "components")
        self.bundled_skills = self.bundled_directory / "skills" / "daisyui"
        self.cache_directory = (
            cache_directory
            if cache_directory is not None
            else Path(user_cache_dir("daisyui-mcp"))
        )
        self.cache_file = self.cache_directory / "content.json"
        self.fetcher = fetcher or _fetch_text
        self.timeout = timeout
        self._remote_components: dict[str, ComponentDocument] = {}
        self._origin = ContentOrigin.BUNDLED
        self._refreshed_at: datetime | None = None
        self._load_cache()

    def _load_cache(self) -> None:
        try:
            payload = json.loads(self.cache_file.read_text(encoding="utf-8"))
            components = payload.get("components", {})
            if not isinstance(components, dict):
                return
            parsed: dict[str, ComponentDocument] = {}
            for name, value in components.items():
                if not isinstance(name, str) or not isinstance(value, dict):
                    continue
                markdown = value.get("markdown")
                if isinstance(markdown, str):
                    source_url = value.get("source_url")
                    parsed[name] = ComponentDocument(
                        name=name,
                        markdown=markdown,
                        source_url=source_url if isinstance(source_url, str) else None,
                    )
            if parsed:
                self._remote_components = parsed
                self._origin = ContentOrigin.CACHE
                refreshed_at = payload.get("refreshed_at")
                if isinstance(refreshed_at, str):
                    self._refreshed_at = datetime.fromisoformat(refreshed_at)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return

    def _write_cache(
        self, components: dict[str, ComponentDocument], refreshed_at: datetime
    ) -> None:
        payload = {
            "source_url": LLMS_URL,
            "refreshed_at": refreshed_at.isoformat(),
            "components": {
                name: {
                    "markdown": document.markdown,
                    "source_url": document.source_url,
                }
                for name, document in components.items()
            },
        }
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        temporary = self.cache_file.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.cache_file)

    def _components(self) -> dict[str, ComponentDocument]:
        if self._remote_components:
            return dict(self._remote_components)
        documents: dict[str, ComponentDocument] = {}
        for summary in self.bundled_catalog.list_components():
            document = self.bundled_catalog.get_component(summary.name)
            if document is not None:
                documents[summary.name] = document
        return documents

    def list_components(self) -> tuple[ComponentSummary, ...]:
        """Return components from the current remote, cache, or bundle."""

        documents = sorted(self._components().values(), key=lambda item: item.name)
        return tuple(_summary(document) for document in documents)

    def get_component(self, name: str) -> ComponentDocument | None:
        """Return a component by canonical name."""

        return self._components().get(_normalise_name(name))

    def list_skills(self) -> tuple[SkillSummary, ...]:
        """Return the packaged official DaisyUI skill summary."""

        skill = self.get_skill("daisyui")
        if skill is None:
            return ()
        return (
            SkillSummary(
                name="daisyui",
                description=(
                    "Official daisyUI component-library skill for Tailwind CSS."
                ),
            ),
        )

    def get_skill(self, name: str) -> SkillDocument | None:
        """Return a bundled skill document without permitting traversal."""

        if _normalise_name(name) != "daisyui":
            return None
        path = self.bundled_skills / "SKILL.md"
        try:
            markdown = path.read_text(encoding="utf-8")
        except OSError:
            return None
        return SkillDocument(name="daisyui", markdown=markdown, source_url=SKILLS_URL)

    def search(self, query: str) -> tuple[SearchMatch, ...]:
        """Search component and skill names/descriptions deterministically."""

        needle = _normalise_query(query)
        if not needle:
            return ()
        matches: list[SearchMatch] = []
        for component in self.list_components():
            haystack = f"{component.name} {component.description}".lower()
            if needle == component.name:
                score = 1.0
            elif component.name.startswith(needle):
                score = 0.85
            elif needle in haystack:
                score = 0.6
            else:
                continue
            matches.append(SearchMatch(component.name, component.description, score))
        for skill in self.list_skills():
            haystack = f"{skill.name} {skill.description}".lower()
            if needle in haystack:
                matches.append(SearchMatch(skill.name, skill.description, 0.5))
        return tuple(sorted(matches, key=lambda item: (-item.score, item.name)))

    def refresh(self, *, timeout: float | None = None) -> RefreshResult:
        """Fetch current official docs and atomically update the persistent cache."""

        selected_timeout = self.timeout if timeout is None else timeout
        try:
            components = parse_remote_components(
                self.fetcher(LLMS_URL, selected_timeout)
            )
            refreshed_at = _now()
            self._write_cache(components, refreshed_at)
            self._remote_components = components
            self._origin = ContentOrigin.REMOTE
            self._refreshed_at = refreshed_at
            return RefreshResult(
                origin=self._origin,
                component_count=len(components),
                skill_count=len(self.list_skills()),
                refreshed_at=refreshed_at,
                message=(
                    f"Refreshed {len(components)} DaisyUI components from {LLMS_URL}."
                ),
            )
        except (OSError, UnicodeError, ValueError, TimeoutError) as error:
            origin = (
                ContentOrigin.CACHE
                if self.cache_file.is_file() and self._remote_components
                else ContentOrigin.BUNDLED
            )
            self._origin = origin
            return RefreshResult(
                origin=origin,
                component_count=len(self.list_components()),
                skill_count=len(self.list_skills()),
                refreshed_at=self._refreshed_at,
                message=f"Refresh failed; serving {origin.value} content: {error}",
            )

    def install_skills(
        self, target: Path | None = None, *, timeout: float | None = None
    ) -> SkillInstallResult:
        """Install official skills using the bundled snapshot as fallback."""

        return install_official_skills(
            target=target,
            timeout=self.timeout if timeout is None else timeout,
            bundle=self.bundled_skills,
        )

    def status(self) -> ServerStatus:
        """Return the origin and counts for the current content."""

        return ServerStatus(
            origin=self._origin,
            component_count=len(self.list_components()),
            skill_count=len(self.list_skills()),
            refreshed_at=self._refreshed_at,
            cache_path=self.cache_file if self.cache_file.is_file() else None,
        )

    def get_resource(self, uri: str) -> ResourceDocument | None:
        """Resolve stable DaisyUI MCP resource URIs."""

        if uri == "daisyui://components":
            text = "\n".join(
                f"- {item.name}: {item.description}" for item in self.list_components()
            )
            return ResourceDocument(uri, "text/markdown", text)
        if uri == "daisyui://skills":
            text = "\n".join(
                f"- {item.name}: {item.description}" for item in self.list_skills()
            )
            return ResourceDocument(uri, "text/markdown", text)
        if uri == "daisyui://install":
            text = (
                f"Official installation documentation: {INSTALL_DOCS_URL}\n\n"
                "For DaisyUI 5 with Tailwind CSS 4, install daisyUI with "
                'npm i -D daisyui@latest and add @plugin "daisyui"; '
                'after @import "tailwindcss"; in the CSS entrypoint.'
            )
            return ResourceDocument(uri, "text/markdown", text)
        if uri == "daisyui://status":
            status = self.status()
            text = (
                f"origin: {status.origin.value}\n"
                f"components: {status.component_count}\n"
                f"skills: {status.skill_count}\n"
                f"refreshed_at: {status.refreshed_at or 'never'}"
            )
            return ResourceDocument(uri, "text/plain", text)
        component_prefix = "daisyui://component/"
        if uri.startswith(component_prefix):
            component_document = self.get_component(uri.removeprefix(component_prefix))
            if component_document is not None:
                return ResourceDocument(
                    uri, "text/markdown", component_document.markdown
                )
        skill_prefix = "daisyui://skill/"
        if uri.startswith(skill_prefix):
            skill_document = self.get_skill(uri.removeprefix(skill_prefix))
            if skill_document is not None:
                return ResourceDocument(uri, "text/markdown", skill_document.markdown)
        return None

    def export_components(self, directory: Path) -> int:
        """Write current component documents to a maintainer-selected directory."""

        directory.mkdir(parents=True, exist_ok=True)
        count = 0
        for document in self._components().values():
            (directory / f"{document.name}.md").write_text(
                document.markdown, encoding="utf-8"
            )
            count += 1
        return count
