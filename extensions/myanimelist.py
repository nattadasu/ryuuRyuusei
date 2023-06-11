from datetime import datetime as dtime
from datetime import timezone as tz
from typing import Literal
from urllib.parse import quote

import interactions as ipy

from classes.database import DatabaseException, UserDatabase
from classes.i18n import LanguageDict
from classes.jikan import JikanApi, JikanException
from modules.commons import (
    PlatformErrType,
    convert_float_to_time,
    platform_exception_embed,
    sanitize_markdown,
)
from modules.i18n import fetch_language_data


class MyAnimeListCog(ipy.Extension):
    """Extension for interacting with MyAnimeList"""

    myanimelist_head = ipy.SlashCommand(
        name="myanimelist",
        description="Get useful information from MyAnimeList",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5
        )
    )

    @myanimelist_head.subcommand(
        sub_cmd_name="profile",
        description="Get a user's profile",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="The user to get the profile of, if registered, defaults to you",
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
                    ipy.SlashCommandChoice(
                        name="Highly Detailed", value="new"),
                ],
            ),
        ],
    )
    async def myanimelist_profile(
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
        gender = user_data.gender if user_data.gender not in [
            "", None] else "Unset"
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
                    ipy.EmbedField(name="📍 Location",
                                   value=location, inline=True),
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
                    value=ani_fav_list if ani_fav_list not in [
                        "", None] else "Unset",
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
                    value=man_fav_list if man_fav_list not in [
                        "", None] else "Unset",
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
            embed.set_image(
                url=f"https://malheatmap.com/users/{username}/signature")
            embed.set_footer(
                text="Powered by Jikan API for data and MAL Heatmap for Activity Heatmap. Data can be inacurrate as Jikan and Ryuusei cache your profile up to a day"
            )
        else:
            embed.set_footer(
                text='Powered by Jikan API for data. To expand what data will be shown, modify embed_layout parameter to "old" or "new"'
            )

        await ctx.send(embed=embed, components=components)


def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    """Load the Cog"""
    MyAnimeListCog(bot)
