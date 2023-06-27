import os
import time

from interactions import (AutoShardedClient, Client, Extension,
                          IntervalTrigger, Task)

from classes.excepts import ProviderHttpError
from classes.stats.topgg import TopGG
from modules.commons import save_traceback_to_file


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
        print("[Tsk] [Cache] Deleting old cache files, if any")
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
                # Base folder
                base_folder = os.path.join(cache_folder, cache_provider)
                base_duration = durations.get("base", a_day)
                self._delete_old_files(base_folder, base_duration)

                # User folder
                user_folder = os.path.join(base_folder, "user")
                user_duration = durations.get("user", half_day)
                self._delete_old_files(user_folder, user_duration)

                # NSFW folder
                nsfw_folder = os.path.join(base_folder, "nsfw")
                nsfw_duration = durations.get("nsfw", a_week)
                self._delete_old_files(nsfw_folder, nsfw_duration)
            else:
                # Single folder
                folder_path = os.path.join(cache_folder, cache_provider)
                duration = durations
                self._delete_old_files(folder_path, duration)
        print("[Tsk] [Cache] Finished deleting old cache files")

    @Task.create(IntervalTrigger(hours=1))
    async def delete_error_logs(self) -> None:
        """Automatically delete error logs stored in the error_logs folder"""
        error_logs_folder = "errors"
        self._delete_old_files(error_logs_folder, 172800)

    @Task.create(IntervalTrigger(minutes=30))
    async def poll_stats(self) -> None:
        """Poll bot statistic to 3rd party listing sites"""
        server_count = len(self.bot.guilds)
        shard_count = self.bot.total_shards
        try:
            print("[Tsk] [Stats] Polling Top.gg")
            async with TopGG() as top:
                await top.post_bot_stats(
                    guild_count=server_count,
                    shard_count=shard_count,
                )
            print(
                f"[Tsk] [Stats] Poll to Top.gg was completed with {server_count} servers"
            )
        except ProviderHttpError as error:
            print(f"[Tsk] [Stats] Failed to poll to Top.gg: {error}")
            save_traceback_to_file("tasker_topgg", self.bot.user, error)

    @staticmethod
    def _delete_old_files(folder_path: str, duration: int) -> None:
        """
        Delete .json files in a folder that are older than the specified duration

        Args:
            folder_path (str): The path to the folder
            duration (int): The duration in seconds

        Returns:
            None
        """
        current_time = time.time()

        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                modification_time = os.path.getmtime(file_path)
                if file_name.endswith(".json"):
                    if current_time - modification_time > duration:
                        print(f"[Tsk] [Utils] Deleting cache {file_path}")
                        os.remove(file_path)
                elif file_name.endswith(".txt"):
                    if current_time - modification_time > duration:
                        print(f"[Tsk] [Utils] Deleting error log {file_path}")
                        os.remove(file_path)


def setup(bot: Client | AutoShardedClient) -> None:
    BotTasker(bot)
