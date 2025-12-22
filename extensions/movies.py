"""
Movies commands

Available commands:
- /movies search <query> - Search for movies
- /movies info <media_id> - Get information about a movie
- /movies random - Get a random movie
"""

import interactions as ipy

from classes.excepts import ProviderHttpError
from classes.simkl import Simkl, SimklMediaTypes
from modules.commons import (
    generate_search_embed,
    sanitize_markdown,
    save_traceback_to_file,
)
from modules.const import EMOJI_UNEXPECTED_ERROR, STR_RECOMMEND_NATIVE_TITLE
from modules.simkl import simkl_submit


class MoviesCog(ipy.Extension):
    """Movies commands"""

    movies = ipy.SlashCommand(
        name="movies",
        description="Get movie information from SIMKL",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
        ),
    )
    """Movie command initialiser"""

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
        """
        Search for movies

        Parameters
        ----------
        query : str
            The movie title to search for
        """
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Searching",
                description=f"Searching for `{query}` on SIMKL...",
            )
        )
        try:
            fields: list[ipy.EmbedField] = []
            select_options: list[ipy.StringSelectOption] = []
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
                fields.append(
                    ipy.EmbedField(
                        name=f"{md_title}",
                        value=f"`{media_id}`\n{first_aired}",
                        inline=False,
                    )
                )
                select_options.append(
                    ipy.StringSelectOption(
                        label=f"{md_title}",
                        value=f"{media_id}",
                        description=f"{first_aired}",
                    )
                )
            title = f"Search Results for {query}"
            result_embed = generate_search_embed(
                media_type="movies",
                query=query,
                platform="SIMKL",
                homepage="https://simkl.com",
                title=title,
                results=fields,
                icon="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png",
                color=0x0B0F10,
            )
            components = ipy.spread_to_rows(
                ipy.StringSelectMenu(
                    *select_options,
                    placeholder="Choose a movie",
                    custom_id="simkl_search_select_movie",
                ),
                ipy.Button(
                    style=ipy.ButtonStyle.DANGER,
                    label="Cancel",
                    custom_id="message_delete",
                    emoji="🗑️",
                ),
            )
            await send.edit(
                embed=result_embed,
                components=components,
            )
        # pylint: disable=broad-except
        except Exception as _:
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            embed = ipy.Embed(
                title="Error",
                description=f"I couldn't find any movies for `{query}` on SIMKL. Please check your query and try again.",
                color=0xFF0000,
                footer=ipy.EmbedFooter(text=STR_RECOMMEND_NATIVE_TITLE),
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
                    emoji="🗑️",
                ),
            )
            save_traceback_to_file("movies_search", ctx.author, _)
        # pylint: enable=broad-except

    @ipy.component_callback("simkl_search_select_movie")
    async def simkl_search_select_movie(self, ctx: ipy.ComponentContext):
        """Callback for the SIMKL search select menu"""
        await ctx.defer(edit_origin=True)
        entry_id: int = int(ctx.values[0])
        await simkl_submit(ctx, entry_id, "movies", replace=True)

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
        """
        Get information about a movie

        Parameters
        ----------
        media_id : str
            The movie ID on SIMKL or IMDB to get the data from
        """
        await ctx.defer()
        await simkl_submit(ctx, media_id, "movies")

    @movies.subcommand(sub_cmd_name="random", sub_cmd_description="Get a random movie")
    async def movie_random(self, ctx: ipy.SlashContext):
        """
        Get a random movie

        Parameters
        ----------
        None
        """
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
        except ProviderHttpError as _:
            await send.edit(
                embed=ipy.Embed(
                    title="Random Movie",
                    description="We couldn't find any movies. Please try again.",
                    color=0xFF0000,
                )
            )
            save_traceback_to_file("movies_random", ctx.author, _)

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
    """Load the Movies cog."""
    MoviesCog(bot)
