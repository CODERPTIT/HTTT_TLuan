from dataclasses import dataclass


@dataclass
class User:
    userId: int
    fullName: str
    email: str
    phoneNumber: str
    role: str
    active: bool = True
