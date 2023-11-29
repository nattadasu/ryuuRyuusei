from datetime import datetime as dtime
from datetime import timezone as tz
from typing import Literal

import interactions as ipy

from classes.database import DatabaseException, UserDatabase, UserDatabaseClass
from classes.excepts import ProviderHttpError
from classes.shikimori import (Shikimori, ShikimoriUserGender,
                               ShikimoriUserStruct)
from modules.commons import (PlatformErrType, platform_exception_embed,
                             save_traceback_to_file)


class ShikimoriCog(ipy.Extension):
    """Extension for interacting with Shikimori"""

    shikimori_head = ipy.SlashCommand(
        name="shikimori",
        description="Get useful information from Shikimori",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5
        )
    )

    @shikimori_head.subcommand(
        sub_cmd_name="profile",
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
    async def shikimori_profile(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member | ipy.User | None = None,
        shikimori_username: str | None = None,
        embed_layout: Literal["minimal", "old", "new"] = "minimal",
    ) -> None:
        await ctx.defer()
        user_data: ShikimoriUserStruct | None
        base_url = "https://shikimori.one"

        if shikimori_username and user:
            embed = platform_exception_embed(
                description="You can't use both `user` and `shikimori_username` options at the same time!",
                error_type=PlatformErrType.USER,
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
                    error="User hasn't link their account yet",
                )
                await ctx.send(embed=embed)
                return

        try:
            async with Shikimori() as shiki:
                user_data = await shiki.get_user(
                    user_id=shikimori_username,
                    is_nickname=True,
                )
        except ProviderHttpError as e:
            embed = platform_exception_embed(
                description=e.message,
                error_type=PlatformErrType.SYSTEM,
                error="Error while getting user data",
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("shikimori_profile", ctx.author, e)

        if user_data is None:
            embed = platform_exception_embed(
                description=f"User `{shikimori_username}` not found!",
                error_type=PlatformErrType.USER,
                error="User not found",
            )
            await ctx.send(embed=embed)
            return

        username = user_data.nickname
        user_id = user_data.id
        avatar = user_data.image.x160
        user_url = user_data.url
        gender = user_data.sex
        match gender:
            case ShikimoriUserGender.UNKNOWN | None:
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
                case _:
                    continue
            anime_total += stats.size
        # calculate mean score
        anime_mean_score = 0
        anime_ranked = 0
        for score in anime_stats.scores.anime:
            anime_ranked += score.value
            anime_mean_score += int(score.name) * score.value
        anime_mean_score = round(anime_mean_score / anime_ranked, 2)
        title_watched = anime_completed + anime_current + anime_repeating

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
                case _:
                    continue
            manga_total += stats.size
        # calculate mean score
        manga_mean_score = 0
        manga_ranked = 0
        for score in manga_stats.scores.manga:
            manga_ranked += score.value
            manga_mean_score += int(score.name) * score.value
        manga_mean_score = round(manga_mean_score / manga_ranked, 2)
        title_read = manga_completed + manga_current + manga_repeating

        embed_author = ipy.EmbedAuthor(
            name="Shikimori Profile",
            url=base_url,
            icon_url="https://cdn.discordapp.com/emojis/1073441855645155468.webp",
        )
        embed_color = 0x343434
        components = [
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
* Mean Score: ⭐ {anime_mean_score}/10
* Anime Watched: {title_watched:,}"""
            manga_value_str = f"""* Total: {manga_total:,}
* Mean Score: ⭐ {manga_mean_score}/10
* Manga Read: {title_read:,}"""
            embed.add_field(
                name="🎞️ Anime List Summary",
                value=anime_value_str,
                inline=embed_layout == "minimal",
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Anime Statuses",
                    value=f"""👀 Watching: {anime_current:,}
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
                        ani_favs_str += f"{index + 1}. [{fav.name}]({base_url}/animes/{fav.id})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Anime",
                    value=ani_favs_str if ani_favs_str not in [
                        "", None] else "Unset",
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
                    value=f"""👀 Reading: {manga_current:,}
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
                        man_favs_str += f"{index + 1}. [{fav.name}]({base_url}/animes/{fav.id})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Manga",
                    value=man_favs_str if man_favs_str not in [
                        "", None] else "Unset",
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
* Anime Watched: {title_watched:,}
👀 {anime_current:,} | 🔁 {anime_repeating:,} | ✅ {anime_completed:,} | ⏰ {anime_planning:,} | ⏸️ {anime_paused:,} | 🗑️ {anime_dropped:,}""",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Manga List Summary",
                    value=f"""* Total: {manga_total}
* Mean Score: ⭐ {manga_mean_score}/10
* Manga Read: {title_read:,}
👀 {manga_current:,} | 🔁 {manga_repeating:,} | ✅ {manga_completed:,} | ⏰ {manga_planning:,} | ⏸️ {manga_paused:,} | 🗑️ {manga_dropped:,}""",
                    inline=True,
                ),
            )

        await ctx.send(embed=embed, components=components)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    ShikimoriCog(bot)
