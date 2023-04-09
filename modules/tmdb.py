from modules.commons import *
from modules.const import *


async def tmdb_getNsfwStatus(id: int, mediaType: str = "tv") -> bool:
    if mediaType == "tv":
        url = f"https://api.themoviedb.org/3/tv/{id}?api_key={TMDB_API_KEY}&language=en-US"
    elif mediaType == "movies":
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=en-US"
    else:
        raise ValueError("Invalid mediaType")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            jsonText = await resp.text()
            jsonFinal = jload(jsonText)
        await session.close()
        return jsonFinal["adult"]
