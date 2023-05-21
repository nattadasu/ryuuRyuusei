import re
from base64 import b64decode, b64encode
from urllib.parse import urlencode as urlenc
from datetime import datetime

import interactions as ipy
import validators
from plusminus import BaseArithmeticParser as BAP

from classes.isitdownrightnow import WebsiteChecker, WebsiteStatus
from classes.thecolorapi import Color, TheColorApi
from modules.commons import generate_utils_except_embed, snowflake_to_datetime
from modules.i18n import fetch_language_data, read_user_language


class Utilities(ipy.Extension):
    """Utilities commands"""

    def __init__(self, bot: ipy.AutoShardedClient):
        self.bot = bot

    @ipy.slash_command(
        name="utilities",
        description="Get some utilities you might need",
    )
    async def utilities(self, ctx: ipy.SlashContext):
        pass

    @utilities.subcommand(
        sub_cmd_name="math",
        sub_cmd_description="Evaluate a (safe) math expression",
        options=[
            ipy.SlashCommandOption(
                name="expression",
                description="The expression to evaluate",
                type=ipy.OptionType.STRING,
                required=True,
            )
        ],
    )
    async def utilities_math(self, ctx: ipy.SlashContext, expression: str):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["utilities"]
        try:
            exp = BAP().evaluate(expression)
            await ctx.send(
                embed=ipy.Embed(
                    title=l_["commons"]["result"],
                    color=0x996422,
                    fields=[
                        ipy.EmbedField(
                            name=l_["math"]["expression"],
                            value=f"```py\n{expression}```",
                            inline=False,
                        ),
                        ipy.EmbedField(
                            name=l_["commons"]["result"],
                            value=f"```py\n{exp}```",
                            inline=False,
                        ),
                    ],
                )
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    language=ul,
                    description=l_["math"]["exception"],
                    field_name=l_["math"]["expression"],
                    field_value=f"```py\n{expression}```",
                    error=e,
                )
            )

    @utilities.subcommand(
        sub_cmd_name="base64",
        sub_cmd_description="Encode/decode a string to/from base64",
        options=[
            ipy.SlashCommandOption(
                name="mode",
                description="The mode to use",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(name="Encode", value="encode"),
                    ipy.SlashCommandChoice(name="Decode", value="decode"),
                ],
            ),
            ipy.SlashCommandOption(
                name="string",
                description="The string to encode/decode",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def utilities_base64(self, ctx: ipy.SlashContext, mode: str, string: str):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["utilities"]
        try:
            if mode == "encode":
                res = b64encode(string.encode()).decode()
                strVal = f"""```md
    {string}
    ```"""
                resVal = f"""```{res}```"""
            else:
                res = b64decode(string.encode()).decode()
                strVal = f"""```{string}```"""
                resVal = f"""```md
    {res}
    ```"""
            await ctx.send(
                embed=ipy.Embed(
                    title=l_["commons"]["result"],
                    color=0x996422,
                    fields=[
                        ipy.EmbedField(
                            name=l_["base64"]["string"], value=strVal, inline=False
                        ),
                        ipy.EmbedField(
                            name=l_["commons"]["result"], value=resVal, inline=False
                        ),
                    ],
                )
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    language=ul,
                    description=l_["base64"]["exception"],
                    field_name=l_["commons"]["string"],
                    field_value=f"```{string}```",
                    error=e,
                )
            )

    @utilities.subcommand(
        sub_cmd_name="color",
        sub_cmd_description="Get information about a color",
        options=[
            ipy.SlashCommandOption(
                name="color_format",
                description="The format to use",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(name="Hex", value="hex"),
                    ipy.SlashCommandChoice(name="RGB", value="rgb"),
                    ipy.SlashCommandChoice(name="HSL", value="hsl"),
                    ipy.SlashCommandChoice(name="CMYK", value="cmyk"),
                ],
            ),
            ipy.SlashCommandOption(
                name="color_value",
                description="The color to get information about",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def utilities_color(
        self, ctx: ipy.SlashContext, color_format: str, color_value: str
    ):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["utilities"]
        res: dict = {}
        try:
            if (
                color_format == "hex"
                and re.match(r"^#?(?:[0-9a-fA-F]{3}){1,2}$", color_value) is None
            ):
                raise ValueError("Invalid hex color")
            if color_format == "hex" and re.match(r"^#", color_value) is None:
                color_value = f"#{color_value}"
            async with TheColorApi() as tca:
                match color_format:
                    case "hex":
                        res: Color = await tca.color(hex=color_value)
                    case "rgb":
                        res: Color = await tca.color(rgb=color_value)
                    case "hsl":
                        res: Color = await tca.color(hsl=color_value)
                    case "cmyk":
                        res: Color = await tca.color(cmyk=color_value)
            rgb = res.rgb
            col: int = (rgb.r << 16) + (rgb.g << 8) + rgb.b
            fields = [
                ipy.EmbedField(
                    name=l_["color"]["name"],
                    value=f"{res.name.value}",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="HEX",
                    value=f"```css\n{res.hex.value}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="RGB",
                    value=f"```css\n{res.rgb.value}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="HSL",
                    value=f"```css\n{res.hsl.value}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="HSV",
                    value=f"```css\n{res.hsv.value}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="CMYK",
                    value=f"```css\n{res.cmyk.value}\n```",
                    inline=True,
                ),
                ipy.EmbedField(name="DEC", value=f"```py\n{col}\n```", inline=True),
            ]
            embed = ipy.Embed(
                title=l_["commons"]["result"],
                color=col,
                fields=fields,
                footer=ipy.EmbedFooter(text=l_["color"]["powered"]),
            )
            embed.set_thumbnail(url=res.image.bare)
            await ctx.send(
                embed=embed,
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    language=ul,
                    description=l_["color"]["exception"],
                    field_name=l_["color"]["color"],
                    field_value=f"```{color_value}```",
                    error=e,
                )
            )

    @utilities.subcommand(
        sub_cmd_name="qrcode",
        sub_cmd_description="Generate a QR code",
        options=[
            ipy.SlashCommandOption(
                name="string",
                description="The string to encode",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="error_correction",
                description="The error correction level",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(name="Low (~7%, default)", value="L"),
                    ipy.SlashCommandChoice(name="Medium (~15%)", value="M"),
                    ipy.SlashCommandChoice(name="Quality (~25%)", value="Q"),
                    ipy.SlashCommandChoice(name="High (~30%)", value="H"),
                ],
            ),
        ],
    )
    async def utilities_qrcode(
        self, ctx: ipy.SlashContext, string: str, error_correction: str = "L"
    ):
        await ctx.defer()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["utilities"]
        try:
            params = {
                "data": string,
                "size": "500x500",
                "ecc": error_correction,
                "format": "jpg",
            }
            # convert params object to string
            params = urlenc(params)
            embed = ipy.Embed(
                title=l_["commons"]["result"],
                color=0x000000,
                fields=[
                    ipy.EmbedField(
                        name=l_["commons"]["string"],
                        value=f"```{string}```",
                        inline=False,
                    ),
                ],
                footer=ipy.EmbedFooter(text=l_["qrcode"]["powered"]),
            )
            embed.set_image(url=f"https://api.qrserver.com/v1/create-qr-code/?{params}")
            await ctx.send(
                embed=embed,
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    language=ul,
                    description=l_["qrcode"]["exception"],
                    field_name=l_["commons"]["string"],
                    field_value=f"```{string}```",
                    error=e,
                )
            )

    @utilities.subcommand(
        sub_cmd_name="snowflake",
        sub_cmd_description="Convert a Discord Snowflake to a timestamp",
        options=[
            ipy.SlashCommandOption(
                name="snowflake",
                description="The snowflake to convert",
                required=True,
                type=ipy.OptionType.STRING,
            )
        ],
    )
    async def utilities_snowflake(self, ctx: ipy.SlashContext, snowflake: str):
        """Convert a Discord Snowflake to a timestamp"""
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["utilities"]["snowflake"]
        tmsp = int(snowflake_to_datetime(int(snowflake)))
        await ctx.send(
            embed=ipy.Embed(
                title=l_["title"],
                description=l_["text"],
                color=0x1F1F1F,
                fields=[
                    ipy.EmbedField(
                        name=l_["snowflake"],
                        value=f"```py\n{snowflake}\n```",
                        inline=False,
                    ),
                    ipy.EmbedField(
                        name=l_["timestamp"], value=f"```py\n{tmsp}\n```", inline=False
                    ),
                    ipy.EmbedField(name=l_["date"], value=f"<t:{tmsp}:D>", inline=True),
                    ipy.EmbedField(
                        name=l_["full_date"], value=f"<t:{tmsp}:F>", inline=True
                    ),
                    ipy.EmbedField(
                        name=l_["relative"], value=f"<t:{tmsp}:R>", inline=True
                    ),
                ],
            )
        )

    @utilities.subcommand(
        group_name="site",
        group_description="Related to websites",
        sub_cmd_name="status",
        sub_cmd_description="Check the status of a website",
        options=[
            ipy.SlashCommandOption(
                name="url",
                description="The URL to check",
                required=True,
                type=ipy.OptionType.STRING,
            )
        ],
    )
    async def utilities_site_status(self, ctx: ipy.SlashContext, url: str):
        """Check the status of a website"""
        await ctx.defer()
        ul = read_user_language(ctx)
        err_msg: str = ""
        try:
            async with WebsiteChecker() as check:
                status: WebsiteStatus = await check.check_website(url)
                domain = status.url_checked
        except validators.ValidationFailure:
            err_msg = "Invalid URL"
        except BaseException as e:
            err_msg = str(e)

        if err_msg:
            await ctx.send(
                embed=generate_utils_except_embed(
                    language=ul,
                    description="Failed to check the status of the website",
                    field_name="URL",
                    field_value=f"```{url}```",
                    error=err_msg,
                )
            )
        else:
            embed = ipy.Embed(
                author=ipy.EmbedAuthor(
                    name="IsItDownRightNow",
                    url="https://isitdownrightnow.com/",
                ),
                url=f"https://{domain}",
                title=status.website_name,
                fields=[
                    ipy.EmbedField(
                        name="Status", value=status.status_message.title(), inline=True
                    ),
                    ipy.EmbedField(
                        name="Response Time", value=status.response_time, inline=True
                    ),
                    ipy.EmbedField(
                        name="Last Down", value=status.last_down, inline=True
                    ),
                ],
                color=0x566A82,
                footer=ipy.EmbedFooter(text="Powered by IsItDownRightNow"),
                timestamp=datetime.utcnow(),
            )

            embed.set_thumbnail(
                url=f"https://www.isitdownrightnow.com/screenshot/m/{domain}.jpg"
            )
            embed.set_image(url=f"https://www.isitdownrightnow.com/data/{domain}.png")

            await ctx.send(embed=embed)


def setup(bot):
    Utilities(bot)
