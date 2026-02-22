import uuid

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.models.game import GameCreate, GameJoin, GamePublic, GamePublicWithMembers
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


@router.get("/", response_model=list[GamePublic])
def get_games(session: CurrentSession, current_user: CurrentUser) -> list[GamePublic]:
    games = crud.game.get_games_by_user(session=session, user_id=current_user.id)
    return [
        GamePublic(
            id=game.id,
            name=game.name,
            created_at=game.created_at,
            created_by=game.created_by,
            invite_code=game.invite_code,
        )
        for game in games
    ]


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


@router.get("/{game_id}", response_model=GamePublic)
def get_game(session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID) -> GamePublic:
    game = crud.game.get_game_by_id(session=session, game_id=game_id, user_id=current_user.id)
    return GamePublic(
        id=game.id,
        name=game.name,
        created_at=game.created_at,
        created_by=game.created_by,
        invite_code=game.invite_code,
    )


@router.get("/{game_id}/members", response_model=GamePublicWithMembers)
def get_game_members(session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID) -> GamePublicWithMembers:
    game, members = crud.game.get_game_by_id_with_members(session=session, game_id=game_id, user_id=current_user.id)
    return GamePublicWithMembers(
        id=game.id,
        name=game.name,
        created_at=game.created_at,
        created_by=game.created_by,
        invite_code=game.invite_code,
        members=[member.id for member in members],
    )
