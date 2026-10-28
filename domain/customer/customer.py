from dataclasses import dataclass


@dataclass
class Customer:
    customerId: int
    fullName: str
    email: str
    phoneNumber: str
    deliveryAddress: str

