from datetime import datetime

import interactions as ipy

from classes.database import UserDatabase
from classes.pronoundb import PronounDBV2, Pronouns
from modules.commons import sanitize_markdown


def format_username(
    user: ipy.User | ipy.Member,
) -> str:
    """
    Format a username

    Args:
        user (ipy.User | ipy.Member): The user

    Returns:
        str: The formatted username
    """
    username = sanitize_markdown(user.username)
    if user.discriminator not in ["0", None]:
        username += "#" + str(user.discriminator)
    return username


async def generate_discord_profile_embed(
    bot: ipy.AutoShardedClient | ipy.Client,
    ctx: ipy.SlashContext,
    user: ipy.User | ipy.Member | None = None,
) -> ipy.Embed:
    """
    Generate a Discord profile embed

    Args:
        bot (ipy.AutoShardedClient | ipy.Client): The bot client
        ctx (ipy.SlashContext): The context
        user (ipy.User, optional): The user to get the profile of. Defaults to None.

    Returns:
        ipy.Embed: The embed
    """
    userId: str
    if user is None:
        userId = str(ctx.author.id)
    else:
        userId = str(user.id)
    servData = {}
    user_data = await bot.http.get_user(userId)
    data = ipy.User.from_dict(user_data, bot)  # type: ignore
    if ctx.guild:
        servData = await bot.http.get_member(ctx.guild.id, userId)
    if data.accent_color:
        color = data.accent_color.value
    else:
        color = 0x000000
    async with PronounDBV2() as pdb:
        pronouns = await pdb.get_pronouns(pdb.Platform.DISCORD, userId)
    pronouns = "Not set" if len(pronouns.pronouns.en) == 0 else str(pronouns)

    fields = [
        ipy.EmbedField(
            name="Display Name",
            value=sanitize_markdown(data.display_name),
            inline=True,
        ),
        ipy.EmbedField(
            name="Username",
            value=format_username(data),
            inline=True,
        ),
        ipy.EmbedField(
            name="PronounDB Pronoun",
            value=pronouns,
            inline=True,
        ),
        ipy.EmbedField(
            name="Snowflake/ID",
            value=f"`{userId}`",
            inline=True,
        ),
        ipy.EmbedField(
            name="Joined Discord",
            value=f"<t:{int(data.created_at.timestamp())}:R>",
            inline=True,
        ),
    ]
    avatar = data.avatar.url
    # if user is on a server, show server-specific info
    if ctx.guild:
        if servData["avatar"]:  # type: ignore
            # type: ignore
            avatar = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{userId}/avatars/{servData['avatar']}"
            # if avatar is animated, add .gif extension
            if servData["avatar"].startswith("a_"):  # type: ignore
                avatar += ".gif"
            else:
                avatar += ".png"
            avatar += "?size=4096"
        if servData["nick"] is not None:  # type: ignore
            nick = sanitize_markdown(servData["nick"])  # type: ignore
        else:
            nick = sanitize_markdown(data.username)
            nick += " (*default*)"
        joined = datetime.strptime(
            servData["joined_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        joined = int(joined.timestamp())
        joined = f"<t:{joined}:R>"
        if servData["premium_since"]:  # type: ignore
            premium_dt: datetime = datetime.strptime(
                # type: ignore
                servData["premium_since"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            )
            premium_ts: int = int(premium_dt.timestamp())
            premium_str: str = f"Boosting server since <t:{premium_ts}:R>"
        else:
            premium_str = "Not boosting"
        fields += [
            ipy.EmbedField(
                name="Joined Server",
                value=joined,
                inline=True,
            ),
            ipy.EmbedField(
                name="Nickname",
                value=nick,
                inline=True,
            ),
            ipy.EmbedField(
                name="Boost Status",
                value=premium_str,
                inline=True,
            ),
        ]
    if data.banner is not None:
        banner = data.banner.url
    else:
        banner = None
    botStatus = ""
    regStatus = ""
    if data.bot:
        botStatus = "\n🤖 This account is a bot"
    async with UserDatabase() as db:
        reg = await db.check_if_registered(discord_id=ipy.Snowflake(int(userId)))
    if reg is True and userId == str(ctx.author.id):
        regStatus = "\n✅ This user is registered on this bot"
    embed: ipy.Embed = ipy.Embed(
        title="Discord Profile",
        description=f"User information for {data.mention}{botStatus}{regStatus}",
        color=color,
        fields=fields,  # type: ignore
    )

    embed.set_thumbnail(url=avatar)
    if banner is not None:
        embed.set_image(url=banner)

    return embed
