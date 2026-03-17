from dataclasses import dataclass, field
from typing import Optional
from HttpClient import RiotHttpClient
from datetime import datetime

@dataclass
class RiotAccount:
    puuid: str
    game_name: str
    tag_line: str 
    region: str = "europe" 
    profile_icon_id: int = field(default=None)
    summoner_level: int = field(default=None)

    def __post_init__(self):
        """Walidacja po inicjalizacji."""
        if not self.puuid:
            raise ValueError("PUUID nie może być pusty")
        self.game_name = self.game_name.strip()
        self.tag_line = self.tag_line.strip().lstrip("#")

    @classmethod
    def from_riot_id(cls, client: RiotHttpClient, game_name: str, tag_line: str) -> "RiotAccount":
        data = client.get(f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}")
        return cls(
            puuid=data["puuid"],
            game_name=data["gameName"],
            tag_line=data["tagLine"],
        )
    
    @classmethod
    def from_puuid(cls, client: RiotHttpClient, puuid: str) -> "RiotAccount":
        data = client.get(f"/riot/account/v1/accounts/by-puuid/{puuid}")
        return cls(
            puuid=data["puuid"],
            game_name=data["gameName"],
            tag_line=data["tagLine"],
        )
    
    def get_summoner(self, client: RiotHttpClient) -> "RiotAccount":
        data = client.get(f"/lol/summoner/v4/summoners/by-puuid/{self.puuid}")
        self.summoner_level = data["summonerLevel"]
        self.profile_icon_id = data["profileIconId"]

    def get_match_history(self, client:RiotHttpClient, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, max_results: Optional[int] = None) -> list:
        PAGE_SIZE = 100
        all_matches = []
        offset = 0

        base_params = {}
        if start_date:
            base_params["startTime"] = int(start_date.timestamp())
        
        if end_date:
            base_params["endTime"] = int(end_date.timestamp())

        while True:
            if max_results is not None:
                remaining = max_results - len(all_matches)
                if remaining <= 0:
                    break
                page_size = min(remaining, PAGE_SIZE)
            else:
                page_size = PAGE_SIZE  
            
            params ={**base_params, "start": offset, "count": page_size}
            page = client.get(f"/lol/match/v5/matches/by-puuid/{self.puuid}/ids", params=params)
            
            all_matches.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
        return all_matches



if __name__ == "__main__":
    global_client = RiotHttpClient(region="europe")   # do kont Riot
    regional_client = RiotHttpClient(region="eun1")   # do danych LoL
    account = RiotAccount.from_riot_id(global_client, "Ulenidas", "4661")

    match_history = account.get_match_history(global_client, start_date=datetime(2026, 3, 1), end_date=datetime(2026, 3, 16))
    print(match_history)