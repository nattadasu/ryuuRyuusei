import unittest
import os
import sys

try:
    from classes.thecolorapi import TheColorApi
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.thecolorapi import TheColorApi


class TheColorApiTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_color(self):
        async with TheColorApi() as color:
            value = "000000"
            color = await color.color(hex=value)
            # check if color is not None
            self.assertTrue(color["hex"]["clean"] == value)


if __name__ == "__main__":
    unittest.main()
