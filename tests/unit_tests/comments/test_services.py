import pytest
from bson import ObjectId

from app.comments.dao import CommentsDAO
from app.comments.services import CommentService
from app.exceptions.exceptions import ObjectNotFound


class TestServices:
    MOCK_COMMENTS = [{"id": f"67fb6ba0539e68884a03a03{i}",
                      "note_hash_link": "some_hash",
                      "user_id": 1,
                      "body": "string"} for i in range(1, 11)]
    MOCK_COMMENT_WITH_CHILD = {
        "id": ObjectId("67fb6ba0539e68884a03a031"),
        "note_hash_link": "some_hash",
        "user_id": 1,
        "body": "string",
        "children": [
            {
                "id": ObjectId("67fb6ba0539e68884a03a032"),
                "note_hash_link": "some_hash",
                "user_id": 1,
                "body": "string",
                "children": []
            }
        ]
    }

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
            assert int(result[0]["id"][-1]) == (mock_page - 1) * mock_limit + 1
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
        async def mock_get_comment_by_id(comment_id, children):
            if self.MOCK_COMMENT_WITH_CHILD["id"] == comment_id:
                return self.MOCK_COMMENT_WITH_CHILD
            else:
                return []

        monkeypatch.setattr(CommentsDAO, "get_comment_by_id", mock_get_comment_by_id, raising=True)

        if success:
            result = await CommentService.get_comment_by_id(mock_comment_id, mock_children)
            assert result

            if not mock_children:
                assert not result["children"]
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.get_comment_by_id(mock_comment_id, mock_children)
