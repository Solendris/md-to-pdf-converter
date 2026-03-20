"""Konwersja Markdown → PDF za pomocą markdown2 i xhtml2pdf."""

import io
import markdown2
from xhtml2pdf import pisa

PDF_CSS = """
@font-face {
    font-family: 'MainFont';
    src: url('C:/Windows/Fonts/arial.ttf');
}
@font-face {
    font-family: 'MainFont';
    src: url('C:/Windows/Fonts/arialbd.ttf');
    font-weight: bold;
}
@font-face {
    font-family: 'MainFont';
    src: url('C:/Windows/Fonts/ariali.ttf');
    font-style: italic;
}
@font-face {
    font-family: 'CodeFont';
    src: url('C:/Windows/Fonts/consola.ttf');
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'MainFont';
    font-size: 12pt;
    line-height: 1.7;
    color: #1a1a2e;
    padding: 2cm 2.5cm;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'MainFont';
    font-weight: bold;
    color: #16213e;
    margin: 1.2em 0 0.4em;
    line-height: 1.3;
}
h1 { font-size: 22pt; border-bottom: 2px solid #e94560; padding-bottom: 6px; }
h2 { font-size: 17pt; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
h3 { font-size: 14pt; }

p { margin: 0.5em 0; }

a { color: #e94560; text-decoration: none; }

ul, ol { margin: 0.5em 0 0.5em 1.5em; }
li { margin: 0.2em 0; }

blockquote {
    border-left: 3px solid #e94560;
    margin: 0.8em 0;
    padding: 0.4em 0.8em;
    background: #f0f4f8;
    color: #555;
}

code {
    font-family: 'CodeFont';
    font-size: 10pt;
    background: #eef2f7;
    padding: 1px 4px;
    color: #c7254e;
}

pre {
    background: #eef2f7;
    color: #1a1a2e;
    padding: 10px 12px;
    margin: 0.8em 0;
    font-size: 9pt;
    line-height: 1.5;
    border-left: 3px solid #3b82f6;
}
pre code {
    background: none;
    padding: 0;
    color: #1a1a2e;
}

table {
    width: 100%;
    margin: 0.8em 0;
    font-size: 10pt;
}
th {
    background: #e94560;
    color: #fff;
    font-weight: bold;
    padding: 6px 10px;
    text-align: left;
    font-family: 'MainFont';
}
td {
    padding: 5px 10px;
    border-bottom: 1px solid #ddd;
    font-family: 'MainFont';
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 1.2em 0;
}

img { max-width: 100%; }
"""

EXTRAS = ["fenced-code-blocks", "tables", "strike", "task_list", "footnotes"]


def convert_md_to_pdf(md_text: str) -> bytes:
    """Konwertuje tekst Markdown do PDF i zwraca bajty."""
    html_body = markdown2.markdown(md_text, extras=EXTRAS)
    html_doc = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <style>{PDF_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""
    pdf_buffer = io.BytesIO()
    result = pisa.CreatePDF(src=html_doc, dest=pdf_buffer, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"Błąd konwersji PDF: {result.err}")
    return pdf_buffer.getvalue()
