from interactions import AutoShardedClient, Client, Extension, Task, IntervalTrigger
import os
import time
from classes.stats.topgg import TopGG
from classes.excepts import ProviderHttpError


class BotTasker(Extension):
    """Utility task manager for the bot"""

    def __init__(self, bot: Client | AutoShardedClient) -> None:
        """Initialize the tasks"""
        self.bot = bot
        self.delete_cache.start()
        self.poll_stats.start()

    @Task.create(IntervalTrigger(minutes=10))
    async def delete_cache(self) -> None:
        """Automatically delete caches stored in the cache folder saved as JSON"""
        half_day = 43200
        a_day = half_day * 2
        two_and_a_half_days = a_day * 2 + half_day
        a_week = a_day * 7
        a_month = a_day * 30

        known_caches = {
            "anilist": {"base": a_day, "user": half_day, "nsfw": a_week},
            "animeapi": a_day,
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

    @Task.create(IntervalTrigger(minutes=5))
    async def poll_stats(self) -> None:
        """Poll bot statistic to 3rd party listing sites"""
        server_count = len(self.bot.guilds)
        try:
            print("[Tsk] [Stats] Polling Top.gg")
            async with TopGG() as top:
                await top.post_bot_stats(
                    guild_count=server_count,
                )
            print(f"[Tsk] [Stats] Poll to Top.gg was completed with {server_count} servers")
        except ProviderHttpError as e:
            print(f"[Tsk] [Stats] Failed to poll to Top.gg: {e}")

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
                if file_name.endswith(".json"):
                    file_path = os.path.join(root, file_name)
                    modification_time = os.path.getmtime(file_path)
                    if current_time - modification_time > duration:
                        print(f"[Tsk] [Utils] Deleting cache {file_path}")
                        os.remove(file_path)


def setup(bot: Client | AutoShardedClient) -> None:
    BotTasker(bot)
