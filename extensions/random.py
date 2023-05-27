from typing import Literal

import interactions as ipy

from classes.anibrain import AniBrainAI, AniBrainAiMedia
from classes.nekomimidb import NekomimiGender
from classes.randomorg import RandomOrg
from classes.i18n import LanguageDict
from modules.anilist import anilist_submit
from modules.i18n import fetch_language_data, read_user_language
from modules.myanimelist import lookupRandomAnime, mal_submit
from modules.nekomimidb import submit_nekomimi


class Random(ipy.Extension):
    """Random commands"""

    def __init__(self, bot: ipy.AutoShardedClient):
        self.bot = bot

    @ipy.slash_command(
        name="random",
        description="Get a random stuff",
    )
    async def random(self, ctx: ipy.SlashContext):
        pass

    @random.subcommand(
        sub_cmd_name="anime",
        sub_cmd_description="Get a random anime, powered by AnimeAPI",
    )
    async def random_anime(self, ctx: ipy.SlashContext):
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
        anime = lookupRandomAnime()
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

    @random.subcommand(
        sub_cmd_name="manga",
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
        ]
    )
    async def random_manga(self, ctx: ipy.SlashContext, media_type: Literal['manga', 'one_shot', 'light_novel'] = "manga"):
        await ctx.defer()
        send = await ctx.send(
            embed=ipy.Embed(
                title="Random Manga",
                description="Getting a random manga...",
                color=0x02a9ff,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        media_data = list[AniBrainAiMedia]
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
        media_id = int
        for entry in media_data:
            if entry.anilistId is not None:
                media_id = entry.anilistId
                break
        else:
            await send.edit(
                embed=ipy.Embed(
                    title="Random Manga",
                    description="We couldn't find any manga. Please try again.",
                    color=0xff0000,
                )
            )
            return
        await send.edit(
            embed=ipy.Embed(
                title="Random manga",
                description=f"We've found AniList ID [`{media_id}`](https://anilist.co/manga/{media_id}). Fetching info...",
                color=0x02a9ff,
                footer=ipy.EmbedFooter(
                    text="This may take a while...",
                ),
            )
        )
        await anilist_submit(ctx, media_id)

    @random.subcommand(
        group_name="nekomimi",
        group_description="Get a random character in cat ears",
        sub_cmd_name="boy",
        sub_cmd_description="Get an image of boy character in cat ears",
    )
    async def random_nekomimi_boy(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["random"]["nekomimi"]
        await submit_nekomimi(ctx=ctx, gender=NekomimiGender.BOY, lang=l_)

    @random.subcommand(
        group_name="nekomimi",
        group_description="Get a random character in cat ears",
        sub_cmd_name="girl",
        sub_cmd_description="Get an image of girl character in cat ears",
    )
    async def random_nekomimi_girl(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["random"]["nekomimi"]
        await submit_nekomimi(ctx=ctx, gender=NekomimiGender.GIRL, lang=l_)

    @random.subcommand(
        group_name="nekomimi",
        group_description="Get a random character in cat ears",
        sub_cmd_name="randomize",
        sub_cmd_description="Get an image of random character of any gender in cat ears",
    )
    async def random_nekomimi_randomize(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["random"]["nekomimi"]
        await submit_nekomimi(ctx=ctx, lang=l_)

    @random.subcommand(
        sub_cmd_name="number",
        sub_cmd_description="Get a random number",
        options=[
            ipy.SlashCommandOption(
                name="numbers",
                description="Number of numbers to generate",
                required=False,
                type=ipy.OptionType.INTEGER,
                max_value=10000,
            ),
            ipy.SlashCommandOption(
                name="min_value",
                description="Minimum value",
                required=False,
                type=ipy.OptionType.INTEGER,
            ),
            ipy.SlashCommandOption(
                name="max_value",
                description="Maximum value",
                required=False,
                type=ipy.OptionType.INTEGER,
            ),
            ipy.SlashCommandOption(
                name="base",
                description="Base number",
                required=False,
                type=ipy.OptionType.INTEGER,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Decimal",
                        value=10,
                    ),
                    ipy.SlashCommandChoice(
                        name="Binary",
                        value=2,
                    ),
                    ipy.SlashCommandChoice(
                        name="Octal",
                        value=8,
                    ),
                    ipy.SlashCommandChoice(
                        name="Hexadecimal",
                        value=16,
                    ),
                ],
            ),
        ],
    )
    async def random_number(
        self,
        ctx: ipy.SlashContext,
        numbers: int = 1,
        min_value: int = 1,
        max_value: int = 10,
        base: int = 10,
    ):
        async with RandomOrg() as rand:
            numbers = await rand.integers(
                num=numbers, min_val=min_value, max_val=max_value, base=base
            )
        # convert arrays of int to arrays of str
        numbers = [str(i) for i in numbers]
        await ctx.send(
            embed=ipy.Embed(
                description=f"```py\n{', '.join(numbers)}\n```",
                color=0x1F1F1F,
            )
        )

    @random.subcommand(
        sub_cmd_name="string",
        sub_cmd_description="Get a random string",
        options=[
            ipy.SlashCommandOption(
                name="length",
                description="Length of the string",
                required=True,
                type=ipy.OptionType.INTEGER,
                min_value=1,
                max_value=20,
            ),
            ipy.SlashCommandOption(
                name="amount",
                description="Amount of strings to generate",
                required=False,
                type=ipy.OptionType.INTEGER,
            ),
            ipy.SlashCommandOption(
                name="use_uppercase",
                description="Use uppercase letters",
                required=False,
                type=ipy.OptionType.BOOLEAN,
            ),
            ipy.SlashCommandOption(
                name="use_lowercase",
                description="Use lowercase letters",
                required=False,
                type=ipy.OptionType.BOOLEAN,
            ),
            ipy.SlashCommandOption(
                name="use_digits",
                description="Use digits",
                required=False,
                type=ipy.OptionType.BOOLEAN,
            ),
        ],
    )
    async def random_string(
        self,
        ctx: ipy.SlashContext,
        length: int = 10,
        amount: int = 1,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
    ):
        upper = "off" if not use_uppercase else "on"
        lower = "off" if not use_lowercase else "on"
        digits = "off" if not use_digits else "on"
        async with RandomOrg() as rand:
            strings = await rand.strings(
                length=length,
                num=amount,
                upperalpha=upper,
                loweralpha=lower,
                digits=digits,
                unique="on",
            )
        await ctx.send(
            embed=ipy.Embed(
                description=f"```py\n{', '.join(strings)}\n```",
                color=0x1F1F1F,
            )
        )


def setup(bot):
    Random(bot)
