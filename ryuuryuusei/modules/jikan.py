"""
# Jikan API module

This module contains only functions to interact with the Jikan API.

API wrapper specifically are saved in classes/jikan.py
"""

from classes.jikan import JikanApi
from modules.const import CLUB_ID


async def get_member_clubs(username: str) -> list[dict]:
    """
    Get a list of clubs that a user is a member of

    Args:
        username (str): MAL username of the user

    Returns:
        dict: List of clubs that the user is a member of
    """
    async with JikanApi() as jikan:
        clubs = await jikan.get_user_clubs(username)
        return clubs


async def check_if_club_in_list(clubs: list[dict]) -> bool:
    """
    Check if the club is in the list of clubs

    Args:
        clubs (list[dict]): List of clubs

    Returns:
        bool: True if the club is in the list, False if not
    """
    return any(str(club["mal_id"]) == str(CLUB_ID) for club in clubs)


async def check_club_membership(username: str) -> bool:
    """
    Check if a user is a member of the club

    Args:
        username (str): MAL username of the user

    Returns:
        bool: True if the user is a member of the club, False if not
    """
    clubs = await get_member_clubs(username)
    return await check_if_club_in_list(clubs)
