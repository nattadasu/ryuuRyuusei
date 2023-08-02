"""
# Discord Bots API Wrapper

A lite wrapper for the discord.bots.gg API.
"""

import aiohttp

from classes.excepts import ProviderHttpError
from modules.const import BOT_CLIENT_ID, DBGG_API_TOKEN


class DiscordBotsGG:
    """# Discord Bots API Wrapper"""

    def __init__(
            self,
            token: str = DBGG_API_TOKEN,
            bot_id: int = BOT_CLIENT_ID):
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
