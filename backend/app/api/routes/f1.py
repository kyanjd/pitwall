import uuid

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.models.f1 import Driver, F1Session
from fastapi import APIRouter

router = APIRouter(prefix="/f1", tags=["f1"])


@router.get("/season/{season}/sessions", response_model=list[F1Session])
def get_sessions_for_season(session: CurrentSession, season: int) -> list[F1Session]:
    sessions = crud.f1.get_sessions_for_season(session=session, season=season)
    return sessions


@router.get("/session/{f1session_id}/drivers", response_model=list[Driver])
def get_drivers_for_session(session: CurrentSession, f1session_id: uuid.UUID) -> list[Driver]:
    drivers = crud.f1.get_drivers_for_session(session=session, f1session_id=f1session_id)
    return drivers
