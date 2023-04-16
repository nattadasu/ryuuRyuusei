"""# Commons Module

This module contains the common functions used by the other modules."""

from uuid import uuid4 as id4

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

