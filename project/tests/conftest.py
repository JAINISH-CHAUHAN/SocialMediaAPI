# project/tests/conftest.py

import os
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

os.environ["ENV_STATE"] = "test"

from project.database import database, user_table
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

@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {
        "email" : "test@example.net",
        "password" : "1234"
    }
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details