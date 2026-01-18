from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.game import Game
from app.models.game_user import GameUser


class UserBase(SQLModel):
    name: str = Field(index=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    games: list["Game"] = Relationship(back_populates="users", link_model=GameUser)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


class UserPublic(UserBase):
    id: int
    email: EmailStr
