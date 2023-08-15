"""
# Internationalization Bot Module

DROPPED: This module is no longer being developed and will be removed in a future release, and is only included for
compatibility with older versions of the bot.
"""


from json import loads as jlo
from typing import Any

from interactions import BaseContext, InteractionContext

from modules.const import LANGUAGE_CODE


def fetch_language_data(code: str, use_raw: bool = True) -> dict[str, Any]:
    """
    Get the language strings for a given language code

    Args:
        code (str): The language code to get the strings for
        use_raw (bool): Whether to return the raw JSON data or not

    Returns:
        dict[str, Any]: The language strings
    """
    code = "en_US"
    try:
        with open(f"i18n/{code}.json", "r", encoding="utf-8") as file:  # skipcq: PTC-W6004
            data: dict[str, Any] = jlo(file.read())
            if use_raw:
                return data
            return data["strings"]  # type: ignore
    except FileNotFoundError:
        return fetch_language_data(LANGUAGE_CODE)


def read_user_language(ctx: BaseContext | InteractionContext) -> str:
    """
    Read the user's language preference from the database

    Args:
        ctx (BaseContext | InteractionContext): The context to read the user's language preference from

    Returns:
        str: The user's language preference
    """
    del ctx  # unused
    return "en_US"
