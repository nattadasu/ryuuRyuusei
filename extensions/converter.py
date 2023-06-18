import re

import interactions as ipy

from classes.converter import Length, Mass, Temperature, Time, Volume
from modules.const import EMOJI_SUCCESS, EMOJI_UNEXPECTED_ERROR

emoji_err = re.sub(r"(<:.*:)(\d+)(>)", r"\2", EMOJI_UNEXPECTED_ERROR)
emoji_success = re.sub(r"(<:.*:)(\d+)(>)", r"\2", EMOJI_SUCCESS)


def overflow_embed(value: float, from_unit: str, to_unit: str) -> ipy.Embed:
    """Returns an embed for when the result is too large to be displayed"""
    from_unit = from_unit.replace("_", " ")
    to_unit = to_unit.replace("_", " ").title()
    embed = ipy.Embed(
        title="Overflow",
        description="The result is too large to be displayed",
        color=0xFF1149,
        thumbnail=ipy.EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji_err}.png?v=1"
        ),
        fields=[
            ipy.EmbedField(
                name="Value",
                value=f"{value} {from_unit}",
                inline=True
            ),
            ipy.EmbedField(
                name="Unit",
                value=to_unit,
                inline=True
            )
        ]
    )
    return embed


def result_embed(value: float, from_unit: str, to_unit: str, result: int | list[float | str]) -> ipy.Embed:
    """Returns an embed for when the result is too large to be displayed"""
    from_unit = from_unit.replace("_", " ")
    to_unit = to_unit.replace("_", " ")
    if str(value).endswith(".0"):
        value = int(value)
    embed = ipy.Embed(
        title="Result",
        color=0x123388,
        thumbnail=ipy.EmbedAttachment(
            url=f"https://cdn.discordapp.com/emojis/{emoji_success}.png?v=1"
        ),
        fields=[
            ipy.EmbedField(
                name="Value",
                value=f"{value} {from_unit}",
                inline=True
            ),
        ]
    )

    if isinstance(result, list):
        if str(result[0]).endswith(".0"):
            result[0] = int(result[0])
        embed.add_fields(
            ipy.EmbedField(
                name="Result",
                value=f"{result[0]} {to_unit}",
                inline=True
            ),
            ipy.EmbedField(
                name="Context",
                value=f"{result[1]}",
                inline=False
            ),
        )
    else:
        if str(result).endswith(".0"):
            result = int(result)
        embed.add_field(
            name="Result",
            value=f"{result} {to_unit}",
            inline=True
        )

    return embed


