import os
import sys
import unittest

try:
    from classes.anilist import AniList
except ImportError:
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.anilist import AniList


class AniListTest(unittest.IsolatedAsyncioTestCase):
    """AniList test class"""

    async def test_anime_sfw(self):
        """Test anime if it's SFW"""
        async with AniList() as al:
            data = await al.nsfw_check(media_id=1, media_type="ANIME")
        self.assertFalse(data)

    async def test_manga_nsfw(self):
        """Test manga if it's NSFW"""
        async with AniList() as al:
            data = await al.nsfw_check(media_id=106166, media_type=al.MediaType.MANGA)
        self.assertTrue(data)

    async def test_fetch_anime(self):
        """Test fetching anime"""
        async with AniList() as al:
            alData = await al.anime(1)
        self.assertTrue(alData is not None)

    async def test_fetch_manga(self):
        """Test fetching manga"""
        async with AniList() as al:
            alData = await al.manga(106166)
        self.assertTrue(alData is not None)

    async def test_fetch_user(self):
        """Test fetching user"""
        async with AniList() as al:
            alData = await al.user("nattadasu")
        self.assertTrue(alData is not None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
