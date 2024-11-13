"""
Stats extension for the bot.

This extension is used to show bot stats via /stats command.
"""

import platform as pfm
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

import interactions as ipy
import pkg_resources as pipkg
import psutil
from interactions.ext.paginators import Paginator

from classes.stats.dbl import DiscordBotList
from classes.stats.infinity import InfinityBots
from classes.stats.topgg import TopGG
from modules.commons import save_traceback_to_file
from modules.const import (GIT_COMMIT_HASH, GT_HSH, USER_AGENT,
                           VERIFICATION_SERVER)


@dataclass
class ProviderVoteStruct:
    """Provider Vote Struct"""

    name: str
    """Name of the provider"""
    bot_id: int
    """ID of the bot"""
    base_url: str
    """Base URL of the provider"""
    total_votes: int
    """Total votes on the provider"""
    upvote_path: str = "/vote"
    """Path to upvote on the provider"""
    time_limit: int = 0
    """Time limit of vote stats on the provider in hours"""

    @property
    def as_text(self) -> str:
        """
        Get the provider vote stats as text

        Returns:
            str: The provider vote stats as text
        """
        url = f"{self.base_url}{self.bot_id}{self.upvote_path}"
        if self.time_limit == 0:
            return f"* [{self.name}]({url}): {self.total_votes:,} in total"
        return f"* [{self.name}]({url}): {self.total_votes:,} in last {self.time_limit} hours"


@dataclass
class DiskInfo:
    """Disk Information"""

    mountpoint: str
    disk_total: str | None
    disk_used: str | None
    disk_free: str | None
    disk_percentage: float


@dataclass
class SystemInfo:
    """System Information"""

    system: str
    release: str
    version: str
    machine: str
    processor: str
    uptime: datetime
    cpu_physical_cores: int
    cpu_total_cores: int
    cpu_max_frequency: str
    cpu_min_frequency: str
    cpu_current_frequency: str
    cpu_usage_cores: list[float]
    cpu_usage_total: float
    ram_total: str | None
    ram_available: str | None
    ram_used: str | None
    ram_free: str | None
    ram_percentage: float
    swap_total: str | None
    swap_used: str | None
    swap_free: str | None
    swap_percentage: float
    disks: list[DiskInfo]


@dataclass
class PackageInfo:
    """Package Information"""

    name: str
    version: str
    license: str


def get_size(bytes: float | None, suffix: str = "B") -> str | None:
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    if bytes is None:
        return None
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_disk_info() -> list[DiskInfo]:
    """
    Get disk information

    Returns:
        list[DiskInfo]: List of disk information
    """
    disks: list[DiskInfo] = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            disk_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        mountpoint = partition.mountpoint
        disk_total = get_size(disk_usage.total)
        disk_used = get_size(disk_usage.used)
        disk_free = get_size(disk_usage.free)
        disk_percentage = disk_usage.percent
        disks.append(
            DiskInfo(
                mountpoint=mountpoint,
                disk_total=disk_total,
                disk_used=disk_used,
                disk_free=disk_free,
                disk_percentage=disk_percentage,
            )
        )
    return disks


def get_system_info() -> SystemInfo:
    """
    Get system information

    Returns:
        SystemInfo: System information
    """
    cpu_usage_cores = psutil.cpu_percent(percpu=True)
    cpu_usage_total = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disks = get_disk_info()
    return SystemInfo(
        system=pfm.system(),
        release=pfm.release(),
        version=pfm.version(),
        machine=pfm.machine(),
        processor=pfm.processor(),
        uptime=datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc),
        cpu_physical_cores=psutil.cpu_count(logical=False),
        cpu_total_cores=psutil.cpu_count(logical=True),
        cpu_max_frequency=f"{psutil.cpu_freq().max:.2f}Mhz",
        cpu_min_frequency=f"{psutil.cpu_freq().min:.2f}Mhz",
        cpu_current_frequency=f"{psutil.cpu_freq().current:.2f}Mhz",
        cpu_usage_cores=cpu_usage_cores,
        cpu_usage_total=cpu_usage_total,
        ram_total=get_size(ram.total),
        ram_available=get_size(ram.available),
        ram_used=get_size(ram.used),
        ram_free=get_size(ram.free),
        ram_percentage=ram.percent,
        swap_total=get_size(swap.total),
        swap_used=get_size(swap.used),
        swap_free=get_size(swap.free),
        swap_percentage=swap.percent,
        disks=disks,
    )


def get_pkg_license(pkg: pipkg.Distribution) -> str:
    try:
        lines = pkg.get_metadata_lines("METADATA")
    except Exception as _:
        lines = pkg.get_metadata_lines("PKG-INFO")

    for line in lines:
        if line.startswith("License:"):
            return line[9:]
    return "*Licence not found*"


