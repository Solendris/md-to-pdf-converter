"""Konwersja Markdown → PDF za pomocą markdown2 i xhtml2pdf."""

import io
import markdown2
from xhtml2pdf import pisa

PDF_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Fira+Code&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', sans-serif;
    font-size: 13pt;
    line-height: 1.7;
    color: #1a1a2e;
    padding: 2.5cm 3cm;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    color: #16213e;
    margin: 1.4em 0 0.5em;
    line-height: 1.3;
}
h1 { font-size: 2em; border-bottom: 2px solid #e94560; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #ddd; padding-bottom: 0.2em; }
h3 { font-size: 1.2em; }

p { margin: 0.7em 0; }

a { color: #e94560; text-decoration: none; }

ul, ol { margin: 0.7em 0 0.7em 1.8em; }
li { margin: 0.3em 0; }

blockquote {
    border-left: 4px solid #e94560;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f0f4f8;
    border-radius: 0 4px 4px 0;
    color: #555;
}

code {
    font-family: 'Fira Code', monospace;
    font-size: 0.88em;
    background: #f0f4f8;
    padding: 0.15em 0.4em;
    border-radius: 3px;
    color: #e94560;
}

pre {
    background: #1a1a2e;
    color: #e2e8f0;
    padding: 1em 1.2em;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1em 0;
    font-size: 0.85em;
    line-height: 1.6;
}
pre code {
    background: none;
    padding: 0;
    color: inherit;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 0.95em;
}
th {
    background: #16213e;
    color: #fff;
    font-weight: 600;
    padding: 0.6em 1em;
    text-align: left;
}
td {
    padding: 0.5em 1em;
    border-bottom: 1px solid #e2e8f0;
}
tr:nth-child(even) td { background: #f7f9fc; }

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.5em 0;
}

img { max-width: 100%; border-radius: 4px; }
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
