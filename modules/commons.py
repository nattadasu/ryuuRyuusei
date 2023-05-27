"""
# Commons Module

This module contains the common functions used by the other modules.
"""

import re
from datetime import timedelta
from enum import Enum
from re import sub as rSub
from uuid import uuid4 as id4

from interactions import (
    AutoShardedClient,
    Button,
    ButtonStyle,
    ComponentContext,
    Embed,
    EmbedAuthor,
    EmbedField,
    PartialEmoji,
    SlashContext,
)

from classes.anilist import AniListTrailerStruct
from classes.i18n import LanguageDict
from modules.const import BOT_TOKEN, EMOJI_FORBIDDEN
from modules.const import EMOJI_UNEXPECTED_ERROR as EUNER
from modules.const import EMOJI_USER_ERROR, LANGUAGE_CODE
from modules.i18n import fetch_language_data

deflang = fetch_language_data(LANGUAGE_CODE, use_raw=True)


def snowflake_to_datetime(snowflake: int) -> int:
    """
    Convert a Discord snowflake ID to a Unix timestamp.

    Args:
        snowflake (int): A snowflake ID, which is a unique identifier used by Discord to identify objects such as messages and users.

    Returns:
        int: A Unix timestamp representing the time at which the Discord object associated with the snowflake was created.

    Example:
        >>> snowflake_to_datetime(81906984837386880)
        1326169600
    """
    timestamp_bin = bin(int(snowflake) >> 22)
    timestamp_dec = int(timestamp_bin, 0)
    timestamp_unix = (timestamp_dec + 1420070400000) // 1000

    return timestamp_unix


def trim_synopsis(message: str) -> str:
    """
    Trim a string to 1000 characters and add ellipsis if it exceeds that length.

    Args:
        message (str): The string to be trimmed.

    Returns:
        str: The trimmed string with ellipsis appended if the original string exceeded 1000 characters.

    Example:
        >>> trim_synopsis("This is a very long string that is over 1000 characters and needs to be trimmed.")
        'This is a very long string that is over 1000 characters and needs to be trimmed...'
    """
    if len(message) > 1000:
        msg = message[:1000]
        # trim spaces
        msg = msg.strip()
        return msg + "..."
    return message


def sanitize_markdown(text: str) -> str:
    """
    Sanitize a string of Markdown-formatted text by escaping certain characters.

    The following characters are escaped: * _ ` ~ | > < [ ] ( ) / @

    Args:
        text (str): The string of Markdown-formatted text to sanitize.

    Returns:
        str: The sanitized string of text.
    """
    replacements = {
        "\\": "\\\\",
        "_": "\\_",
        "(": "\\(",
        ")": "\\)",
        "[": "\\[",
        "]": "\\]",
        "@": "\\@",
        "*": "\\*",
        "/": "\\/",
        "#": "\\#",
        "`": "\\`",
        "<": "\\<",
        ">": "\\>",
        "|": "\\|",
        "~": "\\~",
    }

    for pattern, repl in replacements.items():
        text = text.replace(pattern, repl)

    return text


def convert_html_to_markdown(text: str) -> str:
    """
    Convert a string of HTML-formatted text to Markdown.

    Args:
        text (str): The string of HTML-formatted text to convert.

    Returns:
        str: The converted string of Markdown-formatted text.
    """
    replacements = {
        r"\n": "",
        r"<(/)?i>|<(/)?em>": "*",
        r"<(/)?b>|<(/)?strong>": "**",
        r"<(/)?u>": "__",
        r"<(/)?strike>|<(/)?s>": "~~",
        r"<(/)?br>": "\n",
    }

    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    return text


def get_random_seed(value: int = 9) -> int:
    """
    Get a random seed number with a specific length.

    Args:
        value (int): The length of the seed number to generate. Defaults to 9.

    Returns:
        int: A random seed number with the specified length.
    """
    seed = id4()

    # negate value
    value = -value

    seed = int(str(seed.int)[value:])
    return seed


