"""Add Urban Dictionary commands to the bot."""

import re
from typing import TypedDict

import aiohttp
import interactions as ipy
from interactions.ext.paginators import Paginator

from classes.urbandictionary import UrbanDictionary as Urban
from classes.urbandictionary import UrbanDictionaryEntry as Entry
from modules.commons import (
    get_nsfw_status,
    platform_exception_embed,
    save_traceback_to_file,
)


class TrustModel(TypedDict):
    """Trust Model for Urban Dictionary entries."""

    entry: Entry
    """Entry"""
    maxratio: float
    """Max ratio of thumbs up to max thumbs up"""
    trustratio: float
    """Trust ratio"""


class UrbanDictionaryCog(ipy.Extension):
    """Urban Dictionary Cog"""

    urban_head = ipy.SlashCommand(
        name="urban",
        description="Search Urban Dictionary for a word or phrase.",
        nsfw=True,
    )

    async def _paginator(
        self, ctx: ipy.SlashContext, pages: list[ipy.Embed]
    ) -> ipy.Message:
        """
        Send multiple embeds with pagination.

        Args:
            ctx (ipy.SlashContext): Slash context
            pages (list[ipy.Embed]): List of embeds to paginate

        Returns:
            ipy.Message: Message object
        """
        paginator = Paginator.create_from_embeds(self.bot, *pages, timeout=30)
        stat = await paginator.send(ctx)
        return stat

    @staticmethod
    def _sort_by_thumbs_up(entries: list[Entry]) -> list[Entry]:
        """
        Sort list of Urban Dictionary entries by thumbs up.

        Args:
            entries (list[Entry]): List of Urban Dictionary entries

        Returns:
            list[Entry]: Sorted list of Urban Dictionary entries
        """
        # get the most thumbs up
        thumbs_up = sorted(entries, key=lambda e: e.thumbs_up, reverse=True)
        max_thumbs_up = thumbs_up[0].thumbs_up
        trusted_list: list[TrustModel] = []

        # Separate trusted and untrusted entries
        for e in thumbs_up:
            try:
                trustratio = e.thumbs_up / (e.thumbs_up + e.thumbs_down)
            except ZeroDivisionError:
                trustratio = 0.0
            if trustratio >= 0.7:
                trusted_list.append(
                    {
                        "entry": e,
                        "maxratio": e.thumbs_up / max_thumbs_up,
                        "trustratio": trustratio,
                    }
                )

        # Sort trusted entries by thumbs up
        trusted_entries = sorted(
            trusted_list, key=lambda t: t["entry"].thumbs_up, reverse=True
        )
        trusted_entries = [t["entry"] for t in trusted_entries]

        # Sort untrusted entries by thumbs up
        untrusted_entries = [e for e in thumbs_up if e not in trusted_entries]

        # If entry is < 70% trusted, put it at the bottom of the list
        untrusted_entries = sorted(
            untrusted_entries, key=lambda e: e.thumbs_up, reverse=True
        )

        # Merge trusted and untrusted entries
        sorted_entries = trusted_entries + untrusted_entries

        return sorted_entries

    @staticmethod
    def _fix_footer(embed: ipy.Embed, cursor: int = 1, total: int = 10) -> ipy.Embed:
        """
        Fix the footer of an Urban Dictionary embed.

        Args:
            embed (ipy.Embed): Embed to fix
            cursor (int, optional): Current page. Defaults to 1.
            total (int, optional): Total number of pages. Defaults to 10.

        Returns:
            ipy.Embed: Fixed embed
        """
        foo = embed.footer
        if not foo:
            return embed
        current = foo.text
        # replace current footer with fixed one with following format:
        # page 1/10 -> page 1 of 10
        replace = re.sub(r"(\d+)/(\d+)", f"{cursor} of {total}", current)
        embed.set_footer(text=replace)
        return embed

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
            await ctx.send(
                embed=platform_exception_embed(
                    description="Failed to get random word from Urban Dictionary.",
                    error=f"{e}",
                )
            )
            save_traceback_to_file("urban_random", ctx.author, e)
            return
        pages: list[ipy.Embed] = []
        entry_lim = self._sort_by_thumbs_up(entry[:limit])
        for pg, e in enumerate(entry_lim):
            embed = self._fix_footer(e.embed, cursor=pg + 1, total=len(entry_lim))
            pages.append(embed)
        await self._paginator(ctx, pages)

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
            await ctx.send(
                embed=platform_exception_embed(
                    description=f"Failed to search Urban Dictionary for `{term}`.",
                    error=f"{e}",
                )
            )
            save_traceback_to_file("urban_random", ctx.author, e)
            return

        pages: list[ipy.Embed] = []
        entry_lim = self._sort_by_thumbs_up(entry[:limit])
        for pg, e in enumerate(entry_lim):
            embed = self._fix_footer(e.embed, cursor=pg + 1, total=len(entry_lim))
            pages.append(embed)
        paginator = Paginator.create_from_embeds(self.bot, *pages, timeout=30)
        await paginator.send(ctx)  # type: ignore

    @urban_search.autocomplete(option_name="term")
    async def urban_search_autocomplete(self, ctx: ipy.AutocompleteContext):
        """Autocomplete Urban Dictionary search term."""
        invalid = {
            "name": f"{ctx.input_text}",
            "value": f"{ctx.input_text}",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.urbandictionary.com/v0/autocomplete-extra?term={ctx.input_text}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results: list[dict[str, str]] = []
                        for d in data["results"][:25]:
                            results.append(
                                {
                                    "name": d["term"][:80],
                                    "value": d["term"],
                                }
                            )
                        await ctx.send(choices=results)  # type: ignore
                    else:
                        await ctx.send(choices=[invalid])  # type: ignore
        except Exception:  # pylint: disable=broad-except
            await ctx.send(choices=[invalid])  # type: ignore

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
            await ctx.send(
                embed=platform_exception_embed(
                    description="Failed to get Urban Dictionary Word of the Day.",
                    error=f"{e}",
                )
            )
            save_traceback_to_file("urban_random", ctx.author, e)
            return
        await ctx.send(embed=entry.embed)  # type: ignore


def setup(bot: ipy.Client):
    """Add the Urban Dictionary Cog to the bot."""
    UrbanDictionaryCog(bot)
