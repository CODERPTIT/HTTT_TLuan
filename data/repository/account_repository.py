import hashlib
import hmac
import re
import secrets
from datetime import datetime, timezone

from sqlalchemy import select, func

from data.infrastructure.order_database import (users, customers, staff, shipping_providers, shipments,
                                                orders, interactions, search_queries)


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("Password must contain at least 10 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"pbkdf2_sha256$600000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, rounds, salt, digest = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(actual, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False


class AccountRepository:
    def __init__(self, connection):
        self.connection = connection

    def find_by_id(self, account_id: int):
        return self.connection.execute(select(users).where(
            users.c.id == account_id, users.c.active == 1)).mappings().first()

    def authenticate(self, email: str, password: str):
        account = self.connection.execute(select(users).where(
            users.c.email == email.strip().lower(), users.c.active == 1)).mappings().first()
        if account and verify_password(password, account["password_hash"]):
            return account
        return None

    def profile(self, account_id: int, include_stats: bool = False):
        account = self.find_by_id(account_id)
        if account is None:
            return None
        customer_id = account["id"] if account["role"] == "CUSTOMER" else None
        result = {"id": account["id"], "email": account["email"], "role": account["role"],
                  "name": account["full_name"], "phone": account["phone"] or "",
                  "active": bool(account["active"]), "customer_id": customer_id}
        if customer_id is not None:
            customer = self.connection.execute(select(customers).where(
                customers.c.id == customer_id)).mappings().one()
            result["address"] = customer["delivery_address"] or ""
            if include_stats:
                result["stats"] = {
                    "orders": self.connection.execute(select(func.count()).select_from(orders).where(
                        orders.c.customer_id == customer_id)).scalar_one(),
                    "interactions": self.connection.execute(select(func.count()).select_from(interactions).where(
                        interactions.c.customer_id == customer_id)).scalar_one(),
                    "searches": self.connection.execute(select(func.count()).select_from(search_queries).where(
                        search_queries.c.customer_id == customer_id)).scalar_one(),
                }
        elif account["role"] == "SHIPPING_PROVIDER":
            provider = self.connection.execute(select(shipping_providers).where(
                shipping_providers.c.user_id == account["id"])).mappings().first()
            result.update(address="", shipping_provider_id=provider["id"] if provider else None,
                          provider_code=provider["provider_code"] if provider else "",
                          provider_name=provider["provider_name"] if provider else "",
                          support_email=provider["support_email"] if provider else "",
                          support_phone=provider["support_phone"] if provider else "",
                          provider_address=provider["address"] if provider else "")
        else:
            employee = self.connection.execute(select(staff).where(
                staff.c.id == account["id"])).mappings().first()
            result.update(address="", employee_code=employee["employee_code"] if employee else "",
                          department=employee["department"] if employee else "",
                          position=employee["position"] if employee else "")
        result["initials"] = "".join(part[0] for part in result["name"].split()[:2]).upper() or "A"
        return result

    def update_customer_profile(self, account_id: int, name: str, phone: str, address: str):
        account = self.find_by_id(account_id)
        if account is None:
            raise LookupError("Account not found")
        if account["role"] != "CUSTOMER":
            raise ValueError("Only Customer profiles can be edited")
        name, phone, address = name.strip(), phone.strip(), address.strip()
        if not 2 <= len(name) <= 100:
            raise ValueError("Name must contain between 2 and 100 characters")
        if phone and not re.fullmatch(r"\+?[0-9][0-9 -]{7,18}", phone):
            raise ValueError("Enter a valid phone number")
        if len(address) > 500:
            raise ValueError("Address must not exceed 500 characters")
        self.connection.execute(users.update().where(users.c.id == account_id).values(
            full_name=name, phone=phone))
        self.connection.execute(customers.update().where(customers.c.id == account_id).values(
            delivery_address=address))
        return self.profile(account_id, include_stats=True)

    def register_customer(self, name: str, email: str, password: str):
        name, email = name.strip(), email.strip().lower()
        if not name or "@" not in email or len(email) > 254:
            raise ValueError("Enter a valid name and email address")
        if self.connection.execute(select(users.c.id).where(users.c.email == email)).first():
            raise ValueError("This email is already registered")
        password_hash = hash_password(password)
        user_id = self.connection.execute(users.insert().values(
            email=email, password_hash=password_hash, role="CUSTOMER", full_name=name, phone="",
            active=1, created_at=datetime.now(timezone.utc).isoformat())).inserted_primary_key[0]
        self.connection.execute(customers.insert().values(id=user_id, delivery_address=""))
        return self.find_by_id(user_id)


def seed_users(connection):
    now = datetime.now(timezone.utc).isoformat()
    for identity in range(1, 4):
        email = f"demo{identity}@example.test"
        user_id = connection.execute(select(users.c.id).where(users.c.email == email)).scalar()
        if user_id is None:
            user_id = connection.execute(users.insert().values(
                id=identity, email=email, password_hash=hash_password("DemoCustomer123!"), role="CUSTOMER",
                full_name=f"Demo Customer {identity}", phone="0901234567", active=1,
                created_at=now)).inserted_primary_key[0]
        if not connection.execute(select(customers.c.id).where(customers.c.id == user_id)).first():
            connection.execute(customers.insert().values(
                id=user_id, delivery_address="123 Nguyen Hue, Ho Chi Minh City"))

    staff_accounts = (
        ("ADMINISTRATOR", "admin@abc.test", "Administrator", "Administration"),
        ("SALES_STAFF", "sales@abc.test", "Sales Staff", "Sales"),
        ("WAREHOUSE_STAFF", "warehouse@abc.test", "Warehouse Staff", "Warehouse"),
        ("MANAGER", "manager@abc.test", "Manager", "Management"),
    )
    for role, email, name, department in staff_accounts:
        user_id = connection.execute(select(users.c.id).where(users.c.email == email)).scalar()
        if user_id is None:
            user_id = connection.execute(users.insert().values(
                email=email, password_hash=hash_password("DemoStaff123!"), role=role,
                full_name=name, phone="", active=1, created_at=now)).inserted_primary_key[0]
        if not connection.execute(select(staff.c.id).where(staff.c.id == user_id)).first():
            connection.execute(staff.insert().values(
                id=user_id, employee_code=f"ABC-{user_id:04}", department=department, position=name))

    provider_email = "shipping@abc.test"
    user_id = connection.execute(select(users.c.id).where(users.c.email == provider_email)).scalar()
    if user_id is None:
        user_id = connection.execute(users.insert().values(
            email=provider_email, password_hash=hash_password("DemoShipping123!"), role="SHIPPING_PROVIDER",
            full_name="ABC Demo Delivery", phone="0909000000", active=1,
            created_at=now)).inserted_primary_key[0]
    provider_id = connection.execute(select(shipping_providers.c.id).where(
        shipping_providers.c.provider_code == "ABC-DELIVERY")).scalar()
    if provider_id is None:
        provider_id = connection.execute(shipping_providers.insert().values(
            user_id=user_id, provider_code="ABC-DELIVERY", provider_name="ABC Demo Delivery",
            support_email=provider_email, support_phone="0909000000",
            address="Ho Chi Minh City", active=1)).inserted_primary_key[0]
    else:
        connection.execute(shipping_providers.update().where(
            shipping_providers.c.id == provider_id).values(
                user_id=user_id, provider_name="ABC Demo Delivery", support_email=provider_email,
                support_phone="0909000000", address="Ho Chi Minh City", active=1))
    connection.execute(shipments.update().where(shipments.c.shipping_provider_id.is_(None)).values(
        shipping_provider_id=provider_id))
