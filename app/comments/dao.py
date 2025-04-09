from beanie import PydanticObjectId
from app.exceptions.exceptions import ParentCommentNotFoundError

from app.comments.models import Comment
from app.comments.schemas import CommentScheme
from loguru import logger


class CommentsDAO:
    @classmethod
    async def insert_comment(cls, comment_data: CommentScheme, user_id: int, note_hash_link: str) -> Comment:
        data = comment_data.model_dump()
        data["user_id"] = user_id
        data["note_hash_link"] = note_hash_link
        parent = await cls._get_parent_comment(comment_data.parent_id)

        comment = Comment(**data)
        await comment.insert()

        if parent:
            parent.children.append(comment)
            await parent.save()
            logger.debug(f"Parent comment {parent.id} added new instance {comment.id}")

        return comment

    @classmethod
    async def get_comment_by_id(cls, comment_id) -> Comment:
        result = await Comment.get(document_id=comment_id, fetch_links=True)
        return result

    @classmethod
    async def get_comments_by_hash_link(cls, note_hash_link: str, limit: int = 100):
        comments = await Comment.find(
            {"note_hash_link": note_hash_link, "parent_id": None},
            fetch_links=True,
            limit=limit
        ).to_list()
        return comments

    @staticmethod
    async def _get_parent_comment(parent_id: PydanticObjectId | None) -> Comment | None:
        if not parent_id:
            return None

        parent = await Comment.get(document_id=parent_id)

        if not parent:
            logger.error("Parent comment wasn't found")
            raise ParentCommentNotFoundError("Parent's comment does not exist")

        return parent
