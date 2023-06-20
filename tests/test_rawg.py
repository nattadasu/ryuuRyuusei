import os
import sys
import unittest

try:
    from classes.rawg import RawgApi, RawgGameData
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.rawg import RawgApi, RawgGameData


class RawgTest(unittest.IsolatedAsyncioTestCase):
    """Rawg API test class"""

    async def test_search_game(self):
        """Test searching"""
        async with RawgApi() as rawg:
            res = await rawg.search("The Witcher 3")
            self.assertIsInstance(res, list)

    async def test_get_game_info(self):
        """Test getting game info"""
        async with RawgApi() as rawg:
            res: RawgGameData = await rawg.get_data(slug="genshin-impact")
            self.assertIsInstance(res, RawgGameData)


if __name__ == "__main__":
    unittest.main(verbosity=2)
