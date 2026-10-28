from pathlib import Path
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from bootstrap import Bootstrap
from presentation.web import configure_routes

BASE = Path(__file__).resolve().parent


def create_app(runtime: Path | None = None) -> FastAPI:
    container = Bootstrap(runtime or Path(os.environ.get("ABC_RUNTIME", BASE / "runtime")))
    app = FastAPI(title="ABC Electronics", docs_url="/api/docs", debug=False)
    app.state.container = container
    app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
    app.mount("/media", StaticFiles(directory=container.images.root), name="media")
    configure_routes(app, BASE / "templates")
    return app


app = create_app()

