import asyncio
import traceback

from jikanpy import AioJikan


class JikanException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"JikanException [{self.status_code}]: {self.message}"


def defineJikanException(errmsg: str) -> JikanException:
    e = str(errmsg).split("=")
    etype = 400
    try:
        etype = int(e[1].split(",")[0])
        errm = e[3].strip()
        if len(e) >= 4:
            for i in range(4, len(e)):
                errm += f"={e[i]}"
        if etype == 403:
            em = "**Jikan unable to reach MyAnimeList at the moment.**\nPlease try again in 3 seconds."
        elif etype == 404:
            em = "**I couldn't find the query on MAL.**\nCheck the spelling or well, maybe they don't exist? 🤔"
        elif etype == 408:
            em = "**Jikan had a timeout while fetching the data**\nPlease try again in 3 seconds."
        else:
            em = f"HTTP {etype}\n{errm}"
    except Exception:
        em = "Unknown error. Full traceback:\n" + traceback.format_exc()

    raise JikanException(em, etype)


class JikanApi:
    async def __aenter__(self):
        """Enter the session"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the session"""
        await self.close()

    async def close(self):
        """Close the session"""

    async def get_member_clubs(self, username: str) -> list[dict]:
        """Get member clubs

        Args:
            username (str): MyAnimeList username

        Returns:
            list[dict]: List of clubs
        """
        try:
            async with AioJikan() as jikan:
                res = await jikan.users(username=username, extension="clubs")
                data: list = res["data"]
                if res["pagination"]["last_visible_page"] > 1:
                    for i in range(2, res["pagination"]["last_visible_page"] + 1):
                        res = await jikan.users(
                            username=username,
                            extension="clubs",
                            page=i,
                        )
                        await asyncio.sleep(1)
                        data.extend(res["data"])
                return data
        except Exception as e:
            defineJikanException(e)

    async def get_user_data(self, username: str) -> dict:
        """Get user data

        Args:
            username (str): MyAnimeList username

        Returns:
            dict: User data
        """
        try:
            async with AioJikan() as jikan:
                res = await jikan.users(username=username, extension="full")
                return res["data"]
        except Exception as e:
            defineJikanException(e)

    async def get_anime_data(self, anime_id: int) -> dict:
        """Get anime data

        Args:
            anime_id (int): MyAnimeList anime ID

        Returns:
            dict: Anime data
        """
        try:
            async with AioJikan() as jikan:
                res = await jikan.anime(anime_id)
                return res
        except Exception as e:
            defineJikanException(e)
