from typing import Literal, Any

import interactions as ipy

from classes.anibrain import AniBrainAI, AniBrainAiMedia
from classes.anilist import AniList
from modules.anilist import anilist_submit
from modules.commons import (generate_search_embed, sanitize_markdown,
                             save_traceback_to_file)
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.i18n import fetch_language_data, read_user_language


class Manga(ipy.Extension):
    """Manga commands"""

    manga_head = ipy.SlashCommand(
        name="manga",
        description="Get manga information from AniList",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
        ),
    )

    @manga_head.subcommand(
        sub_cmd_name="search",
        sub_cmd_description="Search for manga",
        options=[
            ipy.SlashCommandOption(
                name="query",
                description="The manga title to search for",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def manga_search(self, ctx: ipy.SlashContext, query: str):
        await ctx.defer()
        user_lang: str = read_user_language(ctx)
        lang_dict = fetch_language_data(user_lang, use_raw=True)
        send = await ctx.send(
            embed=ipy.Embed(
                title=lang_dict["commons"]["search"]["init_title"],
                description=lang_dict["commons"]["search"]["init"].format(
                    QUERY=query,
                    PLATFORM="AniList",
                ),
            )
        )
        try:
            f: list[ipy.EmbedField] = []
            so: list[ipy.StringSelectOption] = []
            async with AniList() as anilist:
                results = await anilist.search_media(
                    query, limit=5, media_type=anilist.MediaType.MANGA
                )
            if not results:
                raise ValueError("No results found")
            for res in results:
                media_id = res["id"]
                format_raw: str | None = res["format"]
                format_str = (
                    format_raw.capitalize().replace("_", "-")
                    if format_raw
                    else "Unknown format"
                )
                status_raw: str | None = res["status"]
                match status_raw:
                    case None:
                        status = "Unknown status"
                    case "NOT_YET_RELEASED":
                        status = "Not yet released"
                    case _:
                        status = status_raw.capitalize()
                year = res["startDate"]["year"]
                if year is None:
                    year = "Unknown year"
                else:
                    year = str(year)
                title = res["title"]["romaji"]
                if len(title) >= 256:
                    title = title[:253] + "..."
                md_title = sanitize_markdown(title)
                native_title = res["title"]["native"]
                if native_title is not None:
                    md_native_title = sanitize_markdown(native_title)
                    md_native_title += "\n"
                else:
                    md_native_title = ""
                is_adult = "Possibly NSFW 🚫, " if res["isAdult"] else ""
                f.append(
                    ipy.EmbedField(
                        name=md_title,
                        value=f"{md_native_title}{is_adult}{format_str}, {status}, {year}",
                        inline=False,
                    ))
                so.append(
                    ipy.StringSelectOption(
                        label=title[:77] +
                        "..." if len(title) > 77 else title,
                        value=str(media_id),
                        description=f"{format_str}, {status}, {year}",
                    )
                )
            title = lang_dict["commons"]["search"]["result_title"].format(
                QUERY=query,
            )
            result_embed = generate_search_embed(
                language=user_lang,
                mediaType="manga",
                query=query,
                platform="AniList",
                homepage="https://anilist.co",
                title=title,
                results=f,
                icon="https://anilist.co/img/icons/android-chrome-192x192.png",
                color=0x02A9FF,
            )
            components: list[ipy.ActionRow] = ipy.spread_to_rows(
                ipy.StringSelectMenu(
                    *so,
                    placeholder="Choose a manga",
                    custom_id="anilist_manga_search",
                ),
                ipy.Button(
                    style=ipy.ButtonStyle.DANGER,
                    label="Cancel",
                    custom_id="message_delete",
                    emoji="🗑️"
                ),
            )
            await send.edit(
                embed=result_embed,
                components=components,
            )
        # pylint: disable-next=broad-except
        except Exception as _:
            lang_dict: dict[str, Any] = lang_dict["strings"]["manga"]["search"]["exception"]
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            embed_description: str = lang_dict["text"]
            embed_description = embed_description.format(QUERY=f"`{query}`")
            embed = ipy.Embed(
                title=lang_dict["title"],
                description=embed_description,
                color=0xFF0000,
                footer=ipy.EmbedFooter(text=lang_dict["footer"]),
            )
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
            save_traceback_to_file("manga_search", ctx.author, _)

    @ipy.component_callback("anilist_manga_search")
    async def anilist_manga_search(self, ctx: ipy.ComponentContext):
        """Callback for manga search"""
        await ctx.defer()
        entry_id: int = int(ctx.values[0])
        await anilist_submit(ctx, entry_id)
        # grab "message_delete" button
        keep_components: list[ipy.ActionRow] = []
        if ctx.message is None or ctx.message.components is None:
            return
        for action_row in ctx.message.components:
            for comp in action_row.components:  # type: ignore
                if comp.custom_id == "message_delete":  # type: ignore
                    comp.label = "Delete message"  # type: ignore
                    keep_components.append(action_row)
        await ctx.message.edit(components=keep_components)

    @manga_head.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Get manga information",
        options=[
            ipy.SlashCommandOption(
                name="anilist_id",
                description="The manga ID on AniList to get information from",
                type=ipy.OptionType.INTEGER,
                required=True,
            ),
        ],
    )
    async def manga_info(self, ctx: ipy.SlashContext, anilist_id: int):
        await ctx.defer()
        await anilist_submit(ctx, anilist_id)

    @manga_head.subcommand(
        sub_cmd_name="random",
        sub_cmd_description="Get a random manga, powered by AniBrain",
        options=[
            ipy.SlashCommandOption(
                name="media_type",
                description="The media type to get",
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Manga, Manhwa, Manhua (default)",
                        value="manga",
                    ),
                    ipy.SlashCommandChoice(
                        name="One-shot",
                        value="one_shot",
                    ),
                    ipy.SlashCommandChoice(
                        name="Light Novel",
                        value="light_novel",
                    ),
                ],
                required=False,
            ),
        ],
    )
    async def random_manga(
        self,
        ctx: ipy.SlashContext,
        media_type: Literal["manga", "one_shot", "light_novel"] = "manga",
    ):
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Random Manga",
                description="Getting a random manga...",
                color=0x02A9FF,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        media_data = list[AniBrainAiMedia]
        try:
            async with AniBrainAI() as anibrain:
                countries = [
                    anibrain.CountryOfOrigin.JAPAN,
                    anibrain.CountryOfOrigin.KOREA,
                    anibrain.CountryOfOrigin.CHINA,
                ]
                match media_type:
                    case "manga":
                        media_data = await anibrain.get_manga(
                            filter_country=countries,
                        )
                    case "one_shot":
                        media_data = await anibrain.get_one_shot(
                            filter_country=countries,
                        )
                    case "light_novel":
                        media_data = await anibrain.get_light_novel(
                            filter_country=countries,
                        )
            media_id = media_data[0].anilistId
            await send.edit(
                embed=ipy.Embed(
                    title="Random manga",
                    description=f"We've found AniList ID [`{media_id}`](https://anilist.co/manga/{media_id}). Fetching info...",
                    color=0x02A9FF,
                    footer=ipy.EmbedFooter(
                        text="This may take a while...",
                    ),
                )
            )
            await anilist_submit(ctx, media_id)
        # pylint: disable-next=broad-except
        except Exception as _:
            await send.edit(
                embed=ipy.Embed(
                    title="Random Manga",
                    description="We couldn't find any manga. Please try again.",
                    color=0xFF0000,
                )
            )
            save_traceback_to_file("random_manga", ctx.author, _)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    Manga(bot)
