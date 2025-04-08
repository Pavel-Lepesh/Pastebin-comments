from beanie import PydanticObjectId, Link
from fastapi import HTTPException, status
from app.exceptions.exceptions import ParentCommentNotFoundError

from app.comments.models import Comment
from app.comments.schemas import CommentScheme
from loguru import logger


class CommentsDAO:
    @classmethod
    async def insert_comment(cls, comment_data: CommentScheme) -> Comment:
        data = comment_data.model_dump()
        comment = Comment(**data)
        parent = None

        if data["parent_id"]:
            parent = await Comment.get(document_id=data["parent_id"])

            if not parent:
                logger.error("Parent comment wasn't found")
                raise ParentCommentNotFoundError("Parent's comment does not exist")

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
