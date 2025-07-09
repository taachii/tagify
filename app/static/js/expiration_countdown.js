function formatTimeLeft(seconds) {
    if (seconds <= 0) return "Wygasła";

    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);

    return `Dostępna (${h}h ${m}m ${s}s)`;
  }

  function updateCountdowns() {
    document.querySelectorAll(".countdown").forEach(el => {
      let seconds = parseInt(el.getAttribute("data-seconds"));
      if (isNaN(seconds)) return;

      seconds -= 1;
      el.setAttribute("data-seconds", seconds);
      el.textContent = formatTimeLeft(seconds);

      if (seconds <= 0) {
        el.classList.remove("status-active");
        el.classList.add("status-inactive");
        el.textContent = "Wygasła";

        // Ukryj przycisk pobierania ZIP-a, jeśli istnieje
        const row = el.closest("tr");
        if (row) {
          const downloadBtn = row.querySelector(".download-btn");
          if (downloadBtn) downloadBtn.remove();
        }
      }
    });
  }

  setInterval(updateCountdowns, 1000);