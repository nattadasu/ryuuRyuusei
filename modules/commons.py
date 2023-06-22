"""
# Commons Module

This module contains the common functions used by the other modules.
"""

import re
import traceback
from datetime import datetime, timedelta, timezone
from enum import Enum
from re import sub as rSub
from uuid import uuid4 as id4

from interactions import (Button, ButtonStyle, ClientUser, ComponentContext,
                          Embed, EmbedAuthor, EmbedField, Member, PartialEmoji,
                          SlashContext, User)

from classes.anilist import AniListTrailerStruct
from classes.i18n import LanguageDict
from modules.const import EMOJI_FORBIDDEN
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
        "\r": " ",  # remove carriage returns
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

    return text.strip()


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
            count = l_["quantities"][f"{mediaType}"]["many"].format(
                count=len(results))
    dcEm = Embed(
        author=EmbedAuthor(name=platform, url=homepage, icon_url=icon),
        color=color,
        title=title,
        description=l_["commons"]["search"]["result"].format(
            COUNT=count, QUERY=query),
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
    dcEm.set_thumbnail(
        url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm


def generate_commons_except_embed(
    description: str,
    error: str | Exception,
    language: dict | str = "en_US",  # type: ignore
    color: int = 0xFF0000,
) -> Embed:
    """
    Generate an embed for general exceptions.

    Args:
        description (str): A description of the error that occurred.
        error (str): The error message to include in the embed.
        language (dict | str, optional): The language code to use for the error message. Defaults to "en_US".
        color (int, optional): The color of the embed. Defaults to 0xFF0000 (red).

    Returns:
        Embed: A Discord embed object containing information about the error.

    Example:
        >>> lang_dict: LanguageDict = fetch_language_data(code="en_US", use_raw=True)
        >>> generate_commons_except_embed("An error occurred while processing the request.", "Error message", lang_dict)
        <discord.Embed object at 0x...>
    """
    if isinstance(language, str):
        l_ = fetch_language_data(code=language, use_raw=True)
    else:
        l_ = language

    if isinstance(error, Exception):
        error = str(error)

    emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EUNER)
    dcEm = Embed(
        color=color,
        title=l_["commons"]["error"],
        description=description,
        fields=[
            EmbedField(
                name=l_["commons"]["reason"], value=f"{error}", inline=False
            )  # type: ignore
        ],
    )
    dcEm.set_thumbnail(
        url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm


def generate_trailer(
        data: dict | AniListTrailerStruct,
        is_mal: bool = False) -> Button:
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


async def get_nsfw_status(context: ComponentContext | SlashContext) -> bool | None:
    """
    Check if a channel is NSFW or not

    Args:
        context (ComponentContext | SlashContext): The context of the command.

    Returns:
        bool: The age restriction status of the channel, or False if the channel does not have a parent or the parent's age restriction status could not be determined.
    """
    channel = context.channel
    if channel.type in (11, 12):
        nsfwBool = channel.parent_channel.nsfw
    else:
        nsfwBool = channel.nsfw
    return nsfwBool


def pluralize(x):
    """
    Add an "s" to the end of a word if the number is greater than 1.
    Will be dropped once i18n is implemented.

    Args:
        x (int): The number to check.

    Returns:
        str: An "s" if the number is greater than 1, otherwise an empty string.
    """
    return "s" if x > 1 else ""


def convert_float_to_time(
    time_float: float | int,
    use_seconds: bool = False,
    show_weeks: bool = False,
    show_milliseconds: bool = False,
) -> str:
    """
    Convert a float representing a number of days to a string representing the number of days, hours, and minutes.

    Args:
        time_float (float, int): The number of days.
        use_seconds (bool, optional): Is the number of days in seconds? If not, it is assumed to be in days. Defaults to False.
        show_weeks (bool, optional): Whether to show weeks in the output. Defaults to False.
        show_milliseconds (bool, optional): Whether to show milliseconds in the output. Defaults to False.

    Returns:
        str: A string representing the number of months, days, hours, and minutes.
    """
    if use_seconds:
        total_seconds = time_float
    else:
        # Convert day float to total seconds
        total_seconds = float(time_float * 24 * 60 * 60)

    # Create a timedelta object with the total seconds
    delta = timedelta(seconds=total_seconds)

    # Extract years, months, days, hours, minutes, and seconds from the
    # timedelta object
    years = delta.days // 365
    months = delta.days % 365 // 30
    if show_weeks:
        weeks = delta.days % 365 % 30 // 7
        days = delta.days % 365 % 30 % 7
    else:
        weeks = None
        days = delta.days % 365 % 30
    hours = delta.seconds // 3600
    minutes = delta.seconds // 60 % 60
    seconds = delta.seconds % 60
    if show_milliseconds:
        milliseconds = delta.microseconds // 1000
    else:
        milliseconds = None

    words = [
        f"{years} year{pluralize(years)}" if years else "",
        f"{months} month{pluralize(months)}" if months else "",
        f"{weeks} week{pluralize(weeks)}" if weeks else "",
        f"{days} day{pluralize(days)}" if days else "",
        f"{hours} hour{pluralize(hours)}" if hours else "",
        f"{minutes} minute{pluralize(minutes)}" if minutes else "",
        f"{seconds} second{pluralize(seconds)}" if seconds else "",
        f"{milliseconds} millisecond{pluralize(milliseconds)}" if milliseconds else "",
    ]

    result = ", ".join(filter(None, words))

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
    dcEm.set_thumbnail(
        url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm


def generate_delete_button(
    custom_id: str = "message_delete",
    emoji: PartialEmoji | str | None = "🗑️",
    style: ButtonStyle = ButtonStyle.DANGER,
    label: str = "Delete",
    disabled: bool = False,
) -> Button:
    """
    Generate a delete button.

    Args:
        custom_id (str, optional): Custom ID of the button. Defaults to "message_delete".
        emoji (PartialEmoji | str | None, optional): Emoji of the button. Defaults to "🗑️".
        style (ButtonStyle, optional): Style of the button. Defaults to ButtonStyle.DANGER.
        label (str, optional): Label of the button. Defaults to "Delete".
        disabled (bool, optional): Whether the button is disabled. Defaults to False.
    """
    button = Button(
        style=style,
        label=label,
        custom_id=custom_id,
        emoji=emoji,
        disabled=disabled,
    )
    return button


def save_traceback_to_file(
    command: str,
    author: Member | User | ClientUser,
    error: Exception,
    mute_error: bool = False,
) -> None:
    """
    Save traceback to a file.

    Args:
        command (str): Command name
        author (Member | User | ClientUser): Author of the command
        error (Exception): Error
        mute_error (bool, optional): Whether to mute the error. Defaults to False.

    Raises:
        error (Exception): Re-raise the error (for logging purpose)
    """
    if not isinstance(error, Exception):
        return
    error_type = type(error).__name__
    error_str = str(error)
    error_traceback = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    with open(
        f"errors/{command}_{author.id}_{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(f"{error_type}: {error_str}\n\n{error_traceback}")
    if mute_error is False:
        # re-raise the error
        raise error


__all__ = [
    "convert_float_to_time",
    "convert_html_to_markdown",
    "generate_commons_except_embed",
    "generate_delete_button",
    "generate_search_embed",
    "generate_trailer",
    "generate_utils_except_embed",
    "get_nsfw_status",
    "get_random_seed",
    "platform_exception_embed",
    "PlatformErrType",
    "pluralize",
    "sanitize_markdown",
    "save_traceback_to_file",
    "snowflake_to_datetime",
    "trim_synopsis",
]
