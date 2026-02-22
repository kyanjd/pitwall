import uuid

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.models.f1 import Driver, F1SessionPublic
from fastapi import APIRouter

router = APIRouter(prefix="/f1", tags=["f1"])


@router.get("/season/{season}/sessions", response_model=list[F1SessionPublic])
def get_sessions_for_season(session: CurrentSession, season: int) -> list[F1SessionPublic]:
    sessions = crud.f1.get_sessions_for_season(session=session, season=season)
    return [
        F1SessionPublic(
            **s.model_dump(),
            race_name=s.race.name,
            race_round=s.race.round,
            race_season=s.race.season,
        )
        for s in sessions
        if s.race is not None
    ]


@router.get("/session/{f1session_id}/drivers", response_model=list[Driver])
def get_drivers_for_session(session: CurrentSession, f1session_id: uuid.UUID) -> list[Driver]:
    drivers = crud.f1.get_drivers_for_session(session=session, f1session_id=f1session_id)
    return drivers


@router.get("/seasons", response_model=dict[str, list[int]])
def get_seasons(session: CurrentSession) -> dict[str, list[int]]:
    return {"seasons": [2025, 2026]}  # TODO: Get real seasons from DBx
