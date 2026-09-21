"""FastMCP server exposing DaisyUI components, skills, and resources."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

from .content import DaisyUIContentStore

_DEFAULT_STORE: DaisyUIContentStore | None = None


def _get_default_store() -> DaisyUIContentStore:
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = DaisyUIContentStore()
    return _DEFAULT_STORE


def _format_component_list(store: DaisyUIContentStore) -> str:
    summaries = store.list_components()
    if not summaries:
        return "No components found. Ensure the component documentation is installed."
    lines = [f"Available DaisyUI Components ({len(summaries)} total):", ""]
    lines.extend(f"  • {item.name} - {item.description}" for item in summaries)
    lines.extend(("", "Use get_component(name) to get detailed documentation."))
    return "\n".join(lines)


def _format_component_error(name: str, store: DaisyUIContentStore) -> str:
    normalised = name.strip().lower()
    names = tuple(item.name for item in store.list_components())
    suggestions = [
        candidate
        for candidate in names
        if normalised in candidate or candidate in normalised
    ]
    if not suggestions and len(normalised) >= 2:
        suggestions = [
            candidate for candidate in names if candidate.startswith(normalised[:2])
        ]
    suggestion_text = ""
    if suggestions:
        suggestion_text = "\n\nDid you mean one of these?\n  • " + "\n  • ".join(
            sorted(suggestions)[:5]
        )
    return f"Component '{name}' not found.{suggestion_text}\n\nUse list_components()."


def list_components() -> str:
    """List components using the package's default local catalog."""

    return _format_component_list(_get_default_store())


def get_component(name: str) -> str:
    """Return a component document using the package's default local catalog."""

    store = _get_default_store()
    document = store.get_component(name)
    if document is None:
        return _format_component_error(name, store)
    return document.markdown


def _format_search(store: DaisyUIContentStore, query: str) -> str:
    matches = store.search(query)
    if not matches:
        return f"No DaisyUI components or skills matched {query!r}."
    return "\n".join(
        f"- {match.name} ({match.score:.2f}): {match.description}" for match in matches
    )


def _format_status(store: DaisyUIContentStore) -> str:
    status = store.status()
    return (
        f"origin: {status.origin.value}\n"
        f"components: {status.component_count}\n"
        f"skills: {status.skill_count}\n"
        f"refreshed_at: {status.refreshed_at or 'never'}"
    )


def create_server(store: DaisyUIContentStore | None = None) -> FastMCP:
    """Create a FastMCP server with tools and resources registered."""

    from fastmcp import FastMCP

    selected_store = store or DaisyUIContentStore()
    server = FastMCP(name="DaisyUI MCP Server")

    @server.tool
    def list_components() -> str:
        """List all available DaisyUI components and short descriptions."""

        return _format_component_list(selected_store)

    @server.tool
    def get_component(name: str) -> str:
        """Return full Markdown documentation for a named component."""

        document = selected_store.get_component(name)
        if document is None:
            return _format_component_error(name, selected_store)
        return document.markdown

    @server.tool
    def search_daisyui(query: str) -> str:
        """Search DaisyUI components and official skills by name or description."""

        return _format_search(selected_store, query)

    @server.tool
    def list_skills() -> str:
        """List the official DaisyUI skills available to the MCP client."""

        return "\n".join(
            f"- {skill.name}: {skill.description}"
            for skill in selected_store.list_skills()
        )

    @server.tool
    def get_skill(name: str) -> str:
        """Return the Markdown for one official DaisyUI skill."""

        document = selected_store.get_skill(name)
        return (
            document.markdown if document is not None else f"Skill {name!r} not found."
        )

    @server.tool
    def refresh_daisyui() -> str:
        """Refresh official DaisyUI component docs with cached fallback."""

        return selected_store.refresh().message

    @server.tool
    def install_daisyui_skills(target: str | None = None) -> str:
        """Install official DaisyUI skills into a project or explicit target."""

        result = selected_store.install_skills(
            Path(target).expanduser() if target else None
        )
        fallback = " using bundled fallback" if result.used_fallback else ""
        return (
            f"Installed {result.file_count} skill files at {result.target}{fallback}."
        )

    @server.tool
    def daisyui_status() -> str:
        """Return the current content origin and freshness status."""

        return _format_status(selected_store)

    @server.resource("daisyui://components")
    def components_resource() -> str:
        """Expose the component index as an MCP resource."""

        resource = selected_store.get_resource("daisyui://components")
        return resource.text if resource is not None else ""

    @server.resource("daisyui://skills")
    def skills_resource() -> str:
        """Expose the official skill index as an MCP resource."""

        resource = selected_store.get_resource("daisyui://skills")
        return resource.text if resource is not None else ""

    @server.resource("daisyui://install")
    def install_resource() -> str:
        """Expose the current DaisyUI installation guidance as an MCP resource."""

        resource = selected_store.get_resource("daisyui://install")
        return resource.text if resource is not None else ""

    @server.resource("daisyui://status")
    def status_resource() -> str:
        """Expose the content status as an MCP resource."""

        resource = selected_store.get_resource("daisyui://status")
        return resource.text if resource is not None else ""

    return server


_DEFAULT_SERVER: FastMCP | None = None


def _get_default_server() -> FastMCP:
    """Create the process-wide server lazily for lightweight imports."""

    global _DEFAULT_SERVER
    if _DEFAULT_SERVER is None:
        _DEFAULT_SERVER = create_server()
    return _DEFAULT_SERVER


if TYPE_CHECKING:
    mcp: FastMCP


def __getattr__(name: str) -> object:
    """Expose the default server only when it is requested."""

    if name == "mcp":
        return _get_default_server()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def run_server(run: Callable[..., object] | None = None) -> None:
    """Run the server, with an injectable runner for tests and integrations."""

    selected_run = run or _get_default_server().run
    selected_run()
