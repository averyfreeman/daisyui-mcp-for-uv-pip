"""Command-line entry point for the DaisyUI MCP server."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import install_codex_config
from .skills import default_skill_target, install_official_skills


def build_parser() -> argparse.ArgumentParser:
    """Build the public command-line parser."""

    parser = argparse.ArgumentParser(
        prog="daisyui-mcp",
        description="Serve DaisyUI documentation through the Model Context Protocol.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("serve", help="run the MCP server over stdio")
    skills = subparsers.add_parser("skills", help="manage official DaisyUI skills")
    skills_subparsers = skills.add_subparsers(dest="skills_command")
    install = skills_subparsers.add_parser(
        "install",
        help="install the newest official DaisyUI skills",
    )
    install.add_argument("--target", type=Path, help="explicit installation directory")
    install.add_argument("--timeout", type=float, default=20.0)
    skills_subparsers.add_parser("path", help="show the default project-local target")
    config = subparsers.add_parser(
        "config",
        help="manage the Codex MCP profile template",
    )
    config_subparsers = config.add_subparsers(dest="config_command")
    config_install = config_subparsers.add_parser(
        "install",
        help="install a Codex profile template in the current directory",
    )
    config_install.add_argument(
        "--force",
        action="store_true",
        help="replace an existing daisyui-mcp.config.toml",
    )
    subparsers.add_parser("refresh", help="refresh official component documentation")
    subparsers.add_parser("status", help="show content origin and counts")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.command in (None, "serve"):
        from .server import run_server

        run_server()
        return 0
    if arguments.command == "skills":
        if arguments.skills_command == "path":
            print(default_skill_target())
            return 0
        if arguments.skills_command == "install":
            result = install_official_skills(
                target=arguments.target,
                timeout=arguments.timeout,
            )
            fallback = " (bundled fallback)" if result.used_fallback else ""
            print(
                f"Installed {result.file_count} skill files at "
                f"{result.target}{fallback}."
            )
            return 0
        parser.error("choose a skills subcommand")
    if arguments.command == "config":
        if arguments.config_command == "install":
            try:
                destination = install_codex_config(force=arguments.force)
            except FileExistsError as error:
                parser.error(str(error))
            print(
                f"Installed Codex profile template at {destination}.\n"
                "Copy it to $CODEX_HOME/daisyui-mcp.config.toml "
                "(usually ~/.codex/daisyui-mcp.config.toml), then run "
                "`codex --profile daisyui-mcp` from this project directory.\n"
                "Alternatively, register it globally with: "
                "`codex mcp add daisyui-mcp -- daisyui-mcp serve`."
            )
            return 0
        parser.error("choose a config subcommand")
    if arguments.command == "refresh":
        from .content import DaisyUIContentStore

        print(DaisyUIContentStore().refresh().message)
        return 0
    if arguments.command == "status":
        from .content import DaisyUIContentStore

        status = DaisyUIContentStore().status()
        print(
            f"origin: {status.origin.value}\n"
            f"components: {status.component_count}\n"
            f"skills: {status.skill_count}"
        )
        return 0
    parser.error("unknown command")
    return 2
