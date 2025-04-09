from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query
from typing import Annotated
from app.comments.schemas import CommentScheme
from app.comments.models import Comment
from app.comments.dao import CommentsDAO
from loguru import logger
from app.comments.dependencies import get_user_id


router = APIRouter(
    prefix="/{note_hash_link}/comments",
    tags=["Comments"]
)


@router.post("/", status_code=201, summary="Comment creation")
async def create_comment(
        note_hash_link: str,
        comment_data: CommentScheme,
        user_id: int = Depends(get_user_id)) -> Comment:
    comment = await CommentsDAO.insert_comment(comment_data, user_id, note_hash_link)
    logger.info(f"Comment id={comment.id} created")
    return comment


@router.get("/", status_code=200, summary="Fetch all the note comments")
async def get_all_note_comments(note_hash_link: str, limit: Annotated[int, Query(le=100)] = 100):
    comments = await CommentsDAO.get_comments_by_hash_link(note_hash_link, limit)
    return comments


@router.get("/{comment_id}")
async def get_comment_by_id(comment_id: PydanticObjectId) -> Comment:
    comment = await CommentsDAO.get_comment_by_id(comment_id)
    return comment