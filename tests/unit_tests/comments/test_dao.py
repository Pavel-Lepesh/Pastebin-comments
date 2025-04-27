from unittest.mock import AsyncMock, MagicMock

from beanie import PydanticObjectId

from app.comments.dao import CommentsDAO
from app.comments.schemas import CommentInsertScheme


class TestDAO:
    async def test_insert_comment(self, mocker):
        comment_data = CommentInsertScheme(
            note_hash_link="test_hash",
            user_id=1,
            body="Test body",
            parent_id=None
        )

        fake_comment = MagicMock()
        mock_comment_class = mocker.patch("app.comments.dao.Comment", return_value=fake_comment)
        mock_insert = mocker.patch.object(fake_comment, "insert", new_callable=AsyncMock)

        result = await CommentsDAO.insert_comment(comment_data)

        mock_comment_class.assert_called_once_with(
            note_hash_link=comment_data.note_hash_link,
            user_id=comment_data.user_id,
            body=comment_data.body,
            parent_id=comment_data.parent_id
        )
        mock_insert.assert_awaited_once()
        assert result == fake_comment

    async def test_get_comment_by_id(self, mocker):
        mock_data = {
            "comment_id": PydanticObjectId("67fb6ba0539e68884a03a031"),
            "fetch_children": True
        }

        fake_comment = MagicMock()
        mock_get = mocker.patch("app.comments.dao.Comment.get", new_callable=AsyncMock, return_value=fake_comment)

        result = await CommentsDAO.get_comment_by_id(**mock_data)

        mock_get.assert_called_once_with(
            document_id=mock_data["comment_id"],
            fetch_links=mock_data["fetch_children"]
        )
        assert result == fake_comment

    async def test_get_comments_by_hash_link(self, mocker):
        mock_data = {
            "note_hash_link": "some_hash",
            "skip": 0,
            "limit": 10
        }

        fake_comments_list = [MagicMock()]
        mock_find_result = MagicMock()
        mock_find_result.to_list = AsyncMock(return_value=fake_comments_list)
        mock_find = mocker.patch("app.comments.dao.Comment.find", return_value=mock_find_result)

        result = await CommentsDAO.get_comments_by_hash_link(**mock_data)

        mock_find.assert_called_once_with(
            {"note_hash_link": mock_data["note_hash_link"], "parent_id": None},
            skip=mock_data["skip"],
            limit=mock_data["limit"],
            fetch_links=True
        )
        mock_find_result.to_list.assert_awaited_once()
        assert result == fake_comments_list

    async def test_update_comment(self, mocker):
        fake_comment = MagicMock()
        fake_comment.replace = AsyncMock()

        new_body = "Updated body text"

        await CommentsDAO.update_comment(fake_comment, new_body)

        assert fake_comment.body == new_body
        fake_comment.replace.assert_awaited_once()

    async def test_update_parent_comment(self, mocker):
        fake_parent_comment = MagicMock()
        fake_parent_comment.children = []
        fake_parent_comment.replace = AsyncMock()
        fake_children_comment = MagicMock()

        await CommentsDAO.update_parent_comment(fake_parent_comment, fake_children_comment)

        fake_parent_comment.replace.assert_awaited_once()
        assert fake_parent_comment.children[0] == fake_children_comment

    async def test_delete_comments(self, mocker):
        fake_comments = [PydanticObjectId(), PydanticObjectId()]

        mock_comment_class = mocker.patch("app.comments.dao.Comment")
        mock_comment_class.id = "mocked_id"

        mock_find_result = MagicMock()
        mock_find_result.delete = AsyncMock()

        mock_comment_class.find.return_value = mock_find_result

        await CommentsDAO.delete_comments(fake_comments)

        mock_comment_class.find.assert_called_once()
        mock_find_result.delete.assert_awaited_once()
