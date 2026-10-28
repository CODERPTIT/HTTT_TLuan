import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import Bootstrap


@pytest.fixture
def container(tmp_path):
    instance = Bootstrap(tmp_path)
    yield instance
    instance.database.engine.dispose()


@pytest.fixture
def services(container):
    with container.scope() as scope:
        yield scope


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ABC_RUNTIME", str(tmp_path / "default"))
    from main import create_app
    from fastapi.testclient import TestClient
    app = create_app(tmp_path / "web")
    with TestClient(app) as test_client:
        yield test_client
    app.state.container.database.engine.dispose()

