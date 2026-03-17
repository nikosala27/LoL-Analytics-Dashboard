import os
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
        
        self.headers = {
            "X-Riot-Token": self.api_key
        }

    def get(self, endpoint: str):
        """
        Wysyła zapytanie GET do konkretnego endpointu Riot API.
        """
        url = f"{self.base_url}{endpoint}"
        
        # Wysłanie zapytania
        response = requests.get(url, headers=self.headers)
        
        # Sprawdzenie, czy zapytanie się powiodło (np. czy nie ma błędu 403 lub 404)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Błąd {response.status_code}: {response.text}")
            return None

if __name__ == '__main__':
    client = RiotHttpClient()
    data = client.get('/riot/account/v1/accounts/by-riot-id/Ulenidas/4661')
    print(data)