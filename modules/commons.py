"""# Commons Module

This module contains the common functions used by the other modules."""

from re import sub as rSub
from uuid import uuid4 as id4

from interactions import (Embed, EmbedAttachment, EmbedAuthor, EmbedField,
                          EmbedFooter, EmbedProvider, Client, Button,
                          ButtonStyle, PartialEmoji)

from modules.const import EMOJI_UNEXPECTED_ERROR as EUNER
from modules.const import EMOJI_USER_ERROR as EUSER
from modules.const import BOT_TOKEN
from modules.i18n import lang


def snowflake_to_datetime(snowflake: int) -> int:
    """Convert Discord snowflake to datetime object."""
    timestamp_bin = bin(int(snowflake) >> 22)
    timestamp_dec = int(timestamp_bin, 0)
    timestamp_unix = (timestamp_dec + 1420070400000) / 1000

    return timestamp_unix


def trimCyno(message: str) -> str:
    """Trim synopsys to 1000 characters"""
    if len(message) > 1000:
        msg = message[:1000]
        # trim spaces
        msg = msg.strip()
        return msg + "..."
    else:
        return message


def sanitizeMarkdown(text: str) -> str:
    text = text.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`").replace("~", "\\~").replace("|", "\\|").replace(">", "\\>").replace(
        "<", "\\<").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("/", "\\/").replace("@", "\\@")
    return text


def getRandom(value: int = 9) -> int:
    """Get a random seed number with a specific length"""
    seed = id4()
    # negate value
    value = -value
    seed = int(str(seed.int)[value:])
    return seed


def generateSearchSelections(
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
    """Generate an embed for search selections."""
    l_ = lang(code=language, useRaw=True)
    match len(results):
        case 1:
            count = l_["quantities"][f"{mediaType}"]["one"]
        case 2:
            count = l_["quantities"][f"{mediaType}"]["two"]
        case _:
            count = l_["quantities"][f"{mediaType}"]["many"].format(
                count=len(results)
            )
    dcEm = Embed(
            author=EmbedAuthor(
                name=platform,
                url=homepage,
                icon_url=icon
            ),
            thumbnail=EmbedAttachment(
                url=icon
            ),
            color=color,
            title=title,
            description=l_['commons']['search']['result'].format(
                COUNT=count,
                QUERY=query
            ),
            fields=results,
        )

    return dcEm


def utilitiesExceptionEmbed(
    description: str,
    field_name: str,
    field_value: str,
    error: str,
    language: str = "en_US",
    color: hex = 0xFF0000,
) -> Embed:
    """Generate an embed for exceptions in the utilities module."""
    l_ = lang(code=language, useRaw=True)
    emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EUNER)
    dcEm = Embed(
        color=color,
        title=l_['commons']['error'],
        description=description,
        fields=[
            EmbedField(
                name=field_name,
                value=field_value,
                inline=False
            ),
            EmbedField(
                name=l_['commons']['reason'],
                value=f"```md\n{error}\n```",
                inline=False
            )
        ],
        thumbnail=EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
        ),
    )

    return dcEm


def generalExceptionEmbed(
    description: str,
    error: str,
    lang_dict: dict,
    color: hex = 0xFF0000,
) -> Embed:
    l_ = lang_dict
    emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EUNER)
    dcEm = Embed(
        color=color,
        title=l_['commons']['error'],
        description=description,
        fields=[
            EmbedField(
                name=l_['commons']['reason'],
                value=f"```md\n{error}\n```",
                inline=False
            )
        ],
        thumbnail=EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
        ),
    )

    return dcEm


def generateTrailer(data: dict, isMal: bool = False, isSimkl: bool = False) -> Button:
    """Generate a button to a YouTube video"""
    if isMal:
        ytid = data['youtube_id']
    elif isSimkl:
        ytid = data['youtube']
    else:
        ytid = data['id']
    final = Button(
        label="PV/CM on YouTube",
        style=ButtonStyle.LINK,
        url=f"https://www.youtube.com/watch?v={ytid}",
        emoji=PartialEmoji(
            id=975564205228965918,
            name="Youtube"
        )
    )
    return final


async def getParentNsfwStatus(snowflake: int) -> dict:
    """Get a channel age restriction status if command was invoked in a thread/forum"""
    botHttp = Client(token=BOT_TOKEN).http
    guild = await botHttp.get_channel(channel_id=snowflake)
    # close the connection
    return guild['nsfw']
