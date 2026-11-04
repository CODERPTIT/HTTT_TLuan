from application.ports.repositories import CustomerRepositoryPort
from domain.customer.customer import Customer


class CustomerService:
    def __init__(self, customers: CustomerRepositoryPort):
        self.customers = customers

    def getCustomer(self, customerId: int) -> Customer:
        return self.customers.findById(customerId)
