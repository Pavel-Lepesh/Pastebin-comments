import pytest
import asyncio
import json
from httpx import AsyncClient, ASGITransport

from app.comments.dependencies import get_user_id
from app.main import app_v1
from app.db.mongo import init_mongo
from app.comments.models import Comment
from tests.mock_comments import mock_comments


app_v1.dependency_overrides[get_user_id] = lambda: 1


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app_v1), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="class", autouse=True)
async def init_db(event_loop):
    # setting the test event loop for mongo initialisation
    asyncio.set_event_loop(event_loop)

    await init_mongo()

    await Comment.find_all().delete()

    test_comments = json.loads(mock_comments)
    await Comment.insert_many([Comment(**comment) for comment in test_comments])

    yield

    await Comment.find_all().delete()
