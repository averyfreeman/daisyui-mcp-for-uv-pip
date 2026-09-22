# daisyui-mcp

A typed, local Model Context Protocol server for official DaisyUI 5
documentation and agent skills. It is distributed as a normal Python wheel,
works with Python 3.10+, and keeps a bundled offline snapshot for predictable
development.

Published package: https://pypi.org/project/daisyui-mcp/

## Install with uv

Install the MCP server as a user tool:

~~~bash
uv tool install daisyui-mcp
~~~

For optional skill-management dependencies:

~~~bash
uv tool install "daisyui-mcp[skills]"
~~~

## Install with pip

Install the MCP server into the active Python environment:

~~~bash
python -m pip install daisyui-mcp
~~~

For optional skill-management dependencies:

~~~bash
python -m pip install "daisyui-mcp[skills]"
~~~

For local development, sync the committed lockfile:

~~~bash
uv sync --locked --extra dev --extra skills
~~~

## Run

The default command serves MCP over stdio:

~~~bash
daisyui-mcp
~~~

To configure an MCP client, use the installed executable as its command:

~~~text
/absolute/path/to/daisyui-mcp/.venv/bin/daisyui-mcp
~~~

The compatibility module mcp_server.py remains available for older
checkout-based configurations.

## MCP surface

Tools:

- list_components and get_component(name) preserve the original API.
- search_daisyui(query) searches component and skill metadata.
- list_skills() and get_skill(name) expose the bundled official skill.
- refresh_daisyui() refreshes current component docs with cached fallback.
- install_daisyui_skills(target) installs the official skill tree.
- daisyui_status() reports content origin, counts, and refresh time.

Resources:

- daisyui://components
- daisyui://skills
- daisyui://install
- daisyui://status
- daisyui://component/{name}
- daisyui://skill/{name}

The MCP server can install skills into the current project with an explicit
tool call. The CLI equivalent is:

~~~bash
daisyui-mcp skills install
daisyui-mcp skills install --target ./custom/skills/daisyui
~~~

The default target is ./.agents/skills/daisyui. The installer fetches the
official DaisyUI skill tree, validates archive paths, and falls back to the
packaged SKILL.md if the network is unavailable.

## Configure Codex

Install a reusable Codex profile template in the current project:

~~~bash
daisyui-mcp config install
~~~

Copy `daisyui-mcp.config.toml` to
`$CODEX_HOME/daisyui-mcp.config.toml` (usually `~/.codex/`), then run:

~~~bash
codex --profile daisyui-mcp
~~~

The profile starts one stdio MCP server; its complete tools and resources are
available after startup. As a one-time global alternative, run:

~~~bash
codex mcp add daisyui-mcp -- daisyui-mcp serve
~~~

See [examples/config.toml](examples/config.toml) for the equivalent TOML.

## DaisyUI source and refresh behavior

The runtime specification follows the official DaisyUI installation guide:

https://daisyui.com/docs/install/

Current component content is fetched from:

https://daisyui.com/llms.txt

daisyui-mcp refresh stores a JSON snapshot in the platform user cache. The
server serves cached content after a successful prior refresh and bundled
content when no cache exists or the network is unavailable. The package also
bundles current component docs, including aura, megamenu, otp, and tooltip,
plus the official skill entrypoint.

## Development

~~~bash
uv sync --locked --extra dev --extra skills
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
uv run --extra dev mypy src tests
uv run --extra dev pytest
uv run --extra dev python -m build
uv run --extra dev twine check dist/*
~~~

The project uses a src layout, setuptools with setuptools-scm, strict MyPy,
Ruff, pytest, and a committed uv.lock. Git tags such as v0.2.0 determine
the package version used by the release workflow.

## License

MIT. See LICENSE.
