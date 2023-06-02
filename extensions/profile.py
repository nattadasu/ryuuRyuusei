from datetime import datetime as dtime
from datetime import timezone as tz
from typing import Literal
from urllib.parse import quote_plus as urlquote, quote

import interactions as ipy

from classes.anilist import AniList, AniListUserStruct
from classes.database import DatabaseException, UserDatabase, UserDatabaseClass
from classes.excepts import ProviderHttpError
from classes.jikan import JikanApi, JikanException
from classes.lastfm import LastFM, LastFMTrackStruct, LastFMUserStruct
from classes.shikimori import Shikimori, ShikimoriUserGender, ShikimoriUserStruct
from classes.i18n import LanguageDict
from modules.commons import (
    convert_float_to_time,
    generate_commons_except_embed,
    sanitize_markdown,
)
from modules.discord import generate_discord_profile_embed
from modules.i18n import fetch_language_data, read_user_language
from modules.commons import PlatformErrType, platform_exception_embed


class Profile(ipy.Extension):
    """Profile commands"""

    profile = ipy.SlashCommand(
        name="profile",
        description="Get your profile information from various platforms",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5,
        )
    )

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
    async def profile_discord(
        self, ctx: ipy.SlashContext, user: ipy.User | ipy.Member | None = None
    ):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul, use_raw=True)
        try:
            embed = await generate_discord_profile_embed(
                bot=self.bot,
                l_=l_,
                ctx=ctx,
                user=user,
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = generate_commons_except_embed(
                description=l_["strings"]["profile"]["exception"]["general"],
                error=f"{e}",
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
            ipy.SlashCommandOption(
                name="embed_layout",
                description="Layout of the embed",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Minimal (Default)",
                        value="minimal",
                    ),
                    ipy.SlashCommandChoice(name="Classic", value="old"),
                    ipy.SlashCommandChoice(name="Highly Detailed", value="new"),
                ],
            ),
        ],
    )
    async def profile_myanimelist(
        self,
        ctx: ipy.SlashContext,
        user: ipy.User | ipy.Member | None = None,
        mal_username: str | None = None,
        embed_layout: Literal["minimal", "old", "new"] = "minimal",
    ):
        await ctx.defer()
        l_: LanguageDict = fetch_language_data("en_US", True)

        if mal_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `mal_username` options at the same time!",
                error_type=PlatformErrType.USER,
                lang_dict=l_,
                error="User and mal_username options used at the same time",
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            user = ctx.author

        if mal_username is None:
            try:
                async with UserDatabase() as db:
                    user_data = await db.get_user_data(discord_id=user.id)
                    mal_username = user_data.mal_username
            except DatabaseException:
                mal_username = None

        if mal_username is None:
            embed = platform_exception_embed(
                description=f"""{user.mention} haven't registered the MyAnimeList account to the bot yet!
Use `/register` to register, or use `/profile myanimelist mal_username:<username>` to get the profile information of a user without registering their account to the bot""",
                error_type=PlatformErrType.USER,
                lang_dict=l_,
                error="User hasn't registered their MAL account yet",
            )
            await ctx.send(embed=embed)
            return

        try:
            async with JikanApi() as jikan:
                user_data = await jikan.get_user_data(username=mal_username)
        except JikanException as e:
            embed = platform_exception_embed(
                description="Jikan API returned an error",
                error_type=e.status_code,
                lang_dict=l_,
                error=e.message,
            )
            await ctx.send(embed=embed)
            return

        username = sanitize_markdown(user_data.username)
        user_id = user_data.mal_id
        birthday = user_data.birthday
        location = user_data.location
        if location not in ["", None] and isinstance(location, str):
            location_url = (
                f"https://www.openstreetmap.org/search?query={quote(location)}"
            )
            location = f"[{location}]({location_url})"
        else:
            location = "Unset"
        gender = user_data.gender if user_data.gender not in ["", None] else "Unset"
        anime = user_data.statistics.anime
        manga = user_data.statistics.manga
        anime_float = convert_float_to_time(anime.days_watched)
        manga_float = convert_float_to_time(manga.days_read)
        joined = int(user_data.joined.timestamp())
        if birthday is not None:
            timestamped = birthday.timestamp()
            today = dtime.now(tz=tz.utc)
            current_year = today.year
            upcoming = birthday.replace(year=current_year)
            if int(upcoming.timestamp()) < int(today.timestamp()):
                upcoming = upcoming.replace(year=current_year + 1)
            birthday = str(int(timestamped))
            birthday_str = f"<t:{birthday}:D>"
            birthday_rel = f"<t:{birthday}:R>"
            birthday_rem = f"<t:{int(upcoming.timestamp())}:R>"
        else:
            birthday_str = ""
            birthday_rem: str = ""
            birthday_rel: str = ""

        birthday_formatted = (
            f"{birthday_str} {birthday_rel} (Next birthday {birthday_rem})"
            if birthday_str
            else "Unset"
        )
        joined_formatted = f"<t:{joined}:D> (<t:{joined}:R>)"

        components = [
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="MyAnimeList Profile",
                url=f"https://myanimelist.net/profile/{username}",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Anime List",
                url=f"https://myanimelist.net/animelist/{username}",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Manga List",
                url=f"https://myanimelist.net/mangalist/{username}",
            ),
        ]

        embed = ipy.Embed(
            title=username,
            url=f"https://myanimelist.net/profile/{username}",
            author=ipy.EmbedAuthor(
                name="MyAnimeList Profile",
                url="https://myanimelist.net/",
                icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png",
            ),
            color=0x2E51A2,
            timestamp=dtime.now(tz=tz.utc),
        )
        embed.set_thumbnail(url=user_data.images.webp.image_url)

        if embed_layout != "old":
            embed.add_fields(
                ipy.EmbedField(
                    name="👤 User ID",
                    value=f"`{user_id}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="🎉 Account Created", value=joined_formatted, inline=True
                ),
                ipy.EmbedField(
                    name="🎂 Birthday", value=birthday_formatted, inline=True
                ),
            )
            if embed_layout == "new":
                embed.add_fields(
                    ipy.EmbedField(name="🚁 Gender", value=gender, inline=True),
                    ipy.EmbedField(name="📍 Location", value=location, inline=True),
                )
            anime_value_str = f"""* Total: {anime.total_entries:,}
* Mean Score: ⭐ {anime.mean_score}/10
* Days Watched: {anime_float}
* Episodes Watched: {anime.episodes_watched:,}"""
            embed.add_field(
                name="🎞️ Anime List Summary",
                value=anime_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Anime Statuses",
                    value=f"""👀 Currently Watching: {anime.watching:,}
✅ Completed: {anime.completed:,}
⏰ Planned: {anime.plan_to_watch:,}
⏸️ On Hold: {anime.on_hold:,}
🗑️ Dropped: {anime.dropped:,}""",
                    inline=True,
                )
                ani_favs = user_data.favorites.anime
                ani_fav_list = ""
                if len(ani_favs) > 0:
                    ani_fav_top = ani_favs[:5]
                    # generate string
                    for index, anime in enumerate(ani_fav_top):
                        if len(anime.title) >= 100:
                            anime.title = anime.title[:97] + "..."
                        split = anime.url.split("/")
                        if split[-1].isdigit() is False:
                            anime.url = "/".join(split[:-1])
                        ani_fav_list += f"{index+1}. [{anime.title}]({anime.url})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Anime",
                    value=ani_fav_list if ani_fav_list not in ["", None] else "Unset",
                    inline=True,
                )
            manga_value_str = f"""* Total: {manga.total_entries:,}
* Mean Score: ⭐ {manga.mean_score}/10
* Days Read, Estimated: {manga_float}
* Chapters Read: {manga.chapters_read:,}
* Volumes Read: {manga.volumes_read:,}"""
            embed.add_field(
                name="📔 Manga List Summary",
                value=manga_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Manga Statuses",
                    value=f"""👀 Currently Reading: {manga.reading:,}
✅ Completed: {manga.completed:,}
⏰ Planned: {manga.plan_to_read:,}
⏸️ On Hold: {manga.on_hold:,}
🗑️ Dropped: {manga.dropped:,}""",
                    inline=True,
                )
                man_favs = user_data.favorites.manga
                man_fav_list = ""
                if len(man_favs) > 0:
                    man_fav_top = man_favs[:5]
                    for index, manga in enumerate(man_fav_top):
                        if len(manga.title) >= 100:
                            manga.title = manga.title[:97] + "..."
                        split = manga.url.split("/")
                        if split[-1].isdigit() is False:
                            manga.url = "/".join(split[:-1])
                        man_fav_list += f"{index+1}. [{manga.title}]({manga.url})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Manga",
                    value=man_fav_list if man_fav_list not in ["", None] else "Unset",
                    inline=True,
                )
        else:
            embed.add_fields(
                ipy.EmbedField(
                    name="Profile",
                    value=f"""* User ID: `{user_id}`
* Account created: {joined_formatted}
* Birthday: {birthday_formatted}
* Gender: {gender}
* Location: {location}""",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Anime List Summary",
                    value=f"""* Total: {anime.total_entries:,}
* Mean Score: ⭐ {anime.mean_score}/10
* Days Watched: {anime_float}
* Episodes Watched: {anime.episodes_watched:,}
👀 {anime.watching:,} | ✅ {anime.completed:,} | ⏰ {anime.plan_to_watch:,} | ⏸️ {anime.on_hold:,} | 🗑️ {anime.dropped:,}""",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Manga List Summary",
                    value=f"""* Total: {manga.total_entries:,}
* Mean Score: ⭐ {manga.mean_score}/10
* Days Read, Estimated: {manga_float}
* Chapters Read: {manga.chapters_read:,}
* Volumes Read: {manga.volumes_read:,}
👀 {manga.reading:,} | ✅ {manga.completed:,} | ⏰ {manga.plan_to_read:,} | ⏸️ {manga.on_hold:,} | 🗑️ {manga.dropped:,}""",
                    inline=True,
                ),
            )

        if embed_layout != "minimal":
            components += [
                ipy.Button(
                    style=ipy.ButtonStyle.URL,
                    label="anime.plus MALGraph",
                    url=f"https://anime.plus/{username}",
                ),
                ipy.Button(
                    style=ipy.ButtonStyle.URL,
                    label="MAL Badges",
                    url=f"https://mal-badges.com/users/{username}",
                ),
            ]
            embed.set_image(url=f"https://malheatmap.com/users/{username}/signature")
            embed.set_footer(
                text="Powered by Jikan API for data and MAL Heatmap for Activity Heatmap. Data can be inacurrate as Jikan and Ryuusei cache your profile up to a day"
            )
        else:
            embed.set_footer(
                text='Powered by Jikan API for data. To expand what data will be shown, modify embed_layout parameter to "old" or "new"'
            )

        await ctx.send(embed=embed, components=components)

    @profile.subcommand(
        sub_cmd_name="lastfm",
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
    async def profile_lastfm(
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
                lang_dict=l_,
            )
            await ctx.send(embed=embed)
            return

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
Total scrobbles: {profile.playcount:,}
🧑‍🎤 {profile.artist_count:,} 💿 {profile.album_count:,} 🎶 {profile.track_count:,}""",
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

    @profile.subcommand(
        sub_cmd_name="anilist",
        sub_cmd_description="Get your AniList profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to get profile information of",
                type=ipy.OptionType.USER,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="anilist_username",
                description="Username on AniList to get profile information of",
                type=ipy.OptionType.STRING,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="embed_layout",
                description="Layout of the embed",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(name="Card", value="card"),
                    ipy.SlashCommandChoice(name="Minimal (default)", value="minimal"),
                    ipy.SlashCommandChoice(name="Classic", value="old"),
                    ipy.SlashCommandChoice(name="Highly Detailed", value="new"),
                ],
            ),
        ],
    )
    async def profile_anilist(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member | ipy.User | None = None,
        anilist_username: str | None = None,
        embed_layout: Literal["card", "minimal", "old", "new"] = "minimal",
    ) -> None:
        await ctx.defer()
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul, use_raw=True)

        if anilist_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `anilist_username` options at the same time!",
                error_type=PlatformErrType.USER,
                lang_dict=l_,
                error="User and anilist_username options used at the same time",
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            user = ctx.author

        if anilist_username is None:
            try:
                async with UserDatabase() as db:
                    user_data_dc: UserDatabaseClass = await db.get_user_data(
                        discord_id=user.id
                    )
                    anilist_username = user_data_dc.anilist_username
            except DatabaseException:
                anilist_username = None

            if anilist_username is None:
                embed = platform_exception_embed(
                    description=f"""{user.mention} haven't linked the AniList account to the bot yet!
Use `/platform link` to link, or `/profile anilist anilist_username:<anilist_username>` to get the profile information directly""",
                    error_type=PlatformErrType.USER,
                    lang_dict=l_,
                    error="User hasn't link their account yet",
                )
                await ctx.send(embed=embed)
                return

        try:
            async with AniList() as al:
                user_data: AniListUserStruct = await al.user(anilist_username)
        except ProviderHttpError as e:
            embed = platform_exception_embed(
                description="AniList API returned an error",
                error=f"{e}",
                lang_dict=l_,
                error_type=PlatformErrType.SYSTEM,
            )
            await ctx.send(embed=embed)
            return

        username = sanitize_markdown(user_data.name)
        user_id = user_data.id
        avatar = user_data.avatar.large
        user_url = user_data.siteUrl
        created_at = user_data.createdAt
        donator = user_data.donatorTier
        if donator >= 3:
            donator_flair = f" (`{user_data.donatorBadge}`)"
        elif donator >= 1:
            donator_flair = " (Donator)"
        else:
            donator_flair = ""
        donator = f"Tier {donator}" if donator != 0 else "Not a donator"

        banner = user_data.bannerImage
        joined_formatted = (
            f"<t:{int(created_at.timestamp())}:D> (<t:{int(created_at.timestamp())}:R>)"
        )
        anime_current = 0
        anime_planning = 0
        anime_completed = 0
        anime_dropped = 0
        anime_paused = 0
        anime_stats = user_data.statistics.anime
        anime_mean_score = anime_stats.meanScore
        anime_episodes_watched = anime_stats.episodesWatched
        # convert minutes to days
        anime_float = convert_float_to_time(anime_stats.minutesWatched / 1440)
        for status in anime_stats.statuses:
            match status.status:
                case "CURRENT":
                    anime_current = status.count
                case "PLANNING":
                    anime_planning = status.count
                case "COMPLETED":
                    anime_completed = status.count
                case "DROPPED":
                    anime_dropped = status.count
                case "PAUSED":
                    anime_paused = status.count
                case _:
                    continue
        anime_total = (anime_completed + anime_current + anime_dropped + anime_paused + anime_planning)
        manga_current = 0
        manga_planning = 0
        manga_completed = 0
        manga_dropped = 0
        manga_paused = 0
        manga_stats = user_data.statistics.manga
        manga_mean_score = manga_stats.meanScore
        manga_chapters_read = manga_stats.chaptersRead
        manga_volumes_read = manga_stats.volumesRead
        manga_float = convert_float_to_time((8 * manga_chapters_read) / 1440)
        for status in manga_stats.statuses:
            match status.status:
                case "CURRENT":
                    manga_current = status.count
                case "PLANNING":
                    manga_planning = status.count
                case "COMPLETED":
                    manga_completed = status.count
                case "DROPPED":
                    manga_dropped = status.count
                case "PAUSED":
                    manga_paused = status.count
                case _:
                    continue
        manga_total = (manga_completed + manga_current + manga_dropped + manga_paused + manga_planning)
        embed_author = ipy.EmbedAuthor(
            name="AniList Profile",
            url="https://anilist.co",
            icon_url="https://anilist.co/img/icons/android-chrome-192x192.png",
        )
        embed_color = 0x2F80ED
        components = [
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="AniList Profile",
                url=user_url,
            ),
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Anime List",
                url=f"{user_url}/animelist",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Manga List",
                url=f"{user_url}/mangalist",
            ),
        ]
        embed = ipy.Embed(
            title=username,
            url=user_url,
            author=embed_author,
            color=embed_color,
            timestamp=dtime.now(tz=tz.utc),
        )
        embed.set_thumbnail(url=avatar)

        if embed_layout == "card":
            embed.description = f"""* **User ID:** `{user_id}`
* **Account Created:** {joined_formatted}"""
            embed.set_image(
                url=f"https://img.anili.st/user/{user_id}?width=918&height=480"
            )
            await ctx.send(embed=embed, components=components)
            return

        if embed_layout != "old":
            embed.add_fields(
                ipy.EmbedField(
                    name="👤 User ID",
                    value=f"`{user_id}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="🎉 Account Created", value=joined_formatted, inline=True
                ),
                ipy.EmbedField(
                    name="💎 Donator",
                    value=f"{donator}{donator_flair}",
                    inline=True,
                ),
            )
            anime_value_str = f"""* Total: {anime_total:,}
* Mean Score: ⭐ {anime_mean_score}/100
* Days Watched: {anime_float}
* Episodes Watched: {anime_episodes_watched:,}"""
            embed.add_field(
                name="🎞️ Anime List Summary",
                value=anime_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Anime Statuses",
                    value=f"""👀 Currently Watching: {anime_current:,}
✅ Completed: {anime_completed:,}
⏰ Planned: {anime_planning:,}
⏸️ On Hold: {anime_paused:,}
🗑️ Dropped: {anime_dropped:,}""",
                    inline=True,
                )
                ani_favs = user_data.favourites.anime.nodes
                ani_fav_list = ""
                if ani_favs:
                    for index, fav in enumerate(ani_favs):
                        if len(fav.title.romaji) >= 100:
                            fav.title.romaji = fav.title.romaji[:97] + "..."
                        ani_fav_list += (
                            f"{index + 1}. [{fav.title.romaji}]({fav.siteUrl})\n"
                        )
                embed.add_field(
                    name="🌟 Top 5 Favorite Anime",
                    value=ani_fav_list if ani_fav_list else "Unset",
                    inline=True,
                )
            manga_value_str = f"""* Total: {manga_total}
* Mean Score: ⭐ {manga_mean_score}/100
* Days Read, Estimated: {manga_float}
* Chapters Read: {manga_chapters_read:,}
* Volumes Read: {manga_volumes_read:,}"""
            embed.add_field(
                name="📔 Manga List Summary",
                value=manga_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Manga Statuses",
                    value=f"""👀 Currently Reading: {manga_current:,}
✅ Completed: {manga_completed:,}
⏰ Planned: {manga_planning:,}
⏸️ On Hold: {manga_paused:,}
🗑️ Dropped: {manga_dropped:,}""",
                    inline=True,
                )
                manga_favs = user_data.favourites.manga.nodes
                manga_fav_list = ""
                if manga_favs:
                    for index, fav in enumerate(manga_favs):
                        if len(fav.title.romaji) >= 100:
                            fav.title.romaji = fav.title.romaji[:97] + "..."
                        manga_fav_list += (
                            f"{index + 1}. [{fav.title.romaji}]({fav.siteUrl})\n"
                        )
                embed.add_field(
                    name="🌟 Top 5 Favorite Manga",
                    value=manga_fav_list if manga_fav_list else "Unset",
                    inline=True,
                )
        else:
            embed.add_fields(
                ipy.EmbedField(
                    name="Profile",
                    value=f"""* **User ID:** `{user_id}`
* **Account Created:** {joined_formatted}
* **Donator:** {donator}{donator_flair}""",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Anime List Summary",
                    value=f"""* Total: {anime_total:,}
* Mean Score: ⭐ {anime_mean_score}/100
* Days Watched: {anime_float}
* Episodes Watched: {anime_episodes_watched:,}
👀 {anime_current:,} | ✅ {anime_completed:,} | ⏰ {anime_planning:,} | ⏸️ {anime_paused:,} | 🗑️ {anime_dropped:,}""",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Manga List Summary",
                    value=f"""* Total: {manga_total:,}
* Mean Score: ⭐ {manga_mean_score}/100
* Days Read, Estimated: {manga_float}
* Chapters Read: {manga_chapters_read:,}
* Volumes Read: {manga_volumes_read:,}
👀 {manga_current:,} | ✅ {manga_completed:,} | ⏰ {manga_planning:,} | ⏸️ {manga_paused:,} | 🗑️ {manga_dropped:,}""",
                    inline=True,
                ),
            )

        if embed_layout != "minimal":
            components += [
                ipy.Button(
                    style=ipy.ButtonStyle.URL,
                    label="Full Anime Stats",
                    url=f"{user_url}/stats/anime/overview",
                ),
                ipy.Button(
                    style=ipy.ButtonStyle.URL,
                    label="Full Manga Stats",
                    url=f"{user_url}/stats/manga/overview",
                ),
            ]
            if banner:
                embed.set_image(url=banner)

        await ctx.send(embed=embed, components=components)

    @profile.subcommand(
        sub_cmd_name="shikimori",
        sub_cmd_description="Get your Shikimori profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to get profile information of",
                type=ipy.OptionType.USER,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="shikimori_username",
                description="Username on Shikimori to get profile information of",
                type=ipy.OptionType.STRING,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="embed_layout",
                description="Layout of the embed",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(name="Minimal (default)", value="minimal"),
                    ipy.SlashCommandChoice(name="Classic", value="old"),
                    ipy.SlashCommandChoice(name="Highly Detailed", value="new"),
                ],
            ),
        ],
    )
    async def profile_shikimori(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member | ipy.User | None = None,
        shikimori_username: str | None = None,
        embed_layout: Literal["minimal", "old", "new"] = "minimal",
    ) -> None:
        await ctx.defer()
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul, use_raw=True)

        if shikimori_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `shikimori_username` options at the same time!",
                error_type=PlatformErrType.USER,
                lang_dict=l_,
                error="User and shikimori_username options used at the same time",
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            user = ctx.author

        if shikimori_username is None:
            try:
                async with UserDatabase() as db:
                    user_data_dc: UserDatabaseClass = await db.get_user_data(
                        discord_id=user.id
                    )
                    shikimori_username = user_data_dc.shikimori_username
            except DatabaseException:
                shikimori_username = None

            if shikimori_username is None:
                embed = platform_exception_embed(
                    description=f"""{user.mention} haven't linked the Shikimori account to the bot yet!
Use `/platform link` to link, or `/profile shikimori shikimori_username:<shikimori_username>` to get the profile information directly""",
                    error_type=PlatformErrType.USER,
                    lang_dict=l_,
                    error="User hasn't link their account yet",
                )
                await ctx.send(embed=embed)
                return

        try:
            async with Shikimori() as shiki:
                user_data: ShikimoriUserStruct = await shiki.get_user(
                    user_id=shikimori_username,
                    is_nickname=True,
                )
        except ProviderHttpError as e:
            embed = platform_exception_embed(
                description=e.message,
                error_type=PlatformErrType.SYSTEM,
                lang_dict=l_,
                error="Error while getting user data",
            )
            await ctx.send(embed=embed)
            return

        username = user_data.nickname
        user_id = user_data.id
        avatar = user_data.image.x160
        user_url = user_data.url
        gender = user_data.sex
        match gender:
            case ShikimoriUserGender.UNKNOWN:
                gender_str = "Unset"
            case _:
                gender_str = gender.value.capitalize()
        age = user_data.full_years
        if age is None:
            age_str = "Unset"
        else:
            age_str = f"{age} years old"

        anime_completed = 0
        anime_current = 0
        anime_dropped = 0
        anime_paused = 0
        anime_planning = 0
        anime_repeating = 0
        anime_total = 0
        anime_stats = user_data.stats
        for stats in anime_stats.full_statuses.anime:
            match stats.grouped_id:
                case "planned":
                    anime_planning = stats.size
                case "watching":
                    anime_current = stats.size
                case "rewatching":
                    anime_repeating = stats.size
                case "completed":
                    anime_completed = stats.size
                case "on_hold":
                    anime_paused = stats.size
                case "dropped":
                    anime_dropped = stats.size
            anime_total += stats.size
        # calculate mean score
        anime_mean_score = 0
        anime_ranked = 0
        for score in anime_stats.scores.anime:
            anime_ranked += score.value
            anime_mean_score += int(score.name) * score.value
        anime_mean_score = round(anime_mean_score / anime_ranked, 2)

        manga_completed = 0
        manga_current = 0
        manga_dropped = 0
        manga_paused = 0
        manga_planning = 0
        manga_repeating = 0
        manga_total = 0
        manga_stats = user_data.stats
        for stats in manga_stats.full_statuses.manga:
            match stats.grouped_id:
                case "planned":
                    manga_planning = stats.size
                case "watching":
                    manga_current = stats.size
                case "rewatching":
                    manga_repeating = stats.size
                case "completed":
                    manga_completed = stats.size
                case "on_hold":
                    manga_paused = stats.size
                case "dropped":
                    manga_dropped = stats.size
            manga_total += stats.size
        # calculate mean score
        manga_mean_score = 0
        manga_ranked = 0
        for score in manga_stats.scores.manga:
            manga_ranked += score.value
            manga_mean_score += int(score.name) * score.value
        manga_mean_score = round(manga_mean_score / manga_ranked, 2)

        embed_author = ipy.EmbedAuthor(
            name="Shikimori Profile",
            url="https://shikimori.me",
            icon_url="https://cdn.discordapp.com/emojis/1073441855645155468.webp",
        )
        embed_color = 0x343434
        components = [
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Shikimori Profile",
                url=user_url,
            ),
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Anime List",
                url=f"{user_url}/list/anime",
            ),
            ipy.Button(
                style=ipy.ButtonStyle.URL,
                label="Manga List",
                url=f"{user_url}/list/manga",
            ),
        ]
        embed = ipy.Embed(
            title=username,
            url=user_url,
            author=embed_author,
            color=embed_color,
            timestamp=dtime.now(tz=tz.utc),
        )
        embed.set_thumbnail(url=avatar)
        if embed_layout != "old":
            embed.add_fields(
                ipy.EmbedField(
                    name="👤 User ID",
                    value=f"`{user_id}`",
                    inline=True,
                ),
                ipy.EmbedField(name="🎂 Age", value=age_str, inline=True),
                ipy.EmbedField(name="🚁 Gender", value=gender_str, inline=True),
            )
            anime_value_str = f"""* Total: {anime_total:,}
* Mean Score: ⭐ {anime_mean_score}/10"""
            manga_value_str = f"""* Total: {manga_total:,}
* Mean Score: ⭐ {manga_mean_score}/10"""
            embed.add_field(
                name="🎞️ Anime List Summary",
                value=anime_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Anime Statuses",
                    value=f"""👀 Currently Watching: {anime_current:,}
🔁 Repeating: {anime_repeating:,}
✅ Completed: {anime_completed:,}
⏰ Planned: {anime_planning:,}
⏸️ On Hold: {anime_paused:,}
🗑️ Dropped: {anime_dropped:,}""",
                    inline=True,
                )
                ani_favs = user_data.favourites.animes
                ani_favs_str = ""
                if len(ani_favs) > 0:
                    ani_favs_top = ani_favs[:5]
                    for index, fav in enumerate(ani_favs_top):
                        if len(fav.name) >= 100:
                            fav.name = fav.name[:97] + "..."
                        ani_favs_str += f"{index + 1}. [{fav.name}](https://shikimori.me/animes/{fav.id})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Anime",
                    value=ani_favs_str if ani_favs_str not in ["", None] else "Unset",
                    inline=True,
                )
            embed.add_field(
                name="📔 Manga List Summary",
                value=manga_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Manga Statuses",
                    value=f"""👀 Currently Reading: {manga_current:,}
🔁 Repeating: {manga_repeating:,}
✅ Completed: {manga_completed:,}
⏰ Planned: {manga_planning:,}
⏸️ On Hold: {manga_paused:,}
🗑️ Dropped: {manga_dropped:,}""",
                    inline=True,
                )
                man_favs = user_data.favourites.mangas
                man_favs_str = ""
                if len(man_favs) > 0:
                    man_favs_top = man_favs[:5]
                    for index, fav in enumerate(man_favs_top):
                        if len(fav.name) >= 100:
                            fav.name = fav.name[:97] + "..."
                        man_favs_str += f"{index + 1}. [{fav.name}](https://shikimori.me/animes/{fav.id})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Manga",
                    value=man_favs_str if man_favs_str not in ["", None] else "Unset",
                    inline=True,
                )
        else:
            embed.add_fields(
                ipy.EmbedField(
                    name="Profile",
                    value=f"""* User ID: `{user_id}`
* Age: {age_str}
* Gender: {gender_str}""",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Anime List Summary",
                    value=f"""* Total: {anime_total:,}
* Mean Score: ⭐ {anime_mean_score}/10
👀 {anime_current:,} | 🔁 {anime_repeating:,} | ✅ {anime_completed:,} | ⏰ {anime_planning:,} | ⏸️ {anime_paused:,} | 🗑️ {anime_dropped:,}""",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Manga List Summary",
                    value=f"""* Total: {manga_total}
* Mean Score: ⭐ {manga_mean_score}/10
👀 {manga_current:,} | 🔁 {manga_repeating:,} | ✅ {manga_completed:,} | ⏰ {manga_planning:,} | ⏸️ {manga_paused:,} | 🗑️ {manga_dropped:,}""",
                    inline=True,
                ),
            )

        await ctx.send(embed=embed, components=components)


def setup(bot):
    Profile(bot)
