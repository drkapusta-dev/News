from poslovnipuls_pipeline.config import SourceConfig
from poslovnipuls_pipeline.owned_content import iter_owned_content, load_owned_items


def test_iter_owned_content_supports_md_and_txt(tmp_path) -> None:
    md_file = tmp_path / "a.md"
    txt_file = tmp_path / "b.txt"
    ignored_file = tmp_path / "c.html"

    md_file.write_text("# hello", encoding="utf-8")
    txt_file.write_text("hello", encoding="utf-8")
    ignored_file.write_text("<p>ignored</p>", encoding="utf-8")

    files = iter_owned_content(tmp_path)

    assert files == [md_file, txt_file]


def test_load_owned_items_reads_md_and_txt(tmp_path) -> None:
    (tmp_path / "a.md").write_text("# Naslov\nSadrzaj", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Tekstualni naslov\nNastavak", encoding="utf-8")
    source = SourceConfig(
        name="Owned",
        source_type="owned_manual",
        content_dir=tmp_path,
        rights_mode="full_publish",
    )

    items = load_owned_items(source)

    assert len(items) == 2
    assert items[0].link.startswith("owned://")
