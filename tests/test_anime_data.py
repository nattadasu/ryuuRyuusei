import os
import sys
import unittest
from interactions import Embed

try:
    from classes.anilist import AniList
    from classes.animeapi import AnimeApi
    from classes.jikan import JikanApi
    from classes.kitsu import Kitsu
    from classes.myanimelist import MyAnimeList
    from modules.commons import generate_trailer
    from modules.myanimelist import generate_mal
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.anilist import AniList
    from classes.animeapi import AnimeApi
    from classes.jikan import JikanApi
    from classes.kitsu import Kitsu
    from classes.myanimelist import MyAnimeList
    from modules.commons import generate_trailer
    from modules.myanimelist import generate_mal

async def do_anime(ani_id: int, nsfwBool: bool = False) -> Embed:
    alData = {}
    trailer = None
    async with AnimeApi() as aniapi:
        aniApi = await aniapi.get_relation(
            media_id=ani_id, platform=aniapi.AnimeApiPlatforms.MYANIMELIST
        )
    if aniApi["anilist"] is not None:
        async with AniList() as al:
            alData = await al.anime(media_id=aniApi["anilist"])
        if (alData["trailer"] is not None) and (
            alData["trailer"]["site"] == "youtube"
        ):
            trailer = generate_trailer(data=alData["trailer"], is_mal=False)
            trailer = [trailer]
        else:
            trailer = []
    dcEm = await generate_mal(
        ani_id, code="en_US", is_nsfw=nsfwBool, al_dict=alData, anime_api=aniApi
    )
    return dcEm

class AnimeShowcaseTest(unittest.IsolatedAsyncioTestCase):
    async def test_anime_info(self):
        ani_id = 1
        dcEm = await do_anime(ani_id)
        self.assertTrue(dcEm is not None)

    async def test_anime_info_nsfw(self):
        ani_id = 6893
        dcEm = await do_anime(ani_id, True)
        self.assertTrue(dcEm is not None)

    async def test_search_anime_on_anilist(self):
        async with AniList() as al:
            alData = await al.search_media("Naruto", 1, al.MediaType.ANIME)
        self.assertTrue(alData is not None)

    async def test_search_anime_on_myanimelist(self):
        async with MyAnimeList() as mal:
            malData = await mal.search("Naruto", 1)
        self.assertTrue(malData is not None)

    async def test_fetch_anime_from_kitsu(self):
        ktData = await Kitsu().get_anime(1)
        self.assertTrue(ktData is not None)

    async def test_fetch_anime_from_anilist(self):
        async with AniList() as al:
            alData = await al.anime(1)
        self.assertTrue(alData is not None)


if __name__ == "__main__":
    unittest.main()
