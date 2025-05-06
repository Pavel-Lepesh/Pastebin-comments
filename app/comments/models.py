from datetime import datetime, timezone
from typing import List, Optional

from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import Field
from tzlocal import get_localzone


class Comment(Document):
    note_hash_link: Indexed(str)
    user_id: int
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timezone: str = Field(default_factory=lambda: str(get_localzone()))
    body: str
    parent_id: Optional[PydanticObjectId] = None
    children: List[Link["Comment"]] = []

    class Settings:
        name = "comments"
        use_state_management = True
