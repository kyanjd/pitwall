import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

from sqlmodel import Field, Relationship, SQLModel

from app.core.security import create_invite_code


class GameUser(SQLModel, table=True):
    game_id: uuid.UUID = Field(foreign_key="game.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class Game(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    season: int = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    invite_code: str = Field(default_factory=create_invite_code, unique=True)

    members: list["User"] = Relationship(back_populates="games", link_model=GameUser)


class GameCreate(SQLModel):
    name: str
    season: int


class GameJoin(SQLModel):
    invite_code: str


class GamePublic(SQLModel):
    id: uuid.UUID
    name: str
    season: int
    created_at: datetime
    created_by: uuid.UUID
    invite_code: str


class GamePublicWithMembers(GamePublic):
    members: list[uuid.UUID]
