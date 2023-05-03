import os
import sys
import unittest
from time import time

try:
    from classes.database import UserDatabase
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.database import UserDatabase


class DatabaseTest(unittest.IsolatedAsyncioTestCase):
    async def test_save_data(self):
        tmp = int(time())
        async with UserDatabase() as ud:
            resp = await ud.save_to_database(
                1234567890,
                "test_user",
                tmp,
                "test123",
                1234,
                tmp,
                tmp,
                9876543210,
                1234567890,
                "Test Guild",
            )
        self.assertTrue(resp is None)

    async def test_checking(self):
        async with UserDatabase() as ud:
            resp = await ud.check_if_registered(1234567890)
        self.assertTrue(resp is not None)

    async def test_verifying(self):
        async with UserDatabase() as ud:
            try:
                await ud.verify_user(1234567890)
                resp = True
            except:
                resp = False
        self.assertTrue(resp is not None)

    async def test_export_data(self):
        async with UserDatabase() as ud:
            resp = await ud.export_user_data(1234567890)
        self.assertTrue(resp is not None)

    async def test_remove_data(self):
        async with UserDatabase() as ud:
            resp = await ud.drop_user(1234567890)
        self.assertTrue(resp is not None)


if __name__ == "__main__":
    unittest.main()
