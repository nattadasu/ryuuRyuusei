"""# Commons Module

This module contains the common functions used by the other modules."""

from re import sub as rSub
from uuid import uuid4 as id4

from interactions import (Button, ButtonStyle, Client, Embed, EmbedAttachment,
                          EmbedAuthor, EmbedField, PartialEmoji)

from classes.anilist import AniListTrailerStruct
from modules.const import BOT_TOKEN
from modules.const import EMOJI_UNEXPECTED_ERROR as EUNER
from modules.const import LANGUAGE_CODE
from modules.i18n import fetch_language_data

deflang = fetch_language_data(LANGUAGE_CODE, useRaw=True)


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
    timestamp_unix = (timestamp_dec + 1420070400000) / 1000

    return timestamp_unix


def trim_cyno(message: str) -> str:
    """
    Trim a string to 1000 characters and add ellipsis if it exceeds that length.

    Args:
        message (str): The string to be trimmed.

    Returns:
        str: The trimmed string with ellipsis appended if the original string exceeded 1000 characters.

    Example:
        >>> trim_cyno("This is a very long string that is over 1000 characters and needs to be trimmed.")
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
    text = (
        text.replace("*", "\\*")
        .replace("_", "\\_")
        .replace("`", "\\`")
        .replace("~", "\\~")
        .replace("|", "\\|")
        .replace(">", "\\>")
        .replace("<", "\\<")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("/", "\\/")
        .replace("@", "\\@")
    )
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


def genrate_search_embed(
    language: str,
    mediaType: str,
    platform: str,
    homepage: str,
    title: str,
    color: hex,
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
        color (hex): The color of the search embed.
        icon (str): The icon of the search embed.
        query (str): The search query string.
        results (list[EmbedField]): The search results to display in the embed.

    Returns:
        Embed: The generated search selection embed.
    """
    l_ = fetch_language_data(code=language, useRaw=True)
    match len(results):
        case 1:
            count = l_["quantities"][f"{mediaType}"]["one"]
        case 2:
            count = l_["quantities"][f"{mediaType}"]["two"]
        case _:
            count = l_["quantities"][f"{mediaType}"]["many"].format(
                count=len(results))
    dcEm = Embed(
        author=EmbedAuthor(
            name=platform,
            url=homepage,
            icon_url=icon),
        thumbnail=EmbedAttachment(
            url=icon),
        color=color,
        title=title,
        description=l_["commons"]["search"]["result"].format(
            COUNT=count,
            QUERY=query),
        fields=results,
    )

    return dcEm


def generate_utils_except_embed(
    description: str,
    field_name: str,
    field_value: str,
    error: str,
    language: str = "en_US",
    color: hex = 0xFF0000,
) -> Embed:
    """
    Generate an embed for exceptions in the utilities module.

    Args:
        description (str): A description of the error that occurred.
        field_name (str): The name of the field to include in the embed.
        field_value (str): The value of the field to include in the embed.
        error (str): The error message to include in the embed.
        language (str, optional): The language code to use for the error message. Defaults to "en_US".
        color (hex, optional): The color of the embed. Defaults to 0xFF0000 (red).

    Returns:
        Embed: A Discord embed object containing information about the error.

    Example:
        >>> generate_utils_except_embed("An error occurred while processing the request.", "Field", "Value", "Error message")
        <discord.Embed object at 0x...>
    """
    l_ = fetch_language_data(code=language, useRaw=True)
    emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EUNER)
    dcEm = Embed(
        color=color,
        title=l_["commons"]["error"],
        description=description,
        fields=[
            EmbedField(
                name=field_name,
                value=field_value,
                inline=False),
            EmbedField(
                name=l_["commons"]["reason"],
                value=f"```md\n{error}\n```",
                inline=False),
        ],
        thumbnail=EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"),
    )

    return dcEm


def generate_commons_except_embed(
    description: str,
    error: str,
    lang_dict: dict = deflang,
    color: hex = 0xFF0000,
) -> Embed:
    """
    Generate an embed for general exceptions.

    Args:
        description (str): A description of the error that occurred.
        error (str): The error message to include in the embed.
        lang_dict (dict): A dictionary containing language codes and their associated values. Defaults to default language set on .env.
        color (hex, optional): The color of the embed. Defaults to 0xFF0000 (red).

    Returns:
        Embed: A Discord embed object containing information about the error.

    Example:
        >>> lang_dict = fetch_language_data(code="en_US", useRaw=True)
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
                name=l_["commons"]["reason"],
                value=f"```md\n{error}\n```",
                inline=False)],
        thumbnail=EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"),
    )

    return dcEm


def generate_trailer(
        data: dict | AniListTrailerStruct,
        is_mal: bool = False,
        is_simkl: bool = False) -> Button:
    """
    Generate a button for playing the trailer of a given anime.

    Args:
        data (dict | AniListTrailerStruct): A dictionary/dataclass containing information about the anime.
        is_mal (bool, optional): Whether the anime is from MyAnimeList. Defaults to False.
        is_simkl (bool, optional): Whether the anime is from Simkl. Defaults to False.

    Returns:
        Button: A Discord button object for playing the anime's trailer.

    Example:
        >>> data = {"id": "https://www.youtube.com/watch?v=WSrw7cTpNkM"}
        >>> generate_trailer(data)
        <discord_components.button.Button object at 0x...>
    """
    if is_mal:
        ytid = data["youtube_id"]
    elif is_simkl:
        ytid = data["youtube"]
    else:
        ytid = data.id
    final = Button(
        label="PV/CM on YouTube",
        style=ButtonStyle.LINK,
        url=f"https://www.youtube.com/watch?v={ytid}",
        emoji=PartialEmoji(id=975564205228965918, name="Youtube"),
    )
    return final


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
    bot_http = Client(token=BOT_TOKEN).http
    guild = await bot_http.get_channel(channel_id=snowflake)
    # close the connection
    return guild.get("nsfw", False)
