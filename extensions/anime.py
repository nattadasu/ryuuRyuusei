from typing import Literal

import interactions as ipy

from classes.anibrain import AniBrainAI
from modules.anilist import search_al_anime
from modules.commons import (generate_search_embed, sanitize_markdown,
                             save_traceback_to_file)
from modules.const import EMOJI_UNEXPECTED_ERROR, STR_RECOMMEND_NATIVE_TITLE
from modules.myanimelist import (lookup_random_anime, mal_submit,
                                 search_mal_anime)


class Anime(ipy.Extension):
    """Anime commands"""

    anime_head = ipy.SlashCommand(
        name="anime",
        description="Get anime information from MyAnimeList via Jikan and AniList",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
        ),
    )

    @anime_head.subcommand(
        sub_cmd_name="search",
        sub_cmd_description="Search for anime",
        options=[
            ipy.SlashCommandOption(
                name="query",
                description="The anime title to search for",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="provider",
                description="The anime provider to search for",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(
                        name="AniList (Default)", value="anilist"),
                    ipy.SlashCommandChoice(name="MyAnimeList", value="mal"),
                ],
            ),
        ],
    )
    async def anime_search(
        self,
        ctx: ipy.SlashContext,
        query: str,
        provider: Literal["anilist", "mal"] = "anilist",
    ):
        await ctx.defer()
        platform: str = "AniList" if provider == "anilist" else "MyAnimeList"
        send: ipy.Message = await ctx.send(
            embed=ipy.Embed(
                title="Searching...",
                description=f"Searching `{query}` on `{platform}`.",
            )
        )
        try:
            if provider == "anilist":
                res = await search_al_anime(title=query)
            elif provider == "mal":
                res = await search_mal_anime(title=query)
            if not res:
                raise Exception("No result")
            f: list[ipy.EmbedField] = []
            so: list[ipy.StringSelectOption] = []
            for a in res:
                if a["node"]["start_season"] is None:
                    a["node"]["start_season"] = {
                        "season": "Unknown", "year": "Year"}
                media_type: str = a["node"]["media_type"] or "Unknown"
                season: str = a["node"]["start_season"]["season"] or "Unknown"
                year: str = (
                    a["node"]["start_season"]["year"]
                    or "Unknown Year"
                )
                title: str = a["node"]["title"]
                if len(title) >= 256:
                    title = title[:253] + "..."
                mdTitle: str = sanitize_markdown(title)
                alt = a["node"]["alternative_titles"]
                native: str = (
                    sanitize_markdown(alt["ja"]) +
                    "\n" if alt and alt["ja"] else ""
                )
                f.append(
                    ipy.EmbedField(
                        name=mdTitle,
                        value=f"{native}`{a['node']['id']}`, {media_type}, {season} {year}",
                        inline=False,
                    ))
                so.append(
                    ipy.StringSelectOption(
                        label=title[:77] + ("..." if len(title) > 77 else ""),
                        value=a["node"]["id"],
                        description=f"{media_type}, {season} {year}",
                    )
                )
            title = f"Search Results for `{query}`"
            if provider == "anilist":
                title += " (AniList)"
            result = generate_search_embed(
                title=title,
                media_type="anime",
                query=query,
                platform="MyAnimeList",
                homepage="https://myanimelist.net",
                results=f,
                icon="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png",
                color=0x2F51A3,
            )
            components: list[ipy.ActionRow] = ipy.spread_to_rows(
                ipy.StringSelectMenu(
                    *so, placeholder="Choose an anime", custom_id="mal_search"
                ),
                ipy.Button(
                    style=ipy.ButtonStyle.DANGER,
                    label="Cancel",
                    custom_id="message_delete",
                    emoji="🗑️",
                ),
            )
            await send.edit(
                embed=result,
                components=components,
            )
        except Exception as _:
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            err_msg = f"I couldn't able to find any results for {query} on {platform}. Please check your query and try again."
            foo_msg = STR_RECOMMEND_NATIVE_TITLE
            embed = ipy.Embed(
                title="Error",
                description=err_msg.replace("\n", ""),
                color=0xFF0000,
                footer=ipy.EmbedFooter(foo_msg.replace("\n", "")))
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
            )
            await send.edit(
                embed=embed,
                components=ipy.Button(
                    style=ipy.ButtonStyle.DANGER,
                    label="Delete",
                    custom_id="message_delete",
                    emoji="🗑️"
                ),
            )
            save_traceback_to_file("anime_search", ctx.author, _)

    @ipy.component_callback("mal_search")
    async def anime_search_data(self, ctx: ipy.ComponentContext) -> None:
        await ctx.defer()
        ani_id: int = int(ctx.values[0])
        await mal_submit(ctx, ani_id)
        await ctx.message.delete() if ctx.message else None

    @anime_head.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Get anime information",
        options=[
            ipy.SlashCommandOption(
                name="mal_id",
                description="The anime ID on MyAnimeList to get information from",
                type=ipy.OptionType.INTEGER,
                required=True,
            ),
        ],
    )
    async def anime_info(self, ctx: ipy.SlashContext, mal_id: int):
        await ctx.defer()
        await mal_submit(ctx, mal_id)

    @anime_head.subcommand(
        sub_cmd_name="random",
        sub_cmd_description="Get a random anime, powered by AniBrain and AnimeAPI",
        options=[
            ipy.SlashCommandOption(
                name="media_type",
                description="The media type to get",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(name="Any (default)", value="any"),
                    ipy.SlashCommandChoice(name="TV", value="tv"),
                    ipy.SlashCommandChoice(name="Movie", value="movie"),
                    ipy.SlashCommandChoice(name="OVA", value="ova"),
                    ipy.SlashCommandChoice(name="ONA", value="ona"),
                    ipy.SlashCommandChoice(name="Special", value="special"),
                    ipy.SlashCommandChoice(name="TV Short", value="tv short"),
                ],
            )
        ],
    )
    async def anime_random(self, ctx: ipy.SlashContext, media_type: str = "any"):
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Random Anime",
                description="Getting a random anime...",
                color=0x213498,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        try:
            async with AniBrainAI() as ai:
                countries = [
                    ai.CountryOfOrigin.CHINA,
                    ai.CountryOfOrigin.JAPAN,
                    ai.CountryOfOrigin.KOREA,
                    ai.CountryOfOrigin.TAIWAN,
                ]
                if media_type != "any":
                    target_media_type = [ai.AnimeMediaType(media_type)]
                else:
                    target_media_type = "[]"
                media_data = await ai.get_anime(filter_country=countries,
                                                filter_format=target_media_type)
                # find the first anime with a valid MAL ID
                for ani in media_data:
                    if ani.myanimelistId:
                        anime = ani.myanimelistId
                        sauce = "AniBrain"
                        break
                else:
                    raise Exception("No result")
        except Exception as err:
            save_traceback_to_file("anime_random", ctx.author, err, True)
            anime = lookup_random_anime()
            sauce = "AnimeAPI"
        found = ipy.Embed(
            title="Random Anime",
            description=f"We've found MAL ID [`{anime}`](https://myanimelist.net/anime/{anime}) from {sauce}. Fetching info...",
            color=0x213498,
            footer=ipy.EmbedFooter(
                text="This may take a while...",
            ),
        )
        if sauce == "AnimeAPI" and media_type != "any":
            media_type = "TV Short" if media_type == "tv short" else media_type.upper(
            ) if len(media_type) <= 4 else media_type.title()
            media_type = f"an {media_type}" if media_type[0] in "aeiou" else f"a {media_type}"
            found.add_field(
                name="Note",
                value=f"AnimeAPI doesn't support filtering by media type. The anime may not be {media_type}.",
                inline=False,
            )
        await send.edit(
            embed=found
        )
        await mal_submit(ctx, anime)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    Anime(bot)
