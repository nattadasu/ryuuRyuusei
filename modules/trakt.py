from modules.commons import *

async def lookupTrakt(lookup_param: str) -> dict:
    """Lookup Trakt ID via IMDb ID or TMDB ID"""
    async with aiohttp.ClientSession(headers=traktHeader) as session:
        async with session.get(f'https://api.trakt.tv/search/{lookup_param}') as resp:
            trkRes = await resp.json()
        await session.close()
        try:
            return trkRes[0]
        except IndexError:
            raise KeyError


async def getTraktID(trakt_id: int, media_type: str = "show", extended: bool = False) -> dict:
    """Get external IDs provided by Trakt"""
    ext = "?extended=full" if extended is True else ""
    async with aiohttp.ClientSession(headers=traktHeader) as session:
        async with session.get(f'https://api.trakt.tv/{media_type}/{trakt_id}{ext}') as resp:
            trkRes = await resp.json()
        await session.close()
        return trkRes
