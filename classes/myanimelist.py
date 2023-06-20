"""MyAnimeList Asynchronous API Wrapper Class"""

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import MYANIMELIST_CLIENT_ID, USER_AGENT


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

    def __init__(
            self,
            client_id: str = MYANIMELIST_CLIENT_ID,
            nsfw: bool = False):
        """
        Initialize the MyAnimeList Asynchronous API Wrapper

        Args:
            client_id (str): Your MyAnimeList Client ID, default to MYANIMELIST_CLIENT_ID
            nsfw (bool, optional): Whether to include NSFW content in the search results or not. Defaults to False.
        """
        if client_id is None:
            raise ProviderHttpError(
                "Unauthorized, please fill Client ID before using this module", 401)
        self.client_id = client_id
        self.base_url = "https://api.myanimelist.net/v2"
        self.headers = {
            "X-MAL-CLIENT-ID": self.client_id,
            "User-Agent": USER_AGENT}
        self.nsfw = nsfw
        self.session = None

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager"""
        await self.close()

    async def close(self) -> None:
        """Close the aiohttp session"""
        await self.session.close()

    async def anime(self, anime_id: int, fields: str | None = None) -> dict:
        """
        Get anime information by its ID

        Args:
            anime_id (int): The anime ID
            fields (str | None, optional): The fields to return. Defaults to None.

        Returns:
            dict: Anime data
        """
        params = {}
        if fields:
            params["fields"] = fields
        if self.nsfw:
            params["nsfw"] = "true"
        async with self.session.get(
            f"{self.base_url}/anime/{anime_id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int | None = None,
        fields: str | None = None,
    ):
        """
        Search anime by its title

        Args:
            query (str): The query to search
            limit (int, optional): The number of results to return. Defaults to 10.
            offset (int | None, optional): The offset of the results. Defaults to None.
            fields (str | None, optional): The fields to return. Defaults to None.

        Returns:
            dict: Search results
        """
        if limit > 100:
            raise ProviderTypeError(
                "limit must be less than or equal to 100", "int")
        params = {"q": query, "limit": limit}
        if offset:
            params["offset"] = offset
        if fields:
            params["fields"] = fields
        async with self.session.get(
            f"{self.base_url}/anime", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)


__all__ = ["MyAnimeList"]
