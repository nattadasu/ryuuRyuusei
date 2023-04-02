from modules.commons import *


async def getKitsuMetadata(id, media: str = "anime") -> dict:
    """Get anime metadata from Kitsu"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://kitsu.io/api/edge/{media}/{id}') as resp:
            jsonText = await resp.text()
            jsonFinal = jload(jsonText)
        await session.close()
        return jsonFinal
