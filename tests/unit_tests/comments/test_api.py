import pytest
from beanie import PydanticObjectId
from bson import ObjectId
from httpx import AsyncClient
from app.comments.services import CommentService
from app.exceptions.exceptions import ObjectNotFound


class TestAPI:
    @pytest.mark.parametrize(
        "test_page, test_limit, expected_status, result_len",
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
            expected_status,
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
                    "note_hash_link": "some_hash",
                    "created": "2025-04-13T07:45:36.090+00:00",
                    "children": []
                }
            ]

            return result * result_len

        monkeypatch.setattr(CommentService, "get_note_all_comments", mock_get_note_all_comments, raising=True)

        response = await async_client.get(f"/some_hash/comments/?page={test_page}&limit={test_limit}")
        assert response.status_code == expected_status

        if expected_status == 200:
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
        "test_comment_id, test_children, expected_status",
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
            expected_status,
            monkeypatch,
            async_client: AsyncClient
    ):
        async def mock_get_comment_by_id(comment_id: PydanticObjectId, children: bool):

            child = {
                "id": ObjectId("67fb6ba0539e68884a03a031"),
                "user_id": 1,
                "body": "string",
                "note_hash_link": "some_hash",
                "created": "2025-04-13T07:45:36.090000",
                "children": []
            }
            result = {
                "id": ObjectId("67fb6ba0539e68884a03a032"),
                "user_id": 1,
                "body": "Mocked comment",
                "note_hash_link": "some_hash",
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
        assert response.status_code == expected_status

        data = response.json()

        if expected_status == 200:
            if test_children:
                assert data["children"]
                assert data["children"][0]["id"] == "67fb6ba0539e68884a03a031"
            else:
                assert not data["children"]

    @pytest.mark.parametrize(
        "payload, expected_status",
        [
            ({"body": "some text", "parent_id": None}, 201),
            ({"body": "", "parent_id": None}, 422),
            ({}, 422),
            ({"body": "some text", "parent_id": "some_text"}, 422),
            ({"body": "some text", "parent_id": "67fb6ba0539e68884a03a032"}, 201)
        ]
    )
    async def test_create_comment(
            self,
            payload,
            expected_status,
            monkeypatch,
            async_client: AsyncClient
    ):
        async def mock_create_comment(comment_data, user_id, note_hash_link):
            result = {
                "id": ObjectId("67fb6ba0539e68884a03a032"),
                "user_id": 1,  # TODO change test after JWT implementation
                "body": comment_data.body,
                "note_hash_link": "some_hash",
                "created": "2025-04-13T07:45:36.090+00:00",
                "children": []
            }
            return result

        monkeypatch.setattr(CommentService, "create_comment", mock_create_comment, raising=True)

        response = await async_client.post("/some_hash/comments/", json=payload)
        assert response.status_code == expected_status

        if expected_status == 201:
            data = response.json()
            assert data["body"] == payload["body"]
            assert "id" in data
            assert "created" in data

    @pytest.mark.parametrize(
        "payload, expected_status",
        [
            ({"body": "test body"}, 204),
            ({"body": ""}, 422),
            ({}, 422)
        ]
    )
    async def test_update_comment(
            self,
            payload,
            expected_status,
            monkeypatch,
            async_client: AsyncClient
    ):
        async def mock_update_comment(comment_id, comment_data):
            expected_body = "test body"
            assert expected_body == comment_data.body

        monkeypatch.setattr(CommentService, "update_comment", mock_update_comment, raising=True)

        response = await async_client.patch("/comments/67fb6ba0539e68884a03a032", json=payload)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "comment_id, expected_status",
        [
            ("67fb6ba0539e68884a03a032", 204),
            ("", 404)
        ]
    )
    async def test_delete_comment(
            self,
            comment_id,
            expected_status,
            monkeypatch,
            async_client: AsyncClient
    ):
        async def mock_delete_comment(comment_id):
            pass

        monkeypatch.setattr(CommentService, "delete_comment", mock_delete_comment, raising=True)

        response = await async_client.delete(f"/comments/{comment_id}")
        assert response.status_code == expected_status
