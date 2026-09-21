"""Typed public API for the DaisyUI documentation MCP server."""

from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, cast

from .api import (
    ComponentDocument,
    ComponentSummary,
    ContentOrigin,
    ContentStore,
    RefreshResult,
    ResourceDocument,
    SearchMatch,
    ServerStatus,
    SkillDocument,
    SkillInstallResult,
    SkillSummary,
)
from .catalog import ComponentCatalog, default_components_directory
from .content import DaisyUIContentStore

if TYPE_CHECKING:
    from .server import create_server, get_component, list_components, mcp, run_server

try:
    __version__ = version("daisyui-mcp")
except PackageNotFoundError:
    __version__ = "0.1.0"

_SERVER_EXPORTS = frozenset(
    {"create_server", "get_component", "list_components", "mcp", "run_server"}
)


def __getattr__(name: str) -> object:
    """Load server integrations only when a caller requests them."""

    if name not in _SERVER_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from . import server

    return cast(object, getattr(server, name))


__all__ = [
    "ComponentCatalog",
    "ComponentDocument",
    "ComponentSummary",
    "ContentOrigin",
    "ContentStore",
    "DaisyUIContentStore",
    "RefreshResult",
    "ResourceDocument",
    "SearchMatch",
    "ServerStatus",
    "SkillInstallResult",
    "SkillDocument",
    "SkillSummary",
    "create_server",
    "get_component",
    "list_components",
    "mcp",
    "run_server",
    "__version__",
    "default_components_directory",
]
