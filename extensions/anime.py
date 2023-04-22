import asyncio
from re import sub as rSub

import interactions as ipy
from modules.anilist import searchAniListAnime
from modules.commons import generateSearchSelections, sanitizeMarkdown
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.i18n import lang, readUserLang
from modules.myanimelist import malSubmit, searchMalAnime


class Anime(ipy.Extension):
    @ipy.slash_command(
        name="anime",
        description="Get anime information from MyAnimeList",
    )
    async def anime(self, ctx: ipy.SlashContext):
        pass

    @anime.subcommand(
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
        self, ctx: ipy.SlashContext, query: str, provider: str = "anilist"
    ):
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul, useRaw=True)
        send = await ctx.send(
            embed=ipy.Embed(
                title=l_["commons"]["search"]["init_title"],
                description=l_["commons"]["search"]["init"].format(
                    QUERY=query,
                    PLATFORM="MyAnimeList" if provider == "mal" else "AniList",
                ),
            )
        )
        f = []
        so = []
        try:
            if provider == "anilist":
                res = await searchAniListAnime(title=query)
                if res is None or len(res) == 0:
                    raise Exception("No result")
            elif provider == "mal":
                res = await searchMalAnime(title=query)
                if res is None or len(res) == 0:
                    raise Exception("No result")
            for a in res:
                a = a["node"]
                if a["start_season"] is None:
                    a["start_season"] = {"season": "Unknown", "year": "Year"}
                media_type: str = a["media_type"].lower()
                try:
                    media_type = l_["commons"]["media_formats"][media_type]
                except KeyError:
                    media_type = l_["commons"]["unknown"]
                season: str = (
                    a["start_season"]["season"]
                    if a["start_season"]["season"]
                    else "unknown"
                )
                season = l_["commons"]["season"][season]
                year = (
                    a["start_season"]["year"]
                    if a["start_season"]["year"]
                    else l_["commons"]["year"]["unknown"]
                )
                title = a["title"]
                mdTitle = sanitizeMarkdown(title)
                alt = a["alternative_titles"]
                if alt is not None and alt["ja"] is not None:
                    native = sanitizeMarkdown(alt["ja"])
                    native += "\n"
                else:
                    native = ""
                f += [
                    ipy.EmbedField(
                        name=mdTitle[:253] + ("..." if len(mdTitle) > 253 else ""),
                        value=f"{native}`{a['id']}`, {media_type}, {season} {year}",
                        inline=False,
                    )
                ]
                so += [
                    ipy.StringSelectOption(
                        # trim to 80 chars in total
                        label=title[:77] + ("..." if len(title) > 77 else ""),
                        value=a["id"],
                        description=f"{media_type}, {season} {year}",
                    )
                ]
            if len(f) >= 1:
                title = l_["commons"]["search"]["result_title"].format(QUERY=query)
                if provider == "anilist":
                    title += " (AniList)"
                result = generateSearchSelections(
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
                await send.edit(
                    content="",
                    embed=result,
                    components=ipy.ActionRow(
                        ipy.StringSelectMenu(
                            *so, placeholder="Choose an anime", custom_id="mal_search"
                        )
                    ),
                )
            await asyncio.sleep(60)
            await send.edit(components=[])
        except Exception:
            l_ = l_["strings"]["anime"]["search"]["exception"]
            emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EMOJI_UNEXPECTED_ERROR)
            await send.edit(
                content="",
                embed=ipy.Embed(
                    title=l_["title"],
                    description=l_["text"].format(
                        QUERY=query,
                    ),
                    color=0xFF0000,
                    footer=ipy.EmbedFooter(text=l_["footer"]),
                    thumbnail=ipy.EmbedAttachment(
                        url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
                    ),
                ),
            )

    @ipy.component_callback("mal_search")
    async def anime_search_data(self, ctx: ipy.ComponentContext) -> None:
        await ctx.defer()
        ani_id: int = int(ctx.values[0])
        await malSubmit(ctx, ani_id)

    @anime.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Get anime information",
        options=[
            ipy.SlashCommandOption(
                name="id",
                description="The anime ID to get information from",
                type=ipy.OptionType.INTEGER,
                required=True,
            ),
        ],
    )
    async def anime_info(self, ctx: ipy.SlashContext, id: int):
        await ctx.defer()
        await malSubmit(ctx, id)


def setup(bot):
    Anime(bot)
