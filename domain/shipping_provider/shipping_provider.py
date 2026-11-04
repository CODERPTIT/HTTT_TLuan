from dataclasses import dataclass

@dataclass
class ShippingProvider:
    shippingProviderId: int
    providerCode: str
    providerName: str
    supportEmail: str
    supportPhone: str
    address: str
    active: bool = True
