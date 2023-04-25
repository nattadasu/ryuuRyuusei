import interactions as ipy

from classes.nekomimidb import NekomimiDb as neko
from classes.randomorg import RandomOrg
from modules.i18n import fetch_language_data, read_user_language
from modules.myanimelist import lookupRandomAnime, malSubmit
from modules.nekomimidb import submit_nekomimi

gender = neko.Gender


class Random(ipy.Extension):
    @ipy.slash_command(
        name="random",
        description="Get a random stuff",
    )
    async def random(self, ctx: ipy.SlashContext):
        pass

    @random.subcommand(
        sub_cmd_name="anime",
        sub_cmd_description="Get a random anime",
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
        await malSubmit(ctx, anime)

    @random.subcommand(
        group_name="nekomimi",
        group_description="Get a random character in cat ears",
        sub_cmd_name="boy",
        sub_cmd_description="Get an image of boy character in cat ears",
    )
    async def random_nekomimi_boy(self, ctx: ipy.SlashContext):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["random"]["nekomimi"]
        await submit_nekomimi(ctx=ctx, gender=gender.BOY, lang=l_)

    @random.subcommand(
        group_name="nekomimi",
        group_description="Get a random character in cat ears",
        sub_cmd_name="girl",
        sub_cmd_description="Get an image of girl character in cat ears",
    )
    async def random_nekomimi_girl(self, ctx: ipy.SlashContext):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["random"]["nekomimi"]
        await submit_nekomimi(ctx=ctx, gender=gender.GIRL, lang=l_)

    @random.subcommand(
        group_name="nekomimi",
        group_description="Get a random character in cat ears",
        sub_cmd_name="randomize",
        sub_cmd_description="Get an image of random character of any gender in cat ears",
    )
    async def random_nekomimi_randomize(self, ctx: ipy.SlashContext):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["random"]["nekomimi"]
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
                name="min",
                description="Minimum value",
                required=False,
                type=ipy.OptionType.INTEGER,
            ),
            ipy.SlashCommandOption(
                name="max",
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
        min: int = 1,
        max: int = 10,
        base: int = 10,
    ):
        await ctx.defer()
        async with RandomOrg() as rand:
            numbers = await rand.integers(num=numbers, min=min, max=max, base=base)
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
        await ctx.defer()
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
