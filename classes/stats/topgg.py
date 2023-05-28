"""
# Top.gg API Wrapper

A lite wrapper for the top.gg API.
"""

import aiohttp
from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import TOPGG_API_TOKEN, BOT_CLIENT_ID


class TopGG:
    """# Top.gg API Wrapper"""

    def __init__(self, token: str = TOPGG_API_TOKEN, bot_id: int = BOT_CLIENT_ID):
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

    async def __aexit__(self, exc_type, exc, tb):
        """Exit async context"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close()

    async def post_bot_stats(
        self,
        guild_count: int | list[int],
        shards: list[int] = None,
        shard_id: int = None,
        shard_count: int = None,
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
        body: dict = {
            "server_count": guild_count,
        }
        if shards:
            body["shards"] = shards
        elif shard_id is not None and shard_count is not None:
            body["shard_id"] = shard_id
            body["shard_count"] = shard_count
        # both shard_id and shard_count dependent each other,
        # raise ProviderTypeException if it missing one of them
        elif shard_id is None or shard_count is None:
            raise ProviderTypeError(
                "Both shard_id and shard_count must be provided if one of them is provided",
                ["shard_id", "shard_count"],
            )
        async with self.session.post(
            f"{self.base_url}/bots/{self.bot_id}/stats",
            json=body,
            headers=self.headers,
        ) as resp:
            if resp.status not in [200, 204]:
                raise ProviderHttpError(resp.reason, resp.status)
            return resp.status
