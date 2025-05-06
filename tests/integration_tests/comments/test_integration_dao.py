import pytest
from beanie import PydanticObjectId

from app.comments.dao import CommentsDAO
from app.comments.schemas import CommentInsertScheme


class TestIntegrationDAO:
    INSERT_DATA = CommentInsertScheme(
        note_hash_link="hash_3", user_id=1, body="test body", parent_id=None
    )

    async def test_insert_comment(self):
        new_comment = await CommentsDAO.insert_comment(self.INSERT_DATA)
        assert new_comment
        assert new_comment.note_hash_link == self.INSERT_DATA.note_hash_link
        assert new_comment.body == self.INSERT_DATA.body
        assert new_comment.user_id == self.INSERT_DATA.user_id
        assert new_comment.parent_id == self.INSERT_DATA.parent_id

    @pytest.mark.parametrize(
        "comment_id, success",
        [
            (PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"), True),
            (PydanticObjectId("661eb8d5b4a2f431dcb8f1d1"), True),
            (PydanticObjectId("661eb8d5b4a2f431dcb8f110"), False),
        ],
    )
    async def test_get_comment_by_id(self, comment_id, success):
        comment = await CommentsDAO.get_comment_by_id(comment_id, fetch_children=True)

        if success:
            assert comment
            assert comment.id == comment_id
            assert comment.body == "First test comment"
        else:
            assert not comment

    @pytest.mark.parametrize(
        "mock_hash_link, mock_skip, mock_limit, count, success",
        [
            ("hash_1", 0, 10, 1, True),
            ("hash_3", 0, 10, 3, True),
            ("hash_3", 0, 1, 1, True),
            ("unexpected", 0, 1, 1, False),
        ],
    )
    async def test_get_comment_by_hash_link(
        self, mock_hash_link, mock_skip, mock_limit, count, success
    ):
        comments = await CommentsDAO.get_comments_by_hash_link(
            mock_hash_link, mock_skip, mock_limit
        )

        if success:
            assert comments
            assert len(comments) == count
            assert len(comments) <= mock_limit
            assert comments[0].note_hash_link == mock_hash_link
        else:
            assert not comments

    async def test_update_comment(self):
        original_comment = await CommentsDAO.get_comment_by_id(
            PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"), False
        )
        assert original_comment

        await CommentsDAO.update_comment(original_comment, "new_body")
        assert original_comment.body == "new_body"

        updated_comment = await CommentsDAO.get_comment_by_id(
            PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"), False
        )
        assert updated_comment
        assert updated_comment.body == "new_body"

    async def test_update_parent_comment(self):
        new_comment = await CommentsDAO.insert_comment(self.INSERT_DATA)
        assert new_comment

        parent_comment = await CommentsDAO.get_comment_by_id(
            PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"), False
        )
        assert parent_comment

        await CommentsDAO.update_parent_comment(parent_comment, new_comment)

        updated_parent_comment = await CommentsDAO.get_comment_by_id(
            PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"), False
        )
        assert updated_parent_comment
        assert len(updated_parent_comment.children) == 1

    @pytest.mark.parametrize(
        "comments_list",
        [
            [PydanticObjectId("661eb8d5b4a2f431dcb8f1d5")],
            [
                PydanticObjectId("661eb8d5b4a2f431dcb8f1d3"),
                PydanticObjectId("661eb8d5b4a2f431dcb8f1d2"),
            ],
        ],
    )
    async def test_delete_comments(self, comments_list):
        await CommentsDAO.delete_comments(comments_list)

        comments = [
            await CommentsDAO.get_comment_by_id(id_, False) for id_ in comments_list
        ]

        assert not all(comments)
