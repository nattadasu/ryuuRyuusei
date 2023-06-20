import os
import sys
import unittest

try:
    from classes.shikimori import Shikimori, ShikimoriUserStruct
except ImportError:
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.shikimori import Shikimori, ShikimoriUserStruct


class ShikimoriTest(unittest.IsolatedAsyncioTestCase):
    """Test the Shikimori class"""

    async def test_get_user(self):
        """Test getting user from Shikimori"""
        async with Shikimori() as shiki:
            user = await shiki.get_user("nattadasu", is_nickname=True)
        self.assertIsInstance(user, ShikimoriUserStruct)


if __name__ == "__main__":
    unittest.main(verbosity=2)
