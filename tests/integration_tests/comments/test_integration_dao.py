import pytest
from app.comments.dao import CommentsDAO
from app.comments.models import Comment
from beanie import PydanticObjectId


class TestIntegrationDAO:
    @classmethod
    async def test_get_comment_by_id(cls):
        comment = await CommentsDAO.get_comment_by_id(
            PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"),
            fetch_children=False
        )

        assert comment
