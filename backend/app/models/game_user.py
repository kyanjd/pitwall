import uuid

from sqlmodel import Field, SQLModel


class GameUser(SQLModel, table=True):
    game_id: uuid.UUID = Field(foreign_key="game.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
