from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from kodekloud_downloader.helpers import (
    download_all_pdf,
    download_video,
    normalize_name,
    parse_input,
    parse_token,
    sanitize_filename,
)


def test_parse_input_single_number():
    assert parse_input("5") == [5]


def test_parse_input_range():
    assert parse_input("1-4") == [1, 2, 3, 4]


def test_parse_input_combined():
    assert parse_input("1,3-5,8") == [1, 3, 4, 5, 8]


def test_parse_input_invalid_range():
    with pytest.raises(ValueError, match="Invalid range"):
        parse_input("5-2")


def test_sanitize_filename_reserved_windows_chars():
    raw = "File: Name? With * Bad <Chars> and | Slash/Backslash\\"
    cleaned = sanitize_filename(raw)
    for bad_char in '\\/:*?"<>|':
        assert bad_char not in cleaned


def test_sanitize_filename_reserved_device_names():
    for name in ["CON", "prn", "AUX", "NUL", "COM1", "LPT9"]:
        assert sanitize_filename(name) == "_"


def test_sanitize_filename_max_length_and_whitespace():
    raw = "   " + ("a" * 150) + "   "
    cleaned = sanitize_filename(raw, max_length=50)
    assert len(cleaned) <= 50
    assert not cleaned.startswith(" ")
    assert not cleaned.endswith(" ")


def test_normalize_name():
    assert normalize_name("Hello, World! #2026") == "Hello World 2026"


def test_download_all_pdf_handles_tags_without_href(tmp_path: Path):
    """Ensure download_all_pdf doesn't crash with AttributeError on <a> tags lacking href."""
    html = """
    <div>
        <a>Anchor with no href</a>
        <a href="https://example.com/file.pdf">Valid PDF</a>
        <a href="https://example.com/not_a_pdf.html">Not PDF</a>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b"%PDF-1.4 dummy content"
        mock_get.return_value = mock_resp

        # This should NOT raise AttributeError: 'NoneType' object has no attribute 'endswith'
        download_all_pdf(soup, tmp_path, cookie=None)

        assert (tmp_path / "file.pdf").exists()
        assert (tmp_path / "file.pdf").read_bytes() == b"%PDF-1.4 dummy content"


def test_download_video_options_no_conflicting_subtitles():
    """Ensure yt-dlp options don't contain conflicting 'no_write_sub': True when writing subs."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        download_video(
            url="https://player.vimeo.com/video/12345",
            output_path=Path("/tmp/test_video"),
            cookie=None,
            quality="720p",
        )
        assert mock_ydl.called
        opts = mock_ydl.call_args[0][0]
        assert opts.get("writesubtitles") is True
        assert "no_write_sub" not in opts or opts.get("no_write_sub") is not True


def test_parse_token_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_token("non_existent_cookie_file.txt")
