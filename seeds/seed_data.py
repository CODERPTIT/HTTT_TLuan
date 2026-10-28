from decimal import Decimal
from pathlib import Path
from shutil import copyfile
from PIL import Image, ImageDraw
from sqlalchemy import select
from domain.product.product import Product, ProductStatus
from domain.product.category import Category
from domain.product.product_unit import ProductUnit
from domain.product.product_specification import ProductSpecification
from data.infrastructure.product_database import categories, products
from data.infrastructure.order_database import customers
from data.repository.product_repository import ProductRepository
from data.repository.interaction_repository import InteractionRepository
from domain.interaction.interaction import InteractionType

CATALOG = [
    ("Laptops", "ASUS", "ROG Strix G16", "Gaming laptop with powerful graphics", 32990000, "16 GB RAM · RTX 4060 · 165 Hz"),
    ("Laptops", "Dell", "Inspiron 14", "Lightweight laptop for work and study", 18990000, "16 GB RAM · 512 GB SSD"),
    ("Laptops", "Apple", "MacBook Air M3", "Portable laptop with all-day battery", 26990000, "16 GB RAM · 13 inch Retina"),
    ("Smartphones", "Samsung", "Galaxy S24", "Flagship phone with vivid AMOLED display", 17990000, "256 GB · 50 MP camera"),
    ("Smartphones", "Apple", "iPhone 15", "Everyday phone with sharp photography", 18990000, "128 GB · OLED"),
    ("Smartphones", "Samsung", "Galaxy A55", "Balanced phone with long battery life", 9490000, "256 GB · 5000 mAh"),
    ("Televisions", "Samsung", "Crystal UHD 55", "Immersive 4K TV for home entertainment", 12990000, "55 inch · 4K · HDR"),
    ("Televisions", "LG", "OLED C3", "Cinematic 4K TV with deep contrast", 28990000, "55 inch · OLED · 120 Hz"),
    ("Televisions", "Sony", "Bravia X80L", "Natural color 4K TV for family viewing", 18990000, "50 inch · 4K · Google TV"),
    ("Audio", "Sony", "WH-1000XM5", "Wireless noise cancelling headphones", 7490000, "Bluetooth · 30 hour battery"),
    ("Audio", "JBL", "Flip 6", "Portable wireless waterproof speaker", 2490000, "IP67 · 12 hour battery"),
    ("Audio", "Apple", "AirPods Pro", "Wireless noise cancelling earbuds", 5490000, "USB-C · Spatial audio"),
    ("Cameras", "Canon", "EOS R50", "Compact mirrorless camera for creators", 17990000, "24 MP · 4K video"),
    ("Cameras", "Sony", "ZV-E10", "Interchangeable lens camera for video", 15990000, "24 MP · APS-C"),
    ("Cameras", "Canon", "PowerShot V10", "Pocket camera for everyday stories", 8990000, "4K video · wide angle"),
    ("Gaming", "Sony", "PlayStation 5", "Next generation gaming console", 12990000, "1 TB SSD · 4K gaming"),
    ("Gaming", "ASUS", "ROG Ally", "Handheld gaming console on the go", 14990000, "512 GB · 120 Hz"),
    ("Gaming", "Logitech", "G Pro Controller", "Responsive wireless gaming controller", 2490000, "Wireless · programmable buttons"),
    ("Smart Home", "Samsung", "SmartThings Hub", "Connect your smart home devices", 1990000, "Wi-Fi · Matter"),
    ("Smart Home", "LG", "PuriCare Mini", "Compact air purifier for your room", 3290000, "HEPA · quiet mode"),
    ("Smart Home", "Sony", "Smart Speaker", "Voice enabled home audio speaker", 2990000, "Wi-Fi · Bluetooth"),
    ("Accessories", "Logitech", "MX Master 3S", "Precision wireless mouse for productivity", 2290000, "8000 DPI · USB-C"),
    ("Accessories", "Lenovo", "USB-C Dock", "Expand your laptop connectivity", 1790000, "HDMI · USB 3 · 100 W"),
    ("Accessories", "Dell", "UltraSharp 27", "Crisp monitor for creative work", 7990000, "27 inch · QHD · IPS"),
]


