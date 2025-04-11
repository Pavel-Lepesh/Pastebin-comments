from app.comments.dao import CommentsDAO
from app.comments.schemas import CommentScheme, CommentInsertScheme
from beanie.exceptions import DocumentNotFound
from app.exceptions.exceptions import ParentCommentNotFoundError
from loguru import logger


class CommentService:
    @classmethod
    async def create_comment(  # TODO create transaction
            cls,
            comment_data: CommentScheme,
            user_id: int,
            note_hash_link: str
    ):
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
            try:
                await CommentsDAO.update_parent_comment(parent_comment, new_comment)
                logger.debug(f"Parent comment {parent_comment.id} added new instance {new_comment.id}")
            except (ValueError, DocumentNotFound):
                logger.error("Parent comment wasn't found")
                raise ParentCommentNotFoundError

        return new_comment
