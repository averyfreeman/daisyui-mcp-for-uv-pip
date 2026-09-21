# Contributing

## Setup

Use uv and the committed lockfile:

~~~bash
uv sync --locked --extra dev --extra skills
~~~

Run the complete local checks before opening a pull request:

~~~bash
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
uv run --extra dev mypy src tests
uv run --extra dev pytest
~~~

## Content changes

Prefer the official DaisyUI sources. Component content belongs under the
package data directory so wheel installations remain self-contained. Use
daisyui-mcp refresh or update_components.py when updating the snapshot, and
review the resulting component changes rather than committing unrelated cache
files.

## Pull requests

Keep changes focused, add tests for behavior changes, and update the changelog
when the public MCP surface changes.
