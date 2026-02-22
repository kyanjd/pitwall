import uuid

from sqlmodel import Field, SQLModel, UniqueConstraint


class Prediction(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("game_id", "user_id", "f1session_id"),
        UniqueConstraint("game_id", "position_driver_id", "f1session_id"),
        UniqueConstraint("game_id", "dnf_driver_id", "f1session_id"),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    game_id: uuid.UUID = Field(foreign_key="game.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    f1session_id: uuid.UUID = Field(foreign_key="f1session.id", nullable=False)
    position: int = Field(default=10, nullable=False)
    position_driver_id: uuid.UUID = Field(foreign_key="driver.id", nullable=False)
    dnf_driver_id: uuid.UUID = Field(foreign_key="driver.id", nullable=False)
