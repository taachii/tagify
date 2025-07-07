let currentPage = 1;
let token = "";
let corrections = {};

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("previewGallery");
  token = container.dataset.token;

  loadResults();
});

function loadResults() {
  fetch(`/user/classification/preview/data?token=${token}&page=${currentPage}`)
    .then(res => res.json())
    .then(data => {
      renderPreview(data.results);
      renderPagination(data.page, data.total_pages);
    });
}

function renderPreview(items) {
  const gallery = document.getElementById("previewGallery");
  gallery.innerHTML = items.map((item, index) => {
    const selectedValue = corrections[item.filename] || item.predicted_label;

    return `
      <div class="preview-item confidence-${getConfidenceLevel(item.confidence)}">
        <img src="/static/${item.static_path}" alt="${item.filename}">
        <p><strong>${item.filename}</strong></p>
        <p class="confidence-color-${getConfidenceLevel(item.confidence)}">
          Pewność: ${(item.confidence * 100).toFixed(1)}%
        </p>
        <label for="corrections_${index}">Popraw klasę:</label>
        <select name="corrections[${item.filename}]" id="corrections_${index}" data-filename="${item.filename}">
          ${["animals", "buildings", "food", "landscape", "people", "plants", "vehicles"].map(cls => `
            <option value="${cls}" ${cls === selectedValue ? "selected" : ""}>${cls}</option>
          `).join("")}
        </select>
      </div>
    `;
  }).join("");

  // Dodaj listener do każdego selecta
  document.querySelectorAll("select[data-filename]").forEach(select => {
    select.addEventListener("change", () => {
      const filename = select.dataset.filename;
      corrections[filename] = select.value;
    });
  });
}

function getConfidenceLevel(conf) {
  if (conf < 0.4) return "low";
  if (conf < 0.7) return "mid";
  return "high";
}

function renderPagination(current, total) {
  const container = document.getElementById("pagination");
  let html = '';

  html += current > 1
    ? `<button type="button" onclick="goToPage(${current - 1})" class="pagination-btn">&laquo; Poprzednia</button>`
    : `<button type="button" class="pagination-btn disabled" disabled>&laquo; Poprzednia</button>`;

  html += `<span class="pagination-info">${current} / ${total}</span>`;

  html += current < total
    ? `<button type="button" onclick="goToPage(${current + 1})" class="pagination-btn">Następna &raquo;</button>`
    : `<button type="button" class="pagination-btn disabled" disabled>Następna &raquo;</button>`;

  container.innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  loadResults();
}

// Obsługa formularza ZIP
document.getElementById("generateZipForm")?.addEventListener("submit", function () {
  const form = this;

  // Dołącz poprawki jako hidden inputy
  Object.entries(corrections).forEach(([filename, value]) => {
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = `corrections[${filename}]`;
    hiddenInput.value = value;
    form.appendChild(hiddenInput);
  });

  // Spinner i blokada przycisku
  document.getElementById("generatingSpinner").style.display = "block";
  document.body.style.cursor = "progress";

  const btn = form.querySelector('button[type="submit"]');
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Generowanie ZIP-a...";
  }
});
