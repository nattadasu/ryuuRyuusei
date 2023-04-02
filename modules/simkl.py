from modules.commons import *
from modules.const import *


async def searchSimklId(title_id: str, platform: str, media_type: str = None) -> int:
    """Search SIMKL title ID  from other platforms"""
    url = f'https://api.simkl.com/search/id/?{platform}={title_id}'
    if media_type is not None:
        url += f'&type={media_type}'
    url += f"&client_id={SIMKL_CLIENT_ID}"
    try:
        async with aiohttp.ClientSession() as sSession:
            async with sSession.get(url) as sResp:
                idFound = await sResp.json()
                fin = idFound[0]['ids']['simkl']
            await sSession.close()
            return fin
    except:
        return 0


async def getSimklID(simkl_id: int, media_type: str) -> dict:
    """Get external IDs provided by SIMKL"""
    try:
        if simkl_id == 0:
            raise Exception('Simkl ID is 0')
        else:
            async with aiohttp.ClientSession() as gSession:
                async with gSession.get(f'https://api.simkl.com/{media_type}/{simkl_id}?client_id={SIMKL_CLIENT_ID}&extended=full') as gResp:
                    animeFound = await gResp.json()
                    data = animeFound['ids']
                    # Null safe result, if any of the key is not found, it will be replaced with None
                    data = {
                        "title": animeFound.get('title', None),
                        "simkl": data.get('simkl', None),
                        "slug": data.get('slug', None),
                        "poster": animeFound.get('poster', None),
                        "fanart": animeFound.get('fanart', None),
                        "aniType": animeFound.get('anime_type', None),
                        "type": animeFound.get('type', None),
                        "allcin": data.get('allcin', None),
                        "anfo": data.get('anfo', None),
                        "ann": data.get('ann', None),
                        "imdb": data.get('imdb', None),
                        "mal": data.get('mal', None),
                        "offjp": data.get('offjp', None),
                        "tmdb": data.get('tmdb', None),
                        "tvdb": data.get('tvdb', None),
                        "tvdbslug": data.get('tvdbslug', None),
                        "wikien": data.get('wikien', None),
                        "wikijp": data.get('wikijp', None),
                    }
                await gSession.close()
                return data
    except:
        return simkl0rels
