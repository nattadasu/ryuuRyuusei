import re
from base64 import b64decode, b64encode
from datetime import datetime, timezone
from urllib.parse import urlencode as urlenc

import interactions as ipy
import validators  # type: ignore
from plusminus import BaseArithmeticParser as BAP  # type: ignore

from classes.isitdownrightnow import WebsiteChecker, WebsiteStatus
from classes.thecolorapi import Color, TheColorApi
from modules.commons import (
    generate_utils_except_embed,
    save_traceback_to_file,
    snowflake_to_datetime,
)


class Utilities(ipy.Extension):
    """Utilities commands"""

    utilities_head = ipy.SlashCommand(
        name="utilities",
        description="Get some utilities you might need",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
        ),
    )

    @utilities_head.subcommand(
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
        try:
            exp = BAP().evaluate(expression)
            await ctx.send(
                embed=ipy.Embed(
                    title="Math Expression",
                    color=0x996422,
                    fields=[
                        ipy.EmbedField(
                            name="Expression",
                            value=f"```py\n{expression}```",
                            inline=False,
                        ),
                        ipy.EmbedField(
                            name="Result",
                            value=f"```py\n{exp}```",
                            inline=False,
                        ),
                    ],
                )
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    description="An error occurred while evaluating the expression",
                    field_name="Expression",
                    field_value=f"```py\n{expression}```",
                    error=e,
                )
            )
            save_traceback_to_file("utilities_math", ctx.author, e)

    @utilities_head.subcommand(
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
                    title=f"Base64 {mode.title()}",
                    color=0x996422,
                    fields=[
                        ipy.EmbedField(name="String", value=strVal, inline=False),
                        ipy.EmbedField(name="Result", value=resVal, inline=False),
                    ],
                )
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    description=f"An error occurred while {mode}ing the string",
                    field_name="String",
                    field_value=f"```{string}```",
                    error=e,
                )
            )
            save_traceback_to_file("utilities_base64", ctx.author, e)

    @utilities_head.subcommand(
        sub_cmd_name="color",
        sub_cmd_description="Get information about a color",
        options=[
            ipy.SlashCommandOption(
                name="color_format",
                description="The format to use",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(name="ASS/SSA", value="ass"),
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
        res: dict = {}
        try:
            if (
                color_format == "hex"
                and re.match(r"^#?(?:[0-9a-fA-F]{3}){1,2}$", color_value) is None
            ):
                raise ValueError("Invalid hex color")
            if (
                color_format == "ass"
                and re.match(r"^&H[0-9a-fA-F]{6,8}&?$", color_value, re.IGNORECASE)
                is None
            ):
                raise ValueError(
                    "Invalid ASS color (expected &HBBGGRR& or &HAABBGGRR&)"
                )
            if color_format == "hex" and re.match(r"^#", color_value) is None:
                color_value = f"#{color_value}"
            if color_format == "ass":
                ass_hex = color_value.strip("&").replace("H", "").replace("h", "")
                if len(ass_hex) == 6:
                    b, g, r = ass_hex[0:2], ass_hex[2:4], ass_hex[4:6]
                else:
                    b, g, r = ass_hex[2:4], ass_hex[4:6], ass_hex[6:8]
                color_value = f"#{r}{g}{b}"
                color_format = "hex"
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
            ass_color = f"&H{rgb.b:02X}{rgb.g:02X}{rgb.r:02X}&"
            fields = [
                ipy.EmbedField(
                    name="Color name",
                    value=f"{res.name.value}",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="ASS/SSA",
                    value=f"```\n{ass_color}\n```",
                    inline=True,
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
                title="Color Information",
                color=col,
                fields=fields,
                footer=ipy.EmbedFooter(text="Powered by TheColorApi"),
            )
            embed.set_thumbnail(url=res.image.bare)
            await ctx.send(
                embed=embed,
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    description="An error occurred while getting information about the color from TheColorApi",
                    field_name="Color Value",
                    field_value=f"```{color_value}```",
                    error=e,
                )
            )
            save_traceback_to_file("utilities_color", ctx.author, e)

    @utilities_head.subcommand(
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
                title="QR Code",
                color=0x000000,
                fields=[
                    ipy.EmbedField(
                        name="String",
                        value=f"```{string}```",
                        inline=False,
                    ),
                ],
                footer=ipy.EmbedFooter(text="Powered by goQR.me"),
            )
            embed.set_image(url=f"https://api.qrserver.com/v1/create-qr-code/?{params}")
            await ctx.send(
                embed=embed,
            )
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    description="An error occurred while generating the QR code",
                    field_name="String",
                    field_value=f"```{string}```",
                    error=e,
                )
            )
            save_traceback_to_file("utilities_qrcode", ctx.author, e)

    @utilities_head.subcommand(
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
        try:
            bin_len = len(bin(int(snowflake)))
            # Check if the snowflake is valid
            if not snowflake.isdigit():
                raise ValueError("Invalid snowflake")
            # else, check for the bits size should be 64 from binary
            elif bin_len > 64:
                raise ValueError("Snowflake is too big, did you randomly generate it?")
            elif bin_len < 60:
                raise ValueError(
                    "Snowflake is too small, did you randomly generate it?"
                )
            tmsp = int(snowflake_to_datetime(int(snowflake)))
        except Exception as e:
            await ctx.send(
                embed=generate_utils_except_embed(
                    description="An error occurred while converting the snowflake to a timestamp",
                    field_name="Snowflake",
                    field_value=f"```{snowflake}```",
                    error=e,
                )
            )
            save_traceback_to_file("utilities_snowflake", ctx.author, e)
        await ctx.send(
            embed=ipy.Embed(
                title="Snowflake Information",
                description="Below is the information about the snowflake",
                color=0x1F1F1F,
                fields=[
                    ipy.EmbedField(
                        name="Snowflake",
                        value=f"```py\n{snowflake}\n```",
                        inline=False,
                    ),
                    ipy.EmbedField(
                        name="Timestamp", value=f"```py\n{tmsp}\n```", inline=False
                    ),
                    ipy.EmbedField(name="Date", value=f"<t:{tmsp}:D>", inline=True),
                    ipy.EmbedField(
                        name="Full Date", value=f"<t:{tmsp}:F>", inline=True
                    ),
                    ipy.EmbedField(name="Relative", value=f"<t:{tmsp}:R>", inline=True),
                ],
            )
        )

    @utilities_head.subcommand(
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
        err_msg: str = ""
        try:
            async with WebsiteChecker() as check:
                status: WebsiteStatus = await check.check_website(url)
                domain = status.url_checked
                domain = re.sub(r"https?://", "", domain)
                domain = re.sub(r"^www.", "", domain)
                lt = domain[0]
        except validators.ValidationFailure:
            err_msg = "Invalid URL"
        except BaseException as e:
            err_msg = str(e)

        if err_msg:
            await ctx.send(
                embed=generate_utils_except_embed(
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
                    url="https://www.isitdownrightnow.com/",
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
                timestamp=datetime.now(tz=timezone.utc),
            )

            embed.set_thumbnail(
                url=f"https://www.isitdownrightnow.com/screenshot/{lt}/{domain}.jpg"
            )
            # embed.set_image(
            #     url=f"https://www.isitdownrightnow.com/data/{domain}.png")
            # Data was out-of-date, so I'm not using it

            await ctx.send(embed=embed)


def setup(bot: ipy.Client):
    Utilities(bot)
