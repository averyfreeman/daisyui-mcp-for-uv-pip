"""Safe installation of the official DaisyUI agent skill tree."""

from __future__ import annotations

import shutil
import tarfile
from collections.abc import Callable
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.request import Request, urlopen

from .api import SkillInstallResult

SKILLS_ARCHIVE_URL = (
    "https://github.com/saadeghi/daisyui/archive/refs/heads/master.tar.gz"
)
SKILLS_SOURCE_URL = "https://github.com/saadeghi/daisyui/tree/master/skills/daisyui"

_DEFAULT_TARGET_NAME = Path(".agents") / "skills" / "daisyui"
_MAX_ARCHIVE_BYTES = 16 * 1024 * 1024


def default_skill_target(project_directory: Path | None = None) -> Path:
    """Return the explicit project-local installation target."""

    return (project_directory or Path.cwd()) / _DEFAULT_TARGET_NAME


def _download_archive(url: str, timeout: float) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/gzip",
            "User-Agent": "daisyui-mcp/0.1",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = cast(bytes, response.read(_MAX_ARCHIVE_BYTES + 1))
    if len(payload) > _MAX_ARCHIVE_BYTES:
        raise ValueError("DaisyUI skill archive exceeded the safety size limit")
    return payload


def _member_relative_path(member_name: str) -> Path | None:
    """Return a safe skill-relative path from an archive member."""

    parts = PurePosixPath(member_name).parts
    marker = ("skills", "daisyui")
    try:
        start = next(
            index
            for index in range(len(parts) - len(marker) + 1)
            if parts[index : index + len(marker)] == marker
        )
    except StopIteration:
        return None
    relative_parts = parts[start + len(marker) :]
    if not relative_parts or any(part in {"", ".", ".."} for part in relative_parts):
        return None
    return Path(*relative_parts)


def _extract_skill_archive(payload: bytes, target: Path) -> int:
    """Extract only the official skill subtree, rejecting unsafe members."""

    extracted: list[tuple[Path, bytes]] = []
    with tarfile.open(fileobj=BytesIO(payload), mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = _member_relative_path(member.name)
            if relative is None:
                continue
            source = archive.extractfile(member)
            if source is None:
                continue
            extracted.append((relative, source.read()))
    if not extracted:
        raise ValueError("DaisyUI skill archive did not contain skills/daisyui")
    target.mkdir(parents=True, exist_ok=True)
    for relative, content in extracted:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    return len(extracted)


def _copy_bundled_skill(bundle: Path, target: Path) -> int:
    """Copy the packaged fallback skill into the requested target."""

    if not bundle.is_dir():
        raise FileNotFoundError(f"Bundled skill directory is missing: {bundle}")
    target.mkdir(parents=True, exist_ok=True)
    files = [
        path
        for path in bundle.rglob("*")
        if path.is_file() and path.name != ".DS_Store"
    ]
    for source in files:
        destination = target / source.relative_to(bundle)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    if not files:
        raise FileNotFoundError(f"Bundled skill directory is empty: {bundle}")
    return len(files)


def install_official_skills(
    target: Path | None = None,
    *,
    timeout: float = 20.0,
    bundle: Path | None = None,
    downloader: Callable[[str, float], bytes] | None = None,
) -> SkillInstallResult:
    """Install the newest official skills, falling back to the bundled snapshot."""

    selected_target = (target or default_skill_target()).expanduser().resolve()
    bundled = bundle or Path(__file__).parent / "data" / "skills" / "daisyui"
    fetch = downloader or _download_archive
    try:
        file_count = _extract_skill_archive(
            fetch(SKILLS_ARCHIVE_URL, timeout), selected_target
        )
        return SkillInstallResult(
            target=selected_target,
            file_count=file_count,
            source_url=SKILLS_SOURCE_URL,
            used_fallback=False,
        )
    except (OSError, ValueError, tarfile.TarError):
        file_count = _copy_bundled_skill(bundled, selected_target)
        return SkillInstallResult(
            target=selected_target,
            file_count=file_count,
            source_url="bundled://daisyui",
            used_fallback=True,
        )
