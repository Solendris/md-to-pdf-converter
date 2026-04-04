from unittest.mock import patch
import runpy
import app
import pytest
import io

def test_app_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_app_convert_no_data(client):
    response = client.post("/convert")
    assert response.status_code == 400

def test_app_convert_with_data(client):
    with patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post("/convert", data={"text": "# Hello"})
        assert response.status_code == 200

def test_upload_file(client):
    file_content = io.BytesIO(b"# Hello")
    with patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post(
            "/convert",
            data={"files": (file_content, "test.md")},
            content_type="multipart/form-data"
        )
        assert response.status_code == 200

def test_file_not_md(client):
    file_content = io.BytesIO(b"# Hello")
    with patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post(
            "/convert",
            data={"files": (file_content, "test.txt")},
            content_type="multipart/form-data"
        )
        assert response.status_code == 400

def test_file_too_large(client):
    file_content = io.BytesIO(b"# Hello" * 1000000)
    with patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post(
            "/convert",
            data={"files": (file_content, "test.md")},
            content_type="multipart/form-data"
        )
        assert response.status_code == 400

def test_unicode_decode_error_fallback_utf8(client):
    raw_bytes = "# Zażółć gęślą jaźń".encode("utf-8")
    file_content = io.BytesIO(raw_bytes)

    with patch("app.chardet.detect", return_value={"encoding": "ascii"}), \
         patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post(
            "/convert",
            data={"files": (file_content, "test.md")},
            content_type="multipart/form-data"
        )
        assert response.status_code == 200


def test_unicode_decode_error_fallback_cp1250(client):
    raw_bytes = b"\xff\xfe# Hello"
    file_content = io.BytesIO(raw_bytes)

    with patch("app.chardet.detect", return_value={"encoding": "ascii"}), \
         patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post(
            "/convert",
            data={"files": (file_content, "test.md")},
            content_type="multipart/form-data"
        )
        assert response.status_code == 200

def test_batch_conversion(client):
    file_content1 = io.BytesIO(b"# Hello")
    file_content2 = io.BytesIO(b"# Hello")
    with patch("app.convert_md_to_pdf", return_value=b"%PDF fake"):
        response = client.post(
            "/convert",
            data={"files": [(file_content1, "test1.md"), (file_content2, "test2.md")]},
            content_type="multipart/form-data"
        )
        assert response.status_code == 200

def test_batch_conversion_with_error(client):
    with patch("app.convert_md_to_pdf", side_effect=Exception("Test error")):
        file_content1 = io.BytesIO(b"# Hello")
        file_content2 = io.BytesIO(b"# Hello")
        response = client.post(
            "/convert",
            data={"files": [(file_content1, "test1.md"), (file_content2, "test2.md")]},
            content_type="multipart/form-data"
        )
        assert response.status_code == 200

def test_convert_exception(client):
    with patch("app.convert_md_to_pdf", side_effect=Exception("fail")):
        response = client.post("/convert", data={"text": "# Hello"})
        assert response.status_code == 500

def test_main_block():
    with patch("flask.Flask.run") as mock_run:
        runpy.run_path("app.py", run_name="__main__")
        mock_run.assert_called_once_with(debug=True)
