"""Serwer Flask — MD to PDF Converter."""

import io
import logging
import zipfile
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
    valid_files = []
    
    # Obsługa przesłanych plików .md
    uploaded_files = request.files.getlist("files")
    if uploaded_files and any(f.filename for f in uploaded_files):
        source = f"pliki ({len(uploaded_files)})"
        
        for f in uploaded_files:
            if not f.filename.endswith(".md"):
                logger.warning("Pominęto plik: %s (nie .md)", f.filename)
                continue
                
            raw = f.read(MAX_FILE_SIZE + 1)
            if len(raw) > MAX_FILE_SIZE:
                logger.warning("Pominęto plik: %s (za duży: %d B)", f.filename, len(raw))
                continue
            
            detected = chardet.detect(raw)
            encoding = detected['encoding'] if detected['encoding'] else "utf-8"
            
            try:
                text = raw.decode(encoding)
            except UnicodeDecodeError:
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw.decode("cp1250", errors="replace")
            
            valid_files.append((f.filename, text))
            
        if not valid_files:
            return jsonify({"error": "Żaden z przesłanych plików nie był poprawnym plikiem .md do 5MB."}), 400

    # Obsługa tekstu wklejonego w edytorze
    elif "text" in request.form and request.form["text"].strip():
        source = "text"
        valid_files.append(("dokument.md", request.form["text"]))

    if not valid_files:
        logger.warning("Żądanie bez treści do konwersji")
        return jsonify({"error": "Brak treści do konwersji"}), 400

    try:
        if len(valid_files) == 1:
            # Konwersja pojedynczego pliku -> zwrotka pliku PDF
            orig_filename, md_text = valid_files[0]
            logger.info("Konwersja 1 pliku: źródło=%s, rozmiar=%d znaków", orig_filename, len(md_text))
            pdf_bytes = convert_md_to_pdf(md_text)
            
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=orig_filename.replace(".md", ".pdf"),
            )
            
        else:
            # Konwersja wielu plików -> zwrotka paczki ZIP
            logger.info("Konwersja paczki %d plików do ZIP", len(valid_files))
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for orig_filename, md_text in valid_files:
                    try:
                        pdf_bytes = convert_md_to_pdf(md_text)
                        pdf_filename = orig_filename.replace(".md", ".pdf")
                        zip_file.writestr(pdf_filename, pdf_bytes)
                    except Exception as e:
                        logger.error("Błąd generowania PDF dla %s: %s", orig_filename, e)
            
            zip_buffer.seek(0)
            return send_file(
                zip_buffer,
                mimetype="application/zip",
                as_attachment=True,
                download_name="dokumenty.zip",
            )
            
    except Exception:
        logger.exception("Błąd ogólny podczas konwersji")
        return jsonify({"error": "Wystąpił błąd serwera"}), 500


if __name__ == "__main__":
    app.run(debug=True)
