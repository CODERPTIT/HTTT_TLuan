document.getElementById("image-open").addEventListener("click", () => document.getElementById("image-dialog").showModal());

const filterToggle = document.getElementById("filter-toggle");
if (filterToggle) {
  filterToggle.addEventListener("click", () => {
    const panel = filterToggle.closest(".filter-panel");
    const expanded = panel.classList.toggle("is-open");
    filterToggle.setAttribute("aria-expanded", String(expanded));
  });
}

const imageInput = document.getElementById("image-input");
const preview = document.getElementById("image-preview");
const stage = document.getElementById("detection-stage");
const boxes = document.getElementById("detection-boxes");
const cropBox = document.getElementById("crop-box");
const detectionStatus = document.getElementById("detection-status");
let previewUrl;
let activeDetection;

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (activeDetection) activeDetection.abort();
  activeDetection = null;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  stage.hidden = true;
  boxes.replaceChildren();
  cropBox.value = "";
  detectionStatus.textContent = "Choose a photo to detect objects automatically.";
  if (!file) return;
  if (file.size > 5 * 1024 * 1024 || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
    imageInput.value = "";
    window.notify("Choose a JPG, PNG or WebP image up to 5 MB.");
    return;
  }
  previewUrl = URL.createObjectURL(file);
  preview.src = previewUrl;
  stage.hidden = false;
  detectObjects(file);
});

async function detectObjects(file) {
  const controller = new AbortController();
  activeDetection = controller;
  detectionStatus.textContent = "Detecting objects… You can search the whole photo now.";
  try {
    const data = new FormData();
    data.append("image", file);
    const response = await fetch("/search/detect", {method: "POST", body: data,
      headers: {Accept: "application/json"}, signal: controller.signal});
    const result = await response.json();
    if (controller !== activeDetection) return;
    if (!response.ok) throw new Error(result.detail || "Object detection failed.");
    if (!result.available) {
      detectionStatus.textContent = "Object detector is unavailable locally. Search will use the whole photo.";
      return;
    }
    if (!result.objects.length) {
      detectionStatus.textContent = "No electronics detected. Search will use the whole photo.";
      return;
    }
    for (const object of result.objects) {
      const [left, top, right, bottom] = object.box;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "detection-box";
      button.style.left = `${left * 100}%`;
      button.style.top = `${top * 100}%`;
      button.style.width = `${(right - left) * 100}%`;
      button.style.height = `${(bottom - top) * 100}%`;
      button.setAttribute("aria-label", `Search the detected ${object.label}`);
      const label = document.createElement("span");
      label.textContent = object.label;
      button.append(label);
      button.addEventListener("click", () => {
        if (button.classList.contains("selected")) {
          button.classList.remove("selected");
          cropBox.value = "";
          detectionStatus.textContent = "No object selected. Search will use the whole photo.";
          return;
        }
        boxes.querySelectorAll(".selected").forEach(item => item.classList.remove("selected"));
        button.classList.add("selected");
        cropBox.value = JSON.stringify(object.box);
        detectionStatus.textContent = `Selected ${object.label}. Search will use this part of the photo.`;
      });
      boxes.append(button);
    }
    detectionStatus.textContent = "Select an object, or leave unselected to search the whole photo.";
  } catch (error) {
    if (controller === activeDetection && error.name !== "AbortError") {
      detectionStatus.textContent = "Could not detect objects. Search will use the whole photo.";
    }
  } finally {
    if (controller === activeDetection) activeDetection = null;
  }
}
