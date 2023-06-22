from datetime import datetime as dtime
from datetime import timezone as tz
from typing import Literal

import interactions as ipy

from classes.anilist import AniList, AniListUserStruct
from classes.database import DatabaseException, UserDatabase, UserDatabaseClass
from classes.excepts import ProviderHttpError
from classes.i18n import LanguageDict
from modules.commons import (PlatformErrType, convert_float_to_time,
                             platform_exception_embed, sanitize_markdown,
                             save_traceback_to_file)
from modules.i18n import fetch_language_data, read_user_language


class AniListCog(ipy.Extension):
    """Extension for interacting with AniList"""

    anilist_head = ipy.SlashCommand(
        name="anilist",
        description="Get useful information from AniList",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5
        )
    )

    @anilist_head.subcommand(
        sub_cmd_name="profile",
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
                    ipy.SlashCommandChoice(
                            name="Card",
                            value="card"),
                    ipy.SlashCommandChoice(
                        name="Minimal (default)",
                        value="minimal"),
                    ipy.SlashCommandChoice(
                        name="Classic",
                        value="old"),
                    ipy.SlashCommandChoice(
                        name="Highly Detailed",
                        value="new"),
                ],
            ),
        ],
    )
    async def anilist_profile(
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
                error=f"{e.message}",
                lang_dict=l_,
                error_type=PlatformErrType.SYSTEM,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("anilist_profile", ctx.author, e)

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
        anime_total = (
            anime_completed
            + anime_current
            + anime_dropped
            + anime_paused
            + anime_planning
        )
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
        manga_total = (
            manga_completed
            + manga_current
            + manga_dropped
            + manga_paused
            + manga_planning
        )
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


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    AniListCog(bot)
