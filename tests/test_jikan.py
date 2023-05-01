import unittest
import os
import sys

try:
    from classes.jikan import JikanApi
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.jikan import JikanApi

class JikanTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_anime_data(self):
        async with JikanApi() as jikan:
            anime = await jikan.get_anime_data(1)
            self.assertIsNotNone(anime)

    async def test_get_user_data(self):
        async with JikanApi() as jikan:
            user = await jikan.get_user_data("nattadasu")
            self.assertIsNotNone(user)

    async def test_get_user_clubs(self):
        async with JikanApi() as jikan:
            clubs = await jikan.get_user_clubs("nattadasu")
            self.assertIsNotNone(clubs)

if __name__ == "__main__":
    unittest.main()