import os
import time

from interactions import (Activity, ActivityType, AutoShardedClient, Client, Extension,
                          IntervalTrigger, Task)

from classes.excepts import ProviderHttpError
from classes.stats.dbgg import DiscordBotsGG
from classes.stats.dbl import DiscordBotList
from classes.stats.infinity import InfinityBots
from classes.stats.topgg import TopGG
from modules.commons import save_traceback_to_file
from modules.const import BOT_DATA


class BotTasker(Extension):
    """Utility task manager for the bot"""

    def __init__(self, bot: Client | AutoShardedClient) -> None:
        """Initialize the tasks"""
        self.bot = bot
        # pylint: disable=no-member
        self.delete_cache.start()
        self.delete_error_logs.start()
        self.poll_stats.start()
        # pylint: enable=no-member

    @Task.create(IntervalTrigger(minutes=10))
    async def delete_cache(self) -> None:
        """Automatically delete caches stored in the cache folder saved as JSON"""
        show_msg = 0
        half_day = 43200
        a_day = half_day * 2
        two_and_a_half_days = a_day * 2 + half_day
        a_week = a_day * 7
        a_month = a_day * 30

        known_caches = {
            "anilist": {"base": a_day, "user": half_day, "nsfw": a_week},
            "animeapi": a_day,
            "exchangerateapi": a_day,
            "jikan": {
                "base": a_day,
                "user": half_day,
            },
            "kitsu": a_day,
            "mangadex": a_day,
            "pronoundb": a_week,
            "rawg": a_day,
            "shikimori": {"base": a_day, "user": half_day},
            "simkl": a_day,
            "spotify": a_week * 2,
            "thecolorapi": a_week,
            "themoviedb": a_month,
            "trakt": a_day,
            "usrbg": two_and_a_half_days,
            "verify": half_day,
        }

        cache_folder = "cache"

        for cache_provider, durations in known_caches.items():
            # to avoid errors, create the folder if it doesn't exist
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)
            if isinstance(durations, dict):
                base_folder = os.path.join(cache_folder, cache_provider)
                # User folder
                user_folder = os.path.join(base_folder, "user")
                user_duration = durations.get("user", half_day)
                show_msg += self._delete_old_files(user_folder, user_duration)

                # NSFW folder
                nsfw_folder = os.path.join(base_folder, "nsfw")
                nsfw_duration = durations.get("nsfw", a_week)
                show_msg += self._delete_old_files(nsfw_folder, nsfw_duration)

                # Base folder
                base_duration = durations.get("base", a_day)
                show_msg += self._delete_old_files(base_folder, base_duration)
            else:
                # Single folder
                folder_path = os.path.join(cache_folder, cache_provider)
                duration = durations
                show_msg += self._delete_old_files(folder_path, duration)
        if show_msg > 0:
            print(f"[Tsk] [Cache] Finished deleting {show_msg:,} files")

    @Task.create(IntervalTrigger(hours=1))
    async def delete_error_logs(self) -> None:
        """Automatically delete error logs stored in the error_logs folder"""
        error_logs_folder = "errors"
        show_msg = self._delete_old_files(error_logs_folder, 172800)
        if show_msg > 0:
            print(f"[Tsk] [Error] Finished deleting {show_msg:,} logs")

    @Task.create(IntervalTrigger(minutes=15))
    async def poll_stats(self) -> None:
        """Poll bot statistic to 3rd party listing sites"""
        server_count = len(self.bot.guilds)
        shard_count = self.bot.total_shards
        server_members: dict[str, int] = BOT_DATA["server_members"]
        users = sum(server_members.values())
        show_msg: list[str] = []
        try:
            async with TopGG() as top:
                await top.post_bot_stats(
                    guild_count=server_count,
                    shard_count=shard_count,
                )
        except ProviderHttpError as error:
            print(f"[Tsk] [Stats] Failed to poll to Top.gg: {error}")
            save_traceback_to_file(
                "tasker_topgg", self.bot.user, error, mute_error=True)
            show_msg.append("Top.gg")

        try:
            async with DiscordBotsGG() as dbgg:
                await dbgg.post_bot_stats(
                    guild_count=server_count,
                    shard_count=shard_count,
                )
        except ProviderHttpError as error:
            print(f"[Tsk] [Stats] Failed to poll to DiscordBots.gg: {error}")
            save_traceback_to_file(
                "tasker_dbgg", self.bot.user, error, mute_error=True)
            show_msg.append("DiscordBots.gg")

        try:
            async with DiscordBotList() as dbl:
                await dbl.post_bot_stats(
                    guild_count=server_count,
                    members=users,
                )
        except ProviderHttpError as error:
            print(f"[Tsk] [Stats] Failed to poll to DiscordBotList: {error}")
            save_traceback_to_file(
                "tasker_dbl", self.bot.user, error, mute_error=True)
            show_msg.append("DiscordBotList.com")

        try:
            async with InfinityBots() as ibgg:
                await ibgg.post_bot_stats(
                    guild_count=server_count,
                    shard_count=shard_count,
                    members=users,
                )
        except ProviderHttpError as error:
            print(f"[Tsk] [Stats] Failed to poll to InfinityBots: {error}")
            save_traceback_to_file(
                "tasker_ibgg", self.bot.user, error, mute_error=True)
            show_msg.append("InfinityBots")

        if len(show_msg) > 0:
            print(
                "[Tsk] [Stats] Polled stats.",
                f"{server_count:,} servers,",
                f"{shard_count:,} shards,",
                f"{users:,} members,",
                f"failed to poll to {', '.join(show_msg)}" if len(
                    show_msg) > 0 else "successfully polled to all sites",
            )

    @Task.create(IntervalTrigger(minutes=10))
    async def update_bot_activity(self) -> None:
        """Update the bot's activity to show the number of guilds and members it is in"""
        old_activity = self.bot.activity.name
        server_members: dict[str, int] = BOT_DATA["server_members"]
        users = sum(server_members.values())
        final = f"{len(self.bot.guilds)} guilds, {users:,} members"
        if old_activity == final:
            return
        await self.bot.change_presence(
            activity=Activity(
                name=final,
                type=ActivityType.WATCHING,
            ),
        )

    @staticmethod
    def _delete_old_files(folder_path: str, duration: int) -> int:
        """
        Delete .json files in a folder that are older than the specified duration

        Args:
            folder_path (str): The path to the folder
            duration (int): The duration in seconds

        Returns:
            int: The number of files deleted
        """
        current_time = time.time()
        return_as = 0

        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                modification_time = os.path.getmtime(file_path)
                if file_name.endswith(".json") or file_name.endswith(".txt"):
                    if current_time - modification_time > duration:
                        os.remove(file_path)
                        return_as += 1

        return return_as


def setup(bot: Client | AutoShardedClient) -> None:
    BotTasker(bot)
