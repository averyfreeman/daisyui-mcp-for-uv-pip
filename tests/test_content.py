"""Tests for current-document parsing, cache fallback, and resources."""

from __future__ import annotations

from pathlib import Path

from daisyui_mcp.api import ContentOrigin
from daisyui_mcp.content import (
    INSTALL_DOCS_URL,
    LLMS_URL,
    DaisyUIContentStore,
    parse_remote_components,
)

SAMPLE_LLMS = """\
## daisyUI components

### Button
A button allows the user to take an action.

#### Class names
- component: btn

#### Syntax
<button class="btn">Button</button>

### Browser mockup
A browser mockup shows a browser window.

#### Class names
- component: mockup-browser

#### Syntax
<div class="mockup-browser"></div>
"""


def test_parse_remote_components_normalises_current_names() -> None:
    """Current llms headings become stable component identifiers."""

    components = parse_remote_components(SAMPLE_LLMS)

    assert set(components) == {"button", "mockup-browser"}
    assert components["mockup-browser"].source_url is not None


def test_refresh_persists_and_reloads_cache(tmp_path: Path) -> None:
    """A successful refresh is available to a new process through JSON cache."""

    calls: list[tuple[str, float]] = []

    def fetch(url: str, timeout: float) -> str:
        calls.append((url, timeout))
        return SAMPLE_LLMS

    store = DaisyUIContentStore(
        cache_directory=tmp_path / "cache",
        fetcher=fetch,
        timeout=4.5,
    )
    result = store.refresh()

    assert result.origin is ContentOrigin.REMOTE
    assert result.component_count == 2
    assert calls == [(LLMS_URL, 4.5)]
    assert (tmp_path / "cache" / "content.json").is_file()

    restored = DaisyUIContentStore(
        cache_directory=tmp_path / "cache",
        fetcher=lambda _url, _timeout: "not used",
    )
    assert restored.status().origin is ContentOrigin.CACHE
    assert restored.get_component("button") is not None


def test_refresh_uses_bundled_fallback_on_network_failure(tmp_path: Path) -> None:
    """Network failure never removes the package's offline content."""

    store = DaisyUIContentStore(
        cache_directory=tmp_path / "cache",
        fetcher=lambda _url, _timeout: (_ for _ in ()).throw(OSError("offline")),
    )

    result = store.refresh()

    assert result.origin is ContentOrigin.BUNDLED
    assert store.get_component("button") is not None
    assert "offline" in result.message


def test_resources_include_installation_specification(tmp_path: Path) -> None:
    """Stable resources expose the current DaisyUI installation contract."""

    store = DaisyUIContentStore(cache_directory=tmp_path / "cache")

    install = store.get_resource("daisyui://install")
    component = store.get_resource("daisyui://component/button")
    invalid = store.get_resource("daisyui://component/../button")

    assert install is not None
    assert INSTALL_DOCS_URL in install.text
    assert component is not None
    assert invalid is None
