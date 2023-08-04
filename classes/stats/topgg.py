"""
# Top.gg API Wrapper

A lite wrapper for the top.gg API.
"""

from dataclasses import dataclass
from datetime import datetime

import aiohttp
from dacite import Config, from_dict

from classes.excepts import ProviderHttpError
from modules.const import BOT_CLIENT_ID, TOPGG_API_TOKEN


@dataclass
class TopGGBotStruct:
    """Top.gg Bot info schema"""

    id: str
    """The id of the bot"""
    username: str
    """The username of the bot"""
    discriminator: str
    """The discriminator of the bot"""
    defAvatar: str
    """The cdn hash of the bot's avatar if the bot has none"""
    prefix: str
    """The prefix of the bot"""
    shortdesc: str
    """The short description of the bot"""
    tags: list[str]
    """The tags of the bot"""
    owners: list[int]
    """of Snowflakes The owners of the bot. First one in the array is the main owner."""
    guilds: list[int]
    """of Snowflakes The guilds featured on the bot page"""
    date: datetime
    """The date the bot was approved"""
    certifiedBot: bool
    """The certified status of the bot"""
    points: int
    """The amount of upvotes the bot has"""
    monthlyPoints: int
    """The amount of upvotes the bot has this month"""
    donatebotguildid: str
    """The guild id for the donatebot setup"""
    avatar: str | None = None
    """The avatar hash of the bot's avatar"""
    lib: str | None = None
    """The library of the bot, deprecated"""
    longdesc: str | None = None
    """The long description of the bot. Can contain HTML and/or Markdown"""
    website: str | None = None
    """The website url of the bot"""
    support: str | None = None
    """The support server invite code of the bot"""
    github: str | None = None
    """The link to the github repo of the bot"""
    invite: str | None = None
    """The custom bot invite url of the bot"""
    server_count: int | None = None
    """The amount of servers the bot has according to posted stats."""
    shard_count: int | None = None
    """The amount of shards the bot has according to posted stats."""
    vanity: str | None = None
    """The vanity url of the bot"""


class TopGG:
    """# Top.gg API Wrapper"""

    def __init__(
            self,
            token: str = TOPGG_API_TOKEN,
            bot_id: int = BOT_CLIENT_ID):
        """
        ## Top.gg API Wrapper

        Args:
            token (str, optional): Top.gg API token. Defaults to TOPGG_API_TOKEN.
            bot_id (int, optional): Bot's client ID. Defaults to BOT_CLIENT_ID.
        """
        self.token = token
        self.base_url = "https://top.gg/api"
        self.session = None
        self.headers = None
        self.bot_id = bot_id

    async def __aenter__(self):
        """Enter async context"""
        self.session = aiohttp.ClientSession()
        self.headers = {"Authorization": self.token}
        return self

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        """Exit async context"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close() if self.session else None

    async def get_bot_stats(self) -> TopGGBotStruct:
        """
        Get bot stats from top.gg

        Returns:
            TopGGBotStruct: Bot stats
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        async with self.session.get(
            f"{self.base_url}/bots/{self.bot_id}",
            headers=self.headers,
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(f"{resp.reason}", resp.status)
            data = await resp.json()
            dacite_config = Config(
                type_hooks={
                    datetime: lambda x: datetime.strptime(
                        x, "%Y-%m-%dT%H:%M:%S.%fZ")
                }
            )
            return from_dict(
                data_class=TopGGBotStruct, data=data, config=dacite_config)

    async def post_bot_stats(
        self,
        guild_count: int | list[int],
        shards: list[int] | None = None,
        shard_id: int | None = None,
        shard_count: int | None = None,
    ) -> int:
        """
        Post bot stats to top.gg

        Args:
            guild_count (int | list[int]): Guild count or list of guild counts.
            shards (list[int], optional): List of shards. Defaults to None.
            shard_id (int, optional): Shard ID. Defaults to None.
            shard_count (int, optional): Shard count. Defaults to None.

        Returns:
            int: HTTP status code
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        body: dict[str, int | list[int]] = {
            "server_count": guild_count,
        }
        if shards:
            body["shards"] = shards
        if shard_id:
            body["shard_id"] = shard_id
        if shard_count:
            body["shard_count"] = shard_count
        async with self.session.post(
            f"{self.base_url}/bots/{self.bot_id}/stats",
            json=body,
            headers=self.headers,
        ) as resp:
            if resp.status not in [200, 204]:
                raise ProviderHttpError(f"{resp.reason}", resp.status)
            return resp.status
