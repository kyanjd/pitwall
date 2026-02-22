import uuid

from sqlmodel import Session, select

from app import crud
from app.core.errors import NotFoundError
from app.models.f1 import Result
from app.models.prediction import Prediction, PredictionCreate
from app.services.score import Scorer


def upsert_prediction(
    *, session: Session, user_id: uuid.UUID, game_id: uuid.UUID, prediction_create: PredictionCreate
) -> Prediction:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
        Prediction.f1session_id == prediction_create.f1session_id,
        Prediction.user_id == user_id,
    )
    existing_prediction = session.exec(statement).first()

    if existing_prediction:
        existing_prediction.position_driver_id = prediction_create.position_driver_id
        existing_prediction.dnf_driver_id = prediction_create.dnf_driver_id
        existing_prediction.position = prediction_create.position
        session.add(existing_prediction)
        return existing_prediction
    else:
        db_obj = Prediction.model_validate(prediction_create)
        db_obj.user_id = user_id
        db_obj.game_id = game_id
        session.add(db_obj)
        return db_obj


def get_predictions_for_session(*, session: Session, game_id: uuid.UUID, f1session_id: uuid.UUID) -> list[Prediction]:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
        Prediction.f1session_id == f1session_id,
    )
    predictions = list(session.exec(statement).all())
    if not predictions:
        raise NotFoundError(f"No predictions found for game {game_id} and session {f1session_id}")
    return predictions


def get_predictions_for_game(*, session: Session, game_id: uuid.UUID) -> list[Prediction]:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
    )
    predictions = list(session.exec(statement).all())
    if not predictions:
        raise NotFoundError(f"No predictions found for game {game_id}")
    return predictions


def get_prediction_for_user_and_session(
    *, session: Session, game_id: uuid.UUID, f1session_id: uuid.UUID, user_id: uuid.UUID
) -> Prediction:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
        Prediction.f1session_id == f1session_id,
        Prediction.user_id == user_id,
    )
    prediction = session.exec(statement).first()
    if not prediction:
        raise NotFoundError(f"No prediction found for game {game_id}, session {f1session_id} and user {user_id}")
    return prediction


def score_prediction(*, session: Session, prediction: Prediction) -> int:
    scorer = Scorer()

    position_result = crud.f1.get_result_by_f1session_and_driver(
        session=session, f1session_id=prediction.f1session_id, driver_id=prediction.position_driver_id
    )
    position_score = scorer.score_position(
        actual_position=position_result.position, predicted_position=prediction.position
    )

    dnf_result = crud.f1.get_result_by_f1session_and_driver(
        session=session, f1session_id=prediction.f1session_id, driver_id=prediction.dnf_driver_id
    )
    dnf_score = scorer.score_dnf(predicted_driver=prediction.dnf_driver_id)
