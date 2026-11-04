import logging
import os
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError


class ObjectDetector:
    LABELS = [
        ("a laptop computer", "Laptop"),
        ("a smartphone", "Smartphone"),
        ("a television", "Television"),
        ("a computer monitor", "Monitor"),
        ("a pair of headphones", "Headphones"),
        ("a digital camera", "Camera"),
        ("a game console", "Game console"),
        ("a game controller", "Game controller"),
        ("a computer mouse", "Mouse"),
        ("a speaker", "Speaker"),
    ]
    _processor = None
    _model = None
    _attempted = False

    def __init__(self):
        self.modelName = os.getenv("LOCAL_DETECTOR_MODEL", "google/owlvit-base-patch32")
        self.mode = os.getenv("AI_DETECT_MODE", "owlvit").lower()
        self.available = False

    def _modelIsCached(self) -> bool:
        directory = "models--" + self.modelName.replace("/", "--")
        roots = [Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub" / directory,
                 Path.home() / ".cache" / "huggingface" / "hub" / directory]
        return any(any((root / "snapshots").glob("*/model.safetensors")) or
                   any((root / "snapshots").glob("*/pytorch_model.bin"))
                   for root in roots if root.exists())

    def _loadModel(self) -> bool:
        if self.mode == "off":
            return False
        if ObjectDetector._model is not None:
            self.available = True
            return True
        if ObjectDetector._attempted or not self._modelIsCached():
            return False
        ObjectDetector._attempted = True
        try:
            from transformers import OwlViTForObjectDetection, OwlViTProcessor
            ObjectDetector._processor = OwlViTProcessor.from_pretrained(self.modelName, local_files_only=True)
            ObjectDetector._model = OwlViTForObjectDetection.from_pretrained(self.modelName, local_files_only=True)
            ObjectDetector._model.eval()
            self.available = True
            return True
        except Exception as error:
            logging.getLogger(__name__).warning("Cached object detector unavailable: %s", error)
            return False

    def detect(self, content: bytes) -> list[dict]:
        if not content or len(content) > 5 * 1024 * 1024:
            raise ValueError("Image must be between 1 byte and 5 MB")
        try:
            with Image.open(BytesIO(content)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"} or source.width * source.height > 16000000:
                    raise ValueError("Upload a JPG, PNG or WebP image up to 16 megapixels")
                picture = ImageOps.exif_transpose(source).convert("RGB")
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
            raise ValueError("Invalid image file") from error
        if not self._loadModel():
            return []

        import torch
        prompts = [prompt for prompt, _ in self.LABELS]
        inputs = self._processor(text=[prompts], images=picture, return_tensors="pt")
        with torch.no_grad():
            output = self._model(**inputs)
        found = self._processor.post_process_object_detection(
            outputs=output, target_sizes=torch.tensor([picture.size[::-1]]), threshold=0.12)[0]
        objects = []
        width, height = picture.size
        for label, score, box in zip(found["labels"], found["scores"], found["boxes"]):
            left, top, right, bottom = box.tolist()
            if right - left < 12 or bottom - top < 12:
                continue
            objects.append({"label": self.LABELS[int(label)][1], "score": round(float(score), 3),
                            "box": [round(max(0, min(1, left / width)), 4),
                                    round(max(0, min(1, top / height)), 4),
                                    round(max(0, min(1, right / width)), 4),
                                    round(max(0, min(1, bottom / height)), 4)]})
        distinct = []
        for candidate in sorted(objects, key=lambda item: item["score"], reverse=True):
            left, top, right, bottom = candidate["box"]
            candidate_area = (right - left) * (bottom - top)
            duplicate = False
            for accepted in distinct:
                other_left, other_top, other_right, other_bottom = accepted["box"]
                intersection = max(0, min(right, other_right) - max(left, other_left)) * max(
                    0, min(bottom, other_bottom) - max(top, other_top))
                other_area = (other_right - other_left) * (other_bottom - other_top)
                if intersection > 0.8 * min(candidate_area, other_area):
                    duplicate = True
                    break
            if not duplicate:
                distinct.append(candidate)
            if len(distinct) == 8:
                break
        return distinct
