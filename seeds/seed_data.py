from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw
from sqlalchemy import select

from data.infrastructure.product_database import categories, products, specifications
from data.repository.customer_repository import CustomerRepository
from data.repository.interaction_repository import InteractionRepository
from data.repository.product_repository import ProductRepository
from domain.interaction.interaction import InteractionType
from domain.product.book import Book
from domain.product.category import Category
from domain.product.electronic import Electronic
from domain.product.fashion import Fashion
from domain.product.furniture import Furniture
from domain.product.product import ProductStatus
from domain.product.product_specification import ProductSpecification
from domain.product.product_unit import ProductUnit


CATEGORY_IDS = {"Electronic": 1, "Book": 2, "Fashion": 3, "Furniture": 4}

CATALOG = [
    ("Electronic", "ASUS ROG Strix G16", "Gaming laptop designed for powerful competitive gaming", 32990000,
     "16 GB RAM Â· RTX 4060 Â· 165 Hz", {"brand": "ASUS", "model": "ROG Strix G16", "powerWattage": 280}),
    ("Electronic", "Dell Inspiron 14", "Lightweight laptop for work and study", 18990000,
     "16 GB RAM Â· 512 GB SSD", {"brand": "Dell", "model": "Inspiron 14", "powerWattage": 65}),
    ("Electronic", "Apple MacBook Air M3", "Portable laptop with all-day battery", 26990000,
     "16 GB RAM Â· 13 inch Retina", {"brand": "Apple", "model": "MacBook Air M3", "powerWattage": 35}),
    ("Electronic", "Samsung Galaxy S24", "Flagship phone with vivid AMOLED display", 17990000,
     "256 GB Â· 50 MP camera", {"brand": "Samsung", "model": "Galaxy S24", "powerWattage": 25}),
    ("Electronic", "Apple iPhone 15", "Everyday phone with sharp photography", 18990000,
     "128 GB Â· OLED", {"brand": "Apple", "model": "iPhone 15", "powerWattage": 20}),
    ("Electronic", "Samsung Galaxy A55", "Balanced phone with long battery life", 9490000,
     "256 GB Â· 5000 mAh", {"brand": "Samsung", "model": "Galaxy A55", "powerWattage": 25}),
    ("Book", "Clean Code", "A handbook of agile software craftsmanship", 690000,
     "Programming Â· Software quality", {"author": "Robert C. Martin", "isbn": "9780132350884",
      "publisher": "Prentice Hall", "publicationYear": 2008, "numberOfPages": 464, "coverType": "Paperback"}),
    ("Book", "Design Patterns", "Reusable object-oriented software patterns", 850000,
     "Programming Â· Object-oriented design", {"author": "Erich Gamma", "isbn": "9780201633610",
      "publisher": "Addison-Wesley", "publicationYear": 1994, "numberOfPages": 395, "coverType": "Hardcover"}),
    ("Book", "Domain-Driven Design", "Tackling complexity in the heart of software", 920000,
     "Architecture Â· Domain modeling", {"author": "Eric Evans", "isbn": "9780321125217",
      "publisher": "Addison-Wesley", "publicationYear": 2003, "numberOfPages": 560, "coverType": "Hardcover"}),
    ("Electronic", "Sony WH-1000XM5", "Wireless noise cancelling headphones", 7490000,
     "Bluetooth Â· 30 hour battery", {"brand": "Sony", "model": "WH-1000XM5", "powerWattage": 5}),
    ("Electronic", "JBL Flip 6", "Portable wireless waterproof speaker", 2490000,
     "IP67 Â· 12 hour battery", {"brand": "JBL", "model": "Flip 6", "powerWattage": 20}),
    ("Electronic", "Apple AirPods Pro", "Wireless noise cancelling earbuds", 5490000,
     "USB-C Â· Spatial audio", {"brand": "Apple", "model": "AirPods Pro", "powerWattage": 5}),
    ("Fashion", "Nike Dri-FIT T-Shirt", "Breathable everyday sports shirt", 790000,
     "Regular fit Â· Moisture wicking", {"brand": "Nike", "size": "M", "color": "black", "material": "Polyester", "gender": "Unisex"}),
    ("Fashion", "Levi's 501 Jeans", "Classic straight-fit denim jeans", 1890000,
     "Straight fit Â· Button fly", {"brand": "Levi's", "size": "32", "color": "blue", "material": "Denim", "gender": "Unisex"}),
    ("Fashion", "Adidas Ultraboost Shoes", "Responsive running shoes for daily training", 3290000,
     "Boost midsole Â· Rubber outsole", {"brand": "Adidas", "size": "42", "color": "black", "material": "Textile", "gender": "Unisex"}),
    ("Electronic", "Sony PlayStation 5", "Next generation gaming console", 12990000,
     "1 TB SSD Â· 4K gaming", {"brand": "Sony", "model": "PlayStation 5", "powerWattage": 350}),
    ("Electronic", "ASUS ROG Ally", "Handheld gaming console on the go", 14990000,
     "512 GB Â· 120 Hz", {"brand": "ASUS", "model": "ROG Ally", "powerWattage": 65}),
    ("Electronic", "Logitech G Pro Controller", "Responsive wireless gaming controller", 2490000,
     "Wireless Â· Programmable buttons", {"brand": "Logitech", "model": "G Pro", "powerWattage": 5}),
    ("Furniture", "IKEA LAGKAPTEN Desk", "Minimal desk for home and office", 2490000,
     "120 Ã— 60 cm Â· Assembly required", {"brand": "IKEA", "material": "Fiberboard", "dimensions": "120x60x73 cm", "weightKg": 18, "assemblyRequired": True}),
    ("Furniture", "Hoa Phat Ergonomic Chair", "Adjustable chair with breathable mesh back", 3590000,
     "Adjustable height Â· Lumbar support", {"brand": "Hoa Phat", "material": "Mesh and steel", "dimensions": "65x65x115 cm", "weightKg": 15, "assemblyRequired": True}),
    ("Furniture", "JYSK HORSENS Bookshelf", "Five-tier bookshelf for compact spaces", 2790000,
     "Five shelves Â· Oak finish", {"brand": "JYSK", "material": "Engineered wood", "dimensions": "80x30x180 cm", "weightKg": 28, "assemblyRequired": True}),
    ("Electronic", "Logitech MX Master 3S", "Precision wireless mouse for productivity", 2290000,
     "8000 DPI Â· USB-C", {"brand": "Logitech", "model": "MX Master 3S", "powerWattage": 5}),
    ("Electronic", "Lenovo USB-C Dock", "Expand your laptop connectivity", 1790000,
     "HDMI Â· USB 3 Â· 100 W", {"brand": "Lenovo", "model": "USB-C Dock", "powerWattage": 100}),
    ("Electronic", "Dell UltraSharp 27", "Crisp monitor for creative work", 7990000,
     "27 inch Â· QHD Â· IPS", {"brand": "Dell", "model": "UltraSharp 27", "powerWattage": 65}),
]

