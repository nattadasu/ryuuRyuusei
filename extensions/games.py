import interactions as ipy

from classes.rawg import RawgApi
from modules.commons import (
    generate_search_embed,
    sanitize_markdown,
    save_traceback_to_file,
)
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.rawg import rawg_submit


class Games(ipy.Extension):
    """Games commands"""

    games_head = ipy.SlashCommand(
        name="games",
        description="Get games information from RAWG",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
        ),
    )

    @games_head.subcommand(
        sub_cmd_name="search",
        sub_cmd_description="Search for games",
        options=[
            ipy.SlashCommandOption(
                name="query",
                description="The game title to search for",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def games_search(self, ctx: ipy.SlashContext, query: str):
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Searching",
                description=f"Searching `{query}` on RAWG...",
            )
        )
        try:
            f: list[ipy.EmbedField] = []
            so: list[ipy.StringSelectOption] = []
            async with RawgApi() as rawg:
                results = await rawg.search(query=query)
            for r in results:
                rhel = r["released"]
                title = r["name"]
                title = sanitize_markdown(title)
                if len(title) >= 256:
                    title = title[:253] + "..."
                f += [
                    ipy.EmbedField(
                        name=title, value=f"*Released on: {rhel}*", inline=False
                    )
                ]
                so += [
                    ipy.StringSelectOption(
                        label=title[:77] + "..." if len(title) >= 80 else title,
                        value=r["slug"],
                        description=f"Released: {rhel}",
                    )
                ]
            result_embed = generate_search_embed(
                media_type="manga",
                query=query,
                platform="RAWG",
                homepage="https://rawg.io",
                title=query,
                results=f,
                icon="https://pbs.twimg.com/profile_images/951372339199045632/-JTt60iX_400x400.jpg",
                color=0x1F1F1F,
            )
            components: list[ipy.ActionRow] = ipy.spread_to_rows(
                ipy.StringSelectMenu(
                    *so,
                    placeholder="Choose a game",
                    custom_id="rawg_games_search",
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
        except Exception as _:
            emoji = EMOJI_UNEXPECTED_ERROR.split(":")[2].split(">")[0]
            embed = ipy.Embed(
                title="Error",
                description=f"I couldn't able to find any results for {query} on RAWG. Please check your query and try again.",
                color=0xFF0000,
                footer=ipy.EmbedFooter(
                    text="Pro tip: Use native title to get the most accurate result... But I can't guarantee if RAWG has original title, it depends."
                ),
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
            save_traceback_to_file("games_search", ctx.author, _)

    @ipy.component_callback("rawg_games_search")
    async def rawg_games_search(self, ctx: ipy.ComponentContext) -> None:
        await ctx.defer()
        entry_id = ctx.values[0]
        await rawg_submit(ctx, entry_id)
        await ctx.message.delete() if ctx.message else None

    @games_head.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Get information about a game",
        options=[
            ipy.SlashCommandOption(
                name="slug",
                description="The game slug on RAWG",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def games_info(self, ctx: ipy.SlashContext, slug: str):
        await ctx.defer()
        await rawg_submit(ctx, slug=slug)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    Games(bot)
