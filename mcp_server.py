"""Compatibility entry point for older checkout-based MCP configurations."""

from daisyui_mcp.server import get_component, list_components, mcp

__all__ = ["get_component", "list_components", "mcp"]


if __name__ == "__main__":
    mcp.run()
