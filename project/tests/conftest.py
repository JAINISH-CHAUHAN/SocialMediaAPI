# project/tests/conftest.py

import os
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

os.environ["ENV_STATE"] = "test"

from project.database import database
from project.main import app







@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as c:
        yield c



@pytest.fixture(autouse=True)
async def db(client) -> AsyncGenerator:
    """Ensure clean state per test"""
    # Now database is connected (client fixture triggered app lifespan)
    # Clean before test
    await database.execute("DELETE FROM comments")
    await database.execute("DELETE FROM posts")
    
    yield
    
    # Clean after test
    await database.execute("DELETE FROM comments")
    await database.execute("DELETE FROM posts")
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac
