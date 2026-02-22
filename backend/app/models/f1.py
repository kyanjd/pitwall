import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class Result(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("driver_id", "f1session_id"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    driver_id: uuid.UUID = Field(foreign_key="driver.id", nullable=False)
    f1session_id: uuid.UUID = Field(foreign_key="f1session.id", nullable=False)
    constructor_id: uuid.UUID = Field(foreign_key="constructor.id", nullable=False)
    position: int = Field(nullable=False)
    position_text: Optional[str] = Field(nullable=True)
    status: Optional[str] = Field(nullable=True)
    grid: Optional[str] = Field(nullable=True)
    laps: Optional[int] = Field(nullable=True)
    dnf_order: Optional[int] = Field(nullable=True)

    driver: Optional["Driver"] = Relationship(back_populates="results")
    constructor: Optional["Constructor"] = Relationship(back_populates="results")
    f1session: Optional["F1Session"] = Relationship(back_populates="results")


class Driver(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    external_id: str = Field(nullable=False, unique=True, index=True)
    code: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)

    results: list["Result"] = Relationship(back_populates="driver")


class Constructor(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    external_id: str = Field(nullable=False, unique=True, index=True)
    name: str = Field(nullable=False)
    nationality: str = Field(nullable=False)

    results: list["Result"] = Relationship(back_populates="constructor")


class F1Session(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("race_id", "type"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    race_id: uuid.UUID = Field(foreign_key="race.id", nullable=False, index=True)
    type: str = Field(nullable=False)  # "FP1", "Qualifying", "Sprint", "Race"
    date: datetime = Field(nullable=False)

    race: Optional["Race"] = Relationship(back_populates="f1sessions")
    results: list["Result"] = Relationship(back_populates="f1session")


class Race(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("season", "round"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    circuit_id: uuid.UUID = Field(foreign_key="circuit.id", nullable=False)
    round: int = Field(nullable=False, index=True)
    season: int = Field(nullable=False, index=True)

    f1sessions: list["F1Session"] = Relationship(back_populates="race")


class F1SessionPublic(SQLModel):
    id: uuid.UUID
    type: str
    date: datetime
    race_id: uuid.UUID
    race_name: str
    race_round: int
    race_season: int


class Circuit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    external_id: str = Field(nullable=False, unique=True, index=True)
    name: str = Field(nullable=False)
    locality: str = Field(nullable=False)
    country: str = Field(nullable=False)
