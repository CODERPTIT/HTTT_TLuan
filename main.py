from pathlib import Path
import os
import secrets
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from application.session_middleware import SignedSessionMiddleware
from bootstrap import Bootstrap
from presentation.web import configure_routes

BASE = Path(__file__).resolve().parent


def _load_environment(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


_load_environment(BASE / ".env")


def create_app(runtime: Path | None = None) -> FastAPI:
    runtime = runtime or Path(os.environ.get("ABC_RUNTIME", BASE / "runtime"))
    container = Bootstrap(runtime)
    app = FastAPI(title="ABC Electronics", docs_url="/api/docs", debug=False)
    secret_path = runtime / ".session_secret"
    if not secret_path.exists():
        secret_path.write_text(secrets.token_hex(32), encoding="ascii")
    app.add_middleware(SignedSessionMiddleware, secret=secret_path.read_text(encoding="ascii"),
                       secure=os.getenv("ABC_HTTPS") == "1")
    app.state.container = container
    app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
    app.mount("/media", StaticFiles(directory=container.images.root), name="media")
    configure_routes(app, BASE / "templates")
    return app


app = create_app()

