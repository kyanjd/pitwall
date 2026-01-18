from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from app.models.game_user import GameUser
from app.models.user import User


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    users: list[User] = Relationship(back_populates="games", link_model=GameUser)
