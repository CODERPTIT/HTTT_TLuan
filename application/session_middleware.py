import base64
import binascii
import hashlib
import hmac
import json
import time
from http.cookies import SimpleCookie
from urllib.parse import urlsplit

from starlette.datastructures import MutableHeaders
from starlette.responses import PlainTextResponse


class SignedSessionMiddleware:
    MAX_AGE = 7 * 24 * 60 * 60

    def __init__(self, app, secret: str, secure: bool = False):
        self.app = app
        self.secret = secret.encode("ascii")
        self.secure = secure

    def _decode(self, value: str) -> dict:
        try:
            payload, signature = value.rsplit(".", 1)
            expected = hmac.new(self.secret, payload.encode("ascii"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return {}
            data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if not isinstance(data, dict) or not isinstance(data.get("issued_at"), int):
                return {}
            if not 0 <= time.time() - data["issued_at"] <= self.MAX_AGE:
                return {}
            session = data.get("session", {})
            return session if isinstance(session, dict) else {}
        except (ValueError, TypeError, KeyError, json.JSONDecodeError, binascii.Error):
            return {}

    def _encode(self, session: dict) -> str:
        payload = base64.urlsafe_b64encode(json.dumps({"issued_at": int(time.time()),
            "session": session}, separators=(",", ":")).encode()).rstrip(b"=").decode("ascii")
        signature = hmac.new(self.secret, payload.encode("ascii"), hashlib.sha256).hexdigest()
        return payload + "." + signature

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers_in = dict(scope.get("headers", []))
        if scope["method"] not in {"GET", "HEAD", "OPTIONS"}:
            origin = headers_in.get(b"origin", b"").decode("latin-1")
            host = headers_in.get(b"host", b"").decode("latin-1")
            if headers_in.get(b"sec-fetch-site") == b"cross-site" or (
                origin and urlsplit(origin).netloc != host):
                return await PlainTextResponse("Cross-site request blocked", status_code=403)(scope, receive, send)
        cookies = SimpleCookie()
        for key, value in scope.get("headers", []):
            if key.lower() == b"cookie":
                try:
                    cookies.load(value.decode("latin-1"))
                except Exception:
                    pass
        original = self._decode(cookies["abc_session"].value) if "abc_session" in cookies else {}
        scope["session"] = dict(original)

        async def send_with_cookie(message):
            if message["type"] == "http.response.start" and scope["session"] != original:
                headers = MutableHeaders(scope=message)
                attributes = "; Path=/; HttpOnly; SameSite=Lax" + ("; Secure" if self.secure else "")
                if scope["session"]:
                    headers.append("set-cookie", "abc_session=" + self._encode(scope["session"])
                        + f"; Max-Age={self.MAX_AGE}" + attributes)
                else:
                    headers.append("set-cookie", "abc_session=; Max-Age=0" + attributes)
            await send(message)

        await self.app(scope, receive, send_with_cookie)
