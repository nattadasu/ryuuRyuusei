import asyncio
import json
import os
import time
import traceback

from aiohttp import ClientSession

from modules.const import USER_AGENT


class JikanException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"JikanException [{self.status_code}]: {self.message}"


def defineJikanException(error_code: int, error_message: str | dict) -> JikanException:
    try:
        match error_code:
            case 403:
                em = "**Jikan unable to reach MyAnimeList at the moment**\nPlease try again in 3 seconds."
            case 404:
                em = "**I couldn't find the query on MAL**\nCheck the spelling or well, maybe they don't exist? 🤔"
            case 408:
                em = "**Jikan had a timeout while fetching the data**\nPlease try again in 3 seconds."
            case 429:
                em = "**I have been rate-limited by Jikan**\nAny queries related to MyAnimeList may not available "
            case 500:
                em = "**Uh, it seems Jikan had a bad day, and this specific endpoint might broken**\nYou could help dev team to resolve this issue"
                if isinstance(error_message, dict) and "report_url" in error_message:
                    em += f" by clicking [this link to directly submit a GitHub Issue]({error_message['report_url']})"
                else:
                    em += f"\nFull message:```\n{error_message}\n```"
            case 503:
                em = "**I think Jikan is dead, server can't be reached** :/"
            case _:
                em = f"HTTP error code: {error_code}\n```\n{error_message}\n```"
    except Exception:
        em = "Unknown error. Full traceback:\n" + traceback.format_exc()

    raise JikanException(em, error_code)


class JikanApi:
    """Jikan API wrapper"""

    def __init__(self):
        self.cache_directory = "cache/jikan"
        self.cache_expiration_time = 86400
        self.base_url = "https://api.jikan.moe/v4"
        self.session = None
        self.user_agent = ""

    async def __aenter__(self):
        """Enter the session"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the session"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close()

    async def get_user_clubs(self, username: str) -> list[dict]:
        """Get user joined clubs

        Args:
            username (str): MyAnimeList username

        Returns:
            list[dict]: List of clubs
        """
        try:
            async with self.session.get(
                f"{self.base_url}/users/{username}/clubs"
            ) as resp:
                if resp.status in [200, 304]:
                    resp_data: dict = await resp.json()
                else:
                    defineJikanException(resp.status, resp.reason)
            clubs: list = resp_data["data"]
            paging: int = resp_data["pagination"]["last_visible_page"]
            if paging > 1:
                for i in range(2, paging + 1):
                    params = {"page": i}
                    async with self.session.get(
                        f"{self.base_url}/users/{username}/clubs", params=params
                    ) as resp:
                        if resp.status in [200, 304]:
                            clubs.extend(resp["data"])
                            await asyncio.sleep(2)
                        else:
                            defineJikanException(resp.status, resp.reason)
            return clubs
        except Exception as e:
            defineJikanException(e)

    async def get_user_data(self, username: str) -> dict:
        """Get user data

        Args:
            username (str): MyAnimeList username

        Actions:
            If Jikan took too long to respond, it will try again in multiples of 3 seconds for exponential backoff

        Returns:
            dict: User data
        """
        self.cache_expiration_time = 43200
        cache_file_path = self.get_cache_file_path(f"user/{username}.json")
        cached_file = self.read_cached_data(cache_file_path)
        if cached_file:
            return cached_file

        retries = 0
        while retries < 3:
            try:
                async with self.session.get(
                    f"{self.base_url}/users/{username}/full"
                ) as resp:
                    if resp.status in [200, 304]:
                        res = await resp.json()
                        res: dict = res["data"]
                    else:
                        raise Exception(await resp.json())
                self.write_data_to_cache(res, cache_file_path)
                return res
            except Exception as e:
                retries += 1
                if retries == 3:
                    errcode: int = e.status_code if hasattr(e, "status_code") else 500
                    errmsg: str | dict = e.message if hasattr(e, "message") else e
                    defineJikanException(errcode, errmsg)
                else:
                    backoff_time = 3**retries
                    await asyncio.sleep(backoff_time)

    async def get_anime_data(self, anime_id: int) -> dict:
        """Get anime data

        Args:
            anime_id (int): MyAnimeList anime ID

        Returns:
            dict: Anime data
        """
        cache_file_path = self.get_cache_file_path(f"anime/{anime_id}.json")
        cached_file = self.read_cached_data(cache_file_path)
        if cached_file:
            return cached_file
        try:
            async with self.session.get(
                f"{self.base_url}/anime/{anime_id}/full"
            ) as resp:
                if resp.status in [200, 304]:
                    res = await resp.json()
                    res = res["data"]
                else:
                    raise Exception(await resp.text())
            self.write_data_to_cache(res, cache_file_path)
            return res
        except Exception as e:
            errcode: int = e.status_code if hasattr(e, "status_code") else 500
            errmsg: str | dict = e.message if hasattr(e, "message") else e
            defineJikanException(errcode, errmsg)

    def get_cache_file_path(self, cache_file_name: str) -> str:
        """Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> dict | None:
        """Read cached data

        Args:
            cache_file_name (str): Cache file name

        Returns:
            dict: Cached data
            None: If cache file does not exist
        """
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as cache_file:
                cache_data = json.load(cache_file)
                cache_age = time.time() - cache_data["timestamp"]
                if cache_age < self.cache_expiration_time:
                    return cache_data["data"]
        return None

    @staticmethod
    def write_data_to_cache(data, cache_file_path: str):
        """Write data to cache

        Args:
            data (any): Data to write
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)
