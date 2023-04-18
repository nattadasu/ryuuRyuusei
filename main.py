import asyncio
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc
import sys
import subprocess

import interactions as ipy

from modules.const import SENTRY_DSN, BOT_TOKEN

now: dtime = dtime.now(tz=tz.utc)

bot = ipy.Client(
    token=BOT_TOKEN,
    status=ipy.Status.IDLE,
    auto_defer=ipy.AutoDefer(
        enabled=True,
        time_until_defer=1.5,
    ),
    activity=ipy.Activity(
        name="Kagamine Len's Live Concert",
        type=ipy.ActivityType.WATCHING,
    )
)


@ipy.listen()
async def on_ready():
    guilds = len(bot.guilds)
    print("[Sys] Bot is ready!")
    print("      Logged in as: " + bot.user.display_name +
          "#" + bot.user.discriminator)
    print("      User ID: " + str(bot.user.id))
    print("      Guilds: " + str(guilds))


async def main():
    """Main function"""
    if SENTRY_DSN:
        bot.load_extension('interactions.ext.sentry',
                           token=SENTRY_DSN)
    bot.load_extension("interactions.ext.jurigged")
    bot.del_unused_app_cmd = True
    bot.sync_interactions = True
    bot.send_command_tracebacks = False

    # git pull
    print("[Sys] Checking for updates...")
    subprocess.run(["git", "pull"])

    from firstRun import firstRun
    # get this python binary's path
    python_path = sys.executable
    python_path = python_path.replace("\\", "/")
    print("[Sys] Python path: " + python_path)
    firstRun(pf=python_path)

    # Load extensions
    print("[Sys] Loading extensions...")
    bot.load_extension("extensions.commons", now=now)
    bot.load_extension("extensions.anime")
    bot.load_extension("extensions.profile")
    bot.load_extension("extensions.random")
    bot.load_extension("extensions.serversettings")
    bot.load_extension("extensions.usersettings")
    bot.load_extension("extensions.utilities")

    await bot.astart()


if __name__ == "__main__":
    print("[Sys] Starting bot...")
    print("[Bcm] Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
    bot_run = pc()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_stop = pc()
        print("[Sys] Bot stopped by user.")
        now: dtime = dtime.now(tz=tz.utc)
        print("[Bcm] Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
        print("      Uptime: " + str(int(bot_stop - bot_run)) +
              "s, or around " + str(int((bot_stop - bot_run) / 60)) + "m")
