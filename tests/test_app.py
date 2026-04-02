from unittest.mock import patch, MagicMock
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
    response = client.post(
        "/convert",
        data={"files": (file_content, "test.md")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
