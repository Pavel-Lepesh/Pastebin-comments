from beanie import Document, Indexed, Link, PydanticObjectId, before_event, Insert, SaveChanges
from datetime import datetime, timezone
from pydantic import Field
from typing import Optional, List
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

    # @before_event(Insert)
    # async def update_timestamps(self):
    #     self.updated = datetime.now(get_localzone())
    #     self.created = datetime.now(get_localzone())
    #     self.timezone = str(get_localzone())

    # @before_event(Insert, SaveChanges)
    # async def update_timestamps(self):
    #     """Обновляет только UTC-метки"""
    #     now = datetime.now(timezone.utc)
    #     if not hasattr(self, "created"):
    #         self.created = now
    #     self.updated = now
