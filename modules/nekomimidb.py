"""# nattadasu/nekomimiDb Module

This module contains the functions used by the nekomimiDb module."""

import pandas as pd
from interactions import Embed, EmbedAttachment, EmbedAuthor, EmbedField, SlashContext as sctx

from modules.commons import getRandom
from modules.platforms import getPlatformColor

def getNekomimi(gender: str | None = None) -> dict:
    """Get a random nekomimi image from the database"""
    seed = getRandom()
    nmDb = pd.read_csv("database/nekomimiDb.tsv", sep="\t")
    nmDb = nmDb.fillna('')
    if gender is not None:
        query = nmDb[nmDb['girlOrBoy'] == f'{gender}']
    else:
        query = nmDb
    # get a random row from the query
    row = query.sample(n=1, random_state=seed)
    return row


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


async def nekomimiSubmit(ctx: sctx, lang: dict, gender: str | None = None):
    """Submit a nekomimi image to Discord"""
    data = getNekomimi(gender=gender)
    dcEm = generateNekomimi(row=data, lang=lang)
    await ctx.send("", embeds=dcEm)
