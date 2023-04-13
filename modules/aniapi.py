from json import loads as jlo

from aiohttp import ClientSession

from modules.const import invAa


async def getNatsuAniApi(id, platform: str) -> dict:
    """Get a relation between anime and other platform via Natsu's AniAPI"""
    try:
        async with ClientSession() as session:
            async with session.get(f'https://aniapi.nattadasu.my.id/{platform}/{id}') as resp:
                jsonText = await resp.text()
                jsonFinal = jlo(jsonText)
            await session.close()
            return jsonFinal
    except:
        aaDict = invAa
        return aaDict
