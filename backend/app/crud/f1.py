import uuid

from sqlmodel import Session, col, select

from app.core.errors import NotFoundError
from app.models.f1 import Circuit, Constructor, Driver, F1Session, Race, Result


def upsert_circuit(*, session: Session, circuit: Circuit) -> Circuit:
    statement = select(Circuit).where(Circuit.external_id == circuit.external_id)
    existing_circuit = session.exec(statement).first()

    if existing_circuit:
        existing_circuit.name = circuit.name
        existing_circuit.locality = circuit.locality
        existing_circuit.country = circuit.country
        session.add(existing_circuit)
        return existing_circuit
    else:
        session.add(circuit)
        return circuit


def upsert_race(*, session: Session, race: Race) -> Race:
    statement = select(Race).where(Race.season == race.season, Race.round == race.round)
    existing_race = session.exec(statement).first()

    if existing_race:
        existing_race.name = race.name
        existing_race.circuit_id = race.circuit_id
        session.add(existing_race)
        return existing_race
    else:
        session.add(race)
        return race


def upsert_f1session(*, session: Session, f1session: F1Session) -> F1Session:
    statement = select(F1Session).where(F1Session.race_id == f1session.race_id, F1Session.type == f1session.type)
    existing_session = session.exec(statement).first()

    if existing_session:
        existing_session.date = f1session.date
        session.add(existing_session)
        return existing_session
    else:
        session.add(f1session)
        return f1session


def upsert_driver(*, session: Session, driver: Driver) -> Driver:
    statement = select(Driver).where(Driver.external_id == driver.external_id)
    existing_driver = session.exec(statement).first()

    if existing_driver:
        existing_driver.code = driver.code
        existing_driver.first_name = driver.first_name
        existing_driver.last_name = driver.last_name
        session.add(existing_driver)
        return existing_driver
    else:
        session.add(driver)
        return driver


def upsert_constructor(*, session: Session, constructor: Constructor) -> Constructor:
    statement = select(Constructor).where(Constructor.external_id == constructor.external_id)
    existing_constructor = session.exec(statement).first()

    if existing_constructor:
        existing_constructor.name = constructor.name
        existing_constructor.nationality = constructor.nationality
        session.add(existing_constructor)
        return existing_constructor
    else:
        session.add(constructor)
        return constructor


def upsert_result(*, session: Session, result: Result) -> Result:
    statement = select(Result).where(Result.driver_id == result.driver_id, Result.f1session_id == result.f1session_id)
    existing_result = session.exec(statement).first()

    if existing_result:
        existing_result.constructor_id = result.constructor_id
        existing_result.position = result.position
        existing_result.position_text = result.position_text
        existing_result.status = result.status
        existing_result.grid = result.grid
        existing_result.laps = result.laps
        session.add(existing_result)
        return existing_result
    else:
        session.add(result)
        return result


def get_result_by_f1session_and_driver(*, session: Session, f1session_id: uuid.UUID, driver_id: uuid.UUID) -> Result:
    statement = select(Result).where(Result.f1session_id == f1session_id, Result.driver_id == driver_id)
    result = session.exec(statement).first()
    if not result:
        raise NotFoundError(f"Result not found for session {f1session_id} and driver {driver_id}")
    return result


def get_first_dnf_by_f1session(*, session: Session, f1session_id: uuid.UUID) -> Driver | None:
    statement = (
        select(Result)
        .where(Result.f1session_id == f1session_id, Result.status != "Finished")
        .order_by(col(Result.dnf_order).asc().nulls_last(), col(Result.laps).asc())
    )
    result = session.exec(statement).first()
    return result.driver if result else None


def set_first_dnf(*, session: Session, f1session_id: uuid.UUID, driver_id: uuid.UUID) -> None:
    results = list(session.exec(select(Result).where(Result.f1session_id == f1session_id)).all())
    for r in results:
        r.dnf_order = None
        session.add(r)
    target = session.exec(
        select(Result).where(Result.f1session_id == f1session_id, Result.driver_id == driver_id)
    ).first()
    if not target:
        raise NotFoundError(f"Result not found for driver {driver_id} in session {f1session_id}")
    target.dnf_order = 1
    session.add(target)
    session.commit()


def get_drivers_for_season(*, session: Session, season: int) -> list[Driver]:
    statement = (
        select(Driver)
        .join(Result)
        .join(F1Session)
        .join(Race)
        .where(Race.season == season)
        .distinct()
    )
    return list(session.exec(statement).all())


def get_drivers_for_session(*, session: Session, f1session_id: uuid.UUID) -> list[Driver]:
    statement = select(Driver).join(Result).where(Result.f1session_id == f1session_id)
    drivers = list(session.exec(statement).all())
    if drivers:
        return drivers

    # No results yet (future race) — fall back to same season's grid, then previous season
    f1session = session.get(F1Session, f1session_id)
    if not f1session:
        return []
    race = session.get(Race, f1session.race_id)
    if not race:
        return []

    drivers = get_drivers_for_season(session=session, season=race.season)
    if not drivers:
        drivers = get_drivers_for_season(session=session, season=race.season - 1)
    return drivers


def get_sessions_for_season(*, session: Session, season: int) -> list[F1Session]:
    statement = select(F1Session).join(Race).where(Race.season == season)
    sessions = list(session.exec(statement).all())
    return sessions


# def read_result_test(*, session: Session):
#     statement = (
#         select(Result)
#         .join(F1Session, Result.f1session_id == F1Session.id)
#         .join(Race, F1Session.race_id == Race.id)
#         .where(Race.season == 2025, Race.round == 11, F1Session.type == "Race", Result.position == 2)
#     )

#     result_10th = session.exec(statement).first()
#     print(result_10th.driver.first_name, result_10th.constructor.name)


# if __name__ == "__main__":
#     from app.db.session import get_session_local

#     with get_session_local() as session:
#         read_result_test(session=session)
