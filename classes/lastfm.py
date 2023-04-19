from enum import Enum
from json import loads

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import LASTFM_API_KEY


class LastFM:
    """LastFM API wrapper"""

    def __init__(self, api_key: str = LASTFM_API_KEY):
        self.api_key = api_key
        self.session = None
        self.base_url = "https://ws.audioscrobbler.com/2.0/"
        self.params = {
            "api_key": self.api_key,
            "format": "json",
        }

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    async def get_user_info(self, username: str):
        """Get user info"""
        params = {
            "method": "user.getinfo",
            "user": username,
        }
        params.update(self.params)
        async with self.session.get(self.base_url, params=params) as resp:
            if resp.status == 404:
                raise ProviderHttpError(
                    "User can not be found on Last.fm. Check the name or register?")
            else:
                jsonText = await resp.text()
                jsonFinal = loads(jsonText)
                ud = jsonFinal['user']
        return ud

    async def get_user_recent_tracks(self, username: str, maximum: int = 9):
        """Get recent tracks"""
        params = {
            "method": "user.getrecenttracks",
            "user": username,
            "limit": maximum,
        }
        params.update(self.params)
        async with self.session.get(self.base_url, params=params) as resp:
            jsonText = await resp.text()
            jsonFinal = loads(jsonText)
            scb = jsonFinal['recenttracks']['track']
        return scb