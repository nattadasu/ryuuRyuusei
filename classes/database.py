import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import pandas as pd
from interactions.models import Snowflake

from modules.const import EMOJI_UNEXPECTED_ERROR, database
from modules.jikan import check_club_membership


@dataclass
class UserDatabaseClass:
    """User Database Class"""

    discord_id: Snowflake
    """User's Discord Snowflake ID"""
    discord_username: str
    """User's Discord username"""
    mal_id: int
    """User's MyAnimeList ID"""
    mal_joined: datetime
    """User's MyAnimeList join date"""
    registered_at: datetime
    """User's registration date"""
    registered_guild_id: Snowflake
    """Guild's Snowflake ID where the user registered"""
    registered_by: Snowflake
    """User's Snowflake ID who registered the user"""
    registered_guild_name: Optional[str] = None
    """Guild's name where the user registered"""
    anilist_id: Optional[int] = None
    """User's AniList ID"""
    anilist_username: Optional[str] = None
    """User's AniList username, as a fallback if ID is unreachable"""
    lastfm_username: Optional[int] = None
    """User's Last.fm username"""
    mal_username: Optional[str] = None
    """User's MyAnimeList username, as a fallback if ID is unreachable"""
    shikimori_id: Optional[int] = None
    """User's Shikimori ID"""
    shikimori_username: Optional[str] = None
    """User's Shikimori username, as a fallback if ID is unreachable"""


