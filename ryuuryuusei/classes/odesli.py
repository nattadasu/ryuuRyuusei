from dataclasses import dataclass
from typing import Literal

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import USER_AGENT

platforms = Literal[
    "amazonMusic",
    "amazonStore",
    "anghami",
    "appleMusic",
    "audiomack",
    "audius",
    "boomplay",
    "deezer",
    "google",
    "googleStore",
    "itunes",
    "napster",
    "pandora",
    "soundcloud",
    "spinrilla",
    "spotify",
    "tidal",
    "yandex",
    "youtube",
    "youtubeMusic",
]
"""Platforms supported on Odesli/Songlink"""

apiProviders = Literal[
    "amazon",
    "anghami",
    "audiomack",
    "audius",
    "boomplay",
    "deezer",
    "google",
    "itunes",
    "napster",
    "pandora",
    "soundcloud",
    "spinrilla",
    "spotify",
    "tidal",
    "yandex",
    "youtube",
]
"""API providers supported on Odesli/Songlink"""


@dataclass
class PlatformLink:
    """
    A Platform will exist here only if there is a match found. E.g. if there
    is no YouTube match found, then neither `youtube` or `youtubeMusic`
    properties will exist here
    """

    entityUniqueId: str
    """
    The unique ID for this entity. Use it to look up data about this entity
    at `entitiesByUniqueId[entityUniqueId]
    """

    country: str
    """The country code for this match"""

    url: str
    """The URL for this match"""

    nativeAppUriMobile: str | None = None
    """
    The native app URI that can be used on mobile devices to open this
    entity directly in the native app
    """

    nativeAppUriDesktop: str | None = None
    """
    The native app URI that can be used on desktop devices to open this
    entity directly in the native app
    """


@dataclass
class EntityUnique:
    """Data for a single entity"""

    id: str
    """
    This is the unique identifier on the streaming platform/API
    provider
    """

    type: Literal["song", "album"]

    title: str | None
    artistName: str | None
    thumbnailUrl: str | None
    thumbnailWidth: int | None
    thumbnailHeight: int | None

    apiProvider: apiProviders
    """
    The API provider that powered this match. Useful if you'd like to use
    this entity's data to query the API directly
    """

    platforms: list[platforms]
    """
    An array of platforms that are "powered" by this entity. E.g. an entity
    from Apple Music will generally have a `platforms` array of
    `["appleMusic", "itunes"]` since both those platforms/links are derived
    from this single entity
    """


@dataclass
class OdesliResponse:
    """Response from Odesli/Songlink API"""

    entityUniqueId: str
    """
    The unique ID for the input entity that was supplied in the request. The
    data for this entity, such as title, artistName, etc. will be found in
    an object at `nodesByUniqueId[entityUniqueId]`
    """

    userCountry: str
    """
    The userCountry query param that was supplied in the request. It signals
    the country/availability we use to query the streaming platforms. Defaults
    to 'US' if no userCountry supplied in the request.

    NOTE: As a fallback, our service may respond with matches that were found
    in a locale other than the userCountry supplied
    """

    pageUrl: str
    """A URL that will render the Songlink page for this entity"""

    linksByPlatform: dict[platforms, PlatformLink]
    """
    A collection of objects. Each key is a platform, and each value is an
    object that contains data for linking to the match
    """

    entitiesByUniqueId: dict[str, EntityUnique]


class Odesli:
    """Odesli/Songlink API wrapper"""

    def __init__(self) -> None:
        self.session = None
        self.headers = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.headers = {"User-Agent": USER_AGENT}
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the async context manager."""
        await self.close()

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()

    async def get_links(
        self,
        url: str | None = None,
        userCountry: str | None = "US",
        songIfSingle: bool = False,
        platform: platforms | None = None,
        stream_type: Literal["song", "album"] = "song",
        stream_id: str | None = None,
    ) -> OdesliResponse:
        """
        Fetch the matching links for a given streaming entity

        Args:
            url (str, optional): The URL of the streaming entity. Defaults to None.
            userCountry (str, optional): The country code to use for matching. Defaults to "US".
            songIfSingle (bool, optional): Whether to return a song link if the entity is a single. Defaults to False.
            platform (platforms, optional): The platform to return links for. If url is supplied, this is ignored. However, if url is not supplied, this is required. Defaults to None.
            stream_type (Literal["song", "album"], optional): The type of streaming entity. If url is supplied, this is ignored. However, if url is not supplied, this is required. Defaults to "song".
            stream_id (str, optional): The ID of the streaming entity. If url is supplied, this is ignored. However, if url is not supplied, this is required. Defaults to None.

        Raises:
            ProviderHttpError: If the request to Odesli/Songlink fails
            ProviderTypeError: If the parameters supplied are invalid or missing

        Returns:
            OdesliResponse: The response from Odesli/Songlink
        """
        if (not url) and (not platform or not stream_type or not stream_id):
            raise ProviderTypeError(
                "If url is not supplied, platform, stream_type and stream_id are required", [
                    platform, stream_type, stream_id], )

        params = {
            "url": url,
            "userCountry": userCountry,
            "songIfSingle": str(songIfSingle).lower(),
        }

        if not url:
            params["platform"] = platform
            params["type"] = stream_type
            params["id"] = stream_id
            del params["url"]

        async with self.session.get(
            "https://api.song.link/v1-alpha.1/links",
            params=params,
            headers=self.headers,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)

            data = await resp.json()

            for k, v in data["linksByPlatform"].items():
                data["linksByPlatform"][k] = PlatformLink(**v)

            for k, v in data["entitiesByUniqueId"].items():
                data["entitiesByUniqueId"][k] = EntityUnique(**v)

            return OdesliResponse(
                entityUniqueId=data["entityUniqueId"],
                userCountry=data["userCountry"],
                pageUrl=data["pageUrl"],
                linksByPlatform=data["linksByPlatform"],
                entitiesByUniqueId=data["entitiesByUniqueId"],
            )
