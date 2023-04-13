"""# Commons Module

This module contains the common functions used by the other modules."""

from uuid import uuid4 as id4


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
