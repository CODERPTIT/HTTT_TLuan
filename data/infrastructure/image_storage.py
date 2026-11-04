from io import BytesIO
from pathlib import Path
from uuid import uuid4
from PIL import Image, UnidentifiedImageError


class ImageStorage:
    MAX_SIZE = 5 * 1024 * 1024
    TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, filename: str, content_type: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in self.TYPES or self.TYPES[suffix] != content_type:
            raise ValueError("Upload a JPG, PNG or WebP image")
        if not content or len(content) > self.MAX_SIZE:
            raise ValueError("Image must be between 1 byte and 5 MB")
        try:
            with Image.open(BytesIO(content)) as picture:
                expected_format = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}[content_type]
                if picture.format != expected_format or picture.width * picture.height > 16000000:
                    raise ValueError("Unsupported image or image dimensions too large")
                picture.verify()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
            raise ValueError("Invalid image file") from error
        reference = uuid4().hex + suffix
        (self.root / reference).write_bytes(content)
        return reference

    def resolve(self, reference: str) -> Path:
        if Path(reference).name != reference or "/" in reference or "\\" in reference:
            raise ValueError("Invalid image reference")
        path = (self.root / reference).resolve()
        if path.parent != self.root or not path.is_file():
            raise ValueError("Image not found")
        return path

    def crop(self, reference: str, box: list[float]) -> str:
        if len(box) != 4 or any(not isinstance(value, (float, int)) or isinstance(value, bool)
                                for value in box):
            raise ValueError("Invalid crop area")
        left, top, right, bottom = box
        if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
            raise ValueError("Invalid crop area")
        with Image.open(self.resolve(reference)) as source:
            from PIL import ImageOps
            picture = ImageOps.exif_transpose(source).convert("RGB")
            width, height = picture.size
            cropped = picture.crop((int(left * width), int(top * height),
                                    max(int(right * width), int(left * width) + 1),
                                    max(int(bottom * height), int(top * height) + 1)))
            buffer = BytesIO()
            cropped.save(buffer, format="JPEG", quality=90)
        return self.save(buffer.getvalue(), "crop.jpg", "image/jpeg")

