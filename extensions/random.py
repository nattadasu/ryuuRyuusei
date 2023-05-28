import re

import interactions as ipy

from classes.randomorg import ProviderHttpError, RandomOrg
from modules.const import (
    EMOJI_ATTENTIVE,
    EMOJI_DOUBTING,
    EMOJI_SUCCESS,
    EMOJI_UNEXPECTED_ERROR
)


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
        sub_cmd_name="8ball",
        sub_cmd_description="Get a random answer to your question",
        options=[
            ipy.SlashCommandOption(
                name="question",
                description="Your question",
                required=True,
                type=ipy.OptionType.STRING,
            ),
        ]
    )
    async def random_8ball(self, ctx: ipy.SlashContext, question: str):
        await ctx.defer()
        try:
            async with RandomOrg() as rand:
                numbers = await rand.integers(num=1, min_val=0, max_val=19, base=10)
        except ProviderHttpError:
            embed = ipy.Embed(
                title="Unexpected error",
                description="An unexpected error has occurred while trying to get a random number from random.org",
                color=0xFF0000,
            )
            embed.set_footer(text="Please try again later")
            emoji = re.sub(r"<:[a-zA-Z0-9_]+:([0-9]+)>", r"\1", EMOJI_UNEXPECTED_ERROR)
            embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png")
            await ctx.send(
                embed=embed,
            )
            return

        answers = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        ans = numbers[0]
        if ans >= 0 and ans < 5:
            emoji = EMOJI_SUCCESS
        elif ans >= 5 and ans < 10:
            emoji = EMOJI_ATTENTIVE
        elif ans >= 10 and ans < 15:
            emoji = EMOJI_DOUBTING
        elif ans >= 15 and ans < 20:
            emoji = EMOJI_UNEXPECTED_ERROR

        emoji = re.sub(r"<:[a-zA-Z0-9_]+:([0-9]+)>", r"\1", emoji)
        emoji_url=f"https://cdn.discordapp.com/emojis/{emoji}.png"

        embed = ipy.Embed(
            title="8ball",
            fields=[
                ipy.EmbedField(
                    name="Question",
                    value=f"{question}",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="My Answer",
                    value=f"**{answers[ans]}**",
                    inline=False,
                ),
            ],
            color=0x1F1F1F,
        )
        embed.set_thumbnail(url=emoji_url)
        await ctx.send(
            embed=embed,
        )


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