class UserDatabase:
    """User Database Wrapper"""

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

    async def check_if_registered(self, discord_id: Snowflake) -> bool:
        """
        Check if user is registered on Database

        Args:
            discord_id (Snowflake): Discord ID of the user

        Returns:
            bool: True if user is registered, False if not
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        val = False
        if str(discord_id) in df["discordId"].values:
            val = True
        return val

    async def save_to_database(self, user_data: UserDatabaseClass):
        """
        Save information regarding to user with their consent

        Args:
            user_data (UserDatabaseClass): Dataclass contains information about an user
        """
        data = {
            "discordId": user_data.discord_id,
            "discordUsername": user_data.discord_username,
            "discordJoined": user_data.discord_id.created_at.timestamp(),
            "malUsername": user_data.mal_username,
            "malId": user_data.mal_id,
            "malJoined": user_data.mal_joined.timestamp(),
            "registeredAt": user_data.registered_at.timestamp(),
            "registeredGuildId": user_data.registered_guild_id,
            "registeredBy": user_data.registered_by,
            "registeredGuildName": user_data.registered_guild_name,
            "anilistUsername": user_data.anilist_username,
            "anilistId": user_data.anilist_id,
            "lastfmUsername": user_data.lastfm_username,
            "shikimoriId": user_data.shikimori_id,
            "shikimoriUsername": user_data.shikimori_username,
        }
        for k, v in data.items():
            if isinstance(v, int):
                data[k] = str(v)
            elif isinstance(v, datetime):
                data[k] = str(int(v.timestamp()))
            elif isinstance(v, float):
                data[k] = str(int(v))
            elif v is None:
                data[k] = '""'
        df = pd.DataFrame(data, index=[0])
        df = df[data.keys()]
        df.to_csv(
            self.database_path,
            sep="\t",
            index=False,
            header=not self._database_exists(),
            mode="a",
        )

    async def update_user(
        self,
        discord_id: Snowflake,
        row: Literal[
            "anilistId",
            "anilistUsername",
            "lastfmUsername",
            "shikimoriId",
            "shikimoriUsername",
        ],
        modified_input: Any,
    ) -> bool:
        """
        Update information about a user that is not essential for the bot

        Args:
            discord_id (Snowflake): Discord ID of the user
            row (Literal["anilistId", "anilistUsername", "lastfmUsername", "shikimoriId", "shikimoriUsername"]): Row to be modified
            modified_input (Any): New value of the row

        Returns:
            bool: True if user is updated, False if not
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        df.loc[df["discordId"] == str(discord_id), row] = modified_input
        df.to_csv(self.database_path, sep="\t", index=False)
        return True

    async def drop_user(self, discord_id: Snowflake) -> bool:
        """
        Drop a user from the database

        Args:
            discord_id (int): Discord ID of the user

        Returns:
            bool: True if user is dropped, False if not
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        df.drop(df[df["discordId"] == str(discord_id)].index, inplace=True)
        df.to_csv(self.database_path, sep="\t", index=False)
        # drop from member settings
        df2 = pd.read_csv("database/member.csv", sep="\t", dtype=str)
        df2.drop(df2[df2["discordId"] == str(discord_id)].index, inplace=True)
        df2.to_csv("database/member.csv", sep="\t", index=False)
        # verify if its success
        verify = await self.check_if_registered(discord_id)
        return not verify

    async def verify_user(self, discord_id: Snowflake) -> bool:
        """
        Verify a user on the database

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
        verified = await check_club_membership(username)
        return verified

    async def get_user_data(self, discord_id: Snowflake) -> UserDatabaseClass:
        """
        Get user data from the database. Similar to `export_user_data`, but with dataclass

        Args:
            discord_id (Snowflake): Discord ID of the user

        Returns:
            UserDatabaseClass: Dataclass contains information about an user
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        df.fillna("", inplace=True)
        row = df[df["discordId"] == str(discord_id)]
        if row.empty:
            raise DatabaseException(
                f"{EMOJI_UNEXPECTED_ERROR} User may not be registered to the bot, or there's unknown error"
            )
        data = row.to_dict(orient="records")[0]
        return UserDatabaseClass(
            discord_id=Snowflake(data["discordId"]),
            discord_username=data["discordUsername"],
            mal_id=int(data["malId"]),
            mal_username=data["malUsername"],
            mal_joined=datetime.fromtimestamp(
                int(data["malJoined"]), tz=timezone.utc),
            anilist_id=data["anilistId"] if data["anilistId"] else None,
            anilist_username=data["anilistUsername"]
            if data["anilistUsername"]
            else None,
            lastfm_username=data["lastfmUsername"] if data["lastfmUsername"] else None,
            registered_at=datetime.fromtimestamp(
                int(data["registeredAt"]), tz=timezone.utc
            ),
            registered_guild_id=Snowflake(data["registeredGuildId"]),
            registered_guild_name=data["registeredGuildName"],
            registered_by=Snowflake(data["registeredBy"]),
            shikimori_id=id(data["shikimoriId"]
                            ) if data["shikimoriId"] else None,
            shikimori_username=data["shikimoriUsername"]
            if data["shikimoriUsername"]
            else None,
        )

    async def export_user_data(self, discord_id: int) -> str:
        """
        Export user data as JSON

        Args:
            discord_id (int): Discord ID of the user

        Returns:
            str: JSON string of the user data
        """
        df = pd.read_csv(self.database_path, sep="\t", dtype=str)
        df.fillna("", inplace=True)
        row = df[df["discordId"] == str(discord_id)]
        if row.empty:
            raise DatabaseException(
                f"{EMOJI_UNEXPECTED_ERROR} User may not be registered to the bot, or there's unknown error"
            )
        data = row.to_dict(orient="records")[0]
        try:
            df2 = pd.read_csv("database/member.csv", sep="\t", dtype=str)
            df2.fillna("", inplace=True)
            row2 = df2[df2["discordId"] == str(discord_id)]
            data2 = row2.to_dict(orient="records")[0]
            data2.pop("discordId")
            data2 = {f"settings_{key}": value for key, value in data2.items()}
            data["has_user_settings"] = True
            data.update(data2)
        except IndexError:
            data["has_user_settings"] = False
        for key, value in data.items():
            value = str(value)
            if value.isdigit():
                data[key] = int(value)
            elif value.lower() == "true":
                data[key] = True
            elif value.lower() == "false":
                data[key] = False
            elif value.lower() in ["null", "", "None"]:
                data[key] = None
            else:
                data[key] = str(value)
        return json.dumps(data)

    def _database_exists(self) -> bool:
        """Check if database exists"""
        try:
            pd.read_csv(self.database_path, sep="\t", dtype=str, nrows=0)
        except pd.errors.EmptyDataError:
            return False
        else:
            return True

    __all__ = [
        "check_if_registered",
        "save_to_database",
        "drop_user",
        "verify_user",
        "export_user_data",
        "close",
    ]


class DatabaseException(Exception):
    """Exception raised for errors in the database."""


__all__ = ["UserDatabase", "DatabaseException"]
