from fastapi import Form, Request
from fastapi.responses import RedirectResponse


def register_auth_routes(app, web):
    @app.get("/login")
    def login_page(request: Request, next: str = ""):
        return web.render(request, "login.html", next=next, error="")

    @app.post("/login")
    def login(request: Request, email: str = Form(...), password: str = Form(...), next: str = Form("")):
        with web.scope(request) as services:
            account = services.auth.authenticate(email, password)
            if account is None:
                return web.templates.TemplateResponse(request=request, name="login.html",
                    context={"next": next, "error": "Invalid email or password"}, status_code=401)
            request.session.clear()
            request.session["account_id"] = account["id"]
            destination = next if next.startswith("/") and not next.startswith("//") else ""
            if not destination:
                destination = ("/" if account["role"] == "CUSTOMER" else
                               "/shipping" if account["role"] == "SHIPPING_PROVIDER" else "/staff")
            return RedirectResponse(destination, status_code=303)

    @app.post("/logout")
    def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    @app.get("/profile")
    def profile(request: Request, saved: bool = False):
        with web.scope(request) as services:
            account = web.requireRole(request, services)
            account = services.auth.profile(account["id"], includeStats=True)
            request.state.account = account
            return web.render(request, "profile.html", profile=account, saved=saved)

    @app.post("/profile")
    def update_profile(request: Request, name: str = Form(...), phone: str = Form(""),
                       address: str = Form("")):
        with web.scope(request) as services:
            account = web.requireRole(request, services, "CUSTOMER")
            services.auth.updateCustomerProfile(account["id"], name, phone, address)
        return RedirectResponse("/profile?saved=true", status_code=303)

    @app.get("/register")
    def register_page(request: Request):
        return web.render(request, "register.html", error="")

    @app.post("/register")
    def register(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
        try:
            with web.scope(request) as services:
                account = services.auth.registerCustomer(name, email, password)
                request.session.clear()
                request.session["account_id"] = account["id"]
                return RedirectResponse("/", status_code=303)
        except ValueError as error:
            return web.templates.TemplateResponse(request=request, name="register.html",
                context={"error": str(error)}, status_code=400)
