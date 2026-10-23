from __future__ import annotations

from deeptutor.agents.loop.pipeline import _repair_source_page_urls


def test_repair_drops_a_corrupted_source_path_when_hash_is_present() -> None:
    """The model can truncate the second long path; the hash still resolves it."""
    text = (
        "![Original source evidence](/api/knowledge-bases/kb/source-page"
        "?source_path=%E8%AE%B2%E4%B9%89%E4%B8%89%E8%87%B3%E5%9B%9B%E7%AB%A0_p103-260.pdf"
        "&page=24&source_hash=54b995&dt_workspace=)"
    )

    repaired = _repair_source_page_urls(text)

    assert "source_path" not in repaired
    assert "page=24" in repaired
    assert "source_hash=54b995" in repaired
    assert "dt_workspace=" in repaired
    assert repaired.startswith(
        "![Original source evidence](/api/knowledge-bases/kb/source-page?"
    )


def test_repair_keeps_links_that_cannot_be_resolved_by_hash() -> None:
    text = "(/api/knowledge-bases/kb/source-page?source_path=a.pdf&page=1)"
    assert _repair_source_page_urls(text) == text


def test_repair_leaves_other_internal_links_alone() -> None:
    text = "![x](/api/knowledge-bases/kb/files/a.pdf#page=1)"
    assert _repair_source_page_urls(text) == text
