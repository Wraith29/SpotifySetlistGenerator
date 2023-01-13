import datetime
import json
import requests

from dotenv import load_dotenv, get_key
from flask import Flask, Blueprint, render_template, redirect, request

from setlist.api_utils import generate_qstr
from setlist.music_brainz import MusicBrainzApi
from setlist.setlist import SetlistApi
from setlist.spotify import SpotifyApi
from setlist.state import State
from setlist.track import Track

bp = Blueprint("main", __name__)
sp_api = SpotifyApi()


def filter_setlists(
    setlists: list[dict[str, str | int]]
) -> list[dict[str, str | int]]:
    def date_from_string(date: str) -> datetime.date:
        values = date.split("-", 3)
        return datetime.date(int(values[2]), int(values[1]), int(values[0]))

    setlists = sorted(
        setlists,
        key=lambda setlist: date_from_string(setlist["eventDate"]),
        reverse=True
    )

    idx = 0
    tour_name = None

    while tour_name is None:
        if idx >= len(setlists):
            raise ValueError("Artist has no recent tour, or no tour name.")

        if "tour" not in setlists[idx].keys():
            idx += 1
            continue

        tour_name = setlists[idx]["tour"]["name"]

    tours = []
    for setlist in setlists:
        if "tour" not in setlist.keys():
            continue
        if "name" not in setlist["tour"].keys():
            continue

        if setlist["tour"]["name"] == tour_name:
            tours.append(setlist)

    return tours


def get_setlist_tracks(setlists: list[dict[str, str]]) -> list[str]:
    tracks = []
    for tour in setlists:
        for album in tour["sets"]["set"]:
            for track in album["song"]:
                tracks.append(track["name"])

    return set(tracks)


def filter_tracks(sl_tracks: list[str], tracks: list[Track]) -> list[Track]:
    result = []
    incl = []

    for track in tracks:
        if track.name in sl_tracks and track.name not in incl:
            result.append(track)
            incl.append(track.name)

    return result


def generate_playlist() -> str:
    sl_api_key = get_key(".env", "SETLIST_API_KEY")
    sl_api = SetlistApi(sl_api_key)

    mb_api = MusicBrainzApi()
    artist_id = mb_api.artist_search_by_name(State.artist_name)["id"]

    setlists = sl_api.get_setlists(artist_id)

    try:
        setlist_info = filter_setlists(setlists)
    except ValueError as ve:
        raise ve

    tour_name = None
    idx = 0

    while tour_name is None:
        if "tour" not in setlist_info[idx].keys():
            idx += 1
            continue
        if "name" not in setlist_info[idx]["tour"].keys():
            idx += 1
            continue
        tour_name = setlist_info[idx]["tour"]["name"]

    setlist_tracks = get_setlist_tracks(setlist_info)

    artist_info = sp_api.search_artist(State.artist_name)

    artist_id = artist_info["id"]

    playlist_id = sp_api.playlist_create(State.artist_name, tour_name)

    album_ids = sp_api.artist_album_ids(artist_id)
    artist_tracks = []

    for album_id in album_ids:
        for track in sp_api.album_get_tracks(album_id):
            artist_tracks.append(track)

    artist_tracks = set(artist_tracks)

    tracks = filter_tracks(setlist_tracks, artist_tracks)

    sp_api.playlist_add_tracks(playlist_id, tracks)

    return f"https://open.spotify.com/playlist/{playlist_id}"


@bp.get("/")
def index_view() -> str:
    return render_template("home.html")


@bp.get("/login")
def login_view() -> str:
    State.artist_name = request.args["artistName"]
    port = get_key(".env", "PORT")
    sp_cid = get_key(".env", "SPOTIFY_CLIENT_ID")

    state = "ThisShouldProbablyBeRandom"
    scope = "user-read-private " \
            "user-read-email " \
            "playlist-modify-public " \
            "playlist-modify-private"

    query = generate_qstr({
        "response_type": "code",
        "client_id": sp_cid,
        "scope": scope,
        "redirect_uri": f"http://localhost:{port}/auth",
        "state": state
    })

    url = f"https://accounts.spotify.com/authorize{query}"

    return redirect(url)


@bp.get("/auth")
def auth_view() -> str:
    port = get_key(".env", "PORT")
    sp_cid = get_key(".env", "SPOTIFY_CLIENT_ID")
    sp_secret = get_key(".env", "SPOTIFY_CLIENT_SECRET")

    code = request.args["code"]

    res = requests.post("https://accounts.spotify.com/api/token", data={
        "code": code,
        "redirect_uri": f"http://localhost:{port}/auth",
        "grant_type": "authorization_code",
        "client_id": sp_cid,
        "client_secret": sp_secret
    }, json=True)

    sp_api.set_token(res.json()["access_token"])
    try:
        playlist_id = generate_playlist()
        return render_template("created.html", id=playlist_id)
    except ValueError as ve:
        return render_template("error.html", msg=ve.args[0])


def main() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(bp)

    return app


if __name__ == "__main__":
    load_dotenv()
    port = int(get_key(".env", "PORT"))
    app = main()

    raise SystemExit(app.run(port=port))
