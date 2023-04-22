"""MyAnimeList Asynchronous API Wrapper Class"""

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError


class MyAnimeList:
    """MyAnimeList Asynchronous API Wrapper

    Parameters
    ----------
    client_id: str
        Your MyAnimeList Client ID
    nsfw: bool
        Whether to include NSFW content in the search results or not

    Functions
    ---------
    anime(anime_id: int, fields: str | None = None)
        Get anime information by its ID
    search(query: str, limit: int = 10, offset: int | None = None, fields: str | None = None)
        Search anime by its title
    """

    def __init__(self, client_id, nsfw: bool = False):
        self.client_id = client_id
        if client_id is None:
            raise ProviderHttpError(
                "Unauthorized, please fill Client ID before using this module", 401)
        self.base_url = "https://api.myanimelist.net/v2"
        self.headers = {"X-MAL-CLIENT-ID": self.client_id}
        self.nsfw = nsfw
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def anime(self, anime_id: int, fields: str | None = None):
        """Get anime information by its ID"""
        params = {}
        if fields:
            params["fields"] = fields
        if self.nsfw:
            params["nsfw"] = "true"
        async with self.session.get(f"{self.base_url}/anime/{anime_id}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def search(self, query: str, limit: int = 10, offset: int | None = None, fields: str | None = None):
        """Search anime by its title"""
        if limit > 100:
            raise ProviderTypeError(
                "limit must be less than or equal to 100", "int")
        params = {"q": query, "limit": limit}
        if offset:
            params["offset"] = offset
        if fields:
            params["fields"] = fields
        async with self.session.get(f"{self.base_url}/anime", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)


__all__ = ["MyAnimeList"]
