import asyncio
import csv
from datetime import datetime as dtime, timezone as tz
from time import perf_counter as pc

import interactions as ipy

from modules.const import *
from modules.i18n import lang, readUserLang, paginateLanguage, setLanguage

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


async def main():
    """Main function"""
    bot.load_extension('interactions.ext.sentry',
                       token=SENTRY_DSN)
    bot.load_extension("interactions.ext.jurigged")
    bot.del_unused_app_cmd = True
    bot.sync_interactions = True
    bot.send_command_tracebacks = False
    bot.sync_ext = True
    await bot.astart()


if __name__ == "__main__":
    print("Starting bot...")
    print("Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
    bot_run = pc()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_stop = pc()
        print("Bot stopped by user.")
        now: dtime = dtime.now(tz=tz.utc)
        print("Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
        print("Uptime: " + str(int(bot_stop - bot_run)) +
              "s, or around " + str(int((bot_stop - bot_run) / 60)) + "m")
