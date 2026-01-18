from sqlmodel import Field, Relationship, SQLModel

from app.models.game import Game
from app.models.game_user import GameUser


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True, nullable=False)

    games: list[Game] = Relationship(back_populates="users", link_model=GameUser)
