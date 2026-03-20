/* global document, File, fetch, URL */
"use strict";

const dropZone    = document.getElementById("drop-zone");
const fileInput   = document.getElementById("file-input");
const fileBadge   = document.getElementById("file-badge");
const fileName    = document.getElementById("file-name");
const fileClear   = document.getElementById("file-clear");
const mdEditor    = document.getElementById("md-editor");
const clearText   = document.getElementById("clear-text");
const convertBtn  = document.getElementById("convert-btn");
const errorMsg    = document.getElementById("error-msg");
const btnText     = convertBtn.querySelector(".btn-text");
const btnSpinner  = convertBtn.querySelector(".btn-spinner");

let selectedFile = null;

/* ===== Helpers ===== */
function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove("hidden");
}
function clearError() {
    errorMsg.classList.add("hidden");
}
function updateConvertBtn() {
    const hasContent = selectedFile !== null || mdEditor.value.trim().length > 0;
    convertBtn.disabled = !hasContent;
}
function setFile(file) {
    if (!file.name.endsWith(".md")) {
        showError("Akceptowane są tylko pliki .md");
        return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    fileBadge.classList.remove("hidden");
    // Wczytaj plik do edytora (podgląd)
    const reader = new FileReader();
    reader.onload = (e) => { mdEditor.value = e.target.result; updateConvertBtn(); };
    reader.readAsText(file, "utf-8");
    clearError();
    updateConvertBtn();
}
function clearFile() {
    selectedFile = null;
    fileInput.value = "";
    fileBadge.classList.add("hidden");
    fileName.textContent = "";
    updateConvertBtn();
}

/* ===== Drag & Drop ===== */
dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});
["dragleave", "dragend"].forEach(ev => {
    dropZone.addEventListener(ev, () => dropZone.classList.remove("drag-over"));
});
dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) setFile(file);
});

/* ===== File Input ===== */
fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) setFile(fileInput.files[0]);
});
fileClear.addEventListener("click", clearFile);

/* ===== Editor ===== */
mdEditor.addEventListener("input", () => { clearError(); updateConvertBtn(); });
clearText.addEventListener("click", () => { mdEditor.value = ""; clearFile(); clearError(); updateConvertBtn(); });

/* ===== Conversion ===== */
convertBtn.addEventListener("click", async () => {
    clearError();

    const formData = new FormData();
    if (selectedFile) {
        formData.append("file", selectedFile);
    } else {
        formData.append("text", mdEditor.value);
    }

    // Stan ładowania
    convertBtn.disabled = true;
    btnText.classList.add("hidden");
    btnSpinner.classList.remove("hidden");

    try {
        const response = await fetch("/convert", { method: "POST", body: formData });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.error || `Błąd serwera: ${response.status}`);
        }

        // Pobierz PDF
        const blob = await response.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement("a");
        a.href     = url;
        a.download = selectedFile ? selectedFile.name.replace(/\.md$/, ".pdf") : "dokument.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);

    } catch (err) {
        showError(err.message || "Nieznany błąd. Spróbuj ponownie.");
    } finally {
        convertBtn.disabled = false;
        btnText.classList.remove("hidden");
        btnSpinner.classList.add("hidden");
        updateConvertBtn();
    }
});
