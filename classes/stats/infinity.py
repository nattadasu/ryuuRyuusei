"""
# Infinity Bots API Wrapper

A lite wrapper for the infinitybots.gg API.
"""

import aiohttp

from classes.excepts import ProviderHttpError
from modules.const import BOT_CLIENT_ID, INFINITY_API_TOKEN


class InfinityBots:
    """# Infinity Bots API Wrapper"""

    def __init__(
            self,
            token: str = INFINITY_API_TOKEN,
            bot_id: int = BOT_CLIENT_ID):
        """
        ## Infinity Bots API Wrapper

        Args:
            token (str, optional): Infinity Bots API token. Defaults to INFINITY_API_TOKEN.
            bot_id (int, optional): Bot's client ID. Defaults to BOT_CLIENT_ID.
        """
        self.token = token
        self.base_url = "https://spider.infinitybots.gg"
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
        members: int | list[int] | None = None,
        shards: list[int] | None = None,
        shard_count: int | None = None,
    ) -> int:
        """
        Post bot stats to infinitybots.gg

        Args:
            guild_count (int | list[int]): Guild count or list of guild counts.
            members (int | list[int], optional): Member count or list of member counts. Defaults to None.
            shards (list[int], optional): List of shard IDs. Defaults to None.
            shard_count (int, optional): Shard count. Defaults to None.

        Raises:
            RuntimeError: Session is not initialized
            ProviderHttpError: Failed to post stats to infinitybots.gg

        Returns:
            int: HTTP status code
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        if isinstance(guild_count, list):
            guild_count = sum(guild_count)
        if isinstance(members, list):
            members = sum(members)

        payload: dict[str, int | list[int]] = {
            "server_count": guild_count,
        }
        if shards:
            payload["shard_list"] = shards
        if shard_count:
            payload["shards"] = shard_count
        if members:
            payload["member_count"] = members

        async with self.session.post(
            f"{self.base_url}/bots/stats",
            headers=self.headers,
            json=payload,
        ) as resp:
            if resp.status not in [200, 204]:
                raise ProviderHttpError(
                    f"Failed to post stats to infinitybots.gg: {resp.status}",
                    resp.status,
                )
            return resp.status
