"""
# nattadasu/nekomimiDb Module

This module contains the functions used by the nekomimiDb module.
"""

from interactions import Embed, EmbedAuthor, EmbedField
from interactions import SlashContext as sctx

from classes.nekomimidb import NekomimiDb as neko
from classes.nekomimidb import NekomimiDbStruct, NekomimiGender
from modules.platforms import get_platform_color


def generate_nekomimi_embed(row: NekomimiDbStruct, lang: dict) -> Embed:
    """
    Generate nekomimi embed

    Args:
        row (NekomimiDbStruct): A row from the database.
        lang (dict): The language dictionary.

    Returns:
        Embed: The generated nekomimi embed.
    """
    img = row.imageUrl
    mediaSource = row.mediaSource
    if mediaSource in ["", None]:
        mediaSource = "Original Character"
    artist = row.artist
    artistUrl = row.artistUrl
    imageSourceUrl = row.imageSourceUrl
    col = get_platform_color(row.platform)
    # Send the image url to the user
    dcEm = Embed(
        title=f"{mediaSource}",
        color=col,
        author=EmbedAuthor(
            name=lang["author"],
            url="https://github.com/nattadasu/nekomimiDb",
            icon_url="https://cdn.discordapp.com/avatars/1080049635621609513/6f79d106de439f917179b7ef052a6ca8.png",
        ),
        fields=[
            EmbedField(
                name=lang["source"]["title"],
                value=f"[{lang['source']['value']}]({imageSourceUrl})",
                inline=True,
            ),
            EmbedField(
                name=lang["artist"],
                value=f"[{artist}]({artistUrl})",
                inline=True),
        ],
    )
    dcEm.set_image(url=img)

    return dcEm


async def submit_nekomimi(ctx: sctx, lang: dict, gender: NekomimiGender = None):
    """
    Submit a nekomimi image to Discord

    Args:
        ctx (interactions.SlashContext): Discord Slash Context
        lang (dict): The language dictionary
        gender (neko.Gender, optional): Gender of a character. Defaults to None.

    Returns:
        None
    """
    await ctx.defer()
    data = neko(gender).get_random_nekomimi()
    dcEm = generate_nekomimi_embed(row=data, lang=lang)
    await ctx.send("", embeds=dcEm)
