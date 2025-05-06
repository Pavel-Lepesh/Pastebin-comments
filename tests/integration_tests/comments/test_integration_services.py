import pytest
from beanie import PydanticObjectId

from app.comments.services import CommentService
from app.exceptions.exceptions import (
    ObjectNotFound,
    ParentConflict,
    ParentCommentNotFoundError,
)
from app.comments.schemas import CommentScheme, CommentUpdateScheme


class TestIntegrationServices:
    @pytest.mark.parametrize(
        "mock_comment_data, user_id, mock_hash_link, success, exception",
        [
            (CommentScheme(body="test body"), 1, "new_hash_link", True, None),
            (
                CommentScheme(
                    body="test body",
                    parent_id=PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"),
                ),
                1,
                "hash_1",
                True,
                None,
            ),
            (
                CommentScheme(
                    body="test body",
                    parent_id=PydanticObjectId("661eb8d5b4a2f431dcb8f100"),
                ),
                1,
                "hash_1",
                False,
                ParentCommentNotFoundError,
            ),
            (
                CommentScheme(
                    body="test body",
                    parent_id=PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"),
                ),
                1,
                "unexpected",
                False,
                ParentConflict,
            ),
        ],
    )
    async def test_create_comment(
        self, mock_comment_data, user_id, mock_hash_link, success, exception
    ):
        if success:
            comment = await CommentService.create_comment(
                mock_comment_data, user_id, mock_hash_link
            )
            assert comment
            assert comment.body == mock_comment_data.body
            assert comment.parent_id == mock_comment_data.parent_id
        else:
            with pytest.raises(exception):
                await CommentService.create_comment(
                    mock_comment_data, user_id, mock_hash_link
                )

    @pytest.mark.parametrize(
        "mock_hash_link, mock_page, mock_limit, count, success",
        [("hash_3", 1, 10, 2, True), ("unexpected", 1, 10, 2, False)],
    )
    async def test_get_note_all_comments(
        self, mock_hash_link, mock_page, mock_limit, count, success
    ):
        if success:
            comments = await CommentService.get_note_all_comments(
                mock_hash_link, mock_page, mock_limit
            )
            assert comments
            assert len(comments) == count
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.get_note_all_comments(
                    mock_hash_link, mock_page, mock_limit
                )

    @pytest.mark.parametrize(
        "mock_comment_id, fetch_children, success",
        [
            (PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"), False, True),
            (PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"), True, True),
            (PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"), False, True),
            (PydanticObjectId("661eb8d5b4a2f431dcb8f100"), True, False),
        ],
    )
    async def test_get_comment_by_id(self, mock_comment_id, fetch_children, success):
        if success:
            comment = await CommentService.get_comment_by_id(
                mock_comment_id, fetch_children
            )
            assert comment
            assert comment.id == mock_comment_id
            assert bool(comment.children) == fetch_children
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.get_comment_by_id(mock_comment_id, fetch_children)

    @pytest.mark.parametrize(
        "mock_comment_id, mock_comment_data, success",
        [
            (
                PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"),
                CommentUpdateScheme(body="new body"),
                True,
            ),
            (
                PydanticObjectId("661eb8d5b4a2f431dcb8f100"),
                CommentUpdateScheme(body="new body"),
                False,
            ),
        ],
    )
    async def test_update_comment(self, mock_comment_id, mock_comment_data, success):
        if success:
            await CommentService.update_comment(mock_comment_id, mock_comment_data, 1)

            comment = await CommentService.get_comment_by_id(mock_comment_id, False)
            assert comment
            assert comment.body == mock_comment_data.body
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.update_comment(
                    mock_comment_id, mock_comment_data, 1
                )

    @pytest.mark.parametrize(
        "mock_comment_id, success",
        [
            (PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"), True),
            (PydanticObjectId("661eb8d5b4a2f431dcb8f100"), False),
        ],
    )
    async def test_delete_comment(self, mock_comment_id, success):
        if success:
            await CommentService.delete_comment(mock_comment_id, 1)

            with pytest.raises(ObjectNotFound):
                await CommentService.get_comment_by_id(mock_comment_id, False)
        else:
            with pytest.raises(ObjectNotFound):
                await CommentService.delete_comment(mock_comment_id, 1)
