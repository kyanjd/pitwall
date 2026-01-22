import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class F1DataClient:
    BASE_URL = "https://api.jolpi.ca/ergast/f1"

    def __init__(self, timeout: int = 10, total_retries: int = 3, backoff_factor: float = 0.5):
        self.timeout = timeout
        self.total_retries = total_retries
        self.backoff_factor = backoff_factor
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        retry = Retry(
            total=self.total_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("https://", adapter)
        return session

    def get(self, url: str) -> dict:
        try:
            url = f"{self.BASE_URL}/{url.lstrip('/')}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return {}

    def race_results_in_round(self, season: int, round: int) -> dict:
        result = self.get(f"{season}/{round}/results.json")
        return result["MRData"]

    def all_races_in_season(self, season: int) -> list:
        # Allows fetching circuits before races are complete
        result = self.get(f"{season}.json")
        race_list = result["MRData"]["RaceTable"]["Races"]
        return race_list

    def all_drivers_in_season(self, season: int) -> list:
        result = self.get(f"{season}/drivers.json")
        driver_list = result["MRData"]["DriverTable"]["Drivers"]
        return driver_list

    def all_constructors_in_season(self, season: int) -> list:
        result = self.get(f"{season}/constructors.json")
        constructor_list = result["MRData"]["ConstructorTable"]["Constructors"]
        return constructor_list

    def all_results_in_season(self, season: int) -> list:
        result = self.get(f"{season}/results.json")
        result_list = result["MRData"]
        return result_list


if __name__ == "__main__":
    pass
    # from app.db.session import engine  # your SQLAlchemy engine
    # from sqlmodel import SQLModel, text

    # SQLModel.metadata.drop_all(engine)
    # with engine.begin() as conn:
    #     conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    client = F1DataClient()
    print(client.race_results_in_round(2025, 1))
