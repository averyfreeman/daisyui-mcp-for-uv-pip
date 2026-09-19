# daisyui-mcp

A small, local MCP server exposing DaisyUI component documentation to AI tools.

## Install with uv

This checkout targets the managed Python 3.12 environment in `.venv`:

```bash
cd daisyui-mcp
uv sync --python 3.12
```

The equivalent explicit editable install is:

```bash
uv pip install --python .venv/bin/python -e .
```

## Run

The server uses MCP stdio transport. Run it from this directory so the bundled
component documentation is available:

```bash
uv run daisyui-mcp
```

Configure an MCP client with the command below when it needs the server:

```text
/absolute/path/to/daisyui-mcp/.venv/bin/daisyui-mcp
```

The server exposes `list_components` and `get_component(name)`. It is a local
design-time documentation tool; the portfolio itself continues to use the npm
daisyUI package at build time.
