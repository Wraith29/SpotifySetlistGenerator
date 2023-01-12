__all__ = ["SetlistApi"]

import requests
from .api_utils import generate_qstr


class SetlistApi:
    def __init__(self, key: str) -> None:
        self.key = key

    def get_setlists(self, artist_id: str) -> list[dict[str, str | int]]:
        url = "https://api.setlist.fm/rest/1.0/search/setlists"
        query = generate_qstr({
            "artistMbid": artist_id,
            "countryCode": "GB",
            "page": 1,
        })

        response = requests.get(url + query, headers={
            "x-api-key": self.key,
            "Accept": "application/json"
        })

        return response.json()["setlist"]
