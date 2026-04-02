from converter import convert_md_to_pdf
import pytest
from unittest.mock import patch, MagicMock

def test_pdf_error_raises_runtime_success():
    mock_result = MagicMock()
    mock_result.err = 0
    with patch("converter.pisa.CreatePDF", return_value=mock_result):
        result = convert_md_to_pdf("# Hello")
        assert isinstance(result, bytes)

def test_pdf_error_raises_runtime_error():
    mock_result = MagicMock()
    mock_result.err = 1
    with patch("converter.pisa.CreatePDF", return_value=mock_result), \
        pytest.raises(RuntimeError):
        convert_md_to_pdf("# Hello")
     