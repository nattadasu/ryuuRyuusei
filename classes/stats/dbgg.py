"""
# Discord Bots API Wrapper

A lite wrapper for the discord.bots.gg API.
"""

from dataclasses import dataclass
from datetime import datetime

import aiohttp
from dacite import Config, from_dict

from classes.excepts import ProviderHttpError
from modules.const import BOT_CLIENT_ID, DBGG_API_TOKEN


@dataclass
class OwnerStruct:
    """Struct for owner object"""

    userId: str
    """The id of the owner"""
    username: str
    """The username of the owner"""
    globalName: str
    """The global name of the owner"""
    discriminator: str
    """The discriminator of the owner"""
    invited: bool
    """Whether the owner has been invited to the bot management or not"""


@dataclass
class DiscordBotsGGBotStruct:
    """Discord Bots info schema"""

    userId: str
    """The id of the bot"""
    clientId: str
    """The id of the bot"""
    username: str
    """The username of the bot"""
    globalName: str | None
    """The global name of the bot"""
    discriminator: str | None
    """The discriminator of the bot"""
    avatarURL: str
    """The url of the bot's avatar"""
    coowners: list[str]
    """The co-owners of the bot"""
    prefix: str
    """The prefix of the bot"""
    helpCommand: str
    """The help command of the bot"""
    libraryName: str
    """The library of the bot"""
    website: str | None
    """The website of the bot"""
    supportInvite: str | None
    """The support server invite of the bot"""
    botInvite: str
    """The invite of the bot"""
    shortDescription: str
    """The short description of the bot"""
    longDescription: str
    """The long description of the bot"""
    openSource: str | None
    """Repo URL of the bot"""
    shardCount: int
    """The shard count of the bot"""
    guildCount: int
    """The guild count of the bot"""
    verified: bool
    """The verified status of the bot"""
    slashCommandsOnly: bool
    """The slash commands only status of the bot"""
    online: bool
    """The online status of the bot"""
    inGuild: bool
    """The status if bot has been invited to Discot Bots server"""
    addedDate: datetime
    """The date for bot added to list"""
    status: str
    """The status of the bot"""
    owner: OwnerStruct
    """The owner of the bot"""
    uptime: int
    """The uptime of the bot"""
    lastOnlineChange: datetime
    """The last time the bot's online status changed"""
    verificationLevel: str
    """The verification level of the bot"""


class DiscordBotsGG:
    """# Discord Bots API Wrapper"""

    def __init__(self, token: str = DBGG_API_TOKEN, bot_id: int = BOT_CLIENT_ID):
        """
        ## Discord Bots API Wrapper

        Args:
            token (str, optional): Discord Bots API token. Defaults to DBGG_API_TOKEN.
            bot_id (int, optional): Bot's client ID. Defaults to BOT_CLIENT_ID.
        """
        self.token = token
        self.base_url = "https://discord.bots.gg/api/v1"
        self.session = None
        self.headers = None
        self.bot_id = bot_id

    async def __aenter__(self):
        """Enter async context"""
        self.session = aiohttp.ClientSession()
        self.headers = {"Authorization": self.token, "Content-Type": "application/json"}
        return self

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        """Exit async context"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close() if self.session else None

    async def get_bot_stats(self, sanitize: bool = False) -> DiscordBotsGGBotStruct:
        """
        Get bot stats from discord.bots.gg

        Returns:
            DiscordBotsGGBotStruct: Bot stats
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        param = "?sanitized=true" if sanitize else ""
        async with self.session.get(
            f"{self.base_url}/bots/{self.bot_id}{param}",
            headers=self.headers,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Discord Bots API returned HTTP status code {resp.status}",
                    resp.status,
                )
            return from_dict(
                data_class=DiscordBotsGGBotStruct,
                data=await resp.json(),
                config=Config(
                    type_hooks={
                        datetime: lambda x: datetime.strptime(
                            x, "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                    }
                ),
            )

    async def post_bot_stats(
        self,
        guild_count: int | list[int],
        shard_id: int | None = None,
        shard_count: int | None = None,
    ) -> int:
        """
        Post bot stats to discord.bots.gg

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

        payload = {
            "guildCount": guild_count,
        }

        if shard_id or shard_count:
            payload["shardId"] = shard_id or 0
            payload["shardCount"] = shard_count or 1

        async with self.session.post(
            f"{self.base_url}/bots/{self.bot_id}/stats",
            headers=self.headers,
            json=payload,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Discord Bots API returned HTTP status code {resp.status}",
                    resp.status,
                )
            return resp.status
