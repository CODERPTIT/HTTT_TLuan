document.getElementById("image-open").addEventListener("click", () => document.getElementById("image-dialog").showModal());
let previewUrl;
document.getElementById("image-input").addEventListener("change", event => {
  const file = event.target.files[0];
  const preview = document.getElementById("image-preview");
  preview.hidden = true;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  if (!file) return;
  if (file.size > 5 * 1024 * 1024 || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
    event.target.value = "";
    window.notify("Choose a JPG, PNG or WebP image up to 5 MB.");
    return;
  }
  previewUrl = URL.createObjectURL(file);
  preview.src = previewUrl;
  preview.hidden = false;
});

