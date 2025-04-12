from beanie import PydanticObjectId

from app.comments.dao import CommentsDAO
from app.comments.schemas import CommentScheme, CommentInsertScheme
from beanie.exceptions import DocumentNotFound
from app.exceptions.exceptions import ParentCommentNotFoundError, ParentConflict, ObjectNotFound
from loguru import logger
from app.comments.models import Comment
from typing import List


class CommentService:
    @classmethod
    async def create_comment(
            cls,
            comment_data: CommentScheme,
            user_id: int,
            note_hash_link: str
    ) -> Comment:
        """Comment creation with checking if a parent comment exists"""
        parent_comment = await CommentsDAO.get_comment_by_id(comment_data.parent_id) if comment_data.parent_id else None

        if comment_data.parent_id and not parent_comment:
            logger.error("Parent comment wasn't found")
            raise ParentCommentNotFoundError

        new_comment_data = CommentInsertScheme(
            note_hash_link=note_hash_link,
            user_id=user_id,
            body=comment_data.body,
            parent_id=comment_data.parent_id
        )

        new_comment = await CommentsDAO.insert_comment(new_comment_data)
        logger.info(f"Comment id={new_comment.id} created")

        if parent_comment:
            if parent_comment.note_hash_link != new_comment.note_hash_link:
                logger.error(f"Parent hash link does not match children hash link (Parent:{parent_comment.id}, Child: {new_comment.id})")
                raise ParentConflict
            try:
                await CommentsDAO.update_parent_comment(parent_comment, new_comment)
                logger.debug(f"Parent comment {parent_comment.id} added new instance {new_comment.id}")
            except (ValueError, DocumentNotFound):
                logger.error("Parent comment wasn't found")
                raise ParentCommentNotFoundError

        return new_comment

    @classmethod
    async def get_note_all_comments(cls, note_hash_link: str, limit: int) -> List[Comment]:
        comments = await CommentsDAO.get_comments_by_hash_link(note_hash_link, limit)

        if not comments:
            raise ObjectNotFound
        return comments

    @classmethod
    async def get_comment_by_id(cls, comment_id: PydanticObjectId, children: bool) -> Comment:
        comment = await CommentsDAO.get_comment_by_id(comment_id, children)

        if not comment:
            raise ObjectNotFound

        if not children:  # mongo doesn't fetch children, but outer model doesn't match pydantic scheme
            comment.children = []
        return comment
