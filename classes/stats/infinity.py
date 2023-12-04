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
    extra_data: dict[str, Any]
    """Platform specific extra data"""
    flags: list[str]
    """The users flags. Note that dovewing has its own list of flags"""
    id: str
    """The users ID"""
    status: str
    """The users current status"""
    username: str
    """The users username"""


@dataclass
class AssetStruct:
    """Banner Information"""

    default_path: str
    """The path to the default asset based on $cdnUrl. May be empty if no default banner"""
    errors: list[str]
    """Any errors that occurred while trying to get the asset"""
    exists: bool
    """Whether the asset exists or not"""
    path: str
    """The path to the asset based on $cdnUrl."""
    type: str
    """The type of asset. May be empty if no default banner"""
    last_modified: datetime | None = None
    """The last modified date of the asset, if it exists"""
    size: int | None = None
    """The size of the asset in bytes, if it exists"""


@dataclass
class LinkStruct:
    """Link Information"""

    name: str
    """Name of the link. Links starting with an underscore are 'asset links' and are not visible"""
    value: str
    """Value of the link. Must normally be HTTPS with the exception of 'asset links'"""


@dataclass
class BaseBotStruct:
    """Basic Bot Information"""

    banner: AssetStruct
    """The bot's banner URL if it has one, otherwise None"""
    bot_id: str
    """The bot's ID"""
    clicks: int
    """The bot's total click amount"""
    invite_clicks: int
    """The bot's invite click count (via users inviting the bot from IBL)"""
    library: str
    """The bot's library"""
    nsfw: bool
    """Whether the bot is NSFW or not"""
    premium: bool
    """Whether the bot is premium or not"""
    servers: int
    """The bot's server count"""
    shards: int
    """The bot's shard count"""
    short: str
    """The bot's short description"""
    tags: list[str]
    """The bot's tags"""
    type: str
    """The bot's type (e.g. pending/approved/certified/denied etc.). Note that we do not filter out denied/banned bots in API"""
    user: UserStruct
    """The bot's user information"""
    vanity: str
    """The bot's vanity URL"""
    vanity_ref: UUID
    """The corresponding vanities itag, this also works to ensure that all bots have an associated vanity"""
    votes: int
    """The bot's vote count"""


@dataclass
class TeamMemberStruct:
    """Team Member Information"""

    created_at: datetime
    """The time the team member was added"""
    data_holder: bool
    """
    Whether the team member is a data holder responsible for all data on the team.

    That is, should performing mass-scale opertion on them affect the team
    """
    flags: list[str]
    """The permissions/flags of the team member"""
    itag: UUID
    """The ID of the team member"""
    mentionable: bool
    """Whether the team member is mentionable (for alerts in bot-logs etc.)"""
    user: UserStruct
    """A user object representing the user"""


@dataclass
class TeamServerStruct:
    """Team Server Information"""

    avatar: str
    """The server's avatar"""
    banner: AssetStruct
    """Banner information/metadata"""
    clicks: int
    """The server's view count"""
    invie_clicks: int
    """The server's invite click count (via users inviting the server from IBL)"""
    name: str
    """The server's name"""
    nsfw: bool
    """Whether the server is NSFW or not"""
    online_members: int
    """The server's online member count"""
    premium: bool
    """Whether the server is a premium server or not"""
    server_id: str
    """The server's ID"""
    short: str
    """The server's short description"""
    tags: list[str]
    """The server's tags"""
    total_members: int
    """The server's total member count"""
    type: str
    """The server's type (e.g. pending/approved/certified/denied etc.)."""
    vanity: str
    """The server's vanity URL"""
    vanity_ref: UUID
    """The corresponding vanities itag, this also works to ensure that all servers have an associated vanity"""
    votes: int
    """The server's vote count"""


@dataclass
class EntitiesStruct:
    """Entities Information of the team"""

    bots: list[BaseBotStruct]
    """Bots of the team"""
    members: list[TeamMemberStruct]
    """Members of the team"""
    servers: list[TeamServerStruct]
    """Servers of the team"""
    targets: list[str]
    """The targets available in the response"""


@dataclass
class TeamStruct:
    """Team Information"""

    avatar: AssetStruct
    """The avatar of the team"""
    banner: AssetStruct
    """The banner of the team"""
    entities: EntitiesStruct
    """The entities of the team"""
    extra_links: list[LinkStruct]
    """The teams' links that it wishes to advertise"""
    id: str
    """The teams ID"""
    name: str
    """The teams name"""
    nsfw: bool
    """Whether the team is NSFW or not"""
    short: str | None
    """The teams short description if it has one, otherwise None"""
    tags: list[str | None] | None
    """The teams tags if it has any, otherwise None"""
    vanity: str
    """The teams vanity URL"""
    vanity_ref: UUID
    """The corresponding vanities itag, this also works to ensure that all teams have an associated vanity"""
    votes: int
    """The teams vote count"""
    vote_banned: bool
    """Whether the team is vote banned or not"""


@dataclass
class BotStruct(BaseBotStruct):
    """Bot Information"""

    approval_note: str | None
    """The note for the bot's approval"""
    captcha_opt_out: bool
    """Whether the bot should have captchas shown if the user has captcha_sponsor_enabled"""
    cert_reason: str | None
    """The reason for the bot being certified"""
    claimed_by: str | None
    """The user who claimed the bot"""
    client_id: str
    """The bot's associated client ID validated using that top-secret Oauth2 API! Used in anti-abuse measures"""
    created_at: datetime
    """The bot's creation date"""
    extra_links: list[LinkStruct]
    """The bot's links that it wishes to advertise"""
    flags: list[str]
    """The bot's flags"""
    invite: str
    """The bot's invite URL. Must be present"""
    itag: UUID
    """The bot's internal ID. An artifact of database migrations"""
    last_claimed: datetime
    """The bot's last claimed date"""
    last_stats_post: datetime | None
    """The list time the bot posted stats to the list. None if never posted"""
    long: str
    """The bot's long description in raw format (HTML/markdown etc. based on the bots settings)"""
    owner: UserStruct | None
    """The bot owner's user information. If in a team, this will be None and team_owner will instead be set"""
    prefix: str
    """The bot's prefix"""
    premium_period_length: int
    """The period of premium for the bot in nanoseconds"""
    shard_list: list[int]
    """The number of servers per shard"""
    start_premium_period: datetime
    """The start of the bot's premium period"""
    team_owner: TeamStruct | None
    """The bot's team owner's team information. If not in a team, this will be None and owner will instead be set"""
    total_uptime: int
    """The bot's total number of uptime checks"""
    unique_clicks: int
    """The bot's unique click count based on SHA256 hashed IPs"""
    uptime: int
    """The bot's total number of successful uptime checks"""
    uptime_last_checked: datetime
    """The bot's last uptime check"""
    users: int
    """The bot's user count"""
    vote_banned: bool
    """Whether the bot is vote banned or not"""


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
        if self.session:
            await self.session.close()
            self.session = None

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
                        # skipcq: PYL-W0108
                        datetime: lambda x: dconv(x),  # pylint: disable=unnecessary-lambda
                        # convert str to UUID
                        UUID: UUID,
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
