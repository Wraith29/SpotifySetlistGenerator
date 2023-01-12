__all__ = ["SpotifyApi"]

import json
import requests

from .track import Track
from .api_utils import generate_qstr


class SpotifyApi:
    """Constructor takes no params"""
    token: str
    id: str

    def __init__(self) -> None:
        self.base_url = "https://api.spotify.com/v1/"

    def make_get_request(
        self,
        url: str,
        data: dict[str, str] = None
    ) -> dict[str, str]:  # Returns the `response.json()`
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        if data is None:
            response = requests.get(
                url, headers=headers
            )
        else:
            response = requests.get(
                url, headers=headers, data=json.dumps(data)
            )

        return response.json()

    def make_post_request(
        self,
        url: str,
        data: dict[str, str] = None
    ) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        if data is None:
            response = requests.post(
                url, headers=headers
            )
        else:
            response = requests.post(
                url, headers=headers, data=json.dumps(data)
            )

        return response.json()

    def set_token(self, token: str) -> None:
        self.token = token

        self.id = self.get_user_id()

    def get_user_id(self) -> str:
        url = self.base_url + "me"

        response = self.make_get_request(url)

        return response["id"]

    def search_artist(self, name: str) -> dict[str, str | int]:
        url = self.base_url + "search" + generate_qstr({
            "type": "artist",
            "q": name
        })

        response = self.make_get_request(url)

        return response["artists"]["items"][0]

    def artist_album_ids(self, artist_id: str) -> list[str]:
        url = self.base_url + f"artists/{artist_id}/albums"

        response = self.make_get_request(url)

        albums = []
        for album in response["items"]:
            albums.append(album["id"])

        return albums

    def album_get_tracks(self, album_id: str) -> list[Track]:
        url = self.base_url + f"albums/{album_id}/tracks"

        response = self.make_get_request(url)

        tracks = []
        for track in response["items"]:
            tracks.append(Track(track["id"], track["name"]))

        return tracks

    def playlist_create(self, band_name: str, tour_name: str) -> str:
        url = self.base_url + f"users/{self.id}/playlists"

        response = self.make_post_request(url, {
            "name": f"{band_name}: {tour_name}",
            "public": True
        })

        return response["id"]

    def playlist_add_tracks(self, pl_id: str, tracks: list[Track]) -> None:
        url = self.base_url + f"playlists/{pl_id}/tracks"

        uris = ','.join([f"spotify:track:{track.id}" for track in tracks])

        self.make_post_request(url + generate_qstr({"uris": uris}))