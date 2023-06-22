import asyncio
import os
import sys
import traceback
from datetime import datetime as dtime
from datetime import timezone as tz

import interactions as ipy
from aiohttp import ClientConnectorError
from interactions.client import const as ipy_const

from modules.commons import convert_float_to_time
from modules.const import BOT_TOKEN, SENTRY_DSN, USER_AGENT
from modules.oobe.commons import UnsupportedVersion

py_ver = sys.version_info

if py_ver < (3, 10):
    raise UnsupportedVersion(
        f"Python version {py_ver.major}.{py_ver.minor}.{py_ver.micro} is not supported. Please use Python 3.10 or newer.",
        f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}",
    )

print(f"[Pyt] Python version : {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
print(f"[Pyt] Python binary  : {sys.executable}")


now: dtime = dtime.now(tz=tz.utc)

ipy_const.CLIENT_FEATURE_FLAGS["FOLLOWUP_INTERACTIONS_FOR_IMAGES"] = True

bot = ipy.AutoShardedClient(
    token=BOT_TOKEN,
    status=ipy.Status.ONLINE,
    activity=ipy.Activity(
        name="random cat videos",
        type=ipy.ActivityType.WATCHING,
    ),
    delete_unused_application_cmds=True,
    sync_interactions=True,
    send_command_tracebacks=False,
)
"""The bot client"""


@ipy.listen()
async def on_ready():
    """
    When the bot is ready

    This function will be called when the bot is ready.
    """
    guilds = len(bot.guilds)
    bg = "[Sys]"
    lbg = len(bg)
    sp = " " * lbg
    print("[Sys] Bot is ready!")
    print(f"{sp} Logged in as : {bot.user.display_name}")
    print(f"{sp} User ID      : {bot.user.id}")
    print(f"{sp} Guilds       : {guilds}")
    print(f"{sp} Shards       : {bot.total_shards}")
    print(f"{sp} User Agent   : {USER_AGENT}")


async def main():
    """
    Main function

    This function will be run before the bot starts.
    """
    print("[Ext] Loading core/bot extensions...")
    exts: list[str] = [
        "interactions.ext.sentry",
    ]
    for i, ext in enumerate(exts):
        i += 1
        pg = f"[Ext] [{i}/{len(exts)}]"
        lpg = len(pg)
        sp = " " * lpg
        print(f"{pg} Loading core/bot extension: {ext}")
        try:
            if ext == "interactions.ext.sentry" and SENTRY_DSN not in [
                    "", None]:
                bot.load_extension(ext, token=SENTRY_DSN, filter=None,
                                   traces_sample_rate=0.3)
            else:
                bot.load_extension(ext)
        except Exception as ea:
            print(f"{pg} Error while loading system extension: " + ext)
            print(f"{sp} {ea}")
            print("[Ext] If this error shows up while restart the bot, ignore")

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
        except Exception as eb:
            print(f"{pg} Error while loading extension: {ext}")
            print(f"{sp} {eb}")
            print(f"{sp} Traceback:")
            traceback.print_exc()
            print("[Cog] If this error shows up while restart the bot, ignore")

    await bot.astart()


def uptime() -> None:
    """
    Prints uptime, how long the bot has been online

    Returns:
        None
    """
    bot_stop: dtime = dtime.now(tz=tz.utc)
    print("[Bcm] Date: " + bot_stop.strftime("%d/%m/%Y %H:%M:%S"))
    differences = bot_stop - bot_run
    total_seconds = differences.total_seconds()
    total_time = convert_float_to_time(total_seconds, use_seconds=True,
                                       show_milliseconds=True)
    print(f"      Uptime: {total_time}")
    return


if __name__ == "__main__":
    print("[Sys] Starting bot...")
    bot_run = now
    print("[Bcm] Date: " + bot_run.strftime("%d/%m/%Y %H:%M:%S"))
    while True:
        try:
            asy = asyncio.run(main())
        except KeyboardInterrupt:
            print("[Sys] Bot stopped by user.")
            uptime()
            sys.exit(0)
        except ClientConnectorError:
            print("[Sys] Bot stopped due to connection error.")
            uptime()
            sys.exit(1)
        except Exception as ex:
            print("[Sys] Bot stopped due to error.")
            print(f"      {ex}")
            print("[Err] Traceback:")
            traceback.print_exc()
            uptime()
            sys.exit(1)
