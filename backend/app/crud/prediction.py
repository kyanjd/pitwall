import uuid

from sqlmodel import Session, select

from app import crud
from app.core.errors import AlreadyExistsError, NotFoundError
from app.models.f1 import Result
from app.models.game import GameUser
from app.models.prediction import MemberScore, Prediction, PredictionCreate, SessionScores
from app.services.score import Scorer


def upsert_prediction(
    *, session: Session, user_id: uuid.UUID, game_id: uuid.UUID, prediction_create: PredictionCreate
) -> Prediction:
    pos_conflict = session.exec(
        select(Prediction).where(
            Prediction.game_id == game_id,
            Prediction.f1session_id == prediction_create.f1session_id,
            Prediction.position_driver_id == prediction_create.position_driver_id,
            Prediction.user_id != user_id,
        )
    ).first()
    if pos_conflict:
        raise AlreadyExistsError("That driver is already picked for 10th by another player")

    dnf_conflict = session.exec(
        select(Prediction).where(
            Prediction.game_id == game_id,
            Prediction.f1session_id == prediction_create.f1session_id,
            Prediction.dnf_driver_id == prediction_create.dnf_driver_id,
            Prediction.user_id != user_id,
        )
    ).first()
    if dnf_conflict:
        raise AlreadyExistsError("That driver is already picked for DNF by another player")

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


def delete_prediction(
    *, session: Session, user_id: uuid.UUID, game_id: uuid.UUID, f1session_id: uuid.UUID
) -> None:
    statement = select(Prediction).where(
        Prediction.game_id == game_id,
        Prediction.f1session_id == f1session_id,
        Prediction.user_id == user_id,
    )
    prediction = session.exec(statement).first()
    if prediction:
        session.delete(prediction)
        session.commit()


def session_has_results(*, session: Session, f1session_id: uuid.UUID) -> bool:
    # position > 0 excludes stub results created by ingest_season_roster (position=0 sentinel)
    statement = select(Result).where(Result.f1session_id == f1session_id, Result.position > 0)
    return session.exec(statement).first() is not None


def score_prediction(*, session: Session, user_id: uuid.UUID, prediction: Prediction) -> MemberScore:
    scorer = Scorer()

    try:
        position_result = crud.f1.get_result_by_f1session_and_driver(
            session=session, f1session_id=prediction.f1session_id, driver_id=prediction.position_driver_id
        )
        position_score = scorer.score_position(
            actual_position=position_result.position, predicted_position=prediction.position
        )
    except NotFoundError:
        position_score = 0

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
        if not session_has_results(session=session, f1session_id=p.f1session_id):
            continue
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

    # Ensure all game members appear, even those with no scored predictions yet
    all_member_ids = session.exec(select(GameUser.user_id).where(GameUser.game_id == game_id)).all()
    for member_id in all_member_ids:
        if member_id not in totals:
            totals[member_id] = MemberScore(user_id=member_id, position_score=0, dnf_score=0)

    return sorted(totals.values(), key=lambda s: s.total_score, reverse=True)
