import interactions as ipy

from classes.excepts import ProviderHttpError
from classes.simkl import Simkl, SimklMediaTypes
from modules.commons import (generate_search_embed, sanitize_markdown,
                             save_traceback_to_file)
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.i18n import fetch_language_data, read_user_language
from modules.simkl import simkl_submit


class TvShow(ipy.Extension):
    """TV commands"""

    tv = ipy.SlashCommand(
        name="tv",
        description="Get TV show information from SIMKL",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
        ),
    )

    @tv.subcommand(
        sub_cmd_name="search",
        sub_cmd_description="Search for TV shows",
        options=[
            ipy.SlashCommandOption(
                name="query",
                description="The TV show title to search for",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def tv_search(self, ctx: ipy.SlashContext, query: str):
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
                    title=query, limit=5, media_type=SimklMediaTypes.TV
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
                mediaType="shows",
                query=query,
                platform="SIMKL",
                homepage="https://simkl.com",
                title=title,
                results=f,
                icon="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png",
                color=0x0B0F10,
            )
            components: list[ipy.ActionRow] = ipy.spread_to_rows(
                ipy.StringSelectMenu(
                    *so,
                    placeholder="Choose a show",
                    custom_id="simkl_search_select_tv",
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
        except Exception as _:
            l_: dict[str, str] = l_["strings"]["tv"]["search"]["exception"]
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
            await send.edit(
                embed=embed,
                components=ipy.Button(
                    style=ipy.ButtonStyle.DANGER,
                    label="Delete",
                    custom_id="message_delete",
                    emoji="🗑️"
                ),
            )
            save_traceback_to_file("tv_search", ctx.author, _)

    @ipy.component_callback("simkl_search_select_tv")
    async def simkl_search_select_tv(self, ctx: ipy.ComponentContext):
        await ctx.defer()
        entry_id: int = int(ctx.values[0])
        await simkl_submit(ctx, entry_id, "tv")
        # grab "message_delete" button
        keep_components: list[ipy.ActionRow] = []
        for action_row in ctx.message.components:
            for comp in action_row.components:
                if comp.custom_id == "message_delete":
                    comp.label = "Delete message"
                    keep_components.append(action_row)
        await ctx.message.edit(components=keep_components)

    @tv.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Get information about a TV show",
        options=[
            ipy.SlashCommandOption(
                name="media_id",
                description="The show ID on SIMKL or IMDB to get the data from",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def tv_info(self, ctx: ipy.SlashContext, media_id: str):
        await ctx.defer()
        await simkl_submit(ctx, media_id)

    @tv.subcommand(sub_cmd_name="random",
                   sub_cmd_description="Get a random TV show")
    async def tv_random(self, ctx: ipy.SlashContext):
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Random TV Show",
                description="Getting a random TV Show...",
                color=0x0B0F10,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        try:
            async with Simkl() as simkl:
                rand = await simkl.get_random_title(media_type=SimklMediaTypes.TV)
                rand_id = rand["simkl_id"]
        except ProviderHttpError as _:
            await send.edit(
                embed=ipy.Embed(
                    title="Random TV Show",
                    description="We couldn't find any show. Please try again.",
                    color=0xFF0000,
                )
            )

            save_traceback_to_file("tv_random", ctx.author, _)

        await send.edit(
            embed=ipy.Embed(
                title="Random TV show",
                description=f"We've found SIMKL ID [`{rand_id}`]({rand['simkl_url']}). Fetching info...",
                color=0x0B0F10,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        await simkl_submit(ctx=ctx, media_id=rand_id, media_type="tv")


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    TvShow(bot)
