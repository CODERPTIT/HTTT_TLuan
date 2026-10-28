from PIL import Image, ImageOps


class ImageEmbeddingService:
    def __init__(self, products):
        self.products = products

    def embed(self, imageReference: str) -> list[float]:
        with Image.open(self.products._imagePath(imageReference)) as source:
            picture = ImageOps.fit(source.convert("RGB"), (16, 16))
            histogram = picture.histogram()
            bins = [sum(histogram[channel * 256 + start:channel * 256 + start + 32]) / 256
                    for channel in range(3) for start in range(0, 256, 32)]
            gray = picture.convert("L")
            pixels = list(gray.get_flattened_data())
            texture = [abs(pixels[position] - pixels[position - 1]) / 255 for position in range(1, 256, 16)]
            return bins + texture

