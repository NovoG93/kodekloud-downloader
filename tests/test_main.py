from kodekloud_downloader.main import (
    _MAX_PATH_LENGTH,
    _shorten_component,
    create_file_path,
)


def test_shorten_component_short_string():
    assert _shorten_component("hello", 10) == "hello"


def test_shorten_component_no_extension():
    assert _shorten_component("very_long_component_name", 10) == "very_long_"


def test_shorten_component_preserves_extension():
    res = _shorten_component("long_document_title.pdf", 15)
    assert res.endswith(".pdf")
    assert len(res) <= 15


def test_create_file_path_under_max_length():
    path = create_file_path(
        output_dir="/tmp/downloads",
        course_name="Docker Basics",
        module_index=1,
        module_name="Getting Started",
        lesson_index=2,
        lesson_name="Containers",
    )
    assert len(str(path)) <= _MAX_PATH_LENGTH
    assert "Docker Basics" in str(path)
    assert "Getting Started" in str(path)
    assert "Containers" in str(path)


def test_create_file_path_truncates_overly_long_path():
    long_course = "A" * 100
    long_module = "B" * 100
    long_lesson = "C" * 100
    path = create_file_path(
        output_dir="/tmp/downloads",
        course_name=long_course,
        module_index=1,
        module_name=long_module,
        lesson_index=1,
        lesson_name=long_lesson,
    )
    assert len(str(path)) <= _MAX_PATH_LENGTH


def test_create_file_path_preserves_extension_when_shortening():
    long_base = "/tmp/" + ("X" * 150)
    path = create_file_path(
        output_dir=long_base,
        course_name="Course A",
        module_index=1,
        module_name="Module B",
        lesson_index=1,
        lesson_name=("Lesson C " * 4) + ".vtt",
    )
    assert len(str(path)) <= _MAX_PATH_LENGTH
    assert str(path).endswith(".vtt")


def test_download_course_handles_401_gracefully():
    from unittest.mock import MagicMock, patch

    import pytest
    import requests

    from kodekloud_downloader.main import download_course

    mock_course = MagicMock()
    mock_course.id = "test-course-id"
    mock_module = MagicMock()
    mock_module.id = "mod-1"
    mock_module.title = "Module 1"
    mock_lesson = MagicMock()
    mock_lesson.id = "lesson-1"
    mock_lesson.title = "Lesson 1"
    mock_lesson.type = "video"
    mock_module.lessons = [mock_lesson]
    mock_course.modules = [mock_module]

    with patch("requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        mock_resp = MagicMock()
        mock_resp.status_code = 401
        http_err = requests.exceptions.HTTPError(
            "401 Client Error: Unauthorized", response=mock_resp
        )
        mock_resp.raise_for_status.side_effect = http_err
        mock_session.get.return_value = mock_resp

        with pytest.raises(SystemExit) as exc_info:
            download_course(
                course=mock_course,
                quality="720p",
                output_dir="/tmp/test",
                max_duplicate_count=3,
                session_token="invalid_token",
            )
        assert "401" in str(exc_info.value) or "expired" in str(exc_info.value).lower()
