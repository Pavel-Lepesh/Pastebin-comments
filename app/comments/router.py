from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query
from typing import Annotated, List
from app.comments.schemas import CommentScheme, CommentResponseScheme
from app.comments.models import Comment
from app.comments.dao import CommentsDAO
from app.comments.services import CommentService
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
        user_id: int = Depends(get_user_id)) -> CommentResponseScheme:
    comment = await CommentService.create_comment(comment_data, user_id, note_hash_link)
    return comment


@router.get("/", status_code=200, summary="Fetch all the note comments")
async def get_all_note_comments(note_hash_link: str,
                                limit: Annotated[int, Query(le=100)] = 100) -> List[CommentResponseScheme]:
    comments = await CommentService.get_note_all_comments(note_hash_link, limit)
    return comments


@router.get("/{comment_id}", status_code=200, summary="Fetch a comment with/without children")
async def get_comment_by_id(comment_id: PydanticObjectId,
                            children: Annotated[bool, Query()] = False) -> CommentResponseScheme:
    comment = await CommentService.get_comment_by_id(comment_id, children)
    return comment