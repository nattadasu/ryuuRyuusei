import asyncio
from typing import Literal

import interactions as ipy

from classes.excepts import ProviderHttpError
from classes.simkl import Simkl, SimklMediaTypes
from modules.simkl import simkl_submit
from modules.commons import generate_search_embed, sanitize_markdown
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.i18n import fetch_language_data, read_user_language


class Movies(ipy.Extension):
    """Movies commands"""

    @ipy.slash_command(
        name="movies",
        description="Get movie information from SIMKL",
    )
    async def movies(self, ctx: ipy.SlashContext):
        pass

    @movies.subcommand(
        sub_cmd_name="search",
        sub_cmd_description="Search for movies",
        options=[
            ipy.SlashCommandOption(
                name="query",
                description="The movie title to search for",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def movie_search(self, ctx: ipy.SlashContext, query: str):
        await ctx.defer()
        ul: str = read_user_language(ctx)
        l_ = fetch_language_data(ul, use_raw=True)
        send = await ctx.send(
            embed=ipy.Embed(
                title=l_["commons"]["search"]["init_title"],
                description=l_["commons"]["search"]["init"].format(
                    QUERY=query,
                    PLATFORM="SIMKL",
                ),
            )
        )
        try:
            f: list[ipy.EmbedField] = []
            so: list[ipy.StringSelectOption] = []
            async with Simkl() as simkl:
                results = await simkl.search_by_title(
                    title=query, limit=5, media_type=SimklMediaTypes.MOVIE
                )
            if not results:
                raise ValueError("No results found")
            for res in results:
                rhel = res["year"]
                first_aired = f"First aired on: {rhel}"
                media_id = res["ids"]["simkl_id"]
                title = res["title"]
                if len(title) >= 256:
                    title = title[:253] + "..."
                md_title = sanitize_markdown(title)
                f.append(
                    ipy.EmbedField(
                        name=f"{md_title}",
                        value=f"`{media_id}`\n{first_aired}",
                        inline=False,
                    )
                )
                so.append(
                    ipy.StringSelectOption(
                        label=f"{md_title}",
                        value=f"{media_id}",
                        description=f"{first_aired}",
                    )
                )
            title = l_["commons"]["search"]["result_title"].format(
                QUERY=query,
            )
            result_embed = generate_search_embed(
                language=ul,
                mediaType="movies",
                query=query,
                platform="SIMKL",
                homepage="https://simkl.com",
                title=title,
                results=f,
                icon="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png",
                color=0x0B0F10,
            )
            components: list[ipy.ActionRow] = [
                ipy.ActionRow(
                    ipy.StringSelectMenu(
                        *so,
                        placeholder="Choose a movie",
                        custom_id="simkl_search_select_movie",
                    ),
                ),
            ]
            await send.edit(
                embed=result_embed,
                components=components,
            )
            await asyncio.sleep(60)
            await send.edit(components=[])
        except Exception as _:
            l_: dict[str, str] = l_["strings"]["movies"]["search"]["exception"]
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            embed = ipy.Embed(
                title=l_["title"],
                description=l_["text"].format(QUERY=f"`{query}`"),
                color=0xFF0000,
                footer=ipy.EmbedFooter(text=l_["footer"]),
            )
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
            )
            await send.edit(embed=embed)

    @ipy.component_callback("simkl_search_select_movie")
    async def simkl_search_select_movie(self, ctx: ipy.ComponentContext):
        await ctx.defer()
        entry_id: int = int(ctx.values[0])
        await simkl_submit(ctx, entry_id, "movies")
        await asyncio.sleep(65)
        await ctx.delete(ctx.message_id)

    @movies.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Get information about a movie",
        options=[
            ipy.SlashCommandOption(
                name="media_id",
                description="The movie ID on SIMKL or IMDB to get the data from",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def movie_info(self, ctx: ipy.SlashContext, media_id: str):
        await ctx.defer()
        await simkl_submit(ctx, media_id, "movies")

    @movies.subcommand(sub_cmd_name="random", sub_cmd_description="Get a random movie")
    async def movie_random(self, ctx: ipy.SlashContext):
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Random Movies",
                description="Getting a random Movies...",
                color=0x0B0F10,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        try:
            async with Simkl() as simkl:
                rand = await simkl.get_random_title(media_type=SimklMediaTypes.MOVIE)
                rand_id = rand["simkl_id"]
        except ProviderHttpError:
            await send.edit(
                embed=ipy.Embed(
                    title="Random Manga",
                    description="We couldn't find any manga. Please try again.",
                    color=0xFF0000,
                )
            )
            return

        await send.edit(
            embed=ipy.Embed(
                title="Random movie",
                description=f"We've found SIMKL ID [`{rand_id}`]({rand['simkl_url']}). Fetching info...",
                color=0x0B0F10,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        await simkl_submit(ctx=ctx, media_id=rand_id, media_type="movies")


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    Movies(bot)
