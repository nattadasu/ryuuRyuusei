import re
from datetime import datetime, timezone

import interactions as ipy
import pandas as pd
from fuzzywuzzy import fuzz

from classes.converter import Length, Mass, Temperature, Time, Volume
from classes.excepts import ProviderHttpError
from classes.exchangerateapi import ExchangeRateAPI, accepted_currencies
from modules.commons import (PlatformErrType, platform_exception_embed,
                             save_traceback_to_file)
from modules.const import EMOJI_SUCCESS, EMOJI_UNEXPECTED_ERROR
from modules.i18n import fetch_language_data, read_user_language

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


def result_embed(value: float, from_unit: str, to_unit: str,
                 result: int | list[float | str]) -> ipy.Embed:
    """Returns an embed for when the result is too large to be displayed"""
    from_unit = from_unit.replace("_", " ")
    to_unit = to_unit.replace("_", " ")
    if str(value).endswith(".0"):
        value = int(value)
    value = f"{value:,}"
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
        result[0] = f"{result[0]:,}"
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
        result = f"{result:,}"
        embed.add_field(
            name="Result",
            value=f"{result} {to_unit}",
            inline=True
        )

    return embed


def search_currency(query: str) -> list[dict[str, str]]:
    """
    Search for a currency using fuzzy search

    Args:
        query (str): The query to search for

    Returns:
        list[dict[str, str]]: The list of currencies that match the query
    """
    currencies = pd.read_csv(
        "database/supported_currencies.tsv", delimiter="\t")
    results = []
    for _, currency in currencies.iterrows():
        code_ratio = fuzz.token_set_ratio(query, currency["Currency Code"])
        name_ratio = fuzz.token_set_ratio(query, currency["Currency Name"])
        country_ratio = fuzz.token_set_ratio(query, currency["Country Name"])
        max_ratio = max(code_ratio, name_ratio, country_ratio)
        if max_ratio >= 70:  # minimum similarity threshold of 70%
            results.append({
                "name": f'{currency["Currency Name"]} ({currency["Currency Code"]})',
                "value": currency["Currency Code"],
            })
    return results[:25]


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
        except OverflowError as e:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_length", ctx.author, e)
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
        except OverflowError as e:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_mass", ctx.author, e)
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
        except OverflowError as e:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_temperature", ctx.author, e)
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
        except OverflowError as e:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_volume", ctx.author, e)
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
        except OverflowError as e:
            embed = overflow_embed(value, from_unit, to_unit)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_time", ctx.author, e)
        embed = result_embed(value, from_unit, to_unit, convert)
        await ctx.send(embed=embed)

    @converter_head.subcommand(
        sub_cmd_name="currency",
        sub_cmd_description="Exchange rates for currencies",
        options=[
            ipy.SlashCommandOption(
                name="value",
                description="The value to convert",
                type=ipy.OptionType.NUMBER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="from_currency",
                description="The currency to convert from",
                type=ipy.OptionType.STRING,
                required=True,
                autocomplete=True,
            ),
            ipy.SlashCommandOption(
                name="to_currency",
                description="The currency to convert to",
                type=ipy.OptionType.STRING,
                required=True,
                autocomplete=True,
            ),
        ],
    )
    async def convert_currency(
        self,
        ctx: ipy.SlashContext,
        value: float,
        from_currency: accepted_currencies,
        to_currency: accepted_currencies,
    ) -> None:
        await ctx.defer()
        lang = read_user_language(ctx)
        l_ = fetch_language_data(lang)
        try:
            async with ExchangeRateAPI() as api:
                convert_raw = await api.get_exchange_rate(
                    from_currency, to_currency, value
                )
                # only 2 decimal places
                convert = round(convert_raw.conversion_result, 3)
                embed = result_embed(value, from_currency,
                                     to_currency, convert)
                embed.set_footer(
                    text="Powered by ExchangeRate-API, data last fetched on"
                )
                embed.timestamp = datetime.fromtimestamp(
                    convert_raw.time_last_update_unix, tz=timezone.utc)
                await ctx.send(embed=embed)
        except ProviderHttpError as e:
            embed = platform_exception_embed(
                description="An error occurred while trying to get exchange rates from ExchangeRate-API.",
                error=f"{e}",
                lang_dict=l_,
                error_type=PlatformErrType.SYSTEM)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_currency", ctx.author, e)
        except OverflowError as e:
            embed = overflow_embed(value, from_currency, to_currency)
            await ctx.send(embed=embed)
            save_traceback_to_file("convert_length", ctx.author, e)

    @convert_currency.autocomplete(option_name="from_currency")
    @convert_currency.autocomplete(option_name="to_currency")
    async def autocomplete_currency(self, ctx: ipy.AutocompleteContext):
        choices = search_currency(ctx.input_text)
        await ctx.send(choices=choices)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    ConverterCog(bot)
