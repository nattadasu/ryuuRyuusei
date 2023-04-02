from modules.commons import *


async def getNatsuAniApi(id, platform: str) -> dict:
    """Get a relation between anime and other platform via Natsu's AniAPI"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://aniapi.nattadasu.my.id/{platform}/{id}') as resp:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
            await session.close()
            return jsonFinal
    except:
        aaDict = invAa
        return aaDict
