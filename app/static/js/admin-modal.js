document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("admin-modal");
  const modalTitle = document.getElementById("modal-title");
  const closeBtn = document.querySelector(".close-modal");

  document.querySelectorAll(".gear-icon").forEach(btn => {
    btn.addEventListener("click", () => {
      const username = btn.getAttribute("data-username");
      modalTitle.textContent = `Opcje dla: ${username}`;
      modal.classList.add("active");
    });
  });

  closeBtn.addEventListener("click", () => {
    modal.classList.remove("active");
  });

  window.addEventListener("click", e => {
    if (e.target === modal) {
      modal.classList.remove("active");
    }
  });
});