def generate_search_embed(
    language: str,
    mediaType: str,
    platform: str,
    homepage: str,
    title: str,
    color: int,
    icon: str,
    query: str,
    results: list[EmbedField],
) -> Embed:
    """
    Generate an embed for search selections.

    Args:
        language (str): The language of the search results.
        mediaType (str): The media type of the search results.
        platform (str): The platform of the search results.
        homepage (str): The homepage of the search results.
        title (str): The title of the search embed.
        color (int): The color of the search embed.
        icon (str): The icon of the search embed.
        query (str): The search query string.
        results (list[EmbedField]): The search results to display in the embed.

    Returns:
        Embed: The generated search selection embed.
    """
    l_: LanguageDict = fetch_language_data(code=language, use_raw=True)
    match len(results):
        case 1:
            count = l_["quantities"][f"{mediaType}"]["one"]
        case 2:
            count = l_["quantities"][f"{mediaType}"]["two"]
        case _:
            count = l_["quantities"][f"{mediaType}"]["many"].format(count=len(results))
    dcEm = Embed(
        author=EmbedAuthor(name=platform, url=homepage, icon_url=icon),
        color=color,
        title=title,
        description=l_["commons"]["search"]["result"].format(COUNT=count, QUERY=query),
        fields=results,  # type: ignore
    )
    dcEm.set_thumbnail(url=icon)

    return dcEm


def generate_utils_except_embed(
    description: str,
    field_name: str,
    field_value: str,
    error: str,
    language: str = "en_US",
    color: int = 0xFF0000,
) -> Embed:
    """
    Generate an embed for exceptions in the utilities module.

    Args:
        description (str): A description of the error that occurred.
        field_name (str): The name of the field to include in the embed.
        field_value (str): The value of the field to include in the embed.
        error (str): The error message to include in the embed.
        language (str, optional): The language code to use for the error message. Defaults to "en_US".
        color (int, optional): The color of the embed. Defaults to 0xFF0000 (red).

    Returns:
        Embed: A Discord embed object containing information about the error.

    Example:
        >>> generate_utils_except_embed("An error occurred while processing the request.", "Field", "Value", "Error message")
        <discord.Embed object at 0x...>
    """
    l_: LanguageDict = fetch_language_data(code=language, use_raw=True)
    emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EUNER)
    dcEm = Embed(
        color=color,
        title=l_["commons"]["error"],
        description=description,
        fields=[
            EmbedField(name=field_name, value=field_value, inline=False),
            EmbedField(
                name=l_["commons"]["reason"], value=f"```md\n{error}\n```", inline=False
            ),
        ],  # type: ignore
    )
    dcEm.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm


def generate_commons_except_embed(
    description: str,
    error: str,
    lang_dict: dict = deflang,  # type: ignore
    color: int = 0xFF0000,
) -> Embed:
    """
    Generate an embed for general exceptions.

    Args:
        description (str): A description of the error that occurred.
        error (str): The error message to include in the embed.
        lang_dict (dict): A dictionary containing language codes and their associated values. Defaults to default language set on .env.
        color (int, optional): The color of the embed. Defaults to 0xFF0000 (red).

    Returns:
        Embed: A Discord embed object containing information about the error.

    Example:
        >>> lang_dict: LanguageDict = fetch_language_data(code="en_US", use_raw=True)
        >>> generate_commons_except_embed("An error occurred while processing the request.", "Error message", lang_dict)
        <discord.Embed object at 0x...>
    """
    l_ = lang_dict
    emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EUNER)
    dcEm = Embed(
        color=color,
        title=l_["commons"]["error"],
        description=description,
        fields=[
            EmbedField(
                name=l_["commons"]["reason"], value=f"```md\n{error}\n```", inline=False
            )  # type: ignore
        ],
    )
    dcEm.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm


