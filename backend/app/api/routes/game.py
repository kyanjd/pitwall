import uuid

from app import crud
from app.api.dependencies import CurrentSession, CurrentUser
from app.core.errors import ForbiddenError
from app.models.game import GameCreate, GameJoin, GamePublic, GamePublicWithMembers
from app.models.prediction import MemberScore, PredictionCreate, PredictionPublic, SessionScores
from app.models.user import UserPublic
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/game", tags=["game"])

## Game routes


@router.post("/", response_model=GamePublic)
def create_game(session: CurrentSession, current_user: CurrentUser, game_create: GameCreate) -> GamePublic:
    game = crud.game.create_game(session=session, game_create=game_create, created_by=current_user.id)
    return GamePublic.model_validate(game)


@router.get("/", response_model=list[GamePublic])
def get_games(session: CurrentSession, current_user: CurrentUser) -> list[GamePublic]:
    games = crud.game.get_games_by_user(session=session, user_id=current_user.id)
    return [GamePublic.model_validate(game) for game in games]


@router.post("/join", response_model=GamePublic)
def join_game(session: CurrentSession, current_user: CurrentUser, join: GameJoin) -> GamePublic:
    game = crud.game.join_game(session=session, invite_code=join.invite_code, user_id=current_user.id)
    return GamePublic.model_validate(game)


@router.get("/{game_id}", response_model=GamePublic)
def get_game(session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID) -> GamePublic:
    game = crud.game.get_game_by_id(session=session, game_id=game_id, user_id=current_user.id)
    return GamePublic.model_validate(game)


@router.get("/{game_id}/members", response_model=GamePublicWithMembers)
def get_game_members(session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID) -> GamePublicWithMembers:
    game, members = crud.game.get_game_by_id_with_members(session=session, game_id=game_id, user_id=current_user.id)
    return GamePublicWithMembers(
        **GamePublic.model_validate(game).model_dump(),
        members=[member.id for member in members],
    )


@router.get("/{game_id}/members/users", response_model=list[UserPublic])
def get_game_member_users(session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID) -> list[UserPublic]:
    _, members = crud.game.get_game_by_id_with_members(session=session, game_id=game_id, user_id=current_user.id)
    return [UserPublic.model_validate(m) for m in members]


## Prediction routes (all within game)


@router.post("/{game_id}/predict", response_model=PredictionPublic)
def make_prediction(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID, prediction_create: PredictionCreate
) -> PredictionPublic:
    prediction = crud.prediction.upsert_prediction(
        session=session, prediction_create=prediction_create, user_id=current_user.id, game_id=game_id
    )
    return PredictionPublic.model_validate(prediction)


@router.get("/{game_id}/f1session/{f1session_id}/predictions", response_model=list[PredictionPublic])
def get_all_predictions_for_session(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID, f1session_id: uuid.UUID
) -> list[PredictionPublic]:
    predictions = crud.prediction.get_predictions_for_session(
        session=session, game_id=game_id, f1session_id=f1session_id
    )
    return [PredictionPublic.model_validate(p) for p in predictions]


@router.get("/{game_id}/predictions", response_model=list[PredictionPublic])
def get_all_predictions_for_game(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID
) -> list[PredictionPublic]:
    predictions = crud.prediction.get_predictions_for_game(session=session, game_id=game_id)
    return [PredictionPublic.model_validate(p) for p in predictions]


@router.get("/{game_id}/f1session/{f1session_id}/me", response_model=PredictionPublic)
def get_my_prediction(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID, f1session_id: uuid.UUID
) -> PredictionPublic:
    prediction = crud.prediction.get_prediction_for_user_and_session(
        session=session, game_id=game_id, f1session_id=f1session_id, user_id=current_user.id
    )
    return PredictionPublic.model_validate(prediction)


@router.get("/{game_id}/f1session/{f1session_id}/score", response_model=MemberScore)
def get_my_score_for_session(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID, f1session_id: uuid.UUID
) -> MemberScore:
    prediction = crud.prediction.get_prediction_for_user_and_session(
        session=session, game_id=game_id, f1session_id=f1session_id, user_id=current_user.id
    )
    member_score = crud.prediction.score_prediction(session=session, user_id=current_user.id, prediction=prediction)
    return member_score


@router.get("/{game_id}/f1session/{f1session_id}/scores", response_model=SessionScores)
def get_scores_for_session(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID, f1session_id: uuid.UUID
) -> SessionScores:
    return crud.prediction.score_session(session=session, game_id=game_id, f1session_id=f1session_id)


@router.get("/{game_id}/scores", response_model=list[MemberScore])
def get_game_leaderboard(
    session: CurrentSession, current_user: CurrentUser, game_id: uuid.UUID
) -> list[MemberScore]:
    return crud.prediction.score_game(session=session, game_id=game_id)


class DnfOverride(BaseModel):
    driver_id: uuid.UUID


@router.patch("/{game_id}/f1session/{f1session_id}/dnf", status_code=204)
def set_first_dnf(
    session: CurrentSession, current_user: CurrentUser,
    game_id: uuid.UUID, f1session_id: uuid.UUID,
    body: DnfOverride,
) -> None:
    game = crud.game.get_game_by_id(session=session, game_id=game_id, user_id=current_user.id)
    if game.created_by != current_user.id:
        raise ForbiddenError("Only the game owner can override DNF results")
    crud.f1.set_first_dnf(session=session, f1session_id=f1session_id, driver_id=body.driver_id)
