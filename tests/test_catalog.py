"""Smoke tests for the typed package foundation."""

from pathlib import Path

from daisyui_mcp.catalog import ComponentCatalog


def test_catalog_lists_and_loads_a_component(tmp_path: Path) -> None:
    """The public catalog boundary parses summaries and full documents."""

    component_path = tmp_path / "button.md"
    component_path.write_text(
        "### button\nButtons allow the user to take actions\n\n#### Syntax\n",
        encoding="utf-8",
    )

    catalog = ComponentCatalog(tmp_path)

    summaries = catalog.list_components()
    assert len(summaries) == 1
    assert summaries[0].name == "button"
    assert summaries[0].description == "Buttons allow the user to take actions"
    document = catalog.get_component(" BUTTON ")
    assert document is not None
    assert document.name == "button"
    assert "#### Syntax" in document.markdown


def test_catalog_rejects_path_traversal(tmp_path: Path) -> None:
    """Names are validated before becoming filesystem paths."""

    catalog = ComponentCatalog(tmp_path)

    assert catalog.get_component("../button") is None
    assert catalog.get_component("button/extra") is None
