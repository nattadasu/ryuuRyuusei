import os
import sys
import unittest

try:
    from classes.spotify import SpotifyApi
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.spotify import SpotifyApi


class SpotifyTest(unittest.IsolatedAsyncioTestCase):
    """Spotify API test class"""

    async def test_authenticate(self):
        """Test authenticating client"""
        async with SpotifyApi() as spotify:
            await spotify.authorize_client()
            # check if token is not None
            self.assertIsNotNone(spotify.token)

    async def test_get_album(self):
        """Test getting album data"""
        async with SpotifyApi() as spotify:
            await spotify.authorize_client()
            album = await spotify.get_album("0sNOF9WDwhWunNAHPD3Baj")
            # check if album is not None
            self.assertIsNotNone(album)

    async def test_get_artist(self):
        """Test getting artist data"""
        async with SpotifyApi() as spotify:
            await spotify.authorize_client()
            artist = await spotify.get_artist("0OdUWJ0sBjDrqHygGUXeCF")
            # check if artist is not None
            self.assertIsNotNone(artist)

    async def test_get_track(self):
        """Test getting track data"""
        async with SpotifyApi() as spotify:
            await spotify.authorize_client()
            track = await spotify.get_track("3n3Ppam7vgaVa1iaRUc9Lp")
            # check if track is not None
            self.assertIsNotNone(track)

    async def test_search(self):
        """Test searching for a track"""
        async with SpotifyApi() as spotify:
            await spotify.authorize_client()
            search = await spotify.search(
                "Never Gonna Give You Up", spotify.MediaType.TRACK, 1, 0
            )
            # check if search is not None
            self.assertIsNotNone(search)


if __name__ == "__main__":
    unittest.main(verbosity=2)
