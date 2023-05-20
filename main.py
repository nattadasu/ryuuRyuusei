import asyncio
import os
import sys
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc

import interactions as ipy

from modules.const import BOT_TOKEN, SENTRY_DSN, USER_AGENT


now: dtime = dtime.now(tz=tz.utc)

bot = ipy.AutoShardedClient(
    token=BOT_TOKEN,
    status=ipy.Status.ONLINE,
    auto_defer=ipy.AutoDefer(
        enabled=True,
        time_until_defer=1.5,
    ),
    activity=ipy.Activity(
        name="random cat videos",
        type=ipy.ActivityType.WATCHING,
    ),
)
"""The bot client"""


@ipy.listen()
async def on_ready():
    """
    When the bot is ready

    This function will be called when the bot is ready.
    """
    guilds = len(bot.guilds)
    print("[Sys] Bot is ready!")
    print(
        "      Logged in as: "
        + bot.user.display_name
        + "#"
        + str(bot.user.discriminator)
    )
    print("      User ID     : " + str(bot.user.id))
    print("      Guilds      : " + str(guilds))
    print("      Shards      : " + str(bot.total_shards))
    print("      User Agent  : " + USER_AGENT)


async def main():
    """
    Main function

    This function will be run before the bot starts.
    """
    print("[Ext] Loading core/bot extensions...")
    exts: list[str] = [
        "interactions.ext.sentry",
        "interactions.ext.jurigged",
    ]
    for i, ext in enumerate(exts):
        i += 1
        pg = f"[Ext] [{i}/{len(exts)}]"
        lpg = len(pg)
        sp  = " " * lpg
        print(f"{pg} Loading core/bot extension: {ext}")
        try:
            if ext == "interactions.ext.sentry" and SENTRY_DSN:
                bot.load_extension(ext, token=SENTRY_DSN)
            bot.load_extension(ext)
        except Exception as e:
            print(f"{pg} Error while loading system extension: " + ext)
            print(sp + str(e))
            print(f"[Ext] If this error shows up while restart the bot, ignore")
    bot.del_unused_app_cmd = True
    bot.sync_interactions = True
    bot.send_command_tracebacks = False

    # Load extensions
    print("[Cog] Loading cog/extensions...")

    # for each .py files in extensions folder, load it, except for commons.py
    exts = os.listdir("extensions")
    for i, ext in enumerate(exts):
        i += 1
        pg = f"[Cog] [{i}/{len(exts)}]"
        lpg = len(pg)
        sp = " " * lpg
        try:
            if ext.endswith(".py"):
                print(f"{pg} Loading cog/extension: {ext}")
                ext = ext[:-3]
                if ext != "commons":
                    bot.load_extension("extensions." + ext)
                else:
                    bot.load_extension("extensions." + ext, now=now)
            else:
                print(f"{pg} Skipping: {ext}, not a .py file")
        except Exception as e:
            print(f"{pg} Error while loading extension: {ext}")
            print({sp} + str(e))
            print("[Cog] If this error shows up while restart the bot, ignore")

    await bot.astart()


if __name__ == "__main__":
    print("[Sys] Starting bot...")
    print("[Bcm] Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
    bot_run = pc()
    while True:
        try:
            asy = asyncio.run(main())
        except KeyboardInterrupt:
            bot_stop = pc()
            print("[Sys] Bot stopped by user.")
            now: dtime = dtime.now(tz=tz.utc)
            print("[Bcm] Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
            print(
                "      Uptime: "
                + str(int(bot_stop - bot_run))
                + "s, or around "
                + str(int((bot_stop - bot_run) / 60))
                + "m"
            )
            sys.exit(0)