PRODUCT_COLORS = (
    "gray", "silver", "silver", "black", "silver", "blue", "white", "yellow",
    "blue", "black", "blue", "white", "black", "blue", "black", "white",
    "white", "black", "white", "gray", "brown", "gray", "silver", "black",
)


def ensure_filter_specifications(connection) -> None:
    product_ids = set(connection.execute(select(products.c.id)).scalars())
    for product_id, color in enumerate(PRODUCT_COLORS, 1):
        if product_id not in product_ids:
            continue
        existing = connection.execute(select(specifications.c.id, specifications.c.value).where(
            specifications.c.product_id == product_id,
            specifications.c.name == "Color")).first()
        if existing is None:
            connection.execute(specifications.insert().values(
                product_id=product_id, name="Color", value=color))
        elif existing.value != color:
            connection.execute(specifications.update().where(
                specifications.c.id == existing.id).values(value=color))


def draw_product(path: Path, category: str, variant: int) -> None:
    picture = Image.new("RGB", (640, 480), "#f1f4fa")
    draw = ImageDraw.Draw(picture)
    accent = f"#{(variant * 73) % 256:02x}{(variant * 131) % 256:02x}{(variant * 197) % 256:02x}"
    draw.ellipse((120, 385, 530, 423), fill="#dce2ec")
    if category == "Electronic":
        draw.rounded_rectangle((122, 78, 518, 330), 18, fill="#202b40")
        draw.rounded_rectangle((137, 93, 503, 313), 9, fill=accent)
        draw.polygon([(122, 330), (518, 330), (574, 385), (66, 385)], fill="#9da9ba")
    elif category == "Book":
        draw.rounded_rectangle((165, 65, 475, 390), 12, fill=accent)
        draw.rectangle((185, 92, 455, 365), fill="#f8fafc")
        draw.rectangle((210, 135, 430, 155), fill=accent)
        draw.rectangle((210, 180, 390, 192), fill="#9da9ba")
    elif category == "Fashion":
        draw.polygon([(260, 80), (380, 80), (465, 145), (415, 220), (390, 195),
                      (390, 390), (250, 390), (250, 195), (225, 220), (175, 145)], fill=accent)
    else:
        draw.rounded_rectangle((110, 170, 530, 215), 8, fill=accent)
        draw.rectangle((135, 215, 165, 385), fill="#536175")
        draw.rectangle((475, 215, 505, 385), fill="#536175")
    picture.save(path)


def _product(identity: int, entry):
    category_name, name, description, price, features, details = entry
    common = dict(
        productId=identity,
        productName=name,
        description=description,
        price=Decimal(price),
        status=ProductStatus.OUT_OF_STOCK if identity == 24 else ProductStatus.ACTIVE,
        category=Category(CATEGORY_IDS[category_name], category_name),
        quantityAvailable=0 if identity == 24 else 12,
        units=[ProductUnit(f"ABC-{identity:03}-001")],
        specifications=[
            ProductSpecification(0, "Key features", features),
            ProductSpecification(0, "Color", PRODUCT_COLORS[identity - 1]),
        ],
    )
    if category_name == "Electronic":
        common["specifications"].append(ProductSpecification(0, "Warranty", "12 months"))
        return Electronic(**common, warrantyMonths=12, **details)
    if category_name == "Book":
        return Book(**common, **details)
    if category_name == "Fashion":
        return Fashion(**common, **details)
    return Furniture(**common, **details)


def seed(connection, image_root: Path) -> None:
    image_root.mkdir(parents=True, exist_ok=True)
    for identity, entry in enumerate(CATALOG, 1):
        path = image_root / f"product-{identity}.png"
        if not path.exists():
            draw_product(path, entry[0], identity)
    if connection.execute(select(products.c.id).limit(1)).first():
        ensure_filter_specifications(connection)
        return
    for name, identity in CATEGORY_IDS.items():
        connection.execute(categories.insert().values(id=identity, name=name))
    repository = ProductRepository(connection)
    for identity, entry in enumerate(CATALOG, 1):
        repository.save(_product(identity, entry))
    interactions = InteractionRepository(connection, repository, CustomerRepository(connection))
    for customer_id, product_id, kind in [(1, 1, "VIEW"), (2, 1, "VIEW"), (2, 2, "PURCHASE"),
                                          (2, 10, "ADD_TO_CART"), (3, 1, "CLICK"), (3, 3, "PURCHASE")]:
        interactions.record(customer_id, repository.findById(product_id), InteractionType(kind))
