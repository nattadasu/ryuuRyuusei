import interactions as ipy

from modules.i18n import lang, readUserLang
from modules.commons import generalExceptionEmbed, sanitizeMarkdown
from datetime import datetime as dtime
from classes.database import UserDatabase

class Profile(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.bot = bot

    @ipy.slash_command(
        name="profile",
        description="Get your profile information",
    )
    async def profile(self, ctx: ipy.SlashContext):
        pass


    @profile.subcommand(
        sub_cmd_name="discord",
        sub_cmd_description="Get your Discord profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to get profile information of",
                type=ipy.OptionType.USER,
                required=False,
            )
        ]
    )
    async def profile_discord(self, ctx: ipy.SlashContext, user: ipy.User = None):
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul, useRaw=True)
        lp = l_['strings']['profile']
        try:
            if user is None:
                userId = ctx.author.id
            else:
                userId = user.id
            servData = {}
            user_data = await self.bot.http.get_user(userId)
            data = ipy.User.from_dict(user_data, self.bot)
            if ctx.guild:
                servData = await self.bot.http.get_member(ctx.guild.id, userId)
            if data.accent_color:
                color = data.accent_color.value
            else:
                color = 0x000000
            fields = [
                ipy.EmbedField(
                    name=lp['commons']['username'],
                    value=data.username + "#" + str(data.discriminator),
                    inline=True,
                ),
                ipy.EmbedField(
                    name=lp['discord']['snowflake'],
                    value=f"`{userId}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name=lp['discord']['joined_discord'],
                    value=f"<t:{int(data.created_at.timestamp())}:R>",
                    inline=True,
                ),
            ]
            avatar = data.avatar.url
            # if user is on a server, show server-specific info
            if ctx.guild:
                if servData['avatar']:
                    avatar = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{userId}/avatars/{servData['avatar']}"
                    # if avatar is animated, add .gif extension
                    if servData['avatar'].startswith("a_"):
                        avatar += ".gif"
                    else:
                        avatar += ".png"
                    avatar += "?size=4096"
                if servData['nick'] is not None:
                    nick = sanitizeMarkdown(servData['nick'])
                else:
                    nick = sanitizeMarkdown(data.username)
                    nick += " " + lp['commons']['default']
                joined = dtime.strptime(
                    servData['joined_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
                joined = int(joined.timestamp())
                joined = f"<t:{joined}:R>"
                if servData['premium_since']:
                    premium = dtime.strptime(
                        servData['premium_since'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    premium: int = int(premium.timestamp())
                    premium = lp['discord']['boost_since'].format(
                        TIMESTAMP=f"<t:{premium}:R>"
                    )
                else:
                    premium = lp['discord']['not_boosting']
                fields += [
                    ipy.EmbedField(
                        name=lp['discord']['joined_server'],
                        value=joined,
                        inline=True,
                    ),
                    ipy.EmbedField(
                        name=lp['commons']['nickname'],
                        value=nick,
                        inline=True,
                    ),
                    ipy.EmbedField(
                        name=lp['discord']['boost_status'],
                        value=premium,
                        inline=True,
                    )
                ]
            if data.banner is not None:
                banner = data.banner.url
            else:
                banner = None
            botStatus = ""
            regStatus = ""
            if data.bot:
                botStatus = "\n🤖 " + lp['commons']['bot']
            async with UserDatabase() as db:
                reg = await db.check_if_registered(discord_id=userId)
            if reg is True:
                regStatus = "\n✅ " + lp['discord']['registered']
            embed = ipy.Embed(
                title=lp['discord']['title'],
                description=lp['commons']['about'].format(
                    USER=data.mention,
                ) + botStatus + regStatus,
                thumbnail=ipy.EmbedAttachment(
                    url=avatar
                ),
                color=color,
                fields=fields,
                images=[
                    ipy.EmbedAttachment(
                        url=banner
                    )
                ]
            )

            await ctx.send(embed=embed)
        except Exception as e:
            embed = generalExceptionEmbed(
                description=l_[
                    'strings']['profile']['commons']['exception']['general'],
                error=e,
                lang_dict=l_,
            )
            await ctx.send(embed=embed)


def setup(bot):
    Profile(bot)
