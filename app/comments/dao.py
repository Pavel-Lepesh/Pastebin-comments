from typing import List

from beanie import PydanticObjectId

from app.comments.models import Comment
from app.comments.schemas import CommentInsertScheme
from beanie.operators import In


class CommentsDAO:
    @classmethod
    async def insert_comment(cls, comment_data: CommentInsertScheme) -> Comment:
        comment = Comment(
            note_hash_link=comment_data.note_hash_link,
            user_id=comment_data.user_id,
            body=comment_data.body,
            parent_id=comment_data.parent_id,
        )
        await comment.insert()
        return comment

    @classmethod
    async def update_parent_comment(
        cls, parent_comment: Comment, children_comment: Comment
    ) -> None:
        parent_comment.children.append(children_comment)
        await parent_comment.replace()

    @classmethod
    async def get_comment_by_id(
        cls, comment_id: PydanticObjectId, fetch_children: bool
    ) -> Comment:
        comment = await Comment.get(document_id=comment_id, fetch_links=fetch_children)
        return comment

    @classmethod
    async def get_comments_by_hash_link(
        cls, note_hash_link: str, skip: int, limit: int
    ) -> List[Comment]:
        comments = await Comment.find(
            # parent_id = None to prevent duplication among children comments
            {"note_hash_link": note_hash_link, "parent_id": None},
            fetch_links=True,
            skip=skip,
            limit=limit,
        ).to_list()
        return comments

    @classmethod
    async def update_comment(cls, comment: Comment, body: str) -> None:
        comment.body = body
        await comment.replace()

    @classmethod
    async def delete_comments(cls, comments: List[PydanticObjectId]) -> None:
        await Comment.find(In(Comment.id, comments)).delete()
