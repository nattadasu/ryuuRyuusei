"""
# nattadasu/nekomimiDb Module

This module contains the functions used by the nekomimiDb module.
"""

from interactions import Embed, EmbedAuthor, EmbedField
from interactions import SlashContext as sctx

from classes.nekomimidb import NekomimiDb as neko
from classes.nekomimidb import NekomimiDbStruct, NekomimiGender
from modules.platforms import get_platform_color, get_platform_name


def determine_domain(url: str) -> str:
    """
    Determine the domain of a URL then return it as Human Readable.

    Args:
        url (str): The URL to check

    Returns:
        str: The domain of the URL
    """
    # split the url by the slashes
    urls = url.split("/")
    domain = urls[2]
    subs = domain.split(".")
    for sub in subs:
        try:
            guess_name = get_platform_name(sub)
        except ValueError:
            guess_name = "Unknown"
        if guess_name != "Unknown":
            return guess_name
    return domain


def generate_nekomimi_embed(row: NekomimiDbStruct) -> Embed:
    """
    Generate nekomimi embed

    Args:
        row (NekomimiDbStruct): A row from the database.

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
            name="Powered by nekomimiDb from nattadasu",
            url="https://github.com/nattadasu/nekomimiDb",
            icon_url="https://cdn.discordapp.com/avatars/1080049635621609513/6f79d106de439f917179b7ef052a6ca8.png",
        ),
    )
    dcEm.add_fields(
        EmbedField(
            name="Image Source",
            value=f"[{determine_domain(imageSourceUrl)}]({imageSourceUrl})",
            inline=True,
        ),
        EmbedField(
            name="Artist",
            value=f"[{artist}]({artistUrl})",
            inline=True),
    )
    dcEm.set_image(url=img)

    return dcEm


async def submit_nekomimi(ctx: sctx, gender: NekomimiGender | None = None) -> None:
    """
    Submit a nekomimi image to Discord

    Args:
        ctx (interactions.SlashContext): Discord Slash Context
        gender (neko.Gender, optional): Gender of a character. Defaults to None.

    Returns:
        None
    """
    await ctx.defer()
    data = neko(gender).get_random_nekomimi()
    dcEm = generate_nekomimi_embed(row=data)
    await ctx.send("", embeds=dcEm)
