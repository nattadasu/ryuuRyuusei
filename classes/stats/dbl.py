"""
# Discord Bot List API Wrapper

A lite wrapper for the discordbotlist.com API.
"""

from dataclasses import dataclass
from datetime import datetime

import aiohttp
from dacite import Config, from_dict

from classes.excepts import ProviderHttpError
from modules.const import BOT_CLIENT_ID, DBL_API_TOKEN


@dataclass
class UserStruct:
    """Struct for user object"""

    user_id: str
    """The id of the user"""
    timestamp: datetime
    """The timestamp of upvote by the user"""
    username: str
    """The username of the user"""
    discriminator: str
    """The discriminator of the user"""
    avatar: str
    """The avatar hash of the user"""


@dataclass
class UpvoteStruct:
    """Struct for upvote object"""

    upvotes: list[UserStruct]
    """The user object of the upvote"""
    total: int
    """The total amount of upvotes in the last 12 hours"""


class DiscordBotList:
    """# Discord Bot List API Wrapper"""

    def __init__(
            self,
            token: str = DBL_API_TOKEN,
            bot_id: int = BOT_CLIENT_ID):
        """
        ## Discord Bot List API Wrapper

        Args:
            token (str, optional): Discord Bot List API token. Defaults to DBL_API_TOKEN.
            bot_id (int, optional): Bot's client ID. Defaults to BOT_CLIENT_ID.
        """
        self.token = token
        self.base_url = "https://discordbotlist.com/api/v1"
        self.session = None
        self.headers = None
        self.bot_id = bot_id

    async def __aenter__(self):
        """Enter async context"""
        self.session = aiohttp.ClientSession()
        self.headers = {"Authorization": self.token,
                        "Content-Type": "application/json"}
        return self

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        """Exit async context"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close() if self.session else None

    async def get_recent_upvotes(self) -> UpvoteStruct:
        """
        Get recent upvotes in past 12 hours

        Returns:
            UpvoteStruct: Upvote data
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        async with self.session.get(
            f"{self.base_url}/bots/{self.bot_id}/upvotes",
            headers=self.headers,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(f"{resp.reason}", resp.status)
            return from_dict(
                data_class=UpvoteStruct,
                data=await resp.json(),
                config=Config(
                    type_hooks={
                        datetime: lambda x: datetime.strptime(
                            x, "%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                )
            )

    async def post_bot_stats(
        self,
        guild_count: int | list[int],
        members: int | list[int] | None = None,
        voice_connections: int | list[int] | None = None,
    ) -> int:
        """
        Post bot stats to discordbotlist.com

        Args:
            guild_count (int | list[int]): Guild count or list of guild counts.
            shard_id (int, optional): Shard ID. Defaults to None.
            shard_count (int, optional): Shard count. Defaults to None.

        Returns:
            int: HTTP status code
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        if isinstance(guild_count, list):
            guild_count = sum(guild_count)

        payload = {"guilds": guild_count}
        if members:
            if isinstance(members, list):
                members = sum(members)
            payload["users"] = members

        if voice_connections:
            if isinstance(voice_connections, list):
                voice_connections = sum(voice_connections)
            payload["voice_connections"] = voice_connections

        async with self.session.post(
            f"{self.base_url}/bots/{self.bot_id}/stats",
            json=payload,
            headers=self.headers,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    f"discordbotlist.com returned HTTP status code {resp.status}",
                    resp.status,
                )
            return resp.status

    async def post_slash_commands(self, commands: list[dict[str, str | int]]) -> int:
        """
        Post slash commands to discordbotlist.com

        Args:
            commands (list[dict[str, str | int]]): List of slash command dictionaries.

        Returns:
            int: HTTP status code
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        async with self.session.post(
            f"{self.base_url}/bots/{self.bot_id}/commands",
            json=commands,
            headers=self.headers,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    f"discordbotlist.com returned HTTP status code {resp.status}",
                    resp.status,
                )
            return resp.status
