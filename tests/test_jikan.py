import os
import sys
import unittest

try:
    from classes.jikan import JikanApi
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.jikan import JikanApi


class JikanTest(unittest.IsolatedAsyncioTestCase):
    """Jikan API test class"""

    async def test_get_anime_data(self):
        """Test getting anime data"""
        async with JikanApi() as jikan:
            anime = await jikan.get_anime_data(1)
            self.assertIsNotNone(anime)

    async def test_get_user_data(self):
        """Test getting user data"""
        async with JikanApi() as jikan:
            user = await jikan.get_user_data("nattadasu")
            self.assertIsNotNone(user)

    async def test_get_user_clubs(self):
        """Test getting user clubs"""
        async with JikanApi() as jikan:
            clubs = await jikan.get_user_clubs("nattadasu")
            self.assertIsNotNone(clubs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
