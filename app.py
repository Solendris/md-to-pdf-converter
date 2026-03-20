"""Serwer Flask — MD to PDF Converter."""

import io
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import chardet
from flask import Flask, request, send_file, render_template, jsonify
from converter import convert_md_to_pdf

app = Flask(__name__)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# --- Logging ---
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

handler = RotatingFileHandler(
    LOG_DIR / "app.log", maxBytes=500_000, backupCount=3, encoding="utf-8"
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
handler.setLevel(logging.INFO)

logger = logging.getLogger("md2pdf")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    md_text = None
    source = "text"

    # Obsługa przesłanego pliku .md
    if "file" in request.files and request.files["file"].filename:
        f = request.files["file"]
        source = f.filename
        if not f.filename.endswith(".md"):
            logger.warning("Odrzucono plik: %s (nie .md)", f.filename)
            return jsonify({"error": "Plik musi mieć rozszerzenie .md"}), 400
        raw = f.read(MAX_FILE_SIZE + 1)
        if len(raw) > MAX_FILE_SIZE:
            logger.warning("Odrzucono plik: %s (za duży: %d B)", f.filename, len(raw))
            return jsonify({"error": "Plik jest za duży (max 5 MB)"}), 413
        
        # Wykrywanie kodowania pliku (bo pliki z Windows mogą być w cp1250)
        detected = chardet.detect(raw)
        encoding = detected['encoding'] if detected['encoding'] else "utf-8"
        # Jeśli bardzo niska pewność lub błąd, spróbujmy utf-8 z fallbackiem na cp1250
        try:
            md_text = raw.decode(encoding)
        except UnicodeDecodeError:
            try:
                md_text = raw.decode("utf-8")
            except UnicodeDecodeError:
                md_text = raw.decode("cp1250", errors="replace")
                
        logger.info("Odczytano plik, wykryte kodowanie: %s", encoding)

    # Obsługa tekstu wklejonego w edytorze
    elif "text" in request.form and request.form["text"].strip():
        md_text = request.form["text"]

    else:
        logger.warning("Żądanie bez treści do konwersji")
        return jsonify({"error": "Brak treści do konwersji"}), 400

    try:
        logger.info("Konwersja: źródło=%s, rozmiar=%d znaków", source, len(md_text))
        pdf_bytes = convert_md_to_pdf(md_text)
        logger.info("Sukces: wygenerowano PDF %d bajtów", len(pdf_bytes))
    except Exception:
        logger.exception("Błąd podczas konwersji")
        return jsonify({"error": "Wystąpił błąd podczas konwersji"}), 500

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="dokument.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
