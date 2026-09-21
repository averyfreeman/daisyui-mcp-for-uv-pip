"""Tests for safe official-skill installation and fallback behavior."""

from __future__ import annotations

import tarfile
from io import BytesIO
from pathlib import Path

from daisyui_mcp.skills import (
    SKILLS_ARCHIVE_URL,
    install_official_skills,
)


def _archive() -> bytes:
    payload = BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        content = b"# daisyUI 5\n"
        info = tarfile.TarInfo("daisyui-master/skills/daisyui/SKILL.md")
        info.size = len(content)
        archive.addfile(info, BytesIO(content))
        nested = b"# install\n"
        nested_info = tarfile.TarInfo("daisyui-master/skills/daisyui/install/SKILL.md")
        nested_info.size = len(nested)
        archive.addfile(nested_info, BytesIO(nested))
    return payload.getvalue()


def test_install_downloads_only_the_official_skill_subtree(tmp_path: Path) -> None:
    """Archive extraction writes skill files under the explicit target."""

    calls: list[tuple[str, float]] = []

    def download(url: str, timeout: float) -> bytes:
        calls.append((url, timeout))
        return _archive()

    result = install_official_skills(
        tmp_path / "target",
        timeout=2.0,
        downloader=download,
    )

    assert result.used_fallback is False
    assert result.file_count == 2
    assert calls == [(SKILLS_ARCHIVE_URL, 2.0)]
    assert (tmp_path / "target" / "SKILL.md").read_text() == "# daisyUI 5\n"
    assert (tmp_path / "target" / "install" / "SKILL.md").is_file()


def test_install_falls_back_to_bundled_skill(tmp_path: Path) -> None:
    """Offline installation still exposes a usable packaged skill."""

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "SKILL.md").write_text("# bundled\n", encoding="utf-8")

    result = install_official_skills(
        tmp_path / "target",
        bundle=bundle,
        downloader=lambda _url, _timeout: b"not a tarball",
    )

    assert result.used_fallback is True
    assert result.file_count == 1
    assert (tmp_path / "target" / "SKILL.md").read_text() == "# bundled\n"
