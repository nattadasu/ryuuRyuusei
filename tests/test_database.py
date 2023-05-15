import os
import sys
import unittest
from time import time

from interactions import Snowflake

try:
    from classes.database import UserDatabase, UserDatabaseClass
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.database import UserDatabase, UserDatabaseClass


class DatabaseTest(unittest.IsolatedAsyncioTestCase):
    async def test_save_data(self):
        tmp = int(time())
        async with UserDatabase() as ud:
            resp = await ud.save_to_database(
                UserDatabaseClass(
                    discord_id=Snowflake(1234567890),
                    mal_id=1234,
                    mal_joined=tmp,
                    mal_username="nattadasu",
                    registered_at=tmp,
                    registered_guild=Snowflake(1234567890),
                    registered_by=Snowflake(1234567890),
                )
            )
        self.assertTrue(resp is None)

    async def test_checking(self):
        async with UserDatabase() as ud:
            resp = await ud.check_if_registered(Snowflake(1234567890))
        self.assertTrue(resp is not None)

    async def test_verifying(self):
        async with UserDatabase() as ud:
            try:
                await ud.verify_user(Snowflake(1234567890))
                resp = True
            except:
                resp = False
        self.assertTrue(resp is not None)

    async def test_export_data(self):
        async with UserDatabase() as ud:
            resp = await ud.export_user_data(Snowflake(1234567890))
        self.assertTrue(resp is not None)

    async def test_remove_data(self):
        async def doit() -> bool:
            drop = await ud.drop_user(Snowflake(1234567890))
            return drop

        async with UserDatabase() as ud:
            resp = await doit()
        if resp is False:
            resp = await doit()
        self.assertTrue(resp is True)


if __name__ == "__main__":
    # tell unittest to do it step-by-step
    unittest.main(verbosity=2)
