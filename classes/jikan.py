import traceback

from jikanpy import AioJikan


class JikanException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"JikanException [{self.status_code}]: {self.message}"


def defineJikanException(errmsg: str) -> JikanException:
    e = str(errmsg).split('=')
    etype = 400
    try:
        etype = int(e[1].split(',')[0])
        errm = e[3].strip()
        if len(e) >= 4:
            for i in range(4, len(e)):
                errm += f"={e[i]}"
        if etype == 403:
            em = f"**Jikan unable to reach MyAnimeList at the moment.**\nPlease try again in 3 seconds."
        elif etype == 404:
            em = f"**I couldn't find the query on MAL.**\nCheck the spelling or well, maybe they don't exist? 🤔"
        elif etype == 408:
            em = f"**Jikan had a timeout while fetching the data**\nPlease try again in 3 seconds."
        else:
            em = f"HTTP {etype}\n{errm}"
    except Exception as e:
        em = "Unknown error. Full traceback:\n" + traceback.format_exc()

    raise JikanException(em, etype)


class JikanApi:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await AioJikan().close()

    async def get_member_clubs(self, username: str) -> dict:
        try:
            res = await AioJikan().users(
                username=username,
                request='clubs',
            )
            return res['data']
        except Exception as e:
            defineJikanException(e)

    async def get_user_data(self, username: str) -> dict:
        try:
            res = await AioJikan().users(username=username, extension="full")
            return res['data']
        except Exception as e:
            defineJikanException(e)

    async def get_anime_data(self, anime_id: int) -> dict:
        try:
            res = await AioJikan().anime(anime_id)
            return res['data']
        except Exception as e:
            defineJikanException(e)
