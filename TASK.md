## Goal

Renew the DaisyUI MCP server from the edited source snapshot, align it with the current DaisyUI 5 documentation and official skills, make the Python package fully typed and pip/uv-installable, and prepare a verified PyPI release for `daisyui-mcp`.

## Acceptance criteria

- The project uses a typed `src/daisyui_mcp` package with setuptools-scm versioning, `py.typed`, compatible runtime dependency ranges, and a committed `uv.lock`.
- The MCP server preserves `list_components` and `get_component`, and adds typed discovery, search, skill, refresh, status, and resource capabilities aligned with the current DaisyUI documentation model.
- Current official DaisyUI component documentation and skill resources are bundled with attribution, refreshed at runtime with bounded network access, and served through validated persistent-cache fallback behavior.
- `daisyui-mcp skills install` supports project-local installation by default and an explicitly supplied CLI target; MCP installation is restricted to the project-local skills directory.
- Production code, CLI code, synchronization code, and tests have complete type annotations and pass strict mypy checks.
- Unit and integration tests cover parsing, lookup, refresh failures, cache fallback, path safety, MCP calls/resources, CLI installation, and package contents.
- Ruff, pytest, mypy, wheel/sdist build, and twine metadata validation pass through the verification command below.
- README, CONTEXT.md, native ADR records, CHANGELOG.md, CI workflow, and OIDC PyPI publish workflow document the supported installation and release process.

## Verification

```sh
uv run --extra dev ruff check . && uv run --extra dev ruff format --check . && uv run --extra dev mypy src tests && uv run --extra dev pytest && temp_dist="$(mktemp -d)" && uv run --extra dev python -m build --outdir "$temp_dist" && uv run --extra dev twine check "$temp_dist"/*
```
