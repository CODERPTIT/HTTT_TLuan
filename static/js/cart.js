async function cartRequest(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Unable to update your bag.");
  return payload;
}
document.querySelectorAll(".add-cart").forEach(form => {
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const button = form.querySelector("button");
    button.disabled = true;
    button.classList.add("is-loading");
    try {
      const result = await cartRequest(form.action, {method: "POST", body: new FormData(form), headers: {Accept: "application/json"}});
      document.getElementById("cart-count").textContent = result.count;
      window.notify("Added to cart");
    } catch (error) { window.notify(error.message); }
    finally { button.disabled = false; button.classList.remove("is-loading"); }
  });
});
document.querySelectorAll(".cart-quantity").forEach(input => {
  input.addEventListener("change", async () => {
    if (!input.reportValidity()) return;
    input.disabled = true;
    try {
      await cartRequest("/cart/items/" + input.dataset.product, {method: "PATCH", headers: {"Content-Type": "application/json", Accept: "application/json"}, body: JSON.stringify({quantity: Number(input.value)})});
      location.reload();
    } catch (error) { window.notify(error.message); input.disabled = false; }
  });
});
document.querySelectorAll(".remove-item").forEach(button => {
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      await cartRequest("/cart/items/" + button.dataset.product, {method: "DELETE", headers: {Accept: "application/json"}});
      location.reload();
    } catch (error) { window.notify(error.message); button.disabled = false; }
  });
});

document.querySelectorAll(".qty-btn").forEach(button => {
  button.addEventListener("click", () => {
    const wrap = button.closest(".qty-stepper-wrap");
    if (!wrap) return;
    const input = wrap.querySelector(".cart-quantity");
    if (!input) return;
    const currentVal = parseInt(input.value, 10) || 1;
    const min = parseInt(input.min, 10) || 1;
    const max = parseInt(input.max, 10) || 999;
    if (button.classList.contains("inc") && currentVal < max) {
      input.value = currentVal + 1;
      input.dispatchEvent(new Event("change"));
    } else if (button.classList.contains("dec") && currentVal > min) {
      input.value = currentVal - 1;
      input.dispatchEvent(new Event("change"));
    }
  });
});


