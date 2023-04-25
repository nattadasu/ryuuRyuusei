"""# nattadasu/nekomimiDb Module

This module contains the functions used by the nekomimiDb module."""

from interactions import Embed, EmbedAttachment, EmbedAuthor, EmbedField
from interactions import SlashContext as sctx

from classes.nekomimidb import NekomimiDb as neko
from modules.platforms import get_platform_color


def generate_nekomimi_embed(row: dict, lang: dict) -> Embed:
    """Generate nekomimi embed

    Args:
        row (dict): A row from the database.
        lang (dict): The language dictionary.

    Returns:
        Embed: The generated nekomimi embed.
    """
    img = row["imageUrl"].values[0]
    mediaSource = row["mediaSource"].values[0]
    if mediaSource == "":
        mediaSource = "Original Character"
    artist = row["artist"].values[0]
    artistUrl = row["artistUrl"].values[0]
    imageSourceUrl = row["imageSourceUrl"].values[0]
    col = get_platform_color(row["platform"].values[0])
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
                name=lang["artist"], value=f"[{artist}]({artistUrl})", inline=True
            ),
        ],
    )

    return dcEm


async def submit_nekomimi(ctx: sctx, lang: dict, gender: neko.Gender = None):
    """Submit a nekomimi image to Discord

    Args:
        ctx (interactions.SlashContext): Discord Slash Context
        lang (dict): The language dictionary
        gender (neko.Gender, optional): Gender of a character. Defaults to None.

    Returns:
        None
    """
    data = neko(gender).get_random_nekomimi()
    dcEm = generate_nekomimi_embed(row=data, lang=lang)
    await ctx.send("", embeds=dcEm)
