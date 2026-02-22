import uuid

from sqlmodel import Session, select

from app import crud
from app.core.errors import NotFoundError
from app.models.f1 import Result
from app.models.prediction import MemberScore, Prediction, PredictionCreate, SessionScores
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
        session.commit()
        session.refresh(existing_prediction)
        return existing_prediction
    else:
        db_obj = Prediction.model_validate(prediction_create, update={"user_id": user_id, "game_id": game_id})
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


def get_predictions_for_session(*, session: Session, game_id: uuid.UUID, f1session_id: uuid.UUID) -> list[Prediction]:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
        Prediction.f1session_id == f1session_id,
    )
    return list(session.exec(statement).all())


def get_predictions_for_game(*, session: Session, game_id: uuid.UUID) -> list[Prediction]:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
    )
    return list(session.exec(statement).all())


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


def score_prediction(*, session: Session, user_id: uuid.UUID, prediction: Prediction) -> MemberScore:
    scorer = Scorer()

    position_result = crud.f1.get_result_by_f1session_and_driver(
        session=session, f1session_id=prediction.f1session_id, driver_id=prediction.position_driver_id
    )
    position_score = scorer.score_position(
        actual_position=position_result.position, predicted_position=prediction.position
    )

    driver = crud.f1.get_first_dnf_by_f1session(session=session, f1session_id=prediction.f1session_id)
    actual_driver = driver.id if driver else None
    dnf_score = scorer.score_dnf(actual_driver=actual_driver, predicted_driver=prediction.dnf_driver_id)

    return MemberScore(user_id=user_id, position_score=position_score, dnf_score=dnf_score)


def score_session(*, session: Session, game_id: uuid.UUID, f1session_id: uuid.UUID) -> SessionScores:
    predictions = get_predictions_for_session(session=session, game_id=game_id, f1session_id=f1session_id)
    member_scores = [score_prediction(session=session, user_id=p.user_id, prediction=p) for p in predictions]
    return SessionScores(f1session_id=f1session_id, member_scores=member_scores)


def score_game(*, session: Session, game_id: uuid.UUID) -> list[MemberScore]:
    predictions = get_predictions_for_game(session=session, game_id=game_id)
    totals: dict[uuid.UUID, MemberScore] = {}
    for p in predictions:
        ms = score_prediction(session=session, user_id=p.user_id, prediction=p)
        if p.user_id in totals:
            existing = totals[p.user_id]
            totals[p.user_id] = MemberScore(
                user_id=p.user_id,
                position_score=existing.position_score + ms.position_score,
                dnf_score=existing.dnf_score + ms.dnf_score,
            )
        else:
            totals[p.user_id] = ms
    return sorted(totals.values(), key=lambda s: s.total_score, reverse=True)
