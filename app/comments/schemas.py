from pydantic import BaseModel, Field
from typing import Optional


class CommentScheme(BaseModel):
    note_hash_link: str
    user_id: int
    body: str = Field(min_length=1, max_length=2000)
    parent_id: Optional[str] = None