def get_pip_pkgs() -> list[PackageInfo]:
    """
    Get pip packages

    Returns:
        list[PackageInfo]: List of pip packages
    """
    final: list[PackageInfo] = []
    for pkg in pipkg.working_set:
        final.append(
            PackageInfo(name=pkg.key, version=pkg.version,
                        license=get_pkg_license(pkg))
        )
    # sort by name
    final.sort(key=lambda x: x.name)
    return final


class Stats(ipy.Extension):
    """Stats command"""

    """Common commands"""

    def __init__(
        self,
        bot: ipy.Client | ipy.AutoShardedClient,
        now: datetime = datetime.now(tz=timezone.utc),
    ):
        """
        Initialize the extension

        Args:
            bot (ipy.Client | ipy.AutoShardedClient): The bot client
            now (datetime, optional): The current time. Defaults to datetime.now(tz=tz.utc).
        """
        self.bot: ipy.Client | ipy.AutoShardedClient = bot
        self.now = now

    base = ipy.SlashCommand(
        name="stats",
        description="Show various statistics and information about the bot",
    )

    deepstats = ipy.SlashCommand(
        name="deepstats",
        description="Show more information about bot",
        scopes=[VERIFICATION_SERVER],
        default_member_permissions=ipy.Permissions.ADMINISTRATOR,
    )

    @base.subcommand(sub_cmd_name="general", sub_cmd_description="Show bot stats")
    async def stats_general(self, ctx: ipy.SlashContext):
        """
        Show bot stats

        Args:
            ctx (ipy.SlashContext): The slash command context
        """
        await ctx.defer()
        bot_id = self.bot.user.id
        msg = await ctx.send(
            embed=ipy.Embed(
                title="Stats", description="Getting stats...", color=0x771921
            )
        )
        # count guilds
        guilds = len(self.bot.guilds)
        shards = self.bot.total_shards
        commands = self.bot.application_commands
        scopes: list[list[int | ipy.Snowflake]] = [
            [0],
            [ctx.author_id],
            [ctx.channel_id],
        ]
        if ctx.guild_id is not None:
            scopes.append([ctx.guild_id])
        scopes = tuple(scopes)
        # check if command is available to known scopes
        commands = [
            command
            for command in commands
            if list(map(int, command.scopes)) in scopes
            and isinstance(command, ipy.SlashCommand)
        ]
        # count commands
        command_count = len(commands)

        # get uptime
        uptime = int(self.now.timestamp())

        # get python ver
        verinfo = sys.version_info
        py_ver = f"{verinfo.major}.{verinfo.minor}.{verinfo.micro}"

        # get upvotes
        provider_votes: list[ProviderVoteStruct] = []

        try:
            async with TopGG() as tgg:
                tgg_info = await tgg.get_bot_stats()
                provider_votes.append(
                    ProviderVoteStruct(
                        name="Top.gg",
                        bot_id=bot_id,
                        base_url="https://top.gg/bot/",
                        total_votes=tgg_info.points,
                    )
                )
        except Exception as err:
            save_traceback_to_file("stats_general-tgg", ctx.author, err, True)

        try:
            async with DiscordBotList() as dbl:
                dbl_stats = await dbl.get_recent_upvotes()
                # dbl_upvote = dbl_stats.total
                provider_votes.append(
                    ProviderVoteStruct(
                        name="Discord Bot List",
                        bot_id=bot_id,
                        base_url="https://discordbotlist.com/bots/",
                        upvote_path="/upvotes",
                        total_votes=dbl_stats.total,
                        time_limit=12,
                    )
                )
        except Exception as err:
            save_traceback_to_file("stats_general-dbl", ctx.author, err, True)

        try:
            async with InfinityBots() as ibl:
                ibl_info = await ibl.get_bot_info(bot_id)
                provider_votes.append(
                    ProviderVoteStruct(
                        name="Infinity Bots",
                        bot_id=bot_id,
                        base_url="https://infinitybots.gg/bot/",
                        total_votes=ibl_info.votes,
                    )
                )
        except Exception as err:
            save_traceback_to_file("stats_general-ibl", ctx.author, err, True)

        provider_votes.sort(key=lambda x: x.name)
        votes_str = "\n".join(
            [vt.as_text for vt in provider_votes]) or "No reports"

        embed = ipy.Embed(
            title="General stats for bot",
            color=0x771921,
            timestamp=ipy.Timestamp.now(tz=timezone.utc),
        )

        embed.add_fields(
            ipy.EmbedField(name="🏠 Guilds", value=f"{guilds:,}", inline=True),
            ipy.EmbedField(name="🔗 Shards", value=f"{shards:,}", inline=True),
            ipy.EmbedField(name="📝 Commands",
                           value=f"{command_count:,}", inline=True),
            ipy.EmbedField(name="🕒 Uptime",
                           value=f"<t:{uptime}:R>", inline=True),
            ipy.EmbedField(name="🐍 Python Version", value=py_ver, inline=True),
            ipy.EmbedField(
                name="🤖 Bot Version",
                value=f"[{GT_HSH}](https://github.com/nattadasu/ryuuRyuusei/commit/{GIT_COMMIT_HASH})",
                inline=True,
            ),
            ipy.EmbedField(name="📈 Upvotes", value=votes_str, inline=False),
            ipy.EmbedField(
                name="🌐 User Agent",
                value=f'```http\nUser-Agent: "{USER_AGENT}"\n```',
                inline=False,
            ),
        )
        embed.set_thumbnail(self.bot.user.avatar.url)
        await msg.edit(embed=embed)

    @base.subcommand(sub_cmd_name="system", sub_cmd_description="Show system stats")
    async def stats_system(self, ctx: ipy.SlashContext):
        """
        Show system stats

        Args:
            ctx (ipy.SlashContext): The slash command context
        """
        await ctx.defer()
        msg = await ctx.send(
            embed=ipy.Embed(
                title="System Stats", description="Getting stats...", color=0x771921
            )
        )

        sys_info = get_system_info()

        cores = ""
        for index, core in enumerate(sys_info.cpu_usage_cores):
            cores += f"  {index}. {core}%\n"

        embed = ipy.Embed(
            title="System stats for bot",
            color=0x771921,
            timestamp=ipy.Timestamp.now(tz=timezone.utc),
        )
        embed.add_fields(
            ipy.EmbedField(
                name="🖱️ Operating System",
                value=f"""* System: {sys_info.system}
* Release Build: {sys_info.version}
* Architecture: {sys_info.machine}
* Processor: {sys_info.processor}
* Uptime: <t:{int(sys_info.uptime.timestamp())}:R>""",
                inline=True,
            ),
            ipy.EmbedField(
                name="🧠 CPU",
                value=f"""* Physical Cores: {sys_info.cpu_physical_cores}
* Total Cores: {sys_info.cpu_total_cores}
* Max Frequency: {sys_info.cpu_max_frequency}
* Min Frequency: {sys_info.cpu_min_frequency}
* Current Frequency: {sys_info.cpu_current_frequency}
* Usage:
{cores}""",
                inline=True,
            ),
            ipy.EmbedField(
                name="💾 RAM",
                value=f"""* Total: {sys_info.ram_total}
* Available: {sys_info.ram_available}
* Used: {sys_info.ram_used}
* Free: {sys_info.ram_free}
* Percentage: {sys_info.ram_percentage}%""",
                inline=True,
            ),
            ipy.EmbedField(
                name="📦 Swap/Virtual Memory",
                value=f"""* Total: {sys_info.swap_total}
* Used: {sys_info.swap_used}
* Free: {sys_info.swap_free}
* Percentage: {sys_info.swap_percentage}%""",
                inline=True,
            ),
        )
        for disk in sys_info.disks:
            if disk.mountpoint.startswith("/snap/") or disk.mountpoint.startswith(
                "/boot"
            ):
                continue
            embed.add_field(
                name=f"💿 Storage ({disk.mountpoint})",
                value=f"""* Total: {disk.disk_total}
* Used: {disk.disk_used}
* Free: {disk.disk_free}
* Percentage: {disk.disk_percentage}%""",
                inline=True,
            )
        embed.set_thumbnail(self.bot.user.avatar.url)
        await msg.edit(embed=embed)

    @deepstats.subcommand(
        sub_cmd_name="packages", sub_cmd_description="Show installed PIP packages"
    )
    async def deepstats_packages(self, ctx: ipy.SlashContext):
        """
        Show installed PIP packages

        Args:
            ctx (ipy.SlashContext): The slash command context
        """
        await ctx.defer()
        # if user is not one of the bot owners, return
        if ctx.author not in self.bot.owners:
            await ctx.send(
                embed=ipy.Embed(
                    title="Error",
                    description="You are not allowed to use this command",
                    color=0x771921,
                )
            )
            return
        message: list[ipy.Embed] = []
        packages = get_pip_pkgs()
        now = ipy.Timestamp.now(tz=timezone.utc)

        for page in range(0, len(packages), 15):
            listed: list[ipy.EmbedField] = []
            for pkg in packages[page: page + 15]:
                listed.append(
                    ipy.EmbedField(
                        name=pkg.name,
                        value=f"Version: {pkg.version}\nLicense: {pkg.license}",
                        inline=True,
                    )
                )
            embed = ipy.Embed(
                title="Installed PIP Packages", color=0x771921, timestamp=now
            )
            embed.add_fields(*listed)
            embed.set_thumbnail(self.bot.user.avatar.url)
            message.append(embed)

        paging = Paginator.create_from_embeds(self.bot, *message, timeout=180)
        await paging.send(ctx)


def setup(bot: ipy.Client | ipy.AutoShardedClient, now: datetime):
    Stats(bot, now)
