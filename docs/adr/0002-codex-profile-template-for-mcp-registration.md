# Use a Codex profile template for DaisyUI MCP registration

The package needs a reproducible way to configure DaisyUI MCP without silently mutating a user’s global Codex configuration. We chose to install a `daisyui-mcp.config.toml` profile template in the current project, explain that it must be copied into `$CODEX_HOME`, and select it with `codex --profile daisyui-mcp`; direct `codex mcp add daisyui-mcp -- daisyui-mcp serve` remains a documented one-time alternative.

## Considered Options

- Write native `.codex/config.toml` project configuration and rely on plain `codex` startup.
- Execute `codex mcp add` automatically and mutate the user’s global configuration.
- Provide a profile template with explicit installation and selection instructions.

The profile template preserves the requested artifact, makes global state changes explicit, and keeps the complete MCP surface behind one stdio server registration.
