"""
# Infinity Bots API Wrapper

A lite wrapper for the infinitybots.gg API.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

import aiohttp
from dacite import Config, from_dict

from classes.excepts import ProviderHttpError
from modules.commons import custom_datetime_converter as dconv
from modules.const import BOT_CLIENT_ID, INFINITY_API_TOKEN


@dataclass
class UserStruct:
    """User Information"""

    avatar: str
    """The users resolved avatar URL for the platform"""
    bot: bool
    """Whether the user is a bot or not"""
    display_name: str
    """The users global display name, if the user still has a discriminator, this will be username+hashtag+discriminator"""
    id: str
    """The users ID"""
    status: str
    """The users current status"""
    username: str
    """The users username"""
    extra_data: dict[str, Any]
    """Platform specific extra data"""


@dataclass
class LinksStruct:
    """Links Information"""

    name: str
    """Name of the link. Links starting with an underscore are 'asset links' and are not visible"""
    value: str
    """Value of the link. Must normally be HTTPS with the exception of 'asset links'"""


@dataclass
class TeamStruct:
    """Team Information"""

    avatar: str
    """The teams resolved avatar URL for the platform"""
    id: str
    """The teams ID"""
    name: str
    """The teams name"""


@dataclass
class BotStruct:
    """Bot Information"""

    approval_note: str | None
    """The note for the bot's approval"""
    banner: str | None
    """The bot's banner URL if it has one, otherwise None"""
    bot_id: str
    """The bot's ID"""
    captcha_opt_out: bool
    """Whether the bot should have captchas shown if the user has captcha_sponsor_enabled"""
    cert_reason: str | None
    """The reason for the bot being certified"""
    claimed_by: str | None
    """The user who claimed the bot"""
    clicks: int
    """The bot's total click amount"""
    client_id: str
    """The bot's associated client ID validated using that top-secret Oauth2 API! Used in anti-abuse measures"""
    created_at: datetime
    """The bot's creation date"""
    extra_links: list[LinksStruct]
    """The bot's links that it wishes to advertise"""
    flags: list[str]
    """The bot's flags"""
    invite: str
    """The bot's invite URL. Must be present"""
    invite_clicks: int
    """The bot's invite click count (via users inviting the bot from IBL)"""
    itag: UUID
    """The bot's internal ID. An artifact of database migrations"""
    last_claimed: datetime
    """The bot's last claimed date"""
    last_stats_post: datetime | None
    """The list time the bot posted stats to the list. None if never posted"""
    legacy_webhooks: bool
    """Whether the bot is using legacy v1 webhooks or not"""
    library: str
    """The bot's library"""
    long: str
    """The bot's long description in raw format (HTML/markdown etc. based on the bots settings)"""
    nsfw: bool
    """Whether the bot is NSFW or not"""
    owner: UserStruct | None
    """The bot owner's user information. If in a team, this will be None and team_owner will instead be set"""
    prefix: str
    """The bot's prefix"""
    premium: bool
    """Whether the bot is premium or not"""
    premium_period_length: int
    """The period of premium for the bot in nanoseconds"""
    servers: int
    """The bot's server count"""
    shard_list: list[int]
    """The number of servers per shard"""
    shards: int
    """The bot's shard count"""
    short: str
    """The bot's short description"""
    start_premium_period: datetime
    """The start of the bot's premium period"""
    tags: list[str]
    """The bot's tags"""
    team_owner: TeamStruct | None
    """The bot's team owner's team information. If not in a team, this will be None and owner will instead be set"""
    total_uptime: int
    """The bot's total number of uptime checks"""
    type: str
    """The bot's type (e.g. pending/approved/certified/denied etc.). Note that we do not filter out denied/banned bots in API"""
    unique_clicks: int
    """The bot's unique click count based on SHA256 hashed IPs"""
    uptime: int
    """The bot's total number of successful uptime checks"""
    uptime_last_checked: datetime
    """The bot's last uptime check"""
    user: UserStruct
    """The bot's user information"""
    users: int
    """The bot's user count"""
    vanity: str
    """The bot's vanity URL"""
    vanity_ref: UUID
    """The corresponding vanities itag, this also works to ensure that all bots have an associated vanity"""
    vote_banned: bool
    """Whether the bot is vote banned or not"""
    votes: int
    """The bot's vote count"""


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
        self.headers = {"Authorization": f"Bot {self.token}",
                        "Content-Type": "application/json"}
        return self

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        """Exit async context"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close() if self.session else None

    async def get_bot_info(self, bot_id: int | str) -> BotStruct:
        """
        Get bot information

        Args:
            bot_id (int | str): Bot's client ID

        Raises:
            RuntimeError: Session is not initialized
            ProviderHttpError: Failed to get bot information

        Returns:
            BotStruct: Bot information
        """
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        async with self.session.get(f"{self.base_url}/bots/{bot_id}") as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Failed to get bot information: {resp.status} {resp.reason}",
                    resp.status,
                )
            return from_dict(
                data_class=BotStruct,
                data=await resp.json(),
                config=Config(
                    type_hooks={
                        datetime: lambda x: dconv(x),
                        # convert str to UUID
                        UUID: lambda x: UUID(x)
                    }
                )
            )

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
            "servers": guild_count,
        }
        if shards:
            payload["shard_list"] = shards
        if shard_count:
            payload["shards"] = shard_count
        if members:
            payload["users"] = members

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
