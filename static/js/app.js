window.notify = function(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => { toast.hidden = true; }, 4500);
};
document.querySelectorAll("form").forEach(form => {
  if (form.method === "dialog" || form.classList.contains("add-cart")) return;
  form.addEventListener("submit", () => {
    const button = form.querySelector('button[type="submit"], button:not([type])');
    if (button) { button.disabled = true; button.classList.add("is-loading"); }
  });
});
window.addEventListener("pageshow", () => {
  document.querySelectorAll(".is-loading").forEach(button => {
    button.disabled = false;
    button.classList.remove("is-loading");
  });
});

