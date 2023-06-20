import os
import sys
import unittest

try:
    from classes.isitdownrightnow import WebsiteChecker, WebsiteStatus
except ImportError:
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.isitdownrightnow import WebsiteChecker, WebsiteStatus


class IsItDownRightNowTest(unittest.IsolatedAsyncioTestCase):
    """IsItDownRightNow test class"""

    async def test_check_website(self):
        """Test checking a website"""
        async with WebsiteChecker() as checker:
            status = await checker.check_website("https://myanimelist.net")
            self.assertIsInstance(status, WebsiteStatus)


if __name__ == "__main__":
    unittest.main(verbosity=2)
