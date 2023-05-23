import os
import sys
import unittest
from interactions import Snowflake

try:
    from classes.usrbg import UserBackgroundStruct, UserBackground
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.usrbg import UserBackgroundStruct, UserBackground


class UserBackgroundTest(unittest.IsolatedAsyncioTestCase):
    """UserBackground API test class"""

    async def test_get_background(self):
        """Test getting background"""
        async with UserBackground() as usrbg:
            res: UserBackgroundStruct = await usrbg.get_background(
                user_id=Snowflake(384089845527478272)
            )
            self.assertIsInstance(res, UserBackgroundStruct)


if __name__ == "__main__":
    unittest.main(verbosity=2)
