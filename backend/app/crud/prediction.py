import uuid

from sqlmodel import Session, select

from app.core.errors import NotFoundError
from app.models.prediction import Prediction, PredictionCreate


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
