"""Add Urban Dictionary commands to the bot."""

import interactions as ipy
import aiohttp
from interactions.ext.paginators import Paginator

from classes.urbandictionary import UrbanDictionary as Urban, UrbanDictionaryEntry as Entry
from modules.commons import platform_exception_embed, save_traceback_to_file, get_nsfw_status


class UrbanDictionaryCog(ipy.Extension):
    """Urban Dictionary Cog"""

    urban_head = ipy.SlashCommand(
        name="urban",
        description="Search Urban Dictionary for a word or phrase.",
        nsfw=True,
    )

    @urban_head.subcommand(
        sub_cmd_name="random",
        sub_cmd_description="Get a random word or phrase from Urban Dictionary.",
        options=[
            ipy.SlashCommandOption(
                name="limit",
                description="Maximum number of results to return.",
                type=ipy.OptionType.INTEGER,
                required=False,
                min_value=1,
                max_value=10,
            ),
        ],
        nsfw=True,
    )
    async def urban_random(self, ctx: ipy.SlashContext, limit: int = 10):
        """Get a random word or phrase from Urban Dictionary."""
        nsfw_status = await get_nsfw_status(ctx) or False
        await ctx.defer(ephemeral=not nsfw_status)
        entry: list[Entry] | None = None
        try:
            async with Urban() as ud:
                entry = await ud.get_random_word()
        except Exception as e:
            await ctx.send(embed=platform_exception_embed(
                description="Failed to get random word from Urban Dictionary.",
                error=f"{e}",
            ))
            save_traceback_to_file("urban_random", ctx.author, e)
            return
        pages: list[ipy.Embed] = []
        for _, e in enumerate(entry[:limit]):
            pages.append(e.embed)
        paginator = Paginator.create_from_embeds(self.bot, *pages, timeout=30)
        await paginator.send(ctx)  # type: ignore

    @urban_head.subcommand(
        sub_cmd_name="search",
        sub_cmd_description="Search Urban Dictionary for a word or phrase.",
        options=[
            ipy.SlashCommandOption(
                name="term",
                description="Word or phrase to search for.",
                type=ipy.OptionType.STRING,
                required=True,
                autocomplete=True,
            ),
            ipy.SlashCommandOption(
                name="limit",
                description="Maximum number of results to return.",
                type=ipy.OptionType.INTEGER,
                required=False,
                min_value=1,
                max_value=10,
            ),
        ],
        nsfw=True,
    )
    async def urban_search(self, ctx: ipy.SlashContext, term: str, limit: int = 10):
        """Search Urban Dictionary for a word or phrase."""
        nsfw_status = await get_nsfw_status(ctx) or False
        await ctx.defer(ephemeral=not nsfw_status)
        entry: list[Entry] | None = None
        try:
            async with Urban() as ud:
                entry = await ud.lookup_definition(term)
        except Exception as e:
            await ctx.send(embed=platform_exception_embed(
                description=f"Failed to search Urban Dictionary for `{term}`.",
                error=f"{e}",
            ))
            save_traceback_to_file("urban_random", ctx.author, e)
            return

        pages: list[ipy.Embed] = []
        for _, e in enumerate(entry[:limit]):
            pages.append(e.embed)
        paginator = Paginator.create_from_embeds(self.bot, *pages, timeout=30)
        await paginator.send(ctx)  # type: ignore

    @urban_search.autocomplete(option_name="term")
    async def urban_search_autocomplete(self, ctx: ipy.AutocompleteContext):
        """Autocomplete Urban Dictionary search term."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.urbandictionary.com/v0/autocomplete-extra?term={ctx.input_text}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results: list[dict[str, str]] = []
                    for d in data["results"][:25]:
                        results.append({
                            "name": d["term"][:80],
                            "value": d["term"],
                        })
                    await ctx.send(choices=results)  # type: ignore
                else:
                    await ctx.send(choices=[{
                        "name": f"{ctx.input_text}",
                        "value": f"{ctx.input_text}",
                    }])

    @urban_head.subcommand(
        sub_cmd_name="wotd",
        sub_cmd_description="Get the Urban Dictionary Word of the Day.",
        nsfw=True,
    )
    async def urban_wotd(self, ctx: ipy.SlashContext):
        """Get the Urban Dictionary Word of the Day."""
        nsfw_status = await get_nsfw_status(ctx) or False
        await ctx.defer(ephemeral=not nsfw_status)
        entry: Entry | None = None
        try:
            async with Urban() as ud:
                entry = await ud.get_word_of_the_day()
        except Exception as e:
            await ctx.send(embed=platform_exception_embed(
                description="Failed to get Urban Dictionary Word of the Day.",
                error=f"{e}",
            ))
            save_traceback_to_file("urban_random", ctx.author, e)
            return
        await ctx.send(embed=entry.embed) # type: ignore


def setup(bot: ipy.Client):
    """Add the Urban Dictionary Cog to the bot."""
    UrbanDictionaryCog(bot)
