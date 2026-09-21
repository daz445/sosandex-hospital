// ── Hospital App — Client JS ──
document.addEventListener("DOMContentLoaded", () => {
  setupModals();
  setupForms();
});

// ── Modal helpers ──
function setupModals() {
  document.querySelectorAll("[data-modal]").forEach(trigger => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const id = trigger.dataset.modal;
      document.getElementById(id)?.classList.add("active");
    });
  });
  document.querySelectorAll(".modal-close, .modal-overlay").forEach(el => {
    el.addEventListener("click", (e) => {
      if (e.target === el || e.target.classList.contains("modal-close")) {
        el.closest(".modal-overlay")?.classList.remove("active");
      }
    });
  });
}

// ── Form handling ──
function setupForms() {
  document.querySelectorAll("form[data-api]").forEach(form => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const url = form.dataset.api;
      const method = form.dataset.method || "POST";
      const redirect = form.dataset.redirect || null;
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());

      try {
        const resp = await fetch(url, {
          method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          throw new Error(err.detail || `Ошибка ${resp.status}`);
        }
        if (redirect) window.location.href = redirect;
        else window.location.reload();
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

// ── Delete confirmation ──
async function confirmDelete(url, label) {
  if (!confirm(`Удалить "${label}"?`)) return;
  const resp = await fetch(url, { method: "DELETE" });
  if (resp.ok) window.location.reload();
  else alert("Ошибка удаления");
}

// ── Cancel appointment ──
async function cancelAppointment(id) {
  if (!confirm("Отменить запись?")) return;
  const resp = await fetch(`/api/appointments/${id}/cancel`, { method: "PUT" });
  if (resp.ok) window.location.reload();
  else alert("Ошибка отмены");
}

// ── Complete appointment ──
async function completeAppointment(id) {
  const resp = await fetch(`/api/appointments/${id}/complete`, { method: "PUT" });
  if (resp.ok) window.location.reload();
  else alert("Ошибка завершения");
}
