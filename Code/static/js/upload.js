const dropZone = document.querySelector(".drop-zone");
const fileInput = document.querySelector("input[type=file]");

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", e => {
    e.preventDefault();
    dropZone.style.background = "#e1f5fe";
});

dropZone.addEventListener("dragleave", () => {
    dropZone.style.background = "white";
});

dropZone.addEventListener("drop", e => {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    dropZone.style.background = "white";
});
