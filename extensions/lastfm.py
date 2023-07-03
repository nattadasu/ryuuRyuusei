from urllib.parse import quote_plus as urlquote

import interactions as ipy

from classes.database import DatabaseException, UserDatabase
from classes.excepts import ProviderHttpError
from classes.i18n import LanguageDict
from classes.lastfm import LastFM, LastFMTrackStruct, LastFMUserStruct
from modules.commons import (PlatformErrType, generate_commons_except_embed,
                             platform_exception_embed, sanitize_markdown,
                             save_traceback_to_file)
from modules.i18n import fetch_language_data, read_user_language


class LastFmCog(ipy.Extension):
    """Extension for interacting with Last.FM"""

    lastfm_head = ipy.SlashCommand(
        name="lastfm",
        description="Get useful information from Last.FM",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5
        )
    )

    @lastfm_head.subcommand(
        sub_cmd_name="profile",
        sub_cmd_description="Get your Last.fm profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to get profile information of",
                type=ipy.OptionType.USER,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="lfm_username",
                description="Username on Last.fm to get profile information of",
                type=ipy.OptionType.STRING,
                required=False,
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
    async def lastfm_profile(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member | ipy.User | None = None,
        lfm_username: str | None = None,
        maximum: int = 9,
    ):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul, use_raw=True)

        if lfm_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `lfm_username` options at the same time!",
                error_type=PlatformErrType.USER,
                lang_dict=l_,
                error="User and lfm_username options used at the same time",
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            user = ctx.author

        if lfm_username is None:
            try:
                async with UserDatabase() as db:
                    user_data = await db.get_user_data(discord_id=user.id)
                    lfm_username = user_data.lastfm_username
            except DatabaseException:
                lfm_username = None

            if lfm_username is None:
                embed = platform_exception_embed(
                    description=f"""{user.mention} haven't linked the Last.fm account to the bot yet!
Use `/platform link` to link, or `/profile lastfm lfm_username:<lastfm_username>` to get the profile information directly""",
                    error_type=PlatformErrType.USER,
                    lang_dict=l_,
                    error="User hasn't link their account yet",
                )
                await ctx.send(embed=embed)
                return

        try:
            async with LastFM() as lfm:
                profile: LastFMUserStruct = await lfm.get_user_info(lfm_username)
                tracks: list[LastFMTrackStruct] = await lfm.get_user_recent_tracks(
                    lfm_username, maximum
                )
        except ProviderHttpError as e:
            embed = generate_commons_except_embed(
                description="Last.fm API is currently unavailable, please try again later",
                error=e,
                language=l_,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("lastfm_profile", ctx.author, e)

        fields = [
            ipy.EmbedField(
                name=f"{'▶️' if tr.nowplaying else ''} {self.trim_lastfm_title(tr.name)}",
                value=f"""{sanitize_markdown(tr.artist.name)}
{sanitize_markdown(tr.album.name)}
{f"<t:{tr.date.epoch}:R>" if not tr.nowplaying else "*Currently playing*"}, [Link]({self.quote_lastfm_url(tr.url)})""",
                inline=True,
            )
            for tr in tracks
        ]

        img = profile.image[-1].url
        lfmpro = profile.subscriber
        badge = "🌟 " if lfmpro else ""
        icShine = f"{badge}Last.FM Pro User\n" if lfmpro else ""
        realName = f"Real name: {profile.realname}\n" if profile.realname else ""

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
Total scrobbles: {int(profile.playcount):,}
🧑‍🎤 {int(profile.artist_count):,} 💿 {int(profile.album_count):,} 🎶 {int(profile.track_count):,}""",
            fields=fields,
        )
        embed.set_thumbnail(url=img)
        await ctx.send(embed=embed)

    @staticmethod
    def trim_lastfm_title(title: str) -> str:
        """
        Trim the title to be used in embed up to 100 chars

        Args:
            title (str): Title to be trimmed

        Returns:
            str: Trimmed title
        """
        if len(title) >= 100:
            title = title[:97] + "..."
        title = sanitize_markdown(title)
        return title

    @staticmethod
    def quote_lastfm_url(url: str) -> str:
        """
        Quote the Last.fm URL to be used in embed

        Args:
            url (str): URL to be quoted

        Returns:
            str: Quoted URL
        """
        scus = url.split("/")
        scus[4] = urlquote(scus[4])
        scus[6] = urlquote(scus[6])
        quoted_url = "/".join(scus)
        quoted_url = quoted_url.replace("%25", "%")
        return quoted_url


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    LastFmCog(bot)
