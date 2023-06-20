import os
import sys
import unittest

try:
    from classes.odesli import Odesli, OdesliResponse
except ImportError:
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.odesli import Odesli, OdesliResponse


class OdesliTest(unittest.IsolatedAsyncioTestCase):
    """Odesli test class"""

    async def test_get_song_links(self):
        """Test getting song links"""
        async with Odesli() as odesli:
            links = await odesli.get_links(
                url="https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
            )
            self.assertIsInstance(links, OdesliResponse)

    async def test_get_album_links(self):
        """Test getting album links"""
        async with Odesli() as odesli:
            links = await odesli.get_links(
                url="https://open.spotify.com/album/6QPkyl04rXwTGlGlcYaRoW"
            )
            self.assertIsInstance(links, OdesliResponse)


if __name__ == "__main__":
    unittest.main(verbosity=2)
