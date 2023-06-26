"""Test MyAnimeListRss class"""

import os
import sys
import unittest

try:
    from classes.rss.myanimelist import MyAnimeListRss, ProviderHttpError
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.rss.myanimelist import MyAnimeListRss, ProviderHttpError


class MyAnimeListRssTest(unittest.IsolatedAsyncioTestCase):
    """MyAnimeListRss test class"""

    async def test_get_user(self):
        """Test get user"""
        async with MyAnimeListRss("anime", False) as malr:
            data = await malr.get_user("nattadasu")
        # confirm that the data is list of RssItem
        self.assertTrue(isinstance(data, list))

    async def test_get_user_with_invalid_username(self):
        """Test get user with invalid username"""
        try:
            async with MyAnimeListRss("anime", False) as malr:
                await malr.get_user("removed-user")
        except ProviderHttpError as error:
            # confirm that the exception is raised
            self.assertTrue(isinstance(error, ProviderHttpError))

    async def test_get_user_with_fetch_individual(self):
        """Test get user with fetch_individual"""
        async with MyAnimeListRss("anime", True) as malr:
            data = await malr.get_user("nattadasu")
        # confirm that the data is list of RssItem
        self.assertTrue(isinstance(data, list))


if __name__ == "__main__":
    unittest.main(verbosity=2)
