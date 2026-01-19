import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class Race(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("season", "round"),)
    id: int = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    circuitId: str = Field(foreign_key="circuit.id", nullable=False)
    round: int = Field(nullable=False, index=True)
    season: int = Field(nullable=False, index=True)
    date: str = Field(nullable=False)


class Circuit(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False)
    locality: str = Field(nullable=False)
    country: str = Field(nullable=False)


class Result(SQLModel, table=True):
    id: int = Field(default_factory=uuid.uuid4, primary_key=True)
    raceId: str = Field(foreign_key="race.id", nullable=False)
    driverId: str = Field(foreign_key="driver.id", nullable=False)
    sessionId: uuid.UUID = Field(foreign_key="session.id", nullable=False)
    position: int = Field(nullable=False)
    status: str = Field(nullable=False)


class Driver(SQLModel, table=True):
    id: str = Field(primary_key=True)
    firstName: str = Field(nullable=False)
    lastName: str = Field(nullable=False)


class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(foreign_key="race.id", nullable=False, index=True)
    type: str = Field(nullable=False)  # "FP1", "Qualifying", "Sprint", "Race"
    date: datetime = Field(nullable=False)
