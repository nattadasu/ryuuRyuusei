"""
Allow migrates database/database.csv to new schema when there's any db changes
"""

from pathlib import Path
from classes.database import UserDatabase
# from modules.oobe.commons import prepare_database
# import pandas as pd
from modules.const import DATABASE_PATH


async def migrate():
    old_path = Path(DATABASE_PATH)
    async with UserDatabase() as db:
        users = await db.get_all_users()

    # rename old database to database.csv.old
    old_path.rename(old_path.with_suffix('.old'))

    # create new database
    async with UserDatabase() as db:
        for user in users:
            await db.save_to_database(user)
