from typing import Literal

import interactions as ipy

from classes.i18n import LanguageDict
from modules.anilist import search_al_anime
from modules.commons import (generate_search_embed, sanitize_markdown,
                             save_traceback_to_file)
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.i18n import fetch_language_data, read_user_language
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
        ul: str = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul, use_raw=True)
        send: ipy.Message = await ctx.send(
            embed=ipy.Embed(
                title=l_["commons"]["search"]["init_title"],
                description=l_["commons"]["search"]["init"].format(
                    QUERY=query,
                    PLATFORM="MyAnimeList" if provider == "mal" else "AniList",
                ),
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
                media_type: str = l_["commons"]["media_formats"].get(
                    a["node"]["media_type"].lower(),
                    l_["commons"]["unknown"],
                )
                season: str = l_["commons"]["season"].get(
                    a["node"]["start_season"]["season"], "unknown"
                )
                year: str = (
                    a["node"]["start_season"]["year"]
                    or l_["commons"]["year"]["unknown"]
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
            title = l_["commons"]["search"]["result_title"].format(QUERY=query)
            if provider == "anilist":
                title += " (AniList)"
            result = generate_search_embed(
                title=title,
                language=ul,
                mediaType="anime",
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
            l_: dict[str, str] = l_["strings"]["anime"]["search"]["exception"]
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            embed = ipy.Embed(
                title=l_["title"], description=l_["text"] .replace(
                    "MyAnimeList", "AniList" if provider == "anilist" else "MyAnimeList") .format(
                    QUERY=f"`{query}`"), color=0xFF0000, footer=ipy.EmbedFooter(
                    text=l_["footer"]), )
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
        # grab "message_delete" button
        keep_components: list[ipy.ActionRow] = []
        for action_row in ctx.message.components:
            for comp in action_row.components:
                if comp.custom_id == "message_delete":
                    comp.label = "Delete message"
                    keep_components.append(action_row)
        await ctx.message.edit(components=keep_components)

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
        sub_cmd_description="Get a random anime, powered by AnimeAPI",
    )
    async def anime_random(self, ctx: ipy.SlashContext):
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
        anime = lookup_random_anime()
        await send.edit(
            embed=ipy.Embed(
                title="Random Anime",
                description=f"We've found MAL ID [`{anime}`](https://myanimelist.net/anime/{anime}). Fetching info...",
                color=0x213498,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        await mal_submit(ctx, anime)


def setup(bot):
    Anime(bot)
