"""
MyAnimeList extension for the bot

Contains:
- /myanimelist profile [user] [mal_username] [embed_layout] - Shows the profile
  of a user on MyAnimeList directly on Discord
"""

import re
from datetime import datetime as dtime
from datetime import timezone as tz
from typing import Any, Literal
from urllib.parse import quote

import interactions as ipy

from classes.database import DatabaseException, UserDatabase
from classes.excepts import ProviderHttpError
from classes.html.myanimelist import HtmlMyAnimeList
from classes.jikan import JikanApi, JikanException, JikanUserStruct
from classes.rss.myanimelist import MediaStatus
from classes.rss.myanimelist import MyAnimeListRss as Rss
from classes.rss.myanimelist import RssItem
from modules.commons import (PlatformErrType, convert_float_to_time,
                             platform_exception_embed, sanitize_markdown,
                             save_traceback_to_file)


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
        sub_cmd_description="Get a user's profile",
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
                        value="minimal"),
                    ipy.SlashCommandChoice(
                        name="Classic",
                        value="old"),
                    ipy.SlashCommandChoice(
                        name="Highly Detailed",
                        value="new"),
                    ipy.SlashCommandChoice(
                        name="Activities by progress",
                        value="timeline"),
                    ipy.SlashCommandChoice(
                        name="Activities by title",
                        value="timeline_title"),
                ],
            ),
        ],
    )
    async def myanimelist_profile(
        self,
        ctx: ipy.SlashContext,
        user: ipy.User | ipy.Member | None = None,
        mal_username: str | None = None,
        embed_layout: Literal["minimal", "old", "new",
                              "timeline", "timeline_title"] = "minimal",
    ):
        """
        /myanimelist profile [user] [mal_username] [embed_layout]

        Get a user's profile

        Parameters
        ----------
        user : ipy.User | ipy.Member | None, optional
            The user to get the profile of, if registered, defaults to you, by default None

        mal_username : str | None, optional
            Username on MyAnimeList to get profile information of, by default None

        embed_layout : Literal["minimal", "old", "new", "timeline", "timeline_title"], optional
            Layout of the embed, by default "minimal"
        """
        await ctx.defer()
        user_data: JikanUserStruct | None = None
        extended: JikanUserStruct = JikanUserStruct(
            mal_id=0, username="", url="", joined=dtime.now())

        if mal_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `mal_username` options at the same time!",
                error_type=PlatformErrType.USER,
                error="User and mal_username options used at the same time",
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            user = ctx.author

        if mal_username is None:
            try:
                async with UserDatabase() as database:
                    data_ = await database.get_user_data(discord_id=user.id)
                    mal_username = data_.mal_username
            except DatabaseException:
                mal_username = None

        if mal_username is None:
            embed = platform_exception_embed(
                description=f"""{user.mention} haven't registered the MyAnimeList account to the bot yet!
Use `/register` to register, or use `/myanimelist profile mal_username:<username>` to get the profile information of a user without registering their account to the bot""",
                error_type=PlatformErrType.USER,
                error="User hasn't registered their MAL account yet",
            )
            await ctx.send(embed=embed)
            return

        try:
            async with HtmlMyAnimeList() as html:
                extended = await html.get_user(mal_username)
            if embed_layout not in ["timeline", "timeline_title"]:
                async with JikanApi() as jikan:
                    user_data = await jikan.get_user_data(mal_username.lower())
            else:
                user_data = extended
        except JikanException as error:
            embed = platform_exception_embed(
                description="Jikan API returned an error",
                error_type=error.status_code,
                error=error.message,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("myanimelist_profile", ctx.author, error)
        except ProviderHttpError as error:
            embed = platform_exception_embed(
                description="MyAnimeList returned an error",
                error_type=error.status_code,
                error=error.message,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("myanimelist_profile", ctx.author, error)

        if user_data is None:
            embed = platform_exception_embed(
                description=f"""We couldn't find the user `{mal_username}` on MyAnimeList!""",
                error_type=PlatformErrType.USER,
                error="User not found",
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
        if user_data.gender not in ["", None]:
            gender = user_data.gender
        else:
            gender = "Unset"
        days_watched = 0
        days_read = 0
        title_watched = 0
        title_read = 0
        if user_data.statistics:
            anime = user_data.statistics.anime
            if anime and anime.days_watched:
                days_watched = anime.days_watched
            if anime and (anime.watching or anime.completed):
                title_watched = (anime.watching or 0) + (anime.completed or 0)
            manga = user_data.statistics.manga
            if manga and manga.days_read:
                days_read = manga.days_read
            if manga and (manga.reading or manga.completed):
                title_read = (manga.reading or 0) + (manga.completed or 0)
        else:
            anime = None
            manga = None
        anime_float = convert_float_to_time(days_watched)
        manga_float = convert_float_to_time(days_read)
        time_wasted = convert_float_to_time(days_watched + days_read)
        joined = int(user_data.joined.timestamp()) if user_data.joined else 0
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

        if embed_layout != "minimal":
            birthday_formatted = (
                f"{birthday_str} {birthday_rel} (Next birthday {birthday_rem})"
                if birthday_str
                else "Unset"
            )
        else:
            birthday_formatted = (
                f"{birthday_str}"
                if birthday_str
                else "Unset"
            )

        if embed_layout == "minimal":
            joined_formatted = f"<t:{joined}:R>"
        else:
            joined_formatted = f"<t:{joined}:D> (<t:{joined}:R>)"

        last_online = extended.last_online.timestamp() if extended.last_online else 0

        components = [
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
            timestamp=dtime.now(tz=tz.utc),  # type: ignore
        )
        if user_data.images and user_data.images.webp:
            embed.set_thumbnail(url=user_data.images.webp.image_url)

        if embed_layout in ["minimal", "new"]:
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
                    ipy.EmbedField(name="🚁 Gender", value=f"{gender}",
                                   inline=True),  # type: ignore
                    ipy.EmbedField(name="📍 Location",
                                   value=location, inline=True),
                    ipy.EmbedField(name="📅 Last Online",
                                   value=f"<t:{int(last_online)}:R>",
                                   inline=True),
                )
            anime_value_str = f"""* Total: {anime.total_entries:,}
* Mean Score: ⭐ {anime.mean_score}/10
* Anime Watched: {title_watched:,}
* Episodes Watched: {anime.episodes_watched:,}
* Time Wasted: {anime_float}"""
            embed.add_field(
                name="🎞️ Anime List Summary",
                value=anime_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Anime Statuses",
                    value=f"""👀 Watching: {anime.watching:,}
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
                    for index, ani in enumerate(ani_fav_top):
                        if len(ani.title) >= 100:
                            ani.title = ani.title[:97] + "..."
                        split = ani.url.split("/")
                        if split[-1].isdigit() is False:
                            ani.url = "/".join(split[:-1])
                        ani_fav_list += f"{index+1}. [{ani.title}]({ani.url})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Anime",
                    value=ani_fav_list if ani_fav_list not in [
                        "", None] else "Unset",
                    inline=True,
                )
            manga_value_str = f"""* Total: {manga.total_entries:,}
* Mean Score: ⭐ {manga.mean_score}/10
* Manga Read: {title_read:,}
* Chapters Read: {manga.chapters_read:,}
* Volumes Read: {manga.volumes_read:,}
* Time Wasted, Estimated: {manga_float}"""
            embed.add_field(
                name="📔 Manga List Summary",
                value=manga_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Manga Statuses",
                    value=f"""👀 Reading: {manga.reading:,}
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
                    for index, man in enumerate(man_fav_top):
                        if len(man.title) >= 100:
                            man.title = man.title[:97] + "..."
                        split = man.url.split("/")
                        if split[-1].isdigit() is False:
                            man.url = "/".join(split[:-1])
                        man_fav_list += f"{index+1}. [{man.title}]({man.url})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Manga",
                    value=man_fav_list if man_fav_list not in [
                        "", None] else "Unset",
                    inline=True,
                )
        elif embed_layout == "old":
            embed.add_fields(
                ipy.EmbedField(
                    name="Profile",
                    value=f"""* User ID: `{user_id}`
* Account created: {joined_formatted}
* Birthday: {birthday_formatted}
* Gender: {gender}
* Location: {location}
* Last Online: <t:{int(last_online)}:R>""",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Anime List Summary",
                    value=f"""* Total: {anime.total_entries:,}
* Mean Score: ⭐ {anime.mean_score}/10
* Anime Watched: {title_watched:,}
* Episodes Watched: {anime.episodes_watched:,}
* Time Wasted: {anime_float}
👀 {anime.watching:,} | ✅ {anime.completed:,} | ⏰ {anime.plan_to_watch:,} | ⏸️ {anime.on_hold:,} | 🗑️ {anime.dropped:,}""",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Manga List Summary",
                    value=f"""* Total: {manga.total_entries:,}
* Mean Score: ⭐ {manga.mean_score}/10
* Manga Read: {title_read:,}
* Chapters Read: {manga.chapters_read:,}
* Volumes Read: {manga.volumes_read:,}
* Time Wasted, Estimated: {manga_float}
👀 {manga.reading:,} | ✅ {manga.completed:,} | ⏰ {manga.plan_to_read:,} | ⏸️ {manga.on_hold:,} | 🗑️ {manga.dropped:,}""",
                    inline=True,
                ),
            )
        elif embed_layout in ["timeline", "timeline_title"]:
            try:
                async with Rss("anime", embed_layout == "timeline") as ani:
                    ani_data = await ani.get_user(username)
                    ani_data_total = len(ani_data)
                if ani_data_total > 0:
                    ani_data: list[RssItem | str] = ani_data[:5]
                    for index, anime in enumerate(ani_data):
                        if isinstance(anime, str):
                            continue
                        if len(anime.title) >= 50:
                            anime.title = anime.title[:47] + "..."
                        # convert to epoch
                        timestamp = int(anime.updated.timestamp())
                        status = ""
                        match anime.status:
                            case MediaStatus.WATCHING:
                                status = "👀"
                            case MediaStatus.COMPLETED:
                                status = "✅"
                            case MediaStatus.ON_HOLD:
                                status = "⏸️"
                            case MediaStatus.DROPPED:
                                status = "🗑️"
                            case MediaStatus.PLAN_TO_WATCH:
                                status = "⏰"
                        anime.progress_to = "*Unknown*" if anime.progress_to is None else anime.progress_to
                        ani_data[index] = f"{index+1}. {status} [{anime.title}]({anime.url}), {anime.progress_from}/{anime.progress_to}, <t:{timestamp}:R>"
                    ani_data.append(f"And {ani_data_total-5} more...")
                else:
                    ani_data = ["No recent activity"]
            except ProviderHttpError as err:
                if err.status_code == 403:
                    man_data = [
                        "No recent activity, most likely due to private profile."]
                else:
                    embed = platform_exception_embed(
                        description="MyAnimeList returned an error",
                        error_type=error.status_code,
                        error=error.message,
                    )
                await ctx.send(embed=embed)
                save_traceback_to_file(
                    "myanimelist_profile", ctx.author, error)
            try:
                async with Rss("manga", embed_layout == "timeline") as man:
                    man_data = await man.get_user(username)
                man_data_total = len(man_data)
                if man_data_total > 0:
                    man_data: list[RssItem | str] = man_data[:5]
                    for index, manga in enumerate(man_data):
                        if isinstance(manga, str):
                            continue
                        if len(manga.title) >= 50:
                            manga.title = manga.title[:47] + "..."
                        # convert to epoch
                        timestamp = int(manga.updated.timestamp())
                        status = ""
                        match manga.status:
                            case MediaStatus.READING:
                                status = "👀"
                            case MediaStatus.PLAN_TO_READ:
                                status = "⏰"
                            case MediaStatus.COMPLETED:
                                status = "✅"
                            case MediaStatus.ON_HOLD:
                                status = "⏸️"
                            case MediaStatus.DROPPED:
                                status = "🗑️"
                        manga.progress_to = "*Unknown*" if manga.progress_to is None else manga.progress_to
                        man_data[index] = f"{index+1}. {status} [{manga.title}]({manga.url}), {manga.progress_from}/{manga.progress_to}, <t:{timestamp}:R>"
                    man_data.append(f"And {man_data_total-5} more...")
                else:
                    man_data = ["No recent activity"]
            except ProviderHttpError as err:
                if err.status_code == 403:
                    man_data = [
                        "No recent activity, most likely due to private profile."]
                else:
                    embed = platform_exception_embed(
                        description="MyAnimeList returned an error",
                        error_type=error.status_code,
                        error=error.message,
                    )
                await ctx.send(embed=embed)
                save_traceback_to_file(
                    "myanimelist_profile", ctx.author, error)
            # convert to string
            ani_data = "\n".join(ani_data)
            man_data = "\n".join(man_data)

            embed.add_field(
                name="📺 Recent Anime Activity",
                value=ani_data,
                inline=True,
            )
            embed.add_field(
                name="📚 Recent Manga Activity",
                value=man_data,
                inline=True,
            )

        if embed_layout in ["old", "new"]:
            components += [
                ipy.Button(
                    style=ipy.ButtonStyle.URL,
                    label="Statistics",
                    url=f"https://myanimelist.net/profile/{username}/statistics"
                ),
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

        foo = ""
        if embed_layout in ["new", "minimal", "old"]:
            if gender:
                direct_pronoun_match = re.search(
                    r'\b(?:he|him|she|her|they|them)\b', gender, re.IGNORECASE)
                if direct_pronoun_match:
                    direct_pronoun = direct_pronoun_match.group().lower()
                    pronouns = {'he': 'his', 'him': 'his', 'she': 'her',
                                'her': 'hers', 'they': 'their', 'them': 'theirs'}[direct_pronoun]
                else:
                    # Define regular expression patterns for each gender and their derivatives
                    male_pattern = r'\b(?:boy|m(ale)?|man|bro(ther)?)\b'
                    female_pattern = r'\b(?:girl|f(emale)?|woman|sis(ter)?)\b'

                    # Check for gender-sensitive matches using regex with case-insensitive flag
                    if re.search(male_pattern, gender, re.IGNORECASE):
                        pronouns = "his"
                    elif re.search(female_pattern, gender, re.IGNORECASE):
                        pronouns = "her"
                    else:
                        pronouns = "their"
            else:
                pronouns = "their"
            if time_wasted.count(",") > 1:
                time_wasted = time_wasted.rsplit(",", 1)
                time_wasted = " and".join(time_wasted)
            foo = f"This user has wasted {pronouns} life watching and reading for {time_wasted}"
        elif embed_layout in ["timeline", "timeline_title"]:
            foo = "Live feed sourced from the user's RSS feed"

        embed.set_footer(text=foo)

        await ctx.send(embed=embed, components=components)


def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    """Load the Cog"""
    MyAnimeListCog(bot)
