import time
from datetime import datetime

from app import crud
from app.db.session import get_session_local
from app.models.f1 import Circuit, Constructor, Driver, F1Session, Race, Result
from app.services.f1 import F1DataClient
from sqlmodel import Session


class Ingestor:
    def __init__(self, session: Session):
        self.client = F1DataClient()
        self.session = session

    def ingest_circuits_for_season(self, season: int):
        races = self.client.all_races_in_season(season)

        for race in races:
            circuit_data = race["Circuit"]
            circuit_model = Circuit(
                external_id=circuit_data["circuitId"],
                name=circuit_data["circuitName"],
                locality=circuit_data["Location"]["locality"],
                country=circuit_data["Location"]["country"],
            )
            crud.f1.upsert_circuit(session=self.session, circuit=circuit_model)

        self.session.commit()

    def ingest(self, season: int):
        start = time.time()
        races = self.client.all_races_in_season(season)

        for race in races:
            try:
                circuit = race["Circuit"]
                circuit_model = Circuit(
                    external_id=circuit["circuitId"],
                    name=circuit["circuitName"],
                    locality=circuit["Location"]["locality"],
                    country=circuit["Location"]["country"],
                )
                circuit_db = crud.f1.upsert_circuit(session=self.session, circuit=circuit_model)

                race_model = Race(
                    name=race["raceName"],
                    circuit_id=circuit_db.id,  # To be set after circuit upsert
                    round=int(race["round"]),
                    season=season,
                )
                race_db = crud.f1.upsert_race(session=self.session, race=race_model)

                f1session_model = F1Session(
                    race_id=race_db.id,
                    type="Race",
                    date=self.to_datetime(race["date"], race["time"]),
                )
                f1session_db = crud.f1.upsert_f1session(session=self.session, f1session=f1session_model)

                results = race["Results"]
                for result in results:
                    driver = result["Driver"]
                    driver_model = Driver(
                        external_id=driver["driverId"],
                        code=driver["code"],
                        first_name=driver["givenName"],
                        last_name=driver["familyName"],
                    )
                    driver_db = crud.f1.upsert_driver(session=self.session, driver=driver_model)

                    constructor = result["Constructor"]
                    constructor_model = Constructor(
                        external_id=constructor["constructorId"],
                        name=constructor["name"],
                        nationality=constructor["nationality"],
                    )
                    constructor_db = crud.f1.upsert_constructor(session=self.session, constructor=constructor_model)

                    result_model = Result(
                        driver_id=driver_db.id,
                        f1session_id=f1session_db.id,
                        constructor_id=constructor_db.id,
                        position=int(result["position"]),
                        position_text=result["positionText"],
                        status=result["status"],
                        grid=result["grid"],
                        laps=int(result["laps"]),
                    )

                    crud.f1.upsert_result(session=self.session, result=result_model)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                print(f"Error ingesting race {race['raceName']}: {e}")

        print(time.time() - start)

    def to_datetime(self, date_str: str, time_str: str) -> datetime:
        dt = datetime.fromisoformat(f"{date_str}T{time_str.replace('Z', '+00:00')}")
        return dt


if __name__ == "__main__":
    with get_session_local() as session:
        ingestor = Ingestor(session=session)
        ingestor.ingest(2025)
