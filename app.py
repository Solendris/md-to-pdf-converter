"""Serwer Flask — MD to PDF Converter."""

import io
from flask import Flask, request, send_file, render_template, jsonify
from converter import convert_md_to_pdf

app = Flask(__name__)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    md_text = None

    # Obsługa przesłanego pliku .md
    if "file" in request.files and request.files["file"].filename:
        f = request.files["file"]
        if not f.filename.endswith(".md"):
            return jsonify({"error": "Plik musi mieć rozszerzenie .md"}), 400
        raw = f.read(MAX_FILE_SIZE + 1)
        if len(raw) > MAX_FILE_SIZE:
            return jsonify({"error": "Plik jest za duży (max 5 MB)"}), 413
        md_text = raw.decode("utf-8", errors="replace")

    # Obsługa tekstu wklejonego w edytorze
    elif "text" in request.form and request.form["text"].strip():
        md_text = request.form["text"]

    else:
        return jsonify({"error": "Brak treści do konwersji"}), 400

    pdf_bytes = convert_md_to_pdf(md_text)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="dokument.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
