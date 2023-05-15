from json import loads
from dataclasses import dataclass
from typing import Literal, Any

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError
from modules.const import LASTFM_API_KEY, USER_AGENT


@dataclass
class LastFMImageStruct:
    """LastFM Image dataclass"""

    size: Literal["small", "medium", "large", "extralarge"] | str | None
    url: str

@dataclass
class LastFMReleaseStruct:
    """LastFM Release dataclass"""

    name: str
    mbid: str

@dataclass
class LastFMDateStruct:
    """LastFM Date dataclass"""

    epoch: int | None
    text: str | None

@dataclass
class LastFMTrackStruct:
    """LastFM Track dataclass"""

    artist: LastFMReleaseStruct | list[LastFMReleaseStruct] | None
    streamable: Literal["0", "1"] | None
    image: LastFMImageStruct | list[LastFMImageStruct] | None
    mbid: str
    album: LastFMReleaseStruct | list[LastFMReleaseStruct] | None
    name: str
    url: str
    nowplaying: bool
    date: LastFMDateStruct | None

@dataclass
class LastFMUserStruct:
    name: str
    age: str
    subscriber: bool | None
    realname: str | None
    bootstrap: str
    playcount: str
    artist_count: str
    playlists: str
    track_count: str
    album_count: str
    image: list[LastFMImageStruct] | None
    registered: LastFMDateStruct | None
    country: str | None
    gender: str | None
    url: str
    type: str

class LastFM:
    """LastFM API wrapper"""

    def __init__(self, api_key: str = LASTFM_API_KEY):
        """Initialize the Last.fm API Wrapper

        Args:
            api_key (str): Last.fm API key, defaults to LASTFM_API_KEY
        """
        self.api_key = api_key
        self.session = None
        self.base_url = "https://ws.audioscrobbler.com/2.0/"
        self.params = {
            "api_key": self.api_key,
            "format": "json",
        }

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager"""
        await self.close()

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()

    def track_dict_to_dataclass(self, data: dict[str, Any]) -> LastFMTrackStruct:
        """Convert track dict to dataclass"""
        if data["image"]:
            for image in data["image"]:
                data["image"][data["image"].index(image)] = LastFMImageStruct(
                    image["size"], image["#text"]
                )
        data["artist"] = LastFMReleaseStruct(
            data["artist"]["#text"], data["artist"]["mbid"]
        ) if data["artist"] else None
        data["album"] = LastFMReleaseStruct(
            data["album"]["#text"], data["album"]["mbid"]
        ) if data["album"] else None
        try:
            data["date"] = LastFMDateStruct(
                int(data["date"]["uts"]), data["date"]["#text"]
            )
        except KeyError:
            data["date"] = LastFMDateStruct(None, None)
        nowplaying = data["@attr"]["nowplaying"] == "true" if "@attr" in data else False
        data["nowplaying"] = nowplaying
        # drop @attr key if any
        if "@attr" in data:
            del data["@attr"]
        return LastFMTrackStruct(**data)


    def user_dict_to_dataclass(self, data: dict[str, Any]) -> LastFMUserStruct:
        """Convert user dict to dataclass"""
        if data["image"]:
            for image in data["image"]:
                data["image"][data["image"].index(image)] = LastFMImageStruct(
                    image["size"], image["#text"]
                )
        data["registered"] = LastFMDateStruct(
            int(data["registered"]["unixtime"]), data["registered"]["#text"]
        )
        data["subscriber"] = data["subscriber"] == "1"
        return LastFMUserStruct(**data)


    async def get_user_info(self, username: str) -> LastFMUserStruct:
        """Get user info

        Args:
            username (str): The username

        Returns:
            LastFMUserStruct: User data
        """
        params = {
            "method": "user.getinfo",
            "user": username,
        }
        params.update(self.params)
        async with self.session.get(self.base_url, params=params) as resp:
            if resp.status == 404:
                raise ProviderHttpError(
                    "User can not be found on Last.fm. Check the name or register?", 404
                )
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Last.fm API returned {resp.status}. Reason: {resp.text()}",
                    resp.status,
                )
            jsonText = await resp.text()
            jsonFinal = loads(jsonText)
            ud = jsonFinal["user"]
        ud = self.user_dict_to_dataclass(ud)
        return ud

    async def get_user_recent_tracks(
        self, username: str, maximum: int = 9
    ) -> list[LastFMTrackStruct]:
        """Get recent tracks

        Args:
            username (str): The username
            maximum (int, optional): The maximum number of tracks to fetch. Defaults to 9.

        Returns:
            list[LastFMTrackStruct]: List of tracks
        """
        if maximum == 0:
            return []
        params = {
            "method": "user.getrecenttracks",
            "user": username,
            "limit": maximum,
        }
        params.update(self.params)
        async with self.session.get(self.base_url, params=params) as resp:
            jsonText = await resp.text()
            if resp.status == 404:
                raise ProviderHttpError(
                    "User can not be found on Last.fm. Check the name or register?", 404
                )
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Last.fm API returned {resp.status}. Reason: {resp.text()}",
                    resp.status,
                )
            jsonFinal = loads(jsonText)
            scb = jsonFinal["recenttracks"]["track"]
            scb = [self.track_dict_to_dataclass(data=track) for track in scb]
        if len(scb) > maximum:
            scb = scb[:maximum]
        return scb
