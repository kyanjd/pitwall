from sqlmodel import Field, SQLModel


class GameUser(SQLModel, table=True):
    game_id: int = Field(foreign_key="game.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
