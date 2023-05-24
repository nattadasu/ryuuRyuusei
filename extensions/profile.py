from datetime import datetime as dtime
from datetime import timezone as tz
from typing import Literal
from urllib.parse import quote_plus as urlquote, quote

import interactions as ipy

from classes.database import DatabaseException, UserDatabase
from classes.excepts import ProviderHttpError
from classes.jikan import JikanApi, JikanException
from classes.lastfm import LastFM, LastFMTrackStruct, LastFMUserStruct
from classes.pronoundb import PronounDB, Pronouns
from modules.commons import (
    convert_float_to_time,
    generate_commons_except_embed,
    sanitize_markdown,
)
from modules.i18n import fetch_language_data, read_user_language
from modules.myanimelist import MalErrType, mal_exception_embed


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
        await ctx.defer()
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
            async with PronounDB() as pdb:
                pronouns = await pdb.get_pronouns(pdb.Platform.DISCORD, userId)
                if pronouns.pronouns == Pronouns.UNSPECIFIED:
                    pronouns = "Unset"
                else:
                    pronouns = pdb.translate_shorthand(pronouns.pronouns)

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
                    ipy.SlashCommandChoice(name="Old", value="old"),
                    ipy.SlashCommandChoice(name="Highly Detailed", value="new"),
                ],
            ),
        ],
    )
    async def profile_myanimelist(
        self,
        ctx: ipy.SlashContext,
        user: ipy.User = None,
        mal_username: str = None,
        embed_layout: Literal["minimal", "old", "new"] = "minimal",
    ):
        await ctx.defer()
        l_ = fetch_language_data("en_US", True)

        if mal_username and user:
            embed = mal_exception_embed(
                description="You can't use both `user` and `mal_username` options at the same time!",
                error_type=MalErrType.USER,
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
            embed = mal_exception_embed(
                description=f"<@!{user.id}> haven't registered the MyAnimeList account to the bot yet!\nUse `/register` to register",
                error_type=MalErrType.USER,
                lang_dict=l_,
                error="User hasn't registered their MAL account yet",
            )
            await ctx.send(embed=embed)
            return

        try:
            async with JikanApi() as jikan:
                user_data = await jikan.get_user_data(username=mal_username)
        except JikanException as e:
            embed = mal_exception_embed(
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
        if location not in ["", None]:
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
            today = dtime.utcnow()
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
                name=f"MyAnimeList Profile",
                url=f"https://myanimelist.net/",
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
            embed.add_field(
                name="🎞️ Anime List Summary",
                value=f"""* Total: {anime.total_entries}
* Mean Score: ⭐ {anime.mean_score}/10
* Days Watched: {anime_float}
* Episodes Watched: {anime.episodes_watched}""",
                inline=True if embed_layout == "minimal" else False,
            ),
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Anime Statuses",
                    value=f"""👀 Currently Watching: {anime.watching}
✅ Completed: {anime.completed}
⏰ Planned: {anime.plan_to_watch}
⏸️ On Hold: {anime.on_hold}
🗑️ Dropped: {anime.dropped}""",
                    inline=True,
                )
                ani_favs = user_data.favorites.anime
                ani_fav_list = ""
                if len(ani_favs) > 0:
                    ani_fav_top = ani_favs[:5]
                    # generate string
                    for index, anime in enumerate(ani_fav_top):
                        # trim title up to 200 characters
                        if len(anime.title) > 200:
                            anime.title = anime.title[:197] + "..."
                        split = anime.url.split("/")
                        if split[-1].isdigit() is False:
                            anime.url = "/".join(split[:-1])
                        ani_fav_list += f"{index+1}. [{anime.title}]({anime.url})\n"
                embed.add_field(
                    name="🌟 Top 5 Favorite Anime",
                    value=ani_fav_list if ani_fav_list not in ["", None] else "Unset",
                    inline=True,
                )
            embed.add_field(
                name="📔 Manga List Summary",
                value=f"""* Total: {manga.total_entries}
* Mean Score: ⭐ {manga.mean_score}/10
* Days Read, Estimated: {manga_float}
* Chapters Read: {manga.chapters_read}
* Volumes Read: {manga.volumes_read}""",
                inline=True if embed_layout == "minimal" else False,
            )
            if embed_layout == "new":
                embed.add_field(
                    name="ℹ️ Manga Statuses",
                    value=f"""👀 Currently Reading: {manga.reading}
✅ Completed: {manga.completed}
⏰ Planned: {manga.plan_to_read}
⏸️ On Hold: {manga.on_hold}
🗑️ Dropped: {manga.dropped}""",
                    inline=True,
                )
                man_favs = user_data.favorites.manga
                man_fav_list = ""
                if len(man_favs) > 0:
                    man_fav_top = man_favs[:5]
                    for index, manga in enumerate(man_fav_top):
                        if len(manga.title) > 200:
                            manga.title = manga.title[:197] + "..."
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
                    value=f"""* Total: {anime.total_entries}
* Mean Score: ⭐ {anime.mean_score}/10
* Days Watched: {anime_float}
* Episodes Watched: {anime.episodes_watched}
👀 {anime.watching} | ✅ {anime.completed} | ⏰ {anime.plan_to_watch} | ⏸️ {anime.on_hold} | 🗑️ {anime.dropped}""",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Manga List Summary",
                    value=f"""* Total: {manga.total_entries}
* Mean Score: ⭐ {manga.mean_score}/10
* Days Read, Estimated: {manga_float}
* Chapters Read: {manga.chapters_read}
* Volumes Read: {manga.volumes_read}
👀 {manga.reading} | ✅ {manga.completed} | ⏰ {manga.plan_to_read} | ⏸️ {manga.on_hold} | 🗑️ {manga.dropped}""",
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
        await ctx.defer()
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
