import os
import sys
import unittest

try:
    from classes.lastfm import LastFM
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.lastfm import LastFM


class LastFmTest(unittest.IsolatedAsyncioTestCase):
    """LastFM API test class"""
    async def test_get_user_info(self):
        """Test getting user info"""
        async with LastFM() as lastfm:
            user = await lastfm.get_user_info("nattadasu")
            # check if user is not None
            self.assertIsNotNone(user)

    async def test_get_user_recent_tracks(self):
        """Test getting user recent tracks"""
        async with LastFM() as lastfm:
            user = await lastfm.get_user_recent_tracks("nattadasu", 1)
            # check if user is not None
            self.assertIsNotNone(user)


if __name__ == "__main__":
    unittest.main(verbosity=2)
