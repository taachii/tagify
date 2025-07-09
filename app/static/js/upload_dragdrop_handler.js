const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("zip_file");
const fileNameDisplay = document.getElementById("file-name");

const updateFileName = file => {
  fileNameDisplay.textContent = file.name;
};

["dragenter", "dragover"].forEach(evt =>
  dropZone?.addEventListener(evt, e => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  })
);

["dragleave", "drop"].forEach(evt =>
  dropZone?.addEventListener(evt, e => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
  })
);

dropZone?.addEventListener("drop", e => {
  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].name.endsWith(".zip")) {
    fileInput.files = files;
    updateFileName(files[0]);
  } else {
    alert("Dozwolone są tylko pliki ZIP.");
  }
});

fileInput?.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    updateFileName(fileInput.files[0]);
  }
});
