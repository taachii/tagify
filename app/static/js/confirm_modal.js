let pendingDeleteForm = null;

document.addEventListener('DOMContentLoaded', () => {
  const yesBtn = document.getElementById("confirmYes");
  const noBtn = document.getElementById("confirmNo");

  if (yesBtn && noBtn) {
    yesBtn.addEventListener("click", () => {
      if (pendingDeleteForm) pendingDeleteForm.submit();
      closeConfirmModal();
    });

    noBtn.addEventListener("click", () => {
      closeConfirmModal();
    });
  }
});

function openConfirmModal(message, form) {
  const modal = document.getElementById("confirmModal");
  const msg = document.getElementById("confirmText");
  if (modal && msg) {
    msg.textContent = message;
    modal.classList.remove("hidden");
    pendingDeleteForm = form;
  }
}

function closeConfirmModal() {
  const modal = document.getElementById("confirmModal");
  if (modal) {
    modal.classList.add("hidden");
    pendingDeleteForm = null;
  }
}
