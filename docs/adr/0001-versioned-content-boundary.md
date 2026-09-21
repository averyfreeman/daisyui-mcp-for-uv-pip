# Keep the typed package boundary independent from refresh state

We want a nice, open-source MCP server to use with DaisyUI without recurring fees, that is also easier for others to access through the pip package manager. The server will expose a typed src/daisyui_mcp package and treat official DaisyUI components and skills as content owned by that package. Bundled content remains available for reproducible offline use, while refresh and cache behavior stays behind the ContentStore boundary so a network failure cannot redefine the public API or the package installation contract.

## Considered Options

- Keep the flat checkout script and read the repository’s working directory at runtime.
- Make the package depend on a live DaisyUI website for every request.
- Use a typed package boundary with bundled content and replaceable refresh state.

The third option keeps pip and uv installations self-contained and gives refresh logic a narrow seam for bounded network access and persistent-cache fallback.
