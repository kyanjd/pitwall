from app import crud
from app.db.session import get_session_local
from app.models.f1 import Circuit, Constructor, Driver
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

    def ingest_drivers_for_season(self, season: int):
        drivers = self.client.all_drivers_in_season(season)

        for driver_data in drivers:
            driver_model = Driver(
                first_name=driver_data["givenName"],
                last_name=driver_data["familyName"],
                constructor_id=None,
                constructor=None,
                results=[],
            )
            # crud.f1.upsert_driver(session=self.session, driver=driver_model)

        self.session.commit()

    def ingest_constructors_for_season(self, season: int):
        constructors = self.client.all_constructors_in_season(season)

        for constructor_data in constructors:
            constructor_model = Constructor(
                external_id=constructor_data["constructorId"],
                name=constructor_data["name"],
                nationality=constructor_data["nationality"],
            )
            # crud.f1.upsert_constructor(session=self.session, constructor=constructor_model)

        self.session.commit()


if __name__ == "__main__":
    with get_session_local() as session:
        ingestor = Ingestor(session=session)
        ingestor.ingest_circuits_for_season(2025)
