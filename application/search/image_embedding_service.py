import logging
import os
from pathlib import Path
from PIL import Image, ImageOps


class ImageEmbeddingService:
    _model = None
    _preprocess = None
    _modelAttempted = False
    _vectors = {}

    def __init__(self, products):
        self.products = products
        self.modelName = os.getenv("LOCAL_IMAGE_MODEL", "Marqo/marqo-fashionSigLIP")
        self.mode = os.getenv("AI_IMAGE_MODE", "siglip").lower()
        self.backend = "basic"

    def _modelIsCached(self) -> bool:
        model_directory = "models--" + self.modelName.replace("/", "--")
        roots = [Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub" / model_directory,
                 Path.home() / ".cache" / "huggingface" / "hub" / model_directory]
        return any(any((root / "snapshots").glob("*/model.safetensors")) for root in roots if root.exists())

    def _loadModel(self) -> bool:
        if self.mode == "basic":
            return False
        if ImageEmbeddingService._model is not None:
            self.backend = "siglip"
            return True
        if ImageEmbeddingService._modelAttempted or not self._modelIsCached():
            return False
        ImageEmbeddingService._modelAttempted = True
        try:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            import open_clip
            model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:" + self.modelName)
            model.eval()
            ImageEmbeddingService._model = model
            ImageEmbeddingService._preprocess = preprocess
            self.backend = "siglip"
            return True
        except Exception as error:
            logging.getLogger(__name__).warning("Cached image model unavailable; using basic fallback: %s", error)
            return False

    @staticmethod
    def _basic(path: Path) -> list[float]:
        with Image.open(path) as source:
            picture = ImageOps.fit(source.convert("RGB"), (16, 16))
            histogram = picture.histogram()
            bins = [sum(histogram[channel * 256 + start:channel * 256 + start + 32]) / 256
                    for channel in range(3) for start in range(0, 256, 32)]
            gray = picture.convert("L")
            pixels = list(gray.get_flattened_data())
            texture = [abs(pixels[position] - pixels[position - 1]) / 255 for position in range(1, 256, 16)]
            return bins + texture

    def embedMany(self, imageReferences: list[str]) -> list[list[float]]:
        paths = [self.products.imagePath(reference) for reference in imageReferences]
        if not self._loadModel():
            self.backend = "basic"
            return [self._basic(path) for path in paths]
        import torch
        vectors = [None] * len(paths)
        pending = []
        positions = []
        for position, path in enumerate(paths):
            key = (str(path.resolve()), path.stat().st_mtime_ns)
            cached = ImageEmbeddingService._vectors.get(key)
            if cached is None:
                with Image.open(path) as source:
                    pending.append(ImageEmbeddingService._preprocess(source.convert("RGB")))
                positions.append((position, key))
            else:
                vectors[position] = cached
        if pending:
            with torch.no_grad():
                encoded = ImageEmbeddingService._model.encode_image(torch.stack(pending), normalize=True).cpu().tolist()
            for (position, key), vector in zip(positions, encoded):
                ImageEmbeddingService._vectors[key] = vector
                vectors[position] = vector
        return vectors

    def embed(self, imageReference: str) -> list[float]:
        return self.embedMany([imageReference])[0]

