import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, app_v1


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app_v1), base_url="http://test") as client:
        yield client
