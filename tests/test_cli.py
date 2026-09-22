"""Tests for the maintainer and configuration CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from daisyui_mcp.cli import build_parser, main
from daisyui_mcp.config import CONFIG_FILENAME, config_template


def test_config_install_writes_profile_template(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The config command writes the packaged profile and instructions."""

    monkeypatch.chdir(tmp_path)

    assert main(["config", "install"]) == 0

    destination = tmp_path / CONFIG_FILENAME
    assert destination.read_text(encoding="utf-8") == config_template()
    output = capsys.readouterr().out
    assert "codex --profile daisyui-mcp" in output
    assert "codex mcp add daisyui-mcp -- daisyui-mcp serve" in output


def test_config_install_refuses_to_replace_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Existing project configuration is protected without --force."""

    monkeypatch.chdir(tmp_path)
    destination = tmp_path / CONFIG_FILENAME
    destination.write_text("custom = true\n", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        main(["config", "install"])

    assert error.value.code == 2
    assert destination.read_text(encoding="utf-8") == "custom = true\n"


def test_config_install_force_replaces_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The explicit force flag replaces an existing template."""

    monkeypatch.chdir(tmp_path)
    destination = tmp_path / CONFIG_FILENAME
    destination.write_text("custom = true\n", encoding="utf-8")

    assert main(["config", "install", "--force"]) == 0
    assert destination.read_text(encoding="utf-8") == config_template()


def test_config_command_is_visible_in_help() -> None:
    """The new submenu is discoverable from the top-level help."""

    help_text = build_parser().format_help()

    assert "config" in help_text
