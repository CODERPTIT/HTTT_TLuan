class AccountService:
    def __init__(self, accounts):
        self.accounts = accounts

    def authenticate(self, email: str, password: str):
        return self.accounts.authenticate(email, password)

    def profile(self, accountId: int, includeStats: bool = False):
        return self.accounts.profile(accountId, include_stats=includeStats)

    def updateCustomerProfile(self, accountId: int, name: str, phone: str, address: str):
        return self.accounts.update_customer_profile(accountId, name, phone, address)

    def registerCustomer(self, name: str, email: str, password: str):
        return self.accounts.register_customer(name, email, password)
