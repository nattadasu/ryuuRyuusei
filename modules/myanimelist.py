"""# MyAnimeList Module

This module contains modules that are related to MyAnimeList or Jikan API."""

from json import dumps
from enum import Enum
import re

from interactions import (ComponentContext, Embed, EmbedAttachment,
                          EmbedAuthor, EmbedField, EmbedFooter, EmbedProvider,
                          SlashContext)
import pandas as pd

from classes.myanimelist import MyAnimeList
from modules.const import MYANIMELIST_CLIENT_ID, EMOJI_UNEXPECTED_ERROR, EMOJI_USER_ERROR, EMOJI_FORBIDDEN
from modules.commons import getRandom

def lookupRandomAnime() -> int:
    """Lookup random anime from MAL"""
    seed = getRandom()
    # open database/mal.csv
    df = pd.read_csv("database/mal.csv", sep="\t")
    # get random anime
    randomAnime = df.sample(n=1, random_state=seed)
    # get anime id
    randomAnimeId: int = randomAnime['mal_id'].values[0]
    return randomAnimeId


async def searchMalAnime(title: str) -> dict:
    """Search anime via MyAnimeList API"""
    fields = [
        "id",
        "title",
        "alternative_titles\{ja\}",
        "start_season",
        "media_type",
    ]
    fields = ",".join(fields)
    async with MyAnimeList(MYANIMELIST_CLIENT_ID) as mal:
        data = await mal.search(title, limit=5, fields=fields)
    return data['data']

async def getMalAnime(anime_id: int) -> dict:
    """Get anime information via MyAnimeList API"""
    fields = [
        "id",
        "title",
        "start_season",
        "media_type",
        "status",
        "num_episodes",
        "mean",
        "rank",
        "popularity",
        "favorites",
        "synopsis",
        "background",
        "genres",
        "source",
        "duration",
        "studios",
        "scored_by",
        "rating",
        "image_url",
        "trailer_url",
        "url",
    ]
    fields = ",".join(fields)
    async with MyAnimeList(MYANIMELIST_CLIENT_ID) as mal:
        data = await mal.anime(anime_id, fields=fields)
    return data['data']


class MalErrType(Enum):
    """MyAnimeList Error Type"""
    USER = EMOJI_USER_ERROR
    NSFW = EMOJI_FORBIDDEN
    SYSTEM = EMOJI_UNEXPECTED_ERROR

def malExceptionEmbed(
    description: str,
    error: str,
    lang_dict: dict,
    error_type: MalErrType | str = MalErrType.SYSTEM,
    color: hex = 0xFF0000,
) -> Embed:
    l_ = lang_dict
    if isinstance(error_type, MalErrType):
        error_type = error_type.value
    emoji = re.sub(r"(<:.*:)(\d+)(>)", r"\2", error_type)
    dcEm = Embed(
        color=color,
        title=l_['commons']['error'],
        description=description,
        fields=[
            EmbedField(
                name=l_['commons']['reason'],
                value=error,
                inline=False
            )
        ],
        thumbnail=EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
        ),
    )

    return dcEm
