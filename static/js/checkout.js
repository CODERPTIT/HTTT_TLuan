const checkoutForm = document.getElementById("checkout-form");
if (checkoutForm) {
  checkoutForm.querySelectorAll('input[name="paymentMethod"]').forEach(input => {
    input.addEventListener("change", () => {
      const failure = checkoutForm.querySelector('input[name="simulateFailure"]');
      failure.disabled = input.value === "Cash on Delivery";
      if (failure.disabled) failure.checked = false;
    });
  });
}

