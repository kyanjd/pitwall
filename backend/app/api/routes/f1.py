import uuid
from typing import Annotated

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.core.config import settings
from app.core.errors import ForbiddenError
from app.models.f1 import Driver, F1SessionPublic, ResultPublic
from app.schema.f1 import F1SessionType
from app.services.ingest import Ingestor
from fastapi import APIRouter, Depends, Header

router = APIRouter(prefix="/f1", tags=["f1"])


def require_admin(x_admin_secret: Annotated[str, Header()] = "") -> None:
    if not settings.ADMIN_SECRET or x_admin_secret != settings.ADMIN_SECRET:
        raise ForbiddenError("Invalid admin secret")


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
    return {"seasons": [2025, 2026]}  # TODO: Get real seasons from DB


# --- Admin endpoints ---

@router.post("/admin/setup/{season}", dependencies=[Depends(require_admin)])
def admin_setup_season(session: CurrentSession, season: int) -> dict:
    """Run once per season: ingest schedule + drivers + seed stub results."""
    Ingestor(session=session).setup_season(season)
    return {"ok": True, "season": season}


@router.post("/admin/ingest/{season}/results", dependencies=[Depends(require_admin)])
def admin_ingest_results(session: CurrentSession, season: int) -> dict:
    """Ingest race + qualifying results for a season."""
    ingestor = Ingestor(session=session)
    ingestor.ingest_results_and_background(season, F1SessionType.RACE)
    ingestor.ingest_results_and_background(season, F1SessionType.QUALIFYING)
    return {"ok": True, "season": season}
