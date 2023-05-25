from datetime import datetime

import interactions as ipy

from classes.database import UserDatabase
from classes.pronoundb import PronounDB, Pronouns
from modules.commons import sanitize_markdown


async def generate_discord_profile_embed(
    bot: ipy.AutoShardedClient | ipy.Client,
    ctx: ipy.SlashContext,
    l_: dict,
    user: ipy.User = None,
) -> ipy.Embed:
    """
    Generate a Discord profile embed

    Args:
        bot (ipy.AutoShardedClient | ipy.Client): The bot client
        ctx (ipy.SlashContext): The context
        l_ (dict): The language data
        user (ipy.User, optional): The user to get the profile of. Defaults to None.

    Returns:
        ipy.Embed: The embed
    """
    lp = l_["strings"]["profile"]
    if user is None:
        userId = ctx.author.id
    else:
        userId = user.id
    servData = {}
    user_data = await bot.http.get_user(userId)
    data = ipy.User.from_dict(user_data, bot)
    if ctx.guild:
        servData = await bot.http.get_member(ctx.guild.id, userId)
    if data.accent_color:
        color = data.accent_color.value
    else:
        color = 0x000000
    async with PronounDB() as pdb:
        pronouns = await pdb.get_pronouns(pdb.Platform.DISCORD, userId)
        if pronouns.pronouns == Pronouns.UNSPECIFIED:
            pronouns = "Unset"
        else:
            pronouns = pdb.translate_shorthand(pronouns.pronouns)

    fields = [
        ipy.EmbedField(
            name=lp["discord"]["display_name"],
            value=sanitize_markdown(data.display_name),
            inline=True,
        ),
        ipy.EmbedField(
            name=lp["commons"]["username"],
            value=sanitize_markdown(data.username + "#" + str(data.discriminator)),
            inline=True,
        ),
        ipy.EmbedField(
            name="PronounDB Pronoun",
            value=pronouns,
            inline=True,
        ),
        ipy.EmbedField(
            name=lp["discord"]["snowflake"],
            value=f"`{userId}`",
            inline=True,
        ),
        ipy.EmbedField(
            name=lp["discord"]["joined_discord"],
            value=f"<t:{int(data.created_at.timestamp())}:R>",
            inline=True,
        ),
    ]
    avatar = data.avatar.url
    # if user is on a server, show server-specific info
    if ctx.guild:
        if servData["avatar"]:
            avatar = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{userId}/avatars/{servData['avatar']}"
            # if avatar is animated, add .gif extension
            if servData["avatar"].startswith("a_"):
                avatar += ".gif"
            else:
                avatar += ".png"
            avatar += "?size=4096"
        if servData["nick"] is not None:
            nick = sanitize_markdown(servData["nick"])
        else:
            nick = sanitize_markdown(data.username)
            nick += " (" + lp["commons"]["default"] + ")"
        joined = datetime.strptime(servData["joined_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        joined = int(joined.timestamp())
        joined = f"<t:{joined}:R>"
        if servData["premium_since"]:
            premium = datetime.strptime(
                servData["premium_since"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            premium: int = int(premium.timestamp())
            premium = lp["discord"]["boost_since"].format(TIMESTAMP=f"<t:{premium}:R>")
        else:
            premium = lp["discord"]["not_boosting"]
        fields += [
            ipy.EmbedField(
                name=lp["discord"]["joined_server"],
                value=joined,
                inline=True,
            ),
            ipy.EmbedField(
                name=lp["commons"]["nickname"],
                value=nick,
                inline=True,
            ),
            ipy.EmbedField(
                name=lp["discord"]["boost_status"],
                value=premium,
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
        botStatus = "\n🤖 " + lp["commons"]["bot"]
    async with UserDatabase() as db:
        reg = await db.check_if_registered(discord_id=userId)
    if reg is True:
        regStatus = "\n✅ " + lp["discord"]["registered"]
    embed = ipy.Embed(
        title=lp["discord"]["title"],
        description=lp["commons"]["about"].format(
            USER=data.mention,
        )
        + botStatus
        + regStatus,
        color=color,
        fields=fields,
    )

    embed.set_thumbnail(url=avatar)
    embed.set_image(url=banner)

    return embed