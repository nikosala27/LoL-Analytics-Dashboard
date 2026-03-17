import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

class RiotHttpClient:
    def __init__(self, region="europe"):
        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            raise ValueError("Brak klucza API! Sprawdź plik .env.")
        self.region = region
        self.base_url = f"https://{self.region}.api.riotgames.com"
        self.session = self.__start_session()

    def __start_session(self):
        session = requests.Session()
        session.headers.update({
            "X-Riot-Token": self.api_key,
            "Content-Type": "application/json"
        })
        return session

    def __api_calls(self, response, *args, **kwargs):
        api_calls_left = response.headers.get("X-Method-Rate-Limit-Count").split(':')
        if int(api_calls_left[0]) == 59:
            print('Exceeded amount of requests. Sleeping')

if __name__ == '__main__':
    client = RiotHttpClient()
    url = client.base_url + '/riot/account/v1/accounts/by-riot-id/Ulenidas/4661'
    resp = client.session.get(url)
    print(resp.headers)