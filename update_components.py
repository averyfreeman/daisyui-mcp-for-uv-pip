"""Refresh the checkout's component snapshot for maintainers."""

from pathlib import Path

from daisyui_mcp.content import DaisyUIContentStore


def main() -> int:
    """Fetch current docs and export them to the legacy components directory."""

    store = DaisyUIContentStore()
    result = store.refresh()
    if result.origin.value == "bundled":
        print(result.message)
        return 1
    count = store.export_components(Path.cwd() / "components")
    print(f"Exported {count} components; {result.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
