from typing import Literal

import interactions as ipy

from classes.anibrain import AniBrainAI
from classes.excepts import ProviderHttpError
from modules.anilist import search_al_anime
from modules.commons import (
    generate_search_embed,
    sanitize_markdown,
    save_traceback_to_file,
)
from modules.const import (
    EMOJI_ATTENTIVE,
    EMOJI_UNEXPECTED_ERROR,
    STR_RECOMMEND_NATIVE_TITLE,
)
from modules.myanimelist import lookup_random_anime, mal_submit, search_mal_anime


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
                    ipy.SlashCommandChoice(name="AniList (Default)", value="anilist"),
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
                    a["node"]["start_season"] = {"season": "Unknown", "year": "Year"}
                media_type: str = a["node"]["media_type"] or "Unknown"
                season: str = a["node"]["start_season"]["season"] or "Unknown"
                year: str = a["node"]["start_season"]["year"] or "Unknown Year"
                title: str = a["node"]["title"]
                if len(title) >= 256:
                    title = title[:253] + "..."
                mdTitle: str = sanitize_markdown(title)
                alt = a["node"]["alternative_titles"]
                native: str = (
                    sanitize_markdown(alt["ja"]) + "\n" if alt and alt["ja"] else ""
                )
                f.append(
                    ipy.EmbedField(
                        name=mdTitle,
                        value=f"{native}`{a['node']['id']}`, {media_type}, {season} {year}",
                        inline=False,
                    )
                )
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
        except Exception as e:
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            al_notice = "Ryuusei uses AniList as the default anime search provider for best match experience, although the media info will be fetched from MyAnimeList."
            err_msg = f"I couldn't able to find any results for `{query}` on `{platform}`. Please check your query and try again."
            err_msg += f"\n-# {al_notice}" if provider == "anilist" else ""
            foo_msg = STR_RECOMMEND_NATIVE_TITLE
            embed = ipy.Embed(
                title="Error",
                description=err_msg,
                color=0xFF0000,
                footer=ipy.EmbedFooter(foo_msg.replace("\n", "")),
            )
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
            )
            # if err type is ProviderHttpError and from AniList, embed the error message
            if provider == "anilist":
                if isinstance(e, ProviderHttpError):
                    embed.add_field(
                        name="Error Message",
                        value=e.message,
                        inline=False,
                    )
                embed.add_field(
                    name="Futher Information",
                    value=f"If you think the title is exist on MyAnimeList, use this command instead:```elixir\n/anime search provider:MyAnimeList query:{query}\n```",
                    inline=False,
                )
            await send.edit(
                embed=embed,
                components=ipy.Button(
                    style=ipy.ButtonStyle.DANGER,
                    label="Delete",
                    custom_id="message_delete",
                    emoji="🗑️",
                ),
            )
            save_traceback_to_file("anime_search", ctx.author, e)

    @ipy.component_callback("mal_search")
    async def anime_search_data(self, ctx: ipy.ComponentContext) -> None:
        # Show loading message by editing the origin
        emoji_id = EMOJI_ATTENTIVE.split(":")[2].split(">")[0]
        loading_embed = ipy.Embed(
            title="Loading...",
            description="Please wait while we fetch the anime information.\n-# If this takes more than 30 seconds, please report to the developer.",
            color=0xFFAA00,
        )
        loading_embed.set_thumbnail(
            url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
        )
        msg = await ctx.edit_origin(embed=loading_embed, components=[])

        ani_id: int = int(ctx.values[0])
        await mal_submit(msg, ani_id, replace=True)

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
                    ipy.SlashCommandChoice(name="TV", value="TV"),
                    ipy.SlashCommandChoice(name="Movie", value="Movie"),
                    ipy.SlashCommandChoice(name="OVA", value="OVA"),
                    ipy.SlashCommandChoice(name="ONA", value="ONA"),
                    ipy.SlashCommandChoice(name="Special", value="Special"),
                    ipy.SlashCommandChoice(name="TV Short", value="TV Short"),
                ],
            ),
            ipy.SlashCommandOption(
                name="country",
                description="The country of origin",
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(name="Any (default)", value="any"),
                    ipy.SlashCommandChoice(name="Japan", value="Japan"),
                    ipy.SlashCommandChoice(name="South Korea", value="South Korea"),
                    ipy.SlashCommandChoice(name="China", value="China"),
                    ipy.SlashCommandChoice(name="Taiwan", value="Taiwan"),
                ],
                required=False,
            ),
            ipy.SlashCommandOption(
                name="min_score",
                description="The minimum score",
                type=ipy.OptionType.NUMBER,
                required=False,
                min_value=0,
                max_value=100,
            ),
            ipy.SlashCommandOption(
                name="release_from",
                description="The release year from",
                type=ipy.OptionType.NUMBER,
                required=False,
                min_value=1930,
            ),
            ipy.SlashCommandOption(
                name="release_to",
                description="The release year to",
                type=ipy.OptionType.NUMBER,
                required=False,
                min_value=1930,
            ),
        ],
    )
    async def anime_random(
        self,
        ctx: ipy.SlashContext,
        media_type: Literal[
            "any", "TV", "Movie", "OVA", "ONA", "Special", "TV Short"
        ] = "any",
        country: Literal["any", "Japan", "South Korea", "China", "Taiwan"] = "any",
        min_score: int = 0,
        release_from: int = 1930,
        release_to: int | None = None,
    ):
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
                countries = (
                    [i for i in ai.CountryOfOrigin]
                    if country == "any"
                    else [ai.CountryOfOrigin(country)]
                )
                if media_type != "any":
                    target_media_type = [ai.AnimeMediaType(media_type.lower())]
                else:
                    target_media_type = "[]"
                media_data = await ai.get_anime(
                    filter_country=countries,
                    filter_format=target_media_type,
                    filter_score=min_score,
                    filter_release_from=release_from,
                    filter_release_to=release_to,
                )
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
        if sauce == "AnimeAPI" and (media_type != "any" or country != "any"):
            errs = []
            if media_type != "any":
                errs.append(f"* Media Type: `{media_type}`")
            if country != "any":
                errs.append(f"* Country: `{country}`")
            if min_score != 0:
                errs.append(f"* Minimum Score: `{min_score}`")
            if release_from != 1930:
                errs.append(f"* Release From: `{release_from}`")
            if release_to is not None:
                errs.append(f"* Release To: `{release_to}`")
            errs_str = "\n".join(errs)
            found.add_field(
                name="Note",
                value=f"AnimeAPI doesn't support filtering.\nIgnores the following filters:\n{errs_str}",
                inline=False,
            )
        await send.edit(embed=found)
        await mal_submit(ctx, anime)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    Anime(bot)
