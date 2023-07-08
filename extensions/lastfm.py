"""Last.FM extension for interacting with Last.FM API"""

from urllib.parse import quote_plus as urlquote
from typing import Any

import interactions as ipy

from classes.database import DatabaseException, UserDatabase
from classes.excepts import ProviderHttpError
from classes.lastfm import LastFM, LastFMTrackStruct, LastFMUserStruct, LastFMReleaseStruct
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
        """
        Get your Last.fm profile information

        Args:
            user (ipy.Member | ipy.User | None, optional): User to get profile information of. Defaults to None.
            lfm_username (str | None, optional): Username on Last.fm to get profile information of. Defaults to None.
            maximum (int, optional): Maximum number of tracks to show. Defaults to 9.

        Raises:
            ProviderHttpError: Last.fm API is currently unavailable
            DatabaseException: Database is currently unavailable

        Returns:
            None: None
        """
        await ctx.defer()
        user_lang = read_user_language(ctx)
        lang_dict: dict[str, Any] = fetch_language_data(user_lang, use_raw=True)

        if lfm_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `lfm_username` options at the same time!",
                error_type=PlatformErrType.USER,
                lang_dict=lang_dict,
                error="User and lfm_username options used at the same time",
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            user = ctx.author

        if lfm_username is None:
            try:
                async with UserDatabase() as database:
                    user_data = await database.get_user_data(discord_id=user.id)
                    lfm_username = user_data.lastfm_username
            except DatabaseException:
                lfm_username = None

            if lfm_username is None:
                embed = platform_exception_embed(
                    description=f"""{user.mention} haven't linked the Last.fm account to the bot yet!
Use `/platform link` to link, or `/profile lastfm lfm_username:<lastfm_username>` to get the profile information directly""",
                    error_type=PlatformErrType.USER,
                    lang_dict=lang_dict,
                    error="User hasn't link their account yet",
                )
                await ctx.send(embed=embed)
                return

        try:
            async with LastFM() as lfm:
                profile: LastFMUserStruct = await lfm.get_user_info(lfm_username)
                try:
                    tracks: list[LastFMTrackStruct] = await lfm.get_user_recent_tracks(
                        lfm_username, maximum
                    )
                except ProviderHttpError:
                    tracks: list[LastFMTrackStruct] = []
        except ProviderHttpError as err:
            embed = generate_commons_except_embed(
                description="Last.fm API is currently unavailable, please try again later",
                error=err,
                language=lang_dict,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("lastfm_profile", ctx.author, err)
            return

        fields: list[ipy.EmbedField] = []

        for lfm_track in tracks:
            if len(tracks) == 0 and maximum != 0:
                fields.append(
                    ipy.EmbedField(
                        name="Warning",
                        value="It seems like you haven't scrobbled anything yet, or your profile is private!",
                        inline=True,
                    )
                )
                break
            tr_title = f"{'▶️' if lfm_track.nowplaying else ''} {self.trim_lastfm_title(lfm_track.name)}"

            if isinstance(lfm_track.artist, list):
                artists: list[str] = []
                for artist in lfm_track.artist:
                    artists.append(sanitize_markdown(artist.name))
                tr_artist = ", ".join(artists)
            # pylint: disable-next=isinstance-second-argument-not-valid-type
            elif isinstance(lfm_track.artist, LastFMReleaseStruct):
                tr_artist = sanitize_markdown(lfm_track.artist.name)
            else:
                tr_artist = ""

            if len(tr_artist) == 0:
                tr_artist = "*Unknown artist*"

            if isinstance(lfm_track.album, list):
                albums: list[str] = []
                for album in lfm_track.album:
                    albums.append(sanitize_markdown(album.name))
                tr_album = ", ".join(albums)
            # pylint: disable-next=isinstance-second-argument-not-valid-type
            elif isinstance(lfm_track.album, LastFMReleaseStruct):
                tr_album = sanitize_markdown(lfm_track.album.name)
            else:
                tr_album = ""

            if len(tr_album) == 0:
                tr_album = "*Unknown album*"

            if lfm_track.date is not None:
                tr_date = f"<t:{lfm_track.date.epoch}:R>" if not lfm_track.nowplaying else "*Currently playing*"
            else:
                tr_date = "Unknown date"

            tr_url = self.quote_lastfm_url(lfm_track.url)

            fields.append(
                ipy.EmbedField(
                    name=tr_title,
                    value=f"""{tr_artist}
{tr_album}
{tr_date}, [Link]({tr_url})""",
                    inline=True,
                )
            )

        if profile.image is not None:
            img = profile.image[-1].url
        else:
            img = ""
        lfmpro = profile.subscriber
        badge = "🌟 " if lfmpro else ""
        pro_user = f"{badge}Last.FM Pro User\n" if lfmpro else ""
        real_name = f"Real name: {profile.realname}\n" if profile.realname else ""

        registered_epoch = profile.registered

        if registered_epoch is not None:
            registered = f"Account created:  <t:{registered_epoch.epoch}:D> (<t:{registered_epoch.epoch}:R>)"
        else:
            registered = ""

        embed = ipy.Embed(
            author=ipy.EmbedAuthor(
                name="Last.fm Profile",
                url="https://last.fm",
                icon_url="https://media.discordapp.net/attachments/923830321433149453/1079483003396432012/Tx1ceVTBn2Xwo2dF.png",
            ),
            title=f"{badge}{profile.name}",
            url=profile.url,
            color=0xF71414,
            description=f"""{pro_user}{real_name}{registered}
Total scrobbles: {int(profile.playcount):,}
🧑‍🎤 {int(profile.artist_count):,} 💿 {int(profile.album_count):,} 🎶 {int(profile.track_count):,}""",
        )
        embed.set_thumbnail(url=img)
        embed.add_fields(*fields)
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
    """Load the extension"""
    LastFmCog(bot)
