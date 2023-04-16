"""# MyAnimeList Module

This module contains modules that are related to MyAnimeList or Jikan API."""

from json import dumps

from interactions import (ComponentContext, Embed, EmbedAttachment,
                          EmbedAuthor, EmbedField, EmbedFooter, EmbedProvider,
                          SlashContext)

from modules.classes.myanimelist import MyAnimeList
from modules.const import MYANIMELIST_CLIENT_ID

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
