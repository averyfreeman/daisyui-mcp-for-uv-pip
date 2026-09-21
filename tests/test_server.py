"""Tests for the FastMCP tool and resource registration surface."""

from __future__ import annotations

import asyncio
from pathlib import Path

from daisyui_mcp.content import DaisyUIContentStore
from daisyui_mcp.server import create_server, get_component, list_components


def test_legacy_tools_remain_available() -> None:
    """The original list/get contract remains usable after the renewal."""

    assert "button" in list_components()
    assert "btn" in get_component("button")


def test_fastmcp_registers_tools_and_resources(tmp_path: Path) -> None:
    """The current FastMCP server exposes the renewed typed surface."""

    store = DaisyUIContentStore(cache_directory=tmp_path / "cache")
    server = create_server(store)

    async def inspect() -> tuple[set[str], set[str]]:
        tools = await server.list_tools()
        resources = await server.list_resources()
        return (
            {tool.name for tool in tools},
            {str(resource.uri) for resource in resources},
        )

    tool_names, resource_uris = asyncio.run(inspect())

    assert {"list_components", "get_component", "search_daisyui"} <= tool_names
    assert {"list_skills", "refresh_daisyui", "install_daisyui_skills"} <= tool_names
    assert "daisyui://components" in resource_uris
    assert "daisyui://install" in resource_uris
