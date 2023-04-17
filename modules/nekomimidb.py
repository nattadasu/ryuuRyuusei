"""# nattadasu/nekomimiDb Module

This module contains the functions used by the nekomimiDb module."""

import pandas as pd
from interactions import Embed, EmbedAttachment, EmbedAuthor, EmbedField
from interactions import SlashContext as sctx

from modules.commons import getRandom
from modules.platforms import getPlatformColor

from classes.nekomimidb import NekomimiDb as neko


def generateNekomimi(row: dict, lang: dict) -> Embed:
    """Generate nekomimi embed"""
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = Embed(
        title=f"{mediaSource}",
        images=[
            EmbedAttachment(
                url=str(img),
            ),
        ],
        color=col,
        author=EmbedAuthor(
            name=lang['author'],
            url="https://github.com/nattadasu/nekomimiDb",
            icon_url="https://cdn.discordapp.com/avatars/1080049635621609513/6f79d106de439f917179b7ef052a6ca8.png",
        ),
        fields=[
            EmbedField(
                name=lang['source']['title'],
                value=f"[{lang['source']['value']}]({imageSourceUrl})",
                inline=True
            ),
            EmbedField(
                name=lang['artist'],
                value=f"[{artist}]({artistUrl})",
                inline=True
            ),
        ],
    )

    return dcEm


async def nekomimiSubmit(ctx: sctx, lang: dict, gender: neko.Gender = None):
    """Submit a nekomimi image to Discord"""
    data = neko(gender).get_random_nekomimi()
    dcEm = generateNekomimi(row=data, lang=lang)
    await ctx.send("", embeds=dcEm)
