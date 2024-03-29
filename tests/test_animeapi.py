import os
import sys
import unittest
from datetime import datetime

try:
    from classes.animeapi import AnimeApi, AnimeApiAnime
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.animeapi import AnimeApi, AnimeApiAnime


class AnimeApiTest(unittest.IsolatedAsyncioTestCase):
    """Anime API test class"""

    async def test_animeapi(self):
        """Test Anime API"""
        async with AnimeApi() as aa:
            resp = await aa.get_relation(
                media_id=1, platform=aa.AnimeApiPlatforms.MYANIMELIST
            )
        self.assertTrue(isinstance(resp, AnimeApiAnime))

    async def test_latest_update(self):
        """Test checking latest update"""
        async with AnimeApi() as aa:
            resp = await aa.get_update_time()
        self.assertTrue(isinstance(resp, datetime))


if __name__ == "__main__":
    unittest.main(verbosity=2)