def generate_trailer(data: dict | AniListTrailerStruct, is_mal: bool = False) -> Button:
    """
    Generate a button for playing the trailer of a given anime.

    Args:
        data (dict | AniListTrailerStruct): A dictionary/dataclass containing information about the anime.
        is_mal (bool, optional): Whether the anime is from MyAnimeList. Defaults to False..

    Returns:
        Button: A Discord button object for playing the anime's trailer.

    Example:
        >>> data = {"id": "https://www.youtube.com/watch?v=WSrw7cTpNkM"}
        >>> generate_trailer(data)
        <discord_components.button.Button object at 0x...>
    """
    if isinstance(data, dict):
        ytid = data.get("youtube_id" if is_mal else "youtube")
    elif isinstance(data, AniListTrailerStruct):
        ytid = data.id
    else:
        raise TypeError("Invalid data type.")
    if not ytid:
        raise ValueError("No trailer found.")
    button = Button(
        label="PV/CM on YouTube",
        style=ButtonStyle.LINK,
        url=f"https://www.youtube.com/watch?v={ytid}",
        emoji=PartialEmoji(id=975564205228965918, name="Youtube"),
    )
    return button


async def get_parent_nsfw_status(snowflake: int) -> bool:
    """
    Get the age restriction status of a channel's parent if the command was invoked in a thread or forum.

    Args:
        snowflake (int): The ID of the channel.

    Returns:
        bool: The age restriction status of the channel's parent, or False if the channel does not have a parent or
              the parent's age restriction status could not be determined.

    Example:
        >>> result = await get_parent_nsfw_status(123456789)
        >>> print(result)
        True
    """
    bot_http = AutoShardedClient(token=BOT_TOKEN).http
    guild = await bot_http.get_channel(channel_id=snowflake)
    # close the connection
    return guild.get("nsfw", False)


async def get_nsfw_status(context: ComponentContext | SlashContext) -> bool:
    """
    Check if a channel is NSFW or not

    Args:
        context (ComponentContext | SlashContext): The context of the command.

    Returns:
        bool: The age restriction status of the channel, or False if the channel does not have a parent or the parent's age restriction status could not be determined.
    """
    channel = context.channel
    if channel.type == 11 or channel.type == 12:
        prId = channel.parent_id
        nsfwBool = await get_parent_nsfw_status(prId)
    else:
        nsfwBool = channel.nsfw
    return nsfwBool


def convert_float_to_time(day_float: float) -> str:
    """
    Convert a float representing a number of days to a string representing the number of days, hours, and minutes.

    Args:
        day_float (float): The number of days.

    Returns:
        str: A string representing the number of months, days, hours, and minutes.
    """
    # Convert day float to total seconds
    total_seconds = int(day_float * 24 * 60 * 60)

    # Create a timedelta object with the total seconds
    delta = timedelta(seconds=total_seconds)

    # Extract months, days, hours, and minutes from the timedelta object
    months = delta.days // 30
    days = delta.days % 30
    hours = (delta.seconds // 3600) % 24
    minutes = (delta.seconds // 60) % 60
    months = f"{months} months, " if months else ""

    # Format the result string
    result = f"{months}{days} days, {hours} hours, {minutes} minutes"

    return result


class PlatformErrType(Enum):
    """Error Type for Platform"""

    USER = EMOJI_USER_ERROR
    NSFW = EMOJI_FORBIDDEN
    SYSTEM = EUNER


def platform_exception_embed(
    description: str,
    error: str,
    lang_dict: dict,
    error_type: PlatformErrType | str = PlatformErrType.SYSTEM,
    color: int = 0xFF0000,
) -> Embed:
    """
    Generate an embed of exception reason for platform.

    Args:
        description (str): Description of the error
        error (str): Error message
        lang_dict (dict): Language dictionary
        error_type (PlatformErrType | str, optional): Error type. Defaults to PlatformErrType.SYSTEM.
        color (int, optional): Embed color. Defaults to 0xFF0000.

    Returns:
        Embed: Embed object
    """
    l_ = lang_dict
    if isinstance(error_type, PlatformErrType):
        error_type = error_type.value
    else:
        error_type = str(error_type)
    emoji = re.sub(r"(<:.*:)(\d+)(>)", r"\2", error_type)
    dcEm = Embed(
        color=color,
        title=l_["commons"]["error"],
        description=description,
        fields=[
            EmbedField(name=l_["commons"]["reason"], value=error, inline=False)
        ],  # type: ignore
    )
    dcEm.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm
