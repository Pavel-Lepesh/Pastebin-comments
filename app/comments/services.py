from typing import List

from beanie import PydanticObjectId
from beanie.exceptions import DocumentNotFound
from loguru import logger

from app.comments.dao import CommentsDAO
from app.comments.models import Comment
from app.comments.schemas import CommentInsertScheme, CommentScheme, CommentUpdateScheme
from app.exceptions.exceptions import (
    AccessDenied,
    ObjectNotFound,
    ParentCommentNotFoundError,
    ParentConflict,
)


class CommentService:
    @classmethod
    async def create_comment(
        cls, comment_data: CommentScheme, user_id: int, note_hash_link: str
    ) -> Comment:
        """Comment creation with checking if a parent comment exists"""
        parent_comment = (
            await CommentsDAO.get_comment_by_id(comment_data.parent_id, False)
            if comment_data.parent_id
            else None
        )

        if comment_data.parent_id and not parent_comment:
            logger.error("Parent comment wasn't found")
            raise ParentCommentNotFoundError

        new_comment_data = CommentInsertScheme(
            note_hash_link=note_hash_link,
            user_id=user_id,
            body=comment_data.body,
            parent_id=comment_data.parent_id,
        )

        new_comment = await CommentsDAO.insert_comment(new_comment_data)
        logger.info(f"Comment id={new_comment.id} created")

        if parent_comment:
            if parent_comment.note_hash_link != new_comment.note_hash_link:
                logger.error(
                    f"Parent hash link does not match children hash link (Parent:{parent_comment.id}, Child: {new_comment.id})"
                )
                raise ParentConflict
            try:
                await CommentsDAO.update_parent_comment(parent_comment, new_comment)
                logger.debug(
                    f"Parent comment {parent_comment.id} added new instance {new_comment.id}"
                )
            except (ValueError, DocumentNotFound):
                logger.error("Parent comment wasn't found")
                raise ParentCommentNotFoundError

        return new_comment

    @classmethod
    async def get_note_all_comments(
        cls, note_hash_link: str, page: int, limit: int
    ) -> List[Comment]:
        skip = (page - 1) * limit
        comments = await CommentsDAO.get_comments_by_hash_link(
            note_hash_link, skip, limit
        )

        if not comments:
            raise ObjectNotFound
        return comments

    @classmethod
    async def get_comment_by_id(
        cls, comment_id: PydanticObjectId, children: bool
    ) -> Comment:
        comment = await CommentsDAO.get_comment_by_id(comment_id, children)

        if not comment:
            raise ObjectNotFound

        if not children:  # mongo doesn't fetch children, but outer model doesn't match pydantic scheme
            comment.children = []
        return comment

    @classmethod
    async def update_comment(
        cls,
        comment_id: PydanticObjectId,
        comment_data: CommentUpdateScheme,
        user_id: int,
    ) -> None:
        comment = await CommentsDAO.get_comment_by_id(comment_id, fetch_children=False)

        if not comment:
            raise ObjectNotFound

        if comment.user_id != user_id:
            raise AccessDenied

        try:
            await CommentsDAO.update_comment(comment, comment_data.body)
        except (ValueError, DocumentNotFound):
            raise ObjectNotFound

    @classmethod
    async def delete_comment(cls, comment_id: PydanticObjectId, user_id: int) -> None:
        """Uses recursion to collect all ids and then delete them in one iteration"""
        comment = await CommentsDAO.get_comment_by_id(comment_id, fetch_children=True)

        if not comment:
            raise ObjectNotFound

        if comment.user_id != user_id:
            raise AccessDenied

        ids: List[PydanticObjectId] = []

        def recursion_deletion(comment: Comment):
            nonlocal ids

            for child in comment.children:
                recursion_deletion(child)

                ids.append(child.id)

        recursion_deletion(comment)

        ids.append(comment.id)

        await CommentsDAO.delete_comments(ids)
