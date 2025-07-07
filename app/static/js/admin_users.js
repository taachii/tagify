let currentPage = 1;
let currentSearch = '';
let pendingDeleteForm = null;

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchBox');
  searchInput.addEventListener('input', debounce(() => {
    currentSearch = searchInput.value.trim();
    currentPage = 1;
    loadUsers();
  }, 300));

  loadUsers();

  document.getElementById("confirmYes")?.addEventListener("click", () => {
    if (pendingDeleteForm) pendingDeleteForm.submit();
    closeConfirmModal();
  });

  document.getElementById("confirmNo")?.addEventListener("click", () => {
    closeConfirmModal();
  });
});

function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

function loadUsers() {
  const url = `/admin/dashboard/data?page=${currentPage}&search=${encodeURIComponent(currentSearch)}`;
  fetch(url)
    .then(res => res.json())
    .then(data => {
      renderTable(data.users);
      renderPagination(data.page, data.total_pages);
    });
}

function renderTable(users) {
  const tableHTML = `
    <table class="admin-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Nazwa użytkownika</th>
          <th>Email</th>
          <th>Rola</th>
          <th>Utworzono</th>
          <th>Status</th>
          <th>Akcje</th>
        </tr>
      </thead>
      <tbody>
        ${users.map(user => `
          <tr class="${user.is_active ? '' : 'inactive-row'}">
            <td>${user.uid}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>${user.created_at}</td>
            <td>
              ${user.is_active ? '<span class="status-active">Aktywny</span>' : '<span class="status-inactive">Nieaktywny</span>'}
            </td>
            <td class="action-cell">
              <a href="/admin/dashboard/user/${user.uid}/edit" class="icon-button" title="Edytuj">
                <i class="fas fa-edit"></i>
              </a>
              <button 
                class="icon-button toggle-active-btn" 
                title="${user.is_active ? 'Dezaktywuj' : 'Aktywuj'}"
                data-user-id="${user.uid}"
                data-action="${user.is_active ? 'deactivate' : 'activate'}"
              >
                <i class="fas ${user.is_active ? 'fa-user-lock' : 'fa-user-check'}"></i>
              </button>
              <form id="delete-user-${user.uid}" action="/admin/dashboard/user/${user.uid}/delete" method="POST" style="display:inline;">
                <button type="button" class="icon-button danger" title="Usuń" onclick="openConfirmModal('Na pewno chcesz usunąć użytkownika?', document.getElementById('delete-user-${user.uid}'))">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </form>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  document.getElementById('usersTable').innerHTML = tableHTML;
}

function renderPagination(current, total) {
  let html = '';

  html += current > 1
    ? `<button class="pagination-btn" onclick="goToPage(${current - 1})">&laquo; Poprzednia</button>`
    : `<button class="pagination-btn disabled" disabled>&laquo; Poprzednia</button>`;

  html += `<span class="pagination-info">${current} / ${total}</span>`;

  html += current < total
    ? `<button class="pagination-btn" onclick="goToPage(${current + 1})">Następna &raquo;</button>`
    : `<button class="pagination-btn disabled" disabled>Następna &raquo;</button>`;

  document.getElementById('pagination').innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  loadUsers();
}

document.addEventListener('click', function (event) {
  if (event.target.closest('.toggle-active-btn')) {
    const button = event.target.closest('.toggle-active-btn');
    const userId = button.dataset.userId;
    const action = button.dataset.action;

    fetch(`/admin/dashboard/user/${userId}/${action}`, {
      method: 'POST'
    })
    .then(response => {
      if (!response.ok) throw new Error('Błąd przy zmianie statusu');
      loadUsers();
    })
    .catch(error => {
      alert('Wystąpił błąd: ' + error.message);
    });
  }
});

function openConfirmModal(message, form) {
  document.getElementById("confirmText").textContent = message;
  document.getElementById("confirmModal").classList.remove("hidden");
  pendingDeleteForm = form;
}

function closeConfirmModal() {
  document.getElementById("confirmModal").classList.add("hidden");
  pendingDeleteForm = null;
}
