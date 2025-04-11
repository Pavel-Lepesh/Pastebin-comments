from beanie import PydanticObjectId
from app.exceptions.exceptions import ParentCommentNotFoundError

from app.comments.models import Comment
from app.comments.schemas import CommentScheme, CommentInsertScheme
from loguru import logger


class CommentsDAO:
    @classmethod
    async def insert_comment(cls, comment_data: CommentInsertScheme) -> Comment:
        comment = Comment(
            note_hash_link=comment_data.note_hash_link,
            user_id=comment_data.user_id,
            body=comment_data.body,
            parent_id=comment_data.parent_id
        )
        await comment.insert()
        return comment

    @classmethod
    async def update_parent_comment(cls, parent_comment: Comment, children_comment: Comment):
        parent_comment.children.append(children_comment)
        await parent_comment.replace()

    @classmethod
    async def get_comment_by_id(cls, comment_id, fetch_children=False) -> Comment:
        result = await Comment.get(document_id=comment_id, fetch_links=fetch_children)
        return result

    @classmethod
    async def get_comments_by_hash_link(cls, note_hash_link: str, limit: int = 100):
        comments = await Comment.find(
            {"note_hash_link": note_hash_link, "parent_id": None},
            fetch_links=True,
            limit=limit
        ).to_list()
        return comments
