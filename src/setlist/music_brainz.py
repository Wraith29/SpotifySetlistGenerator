__all__ = ["MusicBrainzApi"]

import requests


class MusicBrainzApi:
    def __init__(self) -> None:
        self.user_agent_string = "SetlistPlaylistGenerator/1.0.0" \
                                 "(i.acnaylor@gmail.com)"

    def query(self, args: dict[str, str | int]) -> str:
        return "query=" + " AND ".join(
            [f"{k}:{v}" for k, v in args.items()]
        )

    def artist_search_by_name(self, name: str) -> dict[str, str | int]:
        url = "http://musicbrainz.org/ws/2/artist/?"
        query = self.query({"artist": name})

        response = requests.get(url + query, headers={
            "Accept": "application/json",
            "User-Agent": self.user_agent_string
        })

        items = response.json()

        return items["artists"][0]
