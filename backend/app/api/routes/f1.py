import uuid

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.models.f1 import Driver, F1SessionPublic, ResultPublic
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


@router.get("/session/{f1session_id}/results", response_model=list[ResultPublic])
def get_results_for_session(session: CurrentSession, _: CurrentUser, f1session_id: uuid.UUID) -> list[ResultPublic]:
    results = crud.f1.get_results_for_session(session=session, f1session_id=f1session_id)
    first_dnf = crud.f1.get_first_dnf_by_f1session(session=session, f1session_id=f1session_id)
    first_dnf_id = first_dnf.id if first_dnf else None
    return [
        ResultPublic(
            driver_id=r.driver_id,
            driver_code=r.driver.code if r.driver else "???",
            driver_first_name=r.driver.first_name if r.driver else "",
            driver_last_name=r.driver.last_name if r.driver else "",
            position=r.position,
            position_text=r.position_text,
            status=r.status,
            laps=r.laps,
            is_first_dnf=r.driver_id == first_dnf_id,
        )
        for r in results
    ]


@router.get("/seasons", response_model=dict[str, list[int]])
def get_seasons(session: CurrentSession) -> dict[str, list[int]]:
    return {"seasons": [2025, 2026]}  # TODO: Get real seasons from DBx
