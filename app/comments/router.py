from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Request
from app.comments.schemas import CommentScheme
from app.comments.models import Comment
from app.comments.dao import CommentsDAO
from loguru import logger


router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post("/")
async def create_comment(comment_data: CommentScheme) -> Comment:
    comment = await CommentsDAO.insert_comment(comment_data)
    logger.info(f"Comment id={comment.id} created")
    return comment


@router.get("/{comment_id}")
async def get_comment_by_id(comment_id: PydanticObjectId) -> Comment:
    comment = await CommentsDAO.get_comment_by_id(comment_id)
    return comment
