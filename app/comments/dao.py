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
        if data["parent_id"]:
            data["parent_id"] = PydanticObjectId(data["parent_id"])

        comment = Comment(**data)
        await comment.insert()

        if comment.parent_id:
            parent = await Comment.get(comment.parent_id)

            if not parent:
                logger.error("Parent")
                raise ParentCommentNotFoundError("Parent's comment does not exist")

            parent.children.append(comment)
            await parent.save()

        return comment

    @classmethod
    async def find_comment(cls, **kwargs):
        result = await Comment.find(kwargs, fetch_links=True).to_list()
        return result
