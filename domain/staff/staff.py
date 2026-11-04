from dataclasses import dataclass

from domain.user.user import User


@dataclass
class Staff(User):
    employeeCode: str = ""
    department: str = ""
    position: str = ""
