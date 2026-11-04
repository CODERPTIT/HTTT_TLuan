class ShippingProviderService:
    def __init__(self, providers):
        self.providers = providers

    def shipments(self, providerId: int):
        return self.providers.shipments(providerId)

    def markOutForDelivery(self, providerId: int, orderId: int) -> None:
        self.providers.mark_out_for_delivery(providerId, orderId)

    def markDelivered(self, providerId: int, orderId: int) -> None:
        self.providers.mark_delivered(providerId, orderId)
