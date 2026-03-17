import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RiotHttpClient:
    RATE_LIMIT = 59  # max wywołań zanim zaczniemy czekać
    RETRY_AFTER_DEFAULT = 10  # sekundy oczekiwania przy 429

    def __init__(self, region: str = "europe"):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("Brak klucza API! Sprawdź plik .env.")
        self.region = region
        self.base_url = f"https://{self.region}.api.riotgames.com"
        self.session = self._start_session()

    def _start_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "X-Riot-Token": self.api_key,
            "Content-Type": "application/json",
        })
        session.hooks["response"].append(self._handle_rate_limit)
        return session

    def _handle_rate_limit(self, response: requests.Response, *args, **kwargs):
        """Hook podpięty do sesji — sprawdza rate limit po każdej odpowiedzi."""
        rate_limit_count = response.headers.get("X-Method-Rate-Limit-Count")
        if rate_limit_count:
            try:
                used, limit = map(int, rate_limit_count.split(":"))
                logger.info(f"Rate limit: {used}/{limit}")
                if used >= self.RATE_LIMIT:
                    wait = int(response.headers.get("Retry-After", self.RETRY_AFTER_DEFAULT))
                    logger.warning(f"Zbliżamy się do limitu zapytań. Czekam {wait}s...")
                    time.sleep(wait)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Nie udało się sparsować nagłówka rate limit: {e}")

    def get(self, endpoint: str, params: dict = None) -> dict:
        """Wykonuje GET request i zwraca JSON. Obsługuje błędy HTTP i 429."""
        url = self.base_url + endpoint
        try:
            response = self.session.get(url, params=params)

            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", self.RETRY_AFTER_DEFAULT))
                logger.warning(f"429 Too Many Requests. Czekam {wait}s i ponawiam...")
                time.sleep(wait)
                response = self.session.get(url, params=params)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Błąd HTTP {response.status_code}: {e}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error("Błąd połączenia z API Riot.")
            raise
        except requests.exceptions.Timeout:
            logger.error("Przekroczono czas oczekiwania na odpowiedź.")
            raise


if __name__ == "__main__":
    client = RiotHttpClient()
    for i in range(1, 100):
        data = client.get("/riot/account/v1/accounts/by-riot-id/Ulenidas/4661")
        print(data)
        