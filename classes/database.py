import json

import pandas as pd

from modules.const import CLUB_ID, EMOJI_UNEXPECTED_ERROR, database
from modules.jikan import check_club_membership


class UserDatabase:
    def __init__(self, database_path: str = database):
        """Initialize the database

        Args:
            database_path (str, optional): Path to the database. Defaults to database.
        """
        self.database_path = database_path

    async def __aenter__(self):
        """Async context manager entry point"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit point"""
        await self.close()

    async def close(self):
        """Close the database"""

    async def check_if_registered(self, discord_id: int) -> bool:
        """Check if user is registered on Database

        Args:
            discord_id (int): Discord ID of the user

        Returns:
            bool: True if user is registered, False if not
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        val = False
        if str(discord_id) in df["discordId"].values:
            val = True
        return val

    async def save_to_database(
        self,
        discord_id: int,
        discord_username: str,
        discord_joined: int,
        mal_username: str,
        mal_id: int,
        mal_joined: int,
        registered_at: int,
        registered_guild: int,
        registered_by: int,
        guild_name: str,
    ):
        """Save information regarding to user with their consent

        Args:
            discord_id (int): Discord ID of the user
            discord_username (str): Discord username of the user
            discord_joined (int): Discord join date of the user in Epoch
            mal_username (str): MAL username of the user
            mal_id (int): MAL ID of the user
            mal_joined (int): MAL join date of the user in Epoch
            registered_at (int): Date when the user registered in Epoch
            registered_guild (int): Guild ID where the user registered
            registered_by (int): User ID who registered the user
            guild_name (str): Guild name where the user registered
        """
        data = {
            "discordId": str(discord_id),
            "discordUsername": discord_username,
            "discordJoined": str(discord_joined),
            "malUsername": mal_username,
            "malId": str(mal_id),
            "malJoined": str(mal_joined),
            "registeredAt": str(registered_at),
            "registeredGuild": str(registered_guild),
            "registeredBy": str(registered_by),
            "guildName": guild_name,
        }
        df = pd.DataFrame(data, index=[0])
        df.to_csv(
            self.database_path,
            sep="\t",
            index=False,
            header=not self._database_exists(),
            mode="a",
        )

    async def drop_user(self, discord_id: int) -> bool:
        """Drop a user from the database

        Args:
            discord_id (int): Discord ID of the user

        Returns:
            bool: True if user is dropped, False if not
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        df.drop(df[df["discordId"] == str(discord_id)].index, inplace=True)
        df.to_csv(self.database_path, sep="\t", index=False)
        return True

    async def verify_user(self, discord_id: int) -> bool:
        """Verify a user on the database

        Args:
            discord_id (int): Discord ID of the user

        Returns:
            bool: True if user is verified, False if not
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        row = df[df["discordId"] == str(discord_id)]
        if row.empty:
            raise DatabaseException(
                f"{EMOJI_UNEXPECTED_ERROR} User may not be registered to the bot, or there's unknown error"
            )

        username = row.iloc[0]["malUsername"]
        clubs = await check_club_membership(username)
        verified = False
        for club in clubs:
            if str(club["mal_id"]) == str(CLUB_ID):
                verified = True
                break
        else:
            raise DatabaseException(
                f"{EMOJI_UNEXPECTED_ERROR} User is not a member of the club"
            )
        return verified

    async def export_user_data(self, user_id: int) -> str:
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        row = df[df["discordId"] == str(user_id)]
        if row.empty:
            raise DatabaseException(
                f"{EMOJI_UNEXPECTED_ERROR} User may not be registered to the bot, or there's unknown error"
            )
        data = row.to_dict(orient="records")[0]
        for key, value in data.items():
            if value.isdigit():
                data[key] = int(value)
            elif value.lower() == "true":
                data[key] = True
            elif value.lower() == "false":
                data[key] = False
            elif value.lower() == "null":
                data[key] = None
            else:
                data[key] = str(value)
        return json.dumps(data)

    def _database_exists(self):
        try:
            pd.read_csv(self.database_path, sep="\t", dtype=str, nrows=0)
        except pd.errors.EmptyDataError:
            return False
        else:
            return

    __all__ = [
        "check_if_registered",
        "save_to_database",
        "drop_user",
        "verify_user",
        "export_user_data",
        "close",
    ]


class DatabaseException(Exception):
    pass


__all__ = ["UserDatabase", "DatabaseException"]
