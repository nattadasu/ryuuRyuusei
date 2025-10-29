import os
import sys
import unittest

try:
    from classes.html.myanimelist import HtmlMyAnimeList
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.html.myanimelist import HtmlMyAnimeList


class HtmlMyAnimeListTest(unittest.IsolatedAsyncioTestCase):
    """HtmlMyAnimeList test class"""

    async def test_get_user(self):
        """Test get user"""
        async with HtmlMyAnimeList() as hmal:
            data = await hmal.get_user("nattadasu")
            print(data)
        self.assertTrue(data is not None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
