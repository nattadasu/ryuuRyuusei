import os
import sys
import unittest
from asyncio import sleep
from datetime import datetime, timezone
from typing import Any, Coroutine

from interactions import Snowflake

try:
    from classes.database import UserDatabase, UserDatabaseClass
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.database import UserDatabase, UserDatabaseClass


class DatabaseTest(unittest.IsolatedAsyncioTestCase):
    """Database test class"""

    async def test_save_data(self):
        """Test saving data"""
        tmp = datetime.now(tz=timezone.utc)
        async with UserDatabase() as ud:
            resp = await ud.save_to_database(
                UserDatabaseClass(
                    discord_id=Snowflake(1234567890),
                    discord_username="nattadasu",
                    mal_id=1234,
                    mal_joined=tmp,
                    mal_username="nattadasu",
                    registered_at=tmp,
                    registered_guild_id=Snowflake(1234567890),
                    registered_by=Snowflake(1234567890),
                )
            )
        self.assertTrue(resp is None)

    async def test_checking(self):
        """Test checking if registered"""
        async with UserDatabase() as ud:
            resp = await ud.check_if_registered(Snowflake(1234567890))
        self.assertTrue(resp is not None)

    async def test_verifying(self):
        """Test verifying user"""
        async with UserDatabase() as ud:
            try:
                await ud.verify_user(Snowflake(1234567890))
                resp = True
            except BaseException:
                resp = False
        self.assertTrue(resp is not None)

    async def test_export_data(self):
        """Test exporting user data"""
        async with UserDatabase() as ud:
            resp = await ud.export_user_data(1234567890)
        self.assertTrue(resp is not None)

    async def test_remove_data(self):
        """Test removing user data"""

        async def doit() -> bool:
            """Do the thing, very helpful"""
            drop = await ud.drop_user(Snowflake(1234567890))
            return drop

        async with UserDatabase() as ud:
            resp = await doit()
        if resp is False:
            await sleep(5)
            resp = await doit()
        self.assertTrue(resp is True)

    async def asyncTearDown(self) -> Coroutine[Any, Any, None]:
        """Tear down the test"""
        await sleep(2)
        return await super().asyncTearDown()


if __name__ == "__main__":
    # tell unittest to do it step-by-step
    unittest.main(verbosity=2)
