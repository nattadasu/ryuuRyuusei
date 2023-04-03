import csv
import datetime
import html
import json
import time
from json import loads as jload
from urllib.parse import quote as urlquote
from uuid import uuid4 as id4
from zoneinfo import ZoneInfo

import aiohttp
import html5lib
import interactions
import pandas as pd
import regex as re
from bs4 import BeautifulSoup
from jikanpy import AioJikan
import asyncio

from modules.const import *

bannedTags = [
    'Amputation', 'Anal Sex', 'Ashikoki', 'Asphyxiation',
    'Blackmail', 'Bondage', 'Boobjob', 'Cumflation',
    'Cunnilingus', 'Deepthroat', 'DILF', 'Fellatio',
    'Femdom', 'Futanari', 'Group Sex', 'Handjob',
    'Human Pet', 'Incest', 'Inseki', 'Irrumatio',
    'Lactation', 'Masochism', 'Masturbation', 'MILF',
    'Nakadashi', 'Pregnant', 'Prostitution', 'Public Sex',
    'Rape', 'Rimjob', 'Sadism', 'Scat',
    'Scissoring', 'Sex Toys', 'Squirting', 'Sumata',
    'Sweat', 'Tentacles', 'Threesome', 'Vore',
    'Voyeur', 'Watersports', 'Omegaverse'
]

invAa = {
    'title': None,
    'anidb': None,
    'anilist': None,
    'animeplanet': None,
    'anisearch': None,
    'annict': None,
    'kaize': None,
    'kitsu': None,
    'livechart': None,
    'myanimelist': None,
    'notify': None,
    'otakotaku': None,
    'shikimori': None,
    'shoboi': None,
    'silveryasha': None,
    'trakt': None,
    'trakt_type': None,
    'trakt_season': None
}

simkl0rels = {
    'title': None,
    "simkl": None,
    "slug": None,
    "poster": None,
    "fanart": None,
    "anitype": "tv",
    "type": "anime",
    "allcin": None,
    "anfo": None,
    "ann": None,
    "imdb": None,
    "mal": None,
    "offjp": None,
    "tmdb": None,
    "tvdb": None,
    "tvdbslug": None,
    "wikien": None,
    "wikijp": None,
}

traktHeader = {
    'Content-Type': 'applications/json',
    'trakt-api-key': TRAKT_CLIENT_ID,
    'trakt-api-version': TRAKT_API_VERSION
}

jikan = AioJikan()


def snowflake_to_datetime(snowflake: int) -> int:
    """Convert Discord snowflake to datetime object."""
    timestamp_bin = bin(int(snowflake) >> 22)
    timestamp_dec = int(timestamp_bin, 0)
    timestamp_unix = (timestamp_dec + 1420070400000) / 1000

    return timestamp_unix


def returnException(error: str) -> str:
    """Format exception message to a message string"""
    return f"""{EMOJI_UNEXPECTED_ERROR} **Error found!**
There's something wrong with the bot while processing your request.

Error is: {error}"""


def exceptionsToEmbed(error: str) -> interactions.Embed:
    """Format exception message to a embed"""
    embed = interactions.Embed(
        color=0xff0000,
        title="Error",
        description=error,
    )
    return embed


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


def generateTrailer(data: dict, isMal: bool = False) -> interactions.Button:
    """Generate a button to a YouTube video"""
    if isMal:
        ytid = data['youtube_id']
    else:
        ytid = data['id']
    final = interactions.Button(
        type=interactions.ComponentType.BUTTON,
        label="PV/CM on YouTube",
        style=interactions.ButtonStyle.LINK,
        url=f"https://www.youtube.com/watch?v={ytid}",
        emoji=interactions.Emoji(
            id=975564205228965918,
            name="Youtube"
        )
    )
    return final


async def getParentNsfwStatus(snowflake: int) -> dict:
    """Get a channel age restriction status if command was invoked in a thread/forum"""
    botHttp = interactions.HTTPClient(token=BOT_TOKEN)
    guild = await botHttp.get_channel(channel_id=snowflake)
    # close the connection
    return guild['nsfw']


async def getUserData(user_snowflake: int) -> dict:
    """Get user's Discord information"""
    botHttp = interactions.HTTPClient(token=BOT_TOKEN)
    member = await botHttp.get_user(user_id=user_snowflake)
    # close the connection
    return member


async def getGuildMemberData(guild_snowflake: int, user_snowflake: int) -> dict:
    """Get user's Discord information about current server"""
    botHttp = interactions.HTTPClient(token=BOT_TOKEN)
    member = await botHttp.get_member(guild_id=guild_snowflake, member_id=user_snowflake)
    return member


def getRandom(value: int = 9) -> int:
    """Get a random seed number with a specific length"""
    seed = id4()
    # negate value
    value = -value
    seed = int(str(seed.int)[value:])
    return seed


def generateSearchSelections(
    platform: str,
    homepage: str,
    title: str,
    color: hex,
    icon: str,
    query: str,
    results: list[interactions.EmbedField],
) -> interactions.Embed:
    dcEm = interactions.Embed(
            author=interactions.EmbedAuthor(
                name=platform,
                url=homepage,
                icon_url=icon
            ),
            thumbnail=interactions.EmbedImageStruct(
                url=icon
            ),
            color=color,
            title=title,
            description=f"Found **{len(results)} results** for `{query}`, please select by choosing right option in the dropdown below",
            fields=results
        )

    return dcEm


async def getNsfwStatus(channel: interactions.CommandContext.channel) -> bool:
    """Check if a channel is NSFW or not"""
    if channel.type == 11 or channel.type == 12:
        prId = channel.parent_id
        nsfwBool = await getParentNsfwStatus(prId)
    else:
        nsfwBool = channel.nsfw
    return nsfwBool
