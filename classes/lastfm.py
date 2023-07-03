"""LastFM API wrapper"""

from dataclasses import dataclass
from json import loads
from typing import Any, Literal

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError
from modules.const import LASTFM_API_KEY, USER_AGENT


@dataclass
class LastFMImageStruct:
    """LastFM Image dataclass"""

    size: Literal["small", "medium", "large", "extralarge"] | None
    """Image size"""
    url: str
    """Image URL"""


@dataclass
class LastFMReleaseStruct:
    """LastFM Release dataclass"""

    name: str
    """Release name"""
    mbid: str
    """Release MusicBrainz ID"""


@dataclass
class LastFMDateStruct:
    """LastFM Date dataclass"""

    epoch: int | None
    """Date in epoch format"""
    text: str | None
    """Date in text format"""


@dataclass
class LastFMTrackStruct:
    """LastFM Track dataclass"""

    artist: LastFMReleaseStruct | list[LastFMReleaseStruct] | None
    """Track artist"""
    streamable: Literal["0", "1"] | None
    """Is the track streamable"""
    image: LastFMImageStruct | list[LastFMImageStruct] | None
    """Track image"""
    mbid: str
    """Track MusicBrainz ID"""
    album: LastFMReleaseStruct | list[LastFMReleaseStruct] | None
    """Track album"""
    name: str
    """Track name"""
    url: str
    """Track URL"""
    nowplaying: bool
    """Is the track currently playing"""
    date: LastFMDateStruct | None
    """Scrobble date"""


@dataclass
class LastFMUserStruct:
    """LastFM User dataclass"""

    name: str
    """User name"""
    age: str
    """User age"""
    subscriber: bool | None
    """Is the user a subscriber"""
    realname: str | None
    """User real name"""
    bootstrap: str
    """User bootstrap"""
    playcount: str
    """User playcount"""
    artist_count: str
    """User artist count"""
    playlists: str
    """User playlists"""
    track_count: str
    """User track count"""
    album_count: str
    """User album count"""
    image: list[LastFMImageStruct] | None
    """User image"""
    registered: LastFMDateStruct | None
    """User registration date"""
    country: str | None
    """User country"""
    gender: str | None
    """User gender"""
    url: str
    """User URL"""
    type: str
    """User type"""


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

    @staticmethod
    def track_dict_to_dataclass(data: dict[str, Any]) -> LastFMTrackStruct:
        """
        Convert track dict to dataclass

        Args:
            data (dict[str, Any]): Track dict

        Returns:
            LastFMTrackStruct: Track dataclass
        """
        if data["image"]:
            for image in data["image"]:
                data["image"][data["image"].index(image)] = LastFMImageStruct(
                    image["size"], image["#text"]
                )
        data["artist"] = (
            LastFMReleaseStruct(
                data["artist"]["#text"],
                data["artist"]["mbid"]) if data["artist"] else None)
        data["album"] = (
            LastFMReleaseStruct(data["album"]["#text"], data["album"]["mbid"])
            if data["album"]
            else None
        )
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

    @staticmethod
    def user_dict_to_dataclass(data: dict[str, Any]) -> LastFMUserStruct:
        """
        Convert user dict to dataclass

        Args:
            data (dict[str, Any]): User dict

        Returns:
            LastFMUserStruct: User dataclass
        """
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
        """
        Get user info

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
                    "User can not be found on Last.fm. Check the name or register?", 404)
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Last.fm API returned {resp.status}. Reason: {resp.text()}", resp.status, )
            json_text = await resp.text()
            json_final = loads(json_text)
            udb = json_final["user"]
        udb = self.user_dict_to_dataclass(udb)
        return udb

    async def get_user_recent_tracks(
        self, username: str, maximum: int = 9
    ) -> list[LastFMTrackStruct]:
        """
        Get recent tracks

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
            json_text = await resp.text()
            match resp.status:
                case 403:
                    raise ProviderHttpError(
                        "Either user's profile or recent track history set to private",
                        403)
                case 404:
                    raise ProviderHttpError(
                        "User can not be found on Last.fm. Check the name or register?",
                        404)
                case _:
                    if resp.status != 200:
                        raise ProviderHttpError(
                            f"Last.fm API returned {resp.status}. Reason: {json_text}",
                            resp.status)
            json_final = loads(json_text)
            scb = json_final["recenttracks"]["track"]
            scb = [self.track_dict_to_dataclass(data=track) for track in scb]
        if len(scb) > maximum:
            scb = scb[:maximum]
        return scb
