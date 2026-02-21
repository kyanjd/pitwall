from typing import Any

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.core.errors import AlreadyExistsError
from app.models.game import GameCreate, GameJoin, GamePublic
from fastapi import APIRouter

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/", response_model=GamePublic)
def create_game(session: CurrentSession, current_user: CurrentUser, game_create: GameCreate) -> GamePublic:
    game = crud.game.create_game(session=session, game_create=game_create, created_by=current_user.id)
    return GamePublic(
        id=game.id,
        name=game.name,
        created_at=game.created_at,
        created_by=game.created_by,
        invite_code=game.invite_code,
    )


@router.post("/join", response_model=GamePublic)
def join_game(session: CurrentSession, current_user: CurrentUser, join: GameJoin) -> GamePublic:
    game = crud.game.join_game(session=session, invite_code=join.invite_code, user_id=current_user.id)
    return GamePublic(
        id=game.id,
        name=game.name,
        created_at=game.created_at,
        created_by=game.created_by,
        invite_code=game.invite_code,
    )