class ConverterCog(ipy.Extension):
    """Converter cog for the bot"""

    converter_head = ipy.SlashCommand(
        name="converter",
        description="Converts units",
    )

    length_units: list[ipy.SlashCommandChoice] = [
        ipy.SlashCommandChoice("American football field", "football_field"),
        ipy.SlashCommandChoice("Banana (as a scale)", "banana"),
        ipy.SlashCommandChoice("Centimeter (cm)", "centimeter"),
        ipy.SlashCommandChoice("Chain", "chain"),
        ipy.SlashCommandChoice("Decameter (dam)", "decameter"),
        ipy.SlashCommandChoice("Decimeter (dm)", "decimeter"),
        ipy.SlashCommandChoice("Earth radius", "earth_radius"),
        ipy.SlashCommandChoice("Fathom", "fathom"),
        ipy.SlashCommandChoice("Foot (ft)", "foot"),
        ipy.SlashCommandChoice("Hectometer (hm)", "hectometer"),
        ipy.SlashCommandChoice("Inch (in)", "inch"),
        ipy.SlashCommandChoice("Kilometer (km)", "kilometer"),
        ipy.SlashCommandChoice("League", "league"),
        ipy.SlashCommandChoice("Light second", "light_second"),
        ipy.SlashCommandChoice("Lunar distance", "lunar_distance"),
        ipy.SlashCommandChoice("Meter (m)", "meter"),
        ipy.SlashCommandChoice("Mile (mi)", "mile"),
        ipy.SlashCommandChoice("Millimeter (mm)", "millimeter"),
        ipy.SlashCommandChoice("Myriameter (mym)", "myriameter"),
        ipy.SlashCommandChoice("Nautical mile (nmi)", "nautical_mile"),
        ipy.SlashCommandChoice("Rod", "rod"),
        ipy.SlashCommandChoice("Thou", "thou"),
        ipy.SlashCommandChoice("Yard (yd)", "yard"),
    ]

    length_units_extended = length_units + [
        ipy.SlashCommandChoice("Astronomical unit (au)", "astronomical_unit"),
        ipy.SlashCommandChoice("Light year (ly)", "light_year"),
    ]

    @converter_head.subcommand(
        sub_cmd_name="length",
        sub_cmd_description="Converts length units",
        options=[
            ipy.SlashCommandOption(
                name="value",
                description="The value to convert",
                type=ipy.OptionType.NUMBER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="from_unit",
                description="The unit to convert from",
                type=ipy.OptionType.STRING,
                required=True,
                choices=length_units_extended,
            ),
            ipy.SlashCommandOption(
                name="to_unit",
                description="The unit to convert to",
                type=ipy.OptionType.STRING,
                required=True,
                choices=length_units,
            ),
        ]
    )
    async def convert_length(self, ctx: ipy.SlashContext, value: float, from_unit: str, to_unit: str):
        await ctx.defer()
        try:
            convert = Length.convert(value, from_unit, to_unit)
        except OverflowError:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            return
        embed = result_embed(value, from_unit, to_unit, convert)
        await ctx.send(embed=embed)

    mass_units: list[ipy.SlashCommandChoice] = [
        ipy.SlashCommandChoice("Centigram (cg)", "centigram"),
        ipy.SlashCommandChoice("Decagram (dag)", "decagram"),
        ipy.SlashCommandChoice("Decigram (dg)", "decigram"),
        ipy.SlashCommandChoice("Gram (g)", "gram"),
        ipy.SlashCommandChoice("Hectogram (hg)", "hectogram"),
        ipy.SlashCommandChoice("Hundredweight (cwt)", "hundredweight"),
        ipy.SlashCommandChoice("Kilogram (kg)", "kilogram"),
        ipy.SlashCommandChoice("Metric ton (mt)", "metric_ton"),
        ipy.SlashCommandChoice("Milligram (mg)", "milligram"),
        ipy.SlashCommandChoice("Ounce (oz)", "ounce"),
        ipy.SlashCommandChoice("Pound (lb)", "pound"),
        ipy.SlashCommandChoice("Stone (st)", "stone"),
        ipy.SlashCommandChoice("Ton (t)", "ton"),
    ]

    @converter_head.subcommand(
        sub_cmd_name="mass",
        sub_cmd_description="Converts mass units",
        options=[
            ipy.SlashCommandOption(
                name="value",
                description="The value to convert",
                type=ipy.OptionType.NUMBER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="from_unit",
                description="The unit to convert from",
                type=ipy.OptionType.STRING,
                required=True,
                choices=mass_units,
            ),
            ipy.SlashCommandOption(
                name="to_unit",
                description="The unit to convert to",
                type=ipy.OptionType.STRING,
                required=True,
                choices=mass_units,
            ),
        ]
    )
    async def convert_mass(self, ctx: ipy.SlashContext, value: float, from_unit: str, to_unit: str):
        await ctx.defer()
        try:
            convert = Mass.convert(value, from_unit, to_unit)
        except OverflowError:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            return
        embed = result_embed(value, from_unit, to_unit, convert)
        await ctx.send(embed=embed)

    temperature_units: list[ipy.SlashCommandChoice] = [
        ipy.SlashCommandChoice("Celsius (°C)", "celsius"),
        ipy.SlashCommandChoice("Delisle (°De)", "delisle"),
        ipy.SlashCommandChoice("Fahrenheit (°F)", "fahrenheit"),
        ipy.SlashCommandChoice("Kelvin (K)", "kelvin"),
        ipy.SlashCommandChoice("Newton (°N)", "newton"),
        ipy.SlashCommandChoice("Rankine (°R)", "rankine"),
        ipy.SlashCommandChoice("Réaumur (°Ré)", "reaumur"),
        ipy.SlashCommandChoice("Rømer (°Rø)", "romer"),
    ]

    @converter_head.subcommand(
        sub_cmd_name="temperature",
        sub_cmd_description="Converts temperature units",
        options=[
            ipy.SlashCommandOption(
                name="value",
                description="The value to convert",
                type=ipy.OptionType.NUMBER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="from_unit",
                description="The unit to convert from",
                type=ipy.OptionType.STRING,
                required=True,
                choices=temperature_units,
            ),
            ipy.SlashCommandOption(
                name="to_unit",
                description="The unit to convert to",
                type=ipy.OptionType.STRING,
                required=True,
                choices=temperature_units,
            ),
        ]
    )
    async def convert_temperature(self, ctx: ipy.SlashContext, value: float, from_unit: str, to_unit: str):
        await ctx.defer()
        try:
            convert = Temperature.convert(value, from_unit, to_unit)
        except OverflowError:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            return
        embed = result_embed(value, from_unit, to_unit, convert)
        await ctx.send(embed=embed)

    volume_units: list[ipy.SlashCommandChoice] = [
        ipy.SlashCommandChoice("Centiliter (cl)", "centiliter"),
        ipy.SlashCommandChoice(
            "Milliliter (ml)/Cubic centimeter (cm³)", "milliliter"),
        ipy.SlashCommandChoice("Deciliter (dl)", "deciliter"),
        ipy.SlashCommandChoice("Liter (l)/Cubic decimeter (dm³)", "liter"),
        ipy.SlashCommandChoice("Hectoliter (hl)", "hectoliter"),
        ipy.SlashCommandChoice("Kiloliter (kl)", "kiloliter"),
        ipy.SlashCommandChoice("Teaspoon (tsp)", "teaspoon"),
        ipy.SlashCommandChoice("Tablespoon (tbsp)", "tablespoon"),
        ipy.SlashCommandChoice("Fluid ounce (fl oz)", "fluid_ounce"),
        ipy.SlashCommandChoice("Cup (c)", "cup"),
        ipy.SlashCommandChoice("Pint (pt)", "pint"),
        ipy.SlashCommandChoice("Quart (qt)", "quart"),
        ipy.SlashCommandChoice("Gallon (gal)", "gallon"),
    ]

    @converter_head.subcommand(
        sub_cmd_name="volume",
        sub_cmd_description="Converts volume units",
        options=[
            ipy.SlashCommandOption(
                name="value",
                description="The value to convert",
                type=ipy.OptionType.NUMBER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="from_unit",
                description="The unit to convert from",
                type=ipy.OptionType.STRING,
                required=True,
                choices=volume_units,
            ),
            ipy.SlashCommandOption(
                name="to_unit",
                description="The unit to convert to",
                type=ipy.OptionType.STRING,
                required=True,
                choices=volume_units,
            ),
        ]
    )
    async def convert_volume(self, ctx: ipy.SlashContext, value: float, from_unit: str, to_unit: str):
        await ctx.defer()
        try:
            convert = Volume.convert(value, from_unit, to_unit)
        except OverflowError:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            return
        embed = result_embed(value, from_unit, to_unit, convert)
        await ctx.send(embed=embed)

    time_units: list[ipy.SlashCommandChoice] = [
        ipy.SlashCommandChoice("Second (s)", "second"),
        ipy.SlashCommandChoice("Minute (min)", "minute"),
        ipy.SlashCommandChoice("Hour (h)", "hour"),
        ipy.SlashCommandChoice("Day (d)", "day"),
        ipy.SlashCommandChoice("Week (wk)", "week"),
        ipy.SlashCommandChoice("Month (mo)", "month"),
        ipy.SlashCommandChoice("Year (yr)", "year"),
        ipy.SlashCommandChoice("Decade (dec)", "decade"),
        ipy.SlashCommandChoice("Generation (gen)", "generation"),
        ipy.SlashCommandChoice("Century (cent)", "century"),
        ipy.SlashCommandChoice("Millennium (mill)", "millennium"),
    ]

    @converter_head.subcommand(
        sub_cmd_name="time",
        sub_cmd_description="Converts time units",
        options=[
            ipy.SlashCommandOption(
                name="value",
                description="The value to convert",
                type=ipy.OptionType.NUMBER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="from_unit",
                description="The unit to convert from",
                type=ipy.OptionType.STRING,
                required=True,
                choices=time_units,
            ),
            ipy.SlashCommandOption(
                name="to_unit",
                description="The unit to convert to",
                type=ipy.OptionType.STRING,
                required=True,
                choices=time_units,
            ),
        ]
    )
    async def convert_time(self, ctx: ipy.SlashContext, value: float, from_unit: str, to_unit: str):
        await ctx.defer()
        try:
            convert = Time.convert(value, from_unit, to_unit)
        except OverflowError:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            return
        embed = result_embed(value, from_unit, to_unit, convert)
        await ctx.send(embed=embed)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    ConverterCog(bot)
