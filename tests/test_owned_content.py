from poslovnipuls_pipeline.owned_content import iter_owned_content


def test_iter_owned_content_supports_md_and_txt(tmp_path) -> None:
    md_file = tmp_path / "a.md"
    txt_file = tmp_path / "b.txt"
    ignored_file = tmp_path / "c.html"

    md_file.write_text("# hello", encoding="utf-8")
    txt_file.write_text("hello", encoding="utf-8")
    ignored_file.write_text("<p>ignored</p>", encoding="utf-8")

    files = iter_owned_content(tmp_path)

    assert files == [md_file, txt_file]
