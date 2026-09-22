"""Codex profile template installation helpers."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

CONFIG_FILENAME = "daisyui-mcp.config.toml"


def config_template() -> str:
    """Return the packaged Codex profile template."""

    resource = files("daisyui_mcp").joinpath("data").joinpath(CONFIG_FILENAME)
    return resource.read_text(encoding="utf-8")


def install_codex_config(
    project_directory: Path | None = None,
    *,
    force: bool = False,
) -> Path:
    """Install the Codex profile template into a project directory."""

    selected_directory = (project_directory or Path.cwd()).expanduser().resolve()
    destination = selected_directory / CONFIG_FILENAME
    if destination.exists() and not force:
        raise FileExistsError(
            f"Configuration file already exists: {destination}; "
            "use --force to replace it"
        )
    destination.write_text(config_template(), encoding="utf-8")
    return destination
