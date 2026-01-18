import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class F1Client:
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

    def race_results(self, season: int, round: int) -> dict:
        result = self.get(f"{season}/{round}/results.json")
        return result["MRData"]["RaceTable"]["Races"][0]

    def all_races_in_season(self, season: int) -> dict:
        result = self.get(f"{season}.json")
        race_list = result["MRData"]["RaceTable"]["Races"]
        return race_list[0]

    def race_name_from_round(self, season: int, round: int) -> dict:
        result = self.get(f"{season}/{round}/circuits.json")
        circuit_info = result["MRData"]["CircuitTable"]["Circuits"][0]
        return {
            "circuitId": circuit_info["circuitId"],
            "circuitName": circuit_info["circuitName"],
        }


if __name__ == "__main__":
    client = F1Client()
    # print(client.race_results(2026, 1))
    # print(client.race_name_from_round(2026, 20))
    print(client.all_circuits_in_season(2026))
