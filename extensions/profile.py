from datetime import datetime as dtime
from urllib.parse import quote_plus as urlquote

import interactions as ipy

from classes.database import UserDatabase
from classes.excepts import ProviderHttpError
from classes.lastfm import LastFM, LastFMTrackStruct, LastFMUserStruct
from modules.commons import generate_commons_except_embed, sanitize_markdown
from modules.i18n import fetch_language_data, read_user_language


class Profile(ipy.Extension):
    """Profile commands"""

    def __init__(self, bot: ipy.AutoShardedClient):
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
        ],
    )
    async def profile_discord(self, ctx: ipy.SlashContext, user: ipy.User = None):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul, useRaw=True)
        lp = l_["strings"]["profile"]
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
                    name=lp["discord"]["displayName"],
                    value=sanitize_markdown(data.display_name),
                    inline=True,
                ),
                ipy.EmbedField(
                    name=lp["commons"]["username"],
                    value=sanitize_markdown(
                        data.username + "#" + str(data.discriminator)
                    ),
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
                    nick += " " + lp["commons"]["default"]
                joined = dtime.strptime(servData["joined_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                joined = int(joined.timestamp())
                joined = f"<t:{joined}:R>"
                if servData["premium_since"]:
                    premium = dtime.strptime(
                        servData["premium_since"], "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                    premium: int = int(premium.timestamp())
                    premium = lp["discord"]["boost_since"].format(
                        TIMESTAMP=f"<t:{premium}:R>"
                    )
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

            await ctx.send(embed=embed)
        except Exception as e:
            embed = generate_commons_except_embed(
                description=l_["strings"]["profile"]["exception"]["general"],
                error=e,
                lang_dict=l_,
            )
            await ctx.send(embed=embed)

    @profile.subcommand(
        sub_cmd_name="myanimelist",
        sub_cmd_description="Get your MyAnimeList profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to get profile information of",
                type=ipy.OptionType.USER,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="mal_username",
                description="Username on MyAnimeList to get profile information of",
                type=ipy.OptionType.STRING,
                required=False,
            ),
        ],
    )
    async def profile_myanimelist(
        self, ctx: ipy.SlashContext, user: ipy.User = None, mal_username: str = None
    ):
        # ul = read_user_language(ctx)
        # l_ = fetch_language_data(ul, useRaw=True)
        await ctx.send(
            "This command is currently disabled as it not have been implemented yet."
        )

    @profile.subcommand(
        sub_cmd_name="lastfm",
        sub_cmd_description="Get your Last.fm profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="Username on Last.fm to get profile information of",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="maximum",
                description="Maximum number of tracks to show",
                type=ipy.OptionType.INTEGER,
                required=False,
                min_value=0,
                max_value=21,
            ),
        ],
    )
    async def profile_lastfm(self, ctx: ipy.SlashContext, user: str, maximum: int = 9):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul, useRaw=True)
        try:
            async with LastFM() as lfm:
                profile: LastFMUserStruct = await lfm.get_user_info(user)
                tracks: list[LastFMTrackStruct] = await lfm.get_user_recent_tracks(
                    user, maximum
                )
        except ProviderHttpError as e:
            embed = generate_commons_except_embed(
                description=e.message,
                error=e,
                lang_dict=l_,
            )
            await ctx.send(embed=embed)
            return

        fields = []
        if maximum >= 1:
            rpt = "Recently played tracks"
            rptDesc = f"Here are the recently played tracks of {user} on Last.fm"
            fields.append(ipy.EmbedField(name=rpt, value=rptDesc, inline=False))

        for tr in tracks:
            tr.name = sanitize_markdown(tr.name)
            tr.artist.name = sanitize_markdown(tr.artist.name)
            tr.album.name = sanitize_markdown(tr.album.name)
            scu = tr.url
            scus = scu.split("/")
            # assumes the url as such: https://www.last.fm/music/Artist/_/Track
            # so, the artist is at index 4, and track is at index 6
            # in index 4 and 6, encode the string to be url compatible with percent encoding
            # then, join the list back to a string

            scus[4] = urlquote(scus[4])
            scus[6] = urlquote(scus[6])
            scu = "/".join(scus)
            scu = scu.replace("%25", "%")

            if tr.nowplaying is True:
                title = f"▶️ {tr.name}"
                dt = "*Currently playing*"
            else:
                title = tr.name
                dt = tr.date.epoch
                dt = f"<t:{dt}:R>"
            fields += [
                ipy.EmbedField(
                    name=title,
                    value=f"""{tr.artist.name}
{tr.album.name}
{dt}, [Link]({tr.url})""",
                    inline=True,
                )
            ]

        img = profile.image[-1].url
        lfmpro = profile.subscriber
        badge = "🌟 " if lfmpro is True else ""
        icShine = f"{badge}Last.FM Pro User\n" if lfmpro is True else ""
        realName = (
            "Real name: " + profile.realname + "\n"
            if profile.realname not in [None, ""]
            else ""
        )

        embed = ipy.Embed(
            author=ipy.EmbedAuthor(
                name="Last.fm Profile",
                url="https://last.fm",
                icon_url="https://media.discordapp.net/attachments/923830321433149453/1079483003396432012/Tx1ceVTBn2Xwo2dF.png",
            ),
            title=f"{badge}{profile.name}",
            url=profile.url,
            color=0xF71414,
            description=f"""{icShine}{realName}Account created:  <t:{profile.registered.epoch}:D> (<t:{profile.registered.epoch}:R>)
Total scrobbles: {profile.playcount}
🧑‍🎤 {profile.artist_count} 💿 {profile.album_count} 🎶 {profile.track_count}""",
            fields=fields,
        )
        embed.set_thumbnail(url=img)
        await ctx.send(embed=embed)


def setup(bot):
    Profile(bot)
