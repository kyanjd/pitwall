# from typing import TYPE_CHECKING

import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

# if TYPE_CHECKING:
from app.models.game import Game, GameUser


class UserBase(SQLModel):
    name: str = Field(index=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    games: list["Game"] = Relationship(back_populates="members", link_model=GameUser)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


class UserPublic(UserBase):
    id: uuid.UUID
