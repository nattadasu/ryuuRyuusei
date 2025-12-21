import asyncio
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import interactions as ipy
from aiohttp import ClientConnectorError
from interactions.client import const as ipy_const

from modules.commons import convert_float_to_time
from modules.const import BOT_TOKEN, SENTRY_DSN, USER_AGENT
from modules.oobe.commons import UnsupportedVersion

# Check Python version
py_ver = sys.version_info
if py_ver < (3, 10):
    raise UnsupportedVersion(
        f"Python version {py_ver.major}.{py_ver.minor}.{py_ver.micro} is not supported. Please use Python 3.10 or newer.",
        f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}",
    )

print(f"[Pyt] Python version : {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
print(f"[Pyt] Python binary  : {sys.executable}")


# Global state
now = datetime.now(tz=timezone.utc)
"""The current time when bot started"""

# Enable experimental features
ipy_const.CLIENT_FEATURE_FLAGS["FOLLOWUP_INTERACTIONS_FOR_IMAGES"] = True

# Initialize bot
bot = ipy.AutoShardedClient(
    token=BOT_TOKEN,
    status=ipy.Status.IDLE,
    activity=ipy.Activity(
        name="system booting up...",
        type=ipy.ActivityType.LISTENING,
    ),
    delete_unused_application_cmds=True,
    sync_interactions=True,
    send_command_tracebacks=False,
    intents=ipy.Intents.DEFAULT | ipy.Intents.MESSAGE_CONTENT,
)
"""The bot client"""


def print_status(prefix: str, message: str, indent: bool = False) -> None:
    """
    Print a formatted status message

    Args:
        prefix: Status prefix (e.g., "[Sys]", "[Ext]")
        message: Message to print
        indent: Whether to indent (for multi-line status)
    """
    if indent:
        spacing = " " * len(prefix)
        print(f"{spacing} {message}")
    else:
        print(f"{prefix} {message}")


@ipy.listen()
async def on_ready():
    """Event handler for when the bot is ready"""
    guilds = len(bot.guilds)
    print_status("[Sys]", "Bot is ready!")
    print_status("[Sys]", f"Logged in as : {bot.user.display_name}", indent=True)
    print_status("[Sys]", f"User ID      : {bot.user.id}", indent=True)
    print_status("[Sys]", f"Guilds       : {guilds}", indent=True)
    print_status("[Sys]", f"Shards       : {bot.total_shards}", indent=True)
    print_status("[Sys]", f"User Agent   : {USER_AGENT}", indent=True)

    # Set bot status
    await asyncio.sleep(2.5)
    await bot.change_presence(
        activity=ipy.Activity(
            name=f"{guilds} guilds, {bot.total_shards:,} shards",
            type=ipy.ActivityType.WATCHING,
        ),
        status=ipy.Status.ONLINE,
    )


def load_core_extensions() -> None:
    """Load core/bot extensions (like Sentry)"""
    print_status("[Ext]", "Loading core/bot extensions...")

    # Load Sentry if configured
    if SENTRY_DSN not in ["", None]:
        try:
            print_status("[Ext]", "Loading: interactions.ext.sentry")
            bot.load_extension(
                "interactions.ext.sentry",
                token=SENTRY_DSN,
                filter=None,
                traces_sample_rate=0.3,
            )
        except Exception as e:
            print_status("[Ext]", f"Error loading Sentry: {e}")
            print_status("[Ext]", "Continuing without Sentry integration...")


def load_custom_extensions() -> None:
    """Load custom extensions from the extensions folder"""
    print_status("[Cog]", "Loading custom extensions...")

    # Extensions that need special initialization
    special_extensions = {"commons", "stats"}
    extensions_path = Path("extensions")

    # Get all .py files in extensions folder
    extension_files = list(extensions_path.glob("*.py"))
    loaded_count = 0

    for ext_file in extension_files:
        ext_name = ext_file.stem  # Get filename without .py

        # Skip __pycache__ and other special files
        if ext_name.startswith("_"):
            continue

        module_path = f"extensions.{ext_name}"

        try:
            # Load extension with special params if needed
            if ext_name in special_extensions:
                print_status("[Cog]", f"Loading {ext_name} (with custom params)...")
                bot.load_extension(module_path, now=now)
            else:
                print_status("[Cog]", f"Loading {ext_name}...")
                bot.load_extension(module_path)

            loaded_count += 1

        except Exception as e:
            print_status("[Cog]", f"Error loading {ext_name}: {e}")
            print_status("[Cog]", "Traceback:", indent=True)
            traceback.print_exc()

    print_status(
        "[Cog]",
        f"Successfully loaded {loaded_count}/{len(extension_files)} extension(s)",
    )


async def main():
    """Main function - loads extensions and starts the bot"""
    load_core_extensions()
    load_custom_extensions()
    await bot.astart()


def print_uptime(start_time: datetime) -> None:
    """
    Print bot uptime

    Args:
        start_time: When the bot started
    """
    end_time = datetime.now(tz=timezone.utc)
    print_status("[Bcm]", f"Date: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")

    differences = end_time - start_time
    total_seconds = differences.total_seconds()
    total_time = convert_float_to_time(
        total_seconds, use_seconds=True, show_milliseconds=True
    )
    print_status("[Bcm]", f"Uptime: {total_time}", indent=True)


if __name__ == "__main__":
    print_status("[Sys]", "Starting bot...")
    bot_run_time = now
    print_status("[Bcm]", f"Date: {bot_run_time.strftime('%d/%m/%Y %H:%M:%S')}")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_status("[Sys]", "Bot stopped by user.")
        print_uptime(bot_run_time)
        sys.exit(0)
    except ClientConnectorError:
        print_status("[Sys]", "Bot stopped due to connection error.")
        print_uptime(bot_run_time)
        sys.exit(1)
    except Exception as ex:
        print_status("[Sys]", "Bot stopped due to error.")
        print_status("[Sys]", str(ex), indent=True)
        print_status("[Err]", "Traceback:")
        traceback.print_exc()
        print_uptime(bot_run_time)
        sys.exit(1)
