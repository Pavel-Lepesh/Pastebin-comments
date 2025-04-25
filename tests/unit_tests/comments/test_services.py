import pytest
from bson import ObjectId

from app.comments.dao import CommentsDAO
from app.comments.schemas import CommentUpdateScheme, CommentScheme, CommentResponseScheme
from app.comments.services import CommentService
from app.exceptions.exceptions import ObjectNotFound, ParentCommentNotFoundError, ParentConflict


class TestServices:
    MOCK_COMMENTS = [
        CommentResponseScheme(**{
            "id": f"67fb6ba0539e68884a03a03{i}",
            "note_hash_link": "some_hash",
            "user_id": 1,
            "created": "2025-04-13T07:45:36.090+00:00",
            "body": "string"
        }) for i in range(1, 10)
    ]
    MOCK_COMMENT_WITH_CHILD = CommentResponseScheme(**{
        "id": ObjectId("67fb6ba0539e68884a03a031"),
        "note_hash_link": "some_hash",
        "user_id": 1,
        "created": "2025-04-13T07:45:36.090+00:00",
        "body": "string",
        "children": [
            CommentResponseScheme(**{
                "id": ObjectId("67fb6ba0539e68884a03a032"),
                "note_hash_link": "some_hash",
                "user_id": 1,
                "created": "2025-04-13T07:45:36.090+00:00",
                "body": "string",
                "children": [
                    CommentResponseScheme(**{
                        "id": ObjectId("67fb6ba0539e68884a03a033"),
                        "note_hash_link": "some_hash",
                        "user_id": 1,
                        "created": "2025-04-13T07:45:36.090+00:00",
                        "body": "string",
                        "children": []
                    })
                ]
            })
        ]
    })

    async def mock_get_comment_by_id(self, comment_id, fetch_children=None):
        if self.MOCK_COMMENT_WITH_CHILD.id == comment_id:
            return self.MOCK_COMMENT_WITH_CHILD
        else:
            return []

    @pytest.mark.parametrize(
        "mock_comment_data, mock_user_id, mock_hash_link, success, exc",
        [
            (CommentScheme(body="string"), 1, "some_hash", True, None),
            (CommentScheme(body="string", parent_id=ObjectId("67fb6ba0539e68884a03a031")), 1, "some_hash", True, None),
            (CommentScheme(body="string", parent_id=ObjectId("67fb6ba0539e68884a03a042")), 1, "some_hash", False, ParentCommentNotFoundError),
            (CommentScheme(body="string", parent_id=ObjectId("67fb6ba0539e68884a03a031")), 1, "unexpected_hash", False, ParentConflict)
        ]
    )
    async def test_create_comment(
            self,
            mock_comment_data,
            mock_user_id,
            mock_hash_link,
            success,
            exc,
            monkeypatch
    ):
        created_comment = CommentResponseScheme(**{
            "id": ObjectId("67fb6ba0539e68884a03a034"),
            "body": mock_comment_data.body,
            "note_hash_link": mock_hash_link,
            "user_id": mock_user_id,
            "created": "2025-04-13T07:45:36.090+00:00",
            "parent_id": mock_comment_data.parent_id
        })

        async def mock_insert_comment(comment_data):
            return created_comment

        async def mock_update_comment(comment, body):
            return None

        monkeypatch.setattr(CommentsDAO, "get_comment_by_id", self.mock_get_comment_by_id, raising=True)
        monkeypatch.setattr(CommentsDAO, "insert_comment", mock_insert_comment, raising=True)
        monkeypatch.setattr(CommentsDAO, "update_parent_comment", mock_update_comment, raising=True)

        if success:
            result = await CommentService.create_comment(mock_comment_data, mock_user_id, mock_hash_link)
            assert result
            assert result.user_id == mock_user_id
            assert result.body == mock_comment_data.body
        else:
            with pytest.raises(exc):
                await CommentService.create_comment(mock_comment_data, mock_user_id, mock_hash_link)

    @pytest.mark.parametrize(
        "mock_hash_link, mock_page, mock_limit, success",
        [
            ("some_hash", 1, 10, True),
            ("some_hash", 2, 3, True),
            ("some_hash", 10, 20, False),
            ("unexpected_hash", 1, 10, False)
        ]
    )
    async def test_get_note_all_comments(
            self,
            mock_hash_link,
            mock_page,
            mock_limit,
            success,
            monkeypatch
    ):
        async def mock_get_comments_by_hash_link(note_hash_link, skip, limit):
            assert skip == (mock_page - 1) * mock_limit
            assert limit == mock_limit

            if note_hash_link == "some_hash":
                return self.MOCK_COMMENTS[skip:limit + 1]
            else:
                return []

        monkeypatch.setattr(CommentsDAO, "get_comments_by_hash_link", mock_get_comments_by_hash_link, raising=True)

        if success:
            result = await CommentService.get_note_all_comments(mock_hash_link, mock_page, mock_limit)
            assert len(result) <= mock_limit

            # check if a last character of an id is the same as a page
            assert int(str(result[0].id)[-1]) == (mock_page - 1) * mock_limit + 1
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.get_note_all_comments(mock_hash_link, mock_page, mock_limit)

    @pytest.mark.parametrize(
        "mock_comment_id, mock_children, success",
        [
            (ObjectId("67fb6ba0539e68884a03a031"), True, True),
            (ObjectId("67fb6ba0539e68884a03a037"), True, False),
        ]
    )
    async def test_get_comment_by_id(
            self,
            mock_comment_id,
            mock_children,
            success,
            monkeypatch
    ):
        monkeypatch.setattr(CommentsDAO, "get_comment_by_id", self.mock_get_comment_by_id, raising=True)

        if success:
            result = await CommentService.get_comment_by_id(mock_comment_id, mock_children)
            assert result

            if not mock_children:
                assert not result["children"]
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.get_comment_by_id(mock_comment_id, mock_children)

    @pytest.mark.parametrize(
        "mock_comment_id, success",
        [
            (ObjectId("67fb6ba0539e68884a03a031"), True),
            (ObjectId("67fb6ba0539e68884a03a042"), False),
        ]
    )
    async def test_update_comment(
            self,
            mock_comment_id,
            success,
            monkeypatch
    ):
        async def mock_update_comment(comment, body):
            return None

        monkeypatch.setattr(CommentsDAO, "get_comment_by_id", self.mock_get_comment_by_id, raising=True)
        monkeypatch.setattr(CommentsDAO, "update_comment", mock_update_comment, raising=True)

        data = CommentUpdateScheme(body="new body")

        if success:
            result = await CommentService.update_comment(mock_comment_id, data)
            assert not result
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.update_comment(mock_comment_id, data)

    @pytest.mark.parametrize(
        "mock_comment_id, success",
        [
            (ObjectId("67fb6ba0539e68884a03a031"), True),
            (ObjectId("67fb6ba0539e68884a03a033"), False)
        ]
    )
    async def test_delete_comment(
            self,
            mock_comment_id,
            success,
            monkeypatch
    ):
        async def mock_delete_comments(ids):
            assert len(ids) == 3  # the length of MOCK_COMMENT_WITH_CHILD
            return None

        monkeypatch.setattr(CommentsDAO, "get_comment_by_id", self.mock_get_comment_by_id, raising=True)
        monkeypatch.setattr(CommentsDAO, "delete_comments", mock_delete_comments, raising=True)

        if success:
            await CommentService.delete_comment(mock_comment_id)
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.delete_comment(mock_comment_id)
