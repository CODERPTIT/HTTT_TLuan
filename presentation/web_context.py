from fastapi import HTTPException


class WebContext:
    def __init__(self, templates):
        self.templates = templates

    def render(self, request, name, **context):
        return self.templates.TemplateResponse(request=request, name=name,
            context={"account": getattr(request.state, "account", None), **context})

    @staticmethod
    def scope(request, immediate: bool = False):
        return request.app.state.container.scope(immediate=immediate)

    def currentAccount(self, request, services):
        accountId = request.session.get("account_id")
        account = services.auth.profile(accountId) if isinstance(accountId, int) else None
        if account is not None:
            request.state.account = account
        return account

    def requireRole(self, request, services, *roles):
        account = self.currentAccount(request, services)
        if account is None:
            raise HTTPException(status_code=401, detail="Please sign in to continue")
        if roles and account["role"] not in roles:
            raise HTTPException(status_code=403, detail="You do not have access to this page")
        return account

    def customerId(self, request, services):
        account = self.requireRole(request, services, "CUSTOMER")
        services.search.service.customerId = account["customer_id"]
        return account["customer_id"]

    def optionalCustomerId(self, request, services):
        account = self.currentAccount(request, services)
        customerId = account["customer_id"] if account and account["role"] == "CUSTOMER" else None
        services.search.service.customerId = customerId
        return customerId
