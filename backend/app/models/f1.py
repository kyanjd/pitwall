import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class Race(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("season", "round"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    circuit_id: uuid.UUID = Field(foreign_key="circuit.id", nullable=False)
    round: int = Field(nullable=False, index=True)
    season: int = Field(nullable=False, index=True)
    date: str = Field(nullable=False)

    sessions: list["Session"] = Relationship(back_populates="race")


class Circuit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    external_id: str = Field(nullable=False, unique=True, index=True)
    name: str = Field(nullable=False)
    locality: str = Field(nullable=False)
    country: str = Field(nullable=False)


class Result(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    driver_id: uuid.UUID = Field(foreign_key="driver.id", nullable=False)
    session_id: uuid.UUID = Field(foreign_key="session.id", nullable=False)
    position: int = Field(nullable=False)
    status: str = Field(nullable=False)

    driver: Optional["Driver"] = Relationship(back_populates="results")
    session: Optional["Session"] = Relationship(back_populates="results")


class Driver(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    constructor_id: uuid.UUID = Field(foreign_key="constructor.id", nullable=False)

    constructor: Optional["Constructor"] = Relationship(back_populates="drivers")
    results: list["Result"] = Relationship(back_populates="driver")


class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(foreign_key="race.id", nullable=False, index=True)
    type: str = Field(nullable=False)  # "FP1", "Qualifying", "Sprint", "Race"
    date: datetime = Field(nullable=False)

    race: Optional["Race"] = Relationship(back_populates="sessions")
    results: list["Result"] = Relationship(back_populates="session")


class Constructor(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    external_id: str = Field(nullable=False, unique=True, index=True)
    name: str = Field(nullable=False)
    nationality: str = Field(nullable=False)

    drivers: list["Driver"] = Relationship(back_populates="constructor")
