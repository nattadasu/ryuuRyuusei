import asyncio
import csv
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc

import interactions as ipy

from modules.commons import *
from modules.const import *
from modules.i18n import lang, readUserLang
from modules.myanimelist import searchMalAnime

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

    # Load extensions
    print("[Sys] Loading extensions...")
    bot.load_extension("extensions.commons", now=now)
    bot.load_extension("extensions.anime")
    bot.load_extension("extensions.profile")
    bot.load_extension("extensions.random")
    bot.load_extension("extensions.serversettings")
    bot.load_extension("extensions.usersettings")

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
