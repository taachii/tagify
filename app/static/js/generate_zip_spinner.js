document.getElementById("generateZipForm")?.addEventListener("submit", function () {
  document.getElementById("generatingSpinner").style.display = "block";
  document.body.style.cursor = "progress";
  const btn = document.querySelector('button[type="submit"]');
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Generowanie ZIP-a...";
  }
});