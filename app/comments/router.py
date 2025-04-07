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


@router.get("/search")
async def search_comments(body: str) -> List[Comment]:
    comments = await CommentsDAO.find_comment(body=body)
    return comments
