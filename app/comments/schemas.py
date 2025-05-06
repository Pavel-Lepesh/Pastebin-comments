from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class CommentScheme(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: Optional[PydanticObjectId] = None


class CommentInsertScheme(CommentScheme):
    note_hash_link: str
    user_id: int


class CommentResponseScheme(BaseModel):
    id: PydanticObjectId
    note_hash_link: str
    user_id: int
    body: str
    created: datetime
    children: List["CommentResponseScheme"] = None


class CommentUpdateScheme(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
