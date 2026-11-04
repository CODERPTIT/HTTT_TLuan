import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from domain.product.product import Product, ProductStatus


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower().replace("đ", "d"))
    return " ".join("".join(char for char in value if not unicodedata.combining(char)).split())


@dataclass
class QueryFilters:
    semanticText: str
    minimumPrice: Decimal | None = None
    maximumPrice: Decimal | None = None
    brands: set[str] = field(default_factory=set)
    categories: set[str] = field(default_factory=set)
    colors: set[str] = field(default_factory=set)
    availableOnly: bool = False

    AMOUNT = r"\d+(?:[.,]\d+)*\s*(?:trieu|tr|million|m|nghin|ngan|thousand|k|vnd|dong|d)?"
    COLOR_ALIASES = {
        "black": "black", "den": "black",
        "white": "white", "trang": "white",
        "gray": "gray", "grey": "gray", "xam": "gray",
        "silver": "silver", "bac": "silver",
        "blue": "blue", "xanh duong": "blue", "xanh": "blue",
        "green": "green", "xanh la": "green",
        "red": "red", "do": "red",
        "purple": "purple", "tim": "purple",
        "pink": "pink", "hong": "pink",
        "gold": "gold", "vang": "gold",
    }
    CATEGORY_ALIASES = {
        "Laptops": ("may tinh xach tay", "laptops", "laptop"),
        "Smartphones": ("dien thoai thong minh", "dien thoai", "smartphones", "smartphone", "phones", "phone"),
        "Televisions": ("televisions", "television", "tivi", "tv"),
        "Audio": ("thiet bi am thanh", "tai nghe", "loa", "audio", "headphones", "headphone", "earbuds", "speaker"),
        "Cameras": ("may anh", "cameras", "camera"),
        "Gaming": ("may choi game", "gaming console", "game console", "console"),
        "Smart Home": ("nha thong minh", "smart home"),
        "Accessories": ("phu kien", "accessories", "accessory"),
    }

    @classmethod
    def parse(cls, text: str, products: list[Product]) -> "QueryFilters":
        original = _normalize(text)
        working = original
        parsed = cls(semanticText=original)

        range_pattern = re.compile(
            rf"(?:gia\s+)?(?:tu|from|between)\s+({cls.AMOUNT})\s+(?:den|toi|to|and)\s+({cls.AMOUNT})")
        match = range_pattern.search(working)
        if match:
            parsed.minimumPrice = cls._money(match.group(1))
            parsed.maximumPrice = cls._money(match.group(2))
            working = cls._remove(working, match.span())
        else:
            maximum_pattern = re.compile(
                rf"(?:gia\s+)?(?:duoi|nho hon|khong qua|toi da|under|below|up to|less than)\s+({cls.AMOUNT})")
            match = maximum_pattern.search(working)
            if match:
                parsed.maximumPrice = cls._money(match.group(1))
                working = cls._remove(working, match.span())
            minimum_pattern = re.compile(
                rf"(?:gia\s+)?(?:tren|lon hon|it nhat|toi thieu|over|above|from|at least|more than)\s+({cls.AMOUNT})")
            match = minimum_pattern.search(working)
            if match:
                parsed.minimumPrice = cls._money(match.group(1))
                working = cls._remove(working, match.span())

        for brand in sorted({product.brand for product in products}, key=len, reverse=True):
            pattern = re.compile(rf"(?<!\w){re.escape(_normalize(brand))}(?!\w)")
            if pattern.search(working):
                parsed.brands.add(brand)

        for category, aliases in cls.CATEGORY_ALIASES.items():
            for alias in sorted(aliases, key=len, reverse=True):
                pattern = re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)")
                if pattern.search(working):
                    parsed.categories.add(category)
                    break

        color_names = "|".join(re.escape(color) for color in sorted(cls.COLOR_ALIASES, key=len, reverse=True))
        color_pattern = re.compile(rf"(?:mau|color|colour)\s+({color_names})(?!\w)")
        for match in list(color_pattern.finditer(working)):
            parsed.colors.add(cls.COLOR_ALIASES[match.group(1)])
        working = color_pattern.sub(" ", working)

        availability_pattern = re.compile(r"(?<!\w)(?:con hang|san hang|in stock|available)(?!\w)")
        if availability_pattern.search(working):
            parsed.availableOnly = True
            working = availability_pattern.sub(" ", working)

        working = re.sub(r"\b(?:do|san pham|product|products|hang)\b", " ", working)
        parsed.semanticText = " ".join(working.split())
        return parsed

    @classmethod
    def _money(cls, raw: str) -> Decimal:
        match = re.fullmatch(r"\s*(\d+(?:[.,]\d+)*)\s*([a-z]+)?\s*", raw)
        if not match:
            raise ValueError("Invalid price filter")
        number, unit = match.groups()
        unit = unit or ""
        multiplier = Decimal(1)
        if unit in {"trieu", "tr", "million", "m"}:
            multiplier = Decimal(1000000)
        elif unit in {"nghin", "ngan", "thousand", "k"}:
            multiplier = Decimal(1000)
        try:
            if multiplier > 1 and number.count(".") + number.count(",") <= 1:
                value = Decimal(number.replace(",", "."))
            else:
                value = Decimal(number.replace(".", "").replace(",", ""))
        except InvalidOperation as error:
            raise ValueError("Invalid price filter") from error
        return value * multiplier

    @staticmethod
    def _remove(value: str, span: tuple[int, int]) -> str:
        return value[:span[0]] + " " + value[span[1]:]

    def accepts(self, product: Product) -> bool:
        if self.minimumPrice is not None and product.price < self.minimumPrice:
            return False
        if self.maximumPrice is not None and product.price > self.maximumPrice:
            return False
        if self.brands and product.brand not in self.brands:
            return False
        if self.categories and product.category.categoryName not in self.categories:
            return False
        if self.availableOnly and (product.status != ProductStatus.ACTIVE or not product.isAvailable(1)):
            return False
        searchable = _normalize(product.searchableText())
        if self.colors and not any(re.search(rf"(?<!\w){re.escape(color)}(?!\w)", searchable)
                                   for color in self.colors):
            return False
        return True

