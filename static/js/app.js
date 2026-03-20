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

let selectedFiles = [];

/* ===== Helpers ===== */
function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove("hidden");
}
function clearError() {
    errorMsg.classList.add("hidden");
}
function updateConvertBtn() {
    const hasContent = selectedFiles.length > 0 || mdEditor.value.trim().length > 0;
    convertBtn.disabled = !hasContent;
}
function setFiles(fileList) {
    const validFiles = Array.from(fileList).filter(f => f.name.endsWith(".md"));
    if (validFiles.length === 0) {
        showError("Załadowano pliki, ale żaden nie jest w formacie .md");
        return;
    }
    
    selectedFiles = validFiles;
    
    if (selectedFiles.length === 1) {
        fileName.textContent = selectedFiles[0].name;
    } else {
        fileName.textContent = `Wybrano plików: ${selectedFiles.length}`;
    }
    fileBadge.classList.remove("hidden");
    
    // Wczytaj pierwszy plik do edytora jako podgląd
    const reader = new FileReader();
    reader.onload = (e) => { 
        mdEditor.value = e.target.result; 
        if (selectedFiles.length > 1) {
            mdEditor.value += `\n\n... (oraz treść z ${selectedFiles.length - 1} innych plików, które zostaną połączone)`;
        }
        updateConvertBtn(); 
    };
    reader.readAsText(selectedFiles[0], "utf-8");
    clearError();
    updateConvertBtn();
}
function clearFiles() {
    selectedFiles = [];
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
    if (e.dataTransfer.files.length > 0) {
        setFiles(e.dataTransfer.files);
    }
});

/* ===== File Input ===== */
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        setFiles(fileInput.files);
    }
});
fileClear.addEventListener("click", clearFiles);

/* ===== Editor ===== */
mdEditor.addEventListener("input", () => { clearError(); updateConvertBtn(); });
clearText.addEventListener("click", () => { mdEditor.value = ""; clearFiles(); clearError(); updateConvertBtn(); });

/* ===== Conversion ===== */
convertBtn.addEventListener("click", async () => {
    clearError();

    const formData = new FormData();
    if (selectedFiles.length > 0) {
        selectedFiles.forEach(file => {
            formData.append("files", file);
        });
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

        // Pobierz PDF lub ZIP
        const blob = await response.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement("a");
        a.href     = url;
        
        // Określ nazwę pliku
        let downloadName = "dokument.pdf";
        if (selectedFiles.length === 1) {
            downloadName = selectedFiles[0].name.replace(/\.md$/, ".pdf");
        } else if (selectedFiles.length > 1) {
            downloadName = "dokumenty.zip";
        }
        
        a.download = downloadName;
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
