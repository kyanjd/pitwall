import time
import uuid
from datetime import datetime

from app import crud
from app.db.session import get_session_local
from app.models.f1 import Circuit, Constructor, Driver, F1Session, Race, Result
from app.schema.f1 import F1SessionType
from app.services.f1 import F1DataClient
from sqlmodel import Session


class Ingestor:
    def __init__(self, session: Session):
        self.client = F1DataClient()
        self.session = session

    def ingest_circuit_api(self, circuit_data: dict) -> Circuit:
        circuit_model = Circuit(
            external_id=circuit_data["circuitId"],
            name=circuit_data["circuitName"],
            locality=circuit_data["Location"]["locality"],
            country=circuit_data["Location"]["country"],
        )
        circuit_db = crud.f1.upsert_circuit(session=self.session, circuit=circuit_model)
        return circuit_db

    def ingest_race_api(self, race_data: dict, season: int, circuit_id: uuid.UUID) -> Race:
        race_model = Race(
            name=race_data["raceName"],
            circuit_id=circuit_id,
            round=int(race_data["round"]),
            season=season,
        )
        race_db = crud.f1.upsert_race(session=self.session, race=race_model)
        return race_db

    def ingest_f1session_api(
        self, f1session_data: dict, race_id: uuid.UUID, f1session_type: F1SessionType
    ) -> F1Session:
        f1session_model = F1Session(
            race_id=race_id,
            type=f1session_type,
            date=self.to_datetime(f1session_data["date"], f1session_data["time"]),
        )
        f1session_db = crud.f1.upsert_f1session(session=self.session, f1session=f1session_model)
        return f1session_db

    def ingest_driver_api(self, driver_data: dict) -> Driver:
        driver_model = Driver(
            external_id=driver_data["driverId"],
            code=driver_data["code"],
            first_name=driver_data["givenName"],
            last_name=driver_data["familyName"],
        )
        driver_db = crud.f1.upsert_driver(session=self.session, driver=driver_model)
        return driver_db

    def ingest_constructor_api(self, constructor_data: dict) -> Constructor:
        constructor_model = Constructor(
            external_id=constructor_data["constructorId"],
            name=constructor_data["name"],
            nationality=constructor_data["nationality"],
        )
        constructor_db = crud.f1.upsert_constructor(session=self.session, constructor=constructor_model)
        return constructor_db

    def ingest_result_api(
        self, result_data: dict, driver_id: uuid.UUID, f1session_id: uuid.UUID, constructor_id: uuid.UUID
    ) -> Result:
        result_model = Result(
            driver_id=driver_id,
            f1session_id=f1session_id,
            constructor_id=constructor_id,
            position=int(result_data["position"]),
            position_text=result_data.get("positionText"),
            status=result_data.get("status"),
            grid=result_data.get("grid"),
            laps=int(result_data["laps"]) if result_data.get("laps") is not None else None,
        )
        result_db = crud.f1.upsert_result(session=self.session, result=result_model)
        return result_db

    def ingest(self, season: int, f1session_type: F1SessionType = F1SessionType.RACE):
        start = time.time()

        if f1session_type == F1SessionType.RACE:
            races = self.client.all_races_in_season(season)
        elif f1session_type == F1SessionType.QUALIFYING:
            races = self.client.all_qualifying_in_season(season)

        for race in races:
            try:
                circuit_db = self.ingest_circuit_api(race["Circuit"])
                race_db = self.ingest_race_api(race, season, circuit_db.id)
                f1session_db = self.ingest_f1session_api(race, race_db.id, f1session_type)

                results = race[f1session_type.api_results_key]
                for result in results:
                    driver_db = self.ingest_driver_api(result["Driver"])
                    constructor_db = self.ingest_constructor_api(result["Constructor"])

                    _ = self.ingest_result_api(
                        result,
                        driver_id=driver_db.id,
                        f1session_id=f1session_db.id,
                        constructor_id=constructor_db.id,
                    )

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
