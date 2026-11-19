from dataclasses import dataclass

from domain.product.product import Product


@dataclass
class Book(Product):
    author: str = ""
    isbn: str = ""
    publisher: str = ""
    publicationYear: int | None = None
    numberOfPages: int = 0
    coverType: str = "Paperback"

    def searchableAttributes(self) -> list[str]:
        return [self.author, self.isbn, self.publisher,
                "" if self.publicationYear is None else str(self.publicationYear),
                str(self.numberOfPages), self.coverType]
