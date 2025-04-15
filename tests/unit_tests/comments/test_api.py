import pytest
from beanie import PydanticObjectId
from bson import ObjectId
from httpx import AsyncClient
from app.comments.services import CommentService
from app.exceptions.exceptions import ObjectNotFound


class TestAPI:

    @pytest.mark.parametrize(
        "test_page, test_limit, status_code, result_len",
        [
            (1, 10, 200, 1),
            (1, 101, 422, 1),
            (1, -1, 422, 1),
            (-1, 10, 422, 1),
            (1, 10, 200, 0),
            (1, 10, 200, 3),
        ]
    )
    async def test_get_all_note_comments(
            self,
            test_page,
            test_limit,
            status_code,
            result_len,
            monkeypatch,
            async_client: AsyncClient
    ):
        async def mock_get_note_all_comments(note_hash_link: str, page: int, limit: int):
            assert note_hash_link == "some_hash"
            assert page == test_page
            assert limit == test_limit
            result = [
                {
                    "id": "67fb6ba0539e68884a03a032",
                    "user_id": 1,
                    "body": "Mocked comment",
                    "created": "2025-04-13T07:45:36.090+00:00",
                    "children": []
                }
            ]

            return result * result_len

        monkeypatch.setattr(CommentService, "get_note_all_comments", mock_get_note_all_comments, raising=True)

        response = await async_client.get(f"/some_hash/comments/?page={test_page}&limit={test_limit}")
        assert response.status_code == status_code

        if status_code == 200:
            data = response.json()
            assert len(data) == result_len

            if result_len > 0:
                assert isinstance(data, list)
                assert data[0]["id"] == "67fb6ba0539e68884a03a032"
                assert data[0]["user_id"] == 1
                assert data[0]["body"] == "Mocked comment"
                assert data[0]["created"] == "2025-04-13T07:45:36.090000Z"
                assert data[0]["children"] == []

    @pytest.mark.parametrize(
        "test_comment_id, test_children, status_code",
        [
            ("67fb6ba0539e68884a03a032", False, 200),
            ("67fb6ba0539e68884a03a032", True, 200),
            ("67fb6ba0539e68884a03a055", False, 404)
        ]
    )
    async def test_get_comment_by_id(
            self,
            test_comment_id,
            test_children,
            status_code,
            monkeypatch,
            async_client: AsyncClient
    ):
        async def mock_get_comment_by_id(comment_id: PydanticObjectId, children: bool):

            child = {
                "id": ObjectId("67fb6ba0539e68884a03a031"),
                "user_id": 1,
                "body": "string",
                "created": "2025-04-13T07:45:36.090000",
                "children": []
            }
            result = {
                "id": ObjectId("67fb6ba0539e68884a03a032"),
                "user_id": 1,
                "body": "Mocked comment",
                "created": "2025-04-13T07:45:36.090+00:00",
                "children": []
            }

            if comment_id != result["id"]:
                raise ObjectNotFound

            if children:
                result["children"].append(child)

            return result

        monkeypatch.setattr(CommentService, "get_comment_by_id", mock_get_comment_by_id, raising=True)

        response = await async_client.get(f"/comments/{test_comment_id}?children={test_children}")
        assert response.status_code == status_code

        data = response.json()

        if status_code == 200:
            if test_children:
                assert data["children"]
                assert data["children"][0]["id"] == "67fb6ba0539e68884a03a031"
            else:
                assert not data["children"]
