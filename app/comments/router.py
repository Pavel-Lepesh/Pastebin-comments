from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query
from typing import Annotated, List
from app.comments.schemas import CommentScheme, CommentResponseScheme, CommentUpdateScheme
from app.comments.services import CommentService
from app.comments.dependencies import get_user_id


notes_comments_router = APIRouter(
    prefix="/{note_hash_link}/comments",
    tags=["Comments"]
)


comments_router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@notes_comments_router.post("/", status_code=201, summary="Comment creation")
async def create_comment(
        note_hash_link: str,
        comment_data: CommentScheme,
        user_id: int = Depends(get_user_id)) -> CommentResponseScheme:
    comment = await CommentService.create_comment(comment_data, user_id, note_hash_link)
    return comment


@notes_comments_router.get("/", status_code=200, summary="Fetch all the note comments")
async def get_all_note_comments(note_hash_link: str,
                                page: Annotated[int, Query(gt=0)] = 1,
                                limit: Annotated[int, Query(gt=1, le=100)] = 10) -> List[CommentResponseScheme]:
    comments = await CommentService.get_note_all_comments(note_hash_link, page, limit)
    return comments


@comments_router.get("/{comment_id}", status_code=200, summary="Fetch a comment with/without children")
async def get_comment_by_id(comment_id: PydanticObjectId,
                            children: Annotated[bool, Query()] = False) -> CommentResponseScheme:
    comment = await CommentService.get_comment_by_id(comment_id, children)
    return comment


@comments_router.patch("/{comment_id}", status_code=204, summary="Update a comment")
async def update_comment(comment_id: PydanticObjectId, comment_data: CommentUpdateScheme) -> None:
    await CommentService.update_comment(comment_id, comment_data)


@comments_router.delete("/{comment_id}", status_code=204, summary="Delete a comment")
async def delete_comment(comment_id: PydanticObjectId) -> None:
    await CommentService.delete_comment(comment_id)