def draw_product(path: Path, category: str, variant: int) -> None:
    picture = Image.new("RGB", (640, 480), "#f1f4fa")
    draw = ImageDraw.Draw(picture)
    accents = ["#255ca8", "#7856bd", "#0d8b8d"]
    accent = accents[variant % 3]
    draw.ellipse((120, 385, 530, 423), fill="#dce2ec")
    if category in {"Laptops", "Televisions", "Accessories", "Gaming"}:
        draw.rounded_rectangle((122, 78, 518, 330), 18, fill="#202b40")
        draw.rounded_rectangle((137, 93, 503, 313), 9, fill=accent)
        draw.polygon([(137, 313), (315, 135), (503, 260), (503, 313)], fill="#83c5ed")
        if category == "Laptops":
            draw.polygon([(122, 330), (518, 330), (574, 385), (66, 385)], fill="#9da9ba")
            draw.rounded_rectangle((66, 380, 574, 395), 7, fill="#536175")
        else:
            draw.rectangle((302, 330, 338, 384), fill="#536175")
            draw.rounded_rectangle((237, 381, 403, 394), 5, fill="#202b40")
    elif category == "Smartphones":
        draw.rounded_rectangle((218, 48, 422, 412), 30, fill="#202b40")
        draw.rounded_rectangle((230, 61, 410, 398), 22, fill=accent)
        draw.ellipse((240, 160, 440, 350), fill="#9ddbf1")
        draw.rounded_rectangle((286, 66, 354, 80), 7, fill="#202b40")
    elif category == "Audio":
        draw.arc((170, 65, 470, 370), 180, 360, fill="#26344b", width=38)
        draw.rounded_rectangle((154, 222, 232, 369), 28, fill=accent)
        draw.rounded_rectangle((408, 222, 486, 369), 28, fill=accent)
    elif category == "Cameras":
        draw.rounded_rectangle((120, 154, 520, 355), 26, fill="#26344b")
        draw.rounded_rectangle((180, 115, 300, 175), 12, fill="#344661")
        draw.ellipse((235, 166, 424, 355), fill="#121d2c")
        draw.ellipse((258, 189, 401, 332), fill=accent)
        draw.ellipse((282, 212, 377, 307), fill="#8cc4df")
        draw.rectangle((447, 176, 485, 194), fill="#eeeeee")
    else:
        draw.rounded_rectangle((212, 80, 428, 390), 42, fill="#d6deea")
        draw.rounded_rectangle((225, 91, 415, 373), 35, fill="#ffffff")
        draw.ellipse((268, 135, 372, 239), fill=accent)
        for offset in range(6):
            draw.line((258, 275 + offset * 12, 382, 275 + offset * 12), fill="#b5c4d6", width=3)
    picture.save(path)


def seed(connection, image_root: Path) -> None:
    image_root.mkdir(parents=True, exist_ok=True)
    asset_root = Path(__file__).resolve().parents[1] / "static" / "images" / "products"
    for identity, entry in enumerate(CATALOG, 1):
        path = image_root / f"product-{identity}.png"
        asset = asset_root / f"product-{identity}.png"
        if asset.exists():
            copyfile(asset, path)
        elif not path.exists():
            draw_product(path, entry[0], identity)
    if connection.execute(select(products.c.id).limit(1)).first():
        return
    names = list(dict.fromkeys(entry[0] for entry in CATALOG))
    for identity, name in enumerate(names, 1):
        connection.execute(categories.insert().values(id=identity, name=name))
    for identity in range(1, 4):
        connection.execute(customers.insert().values(id=identity, name=f"Demo Customer {identity}",
            email=f"demo{identity}@example.test", phone="0901234567", address="123 Nguyen Hue, Ho Chi Minh City"))
    repository = ProductRepository(connection)
    for identity, (category, brand, model, description, price, specification) in enumerate(CATALOG, 1):
        repository.save(Product(identity, f"{brand} {model}", brand, model, description,
            Decimal(price), ProductStatus.OUT_OF_STOCK if identity == 24 else ProductStatus.ACTIVE,
            Category(names.index(category) + 1, category),
            0 if identity == 24 else 12, [ProductUnit(f"ABC-{identity:03}-001")],
            [ProductSpecification(0, "Key features", specification), ProductSpecification(0, "Warranty", "12 months")]))
    interactions = InteractionRepository(connection, repository)
    for customerId, productId, kind in [(1, 1, "VIEW"), (2, 1, "VIEW"), (2, 2, "PURCHASE"),
                                       (2, 10, "ADD_TO_CART"), (3, 1, "CLICK"), (3, 3, "PURCHASE")]:
        interactions._record(customerId, repository.findById(productId), InteractionType(kind))

