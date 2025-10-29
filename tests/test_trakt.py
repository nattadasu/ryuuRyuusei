import os
import sys
import unittest

try:
    from classes.trakt import Trakt, TraktExtendedMovieStruct
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.trakt import Trakt, TraktExtendedMovieStruct


class TraktTest(unittest.IsolatedAsyncioTestCase):
    """Trakt API test class"""

    async def test_get_ids(self):
        """Test getting ids"""
        async with Trakt() as trakt:
            res = await trakt.lookup(media_id="tt1104001", platform=trakt.Platform.IMDB)
            if res.type == "movie":
                self.assertEqual(res.movie.ids.imdb, "tt1104001")
            elif res.type == "show":
                self.assertEqual(res.show.ids.imdb, "tt1104001")

    async def test_get_title_data(self):
        """Test getting title data"""
        async with Trakt() as trakt:
            res: TraktExtendedMovieStruct = await trakt.get_title_data(
                media_id=12601, media_type=trakt.MediaType.MOVIE
            )
            self.assertIsInstance(res, TraktExtendedMovieStruct)


if __name__ == "__main__":
    unittest.main(verbosity=2)
