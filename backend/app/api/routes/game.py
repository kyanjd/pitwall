import uuid

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.models.game import GameCreate, GameJoin, GamePublic, GamePublicWithMembers
from app.models.prediction import PredictionCreate, PredictionPublic
from fastapi import APIRouter

router = APIRouter(prefix="/game", tags=["game"])

## Game routes


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


## Prediction routes (all within game)


@router.post("/{game_id}/predict", response_model=PredictionPublic)
def make_prediction(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID, prediction_create: PredictionCreate
) -> PredictionPublic:
    prediction = crud.prediction.upsert_prediction(
        session=session, prediction_create=prediction_create, user_id=current_user.id, game_id=game_id
    )
    return PredictionPublic(
        id=prediction.id,
        game_id=prediction.game_id,
        user_id=prediction.user_id,
        f1session_id=prediction.f1session_id,
        position=prediction.position,
        position_driver_id=prediction.position_driver_id,
        dnf_driver_id=prediction.dnf_driver_id,
    )
